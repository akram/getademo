#!/usr/bin/env python3
"""
MCP Multiplexer - Routes tool calls to multiple MCP servers

This multiplexer runs multiple MCP servers as subprocesses and presents
a unified interface with all tools from all servers. Tool calls are routed
to the appropriate server based on tool name.

Usage:
    python -m recorder.mcp_multiplexer
    
Or via the 'recorder-multi' command after installation.
"""

import asyncio
import json
import sys
import os
from typing import Optional
from dataclasses import dataclass, field

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent


@dataclass
class ChildMCP:
    """Represents a child MCP server process."""
    name: str
    command: list[str]
    process: Optional[asyncio.subprocess.Process] = None
    tools: dict[str, dict] = field(default_factory=dict)
    request_id: int = 0
    pending_requests: dict[int, asyncio.Future] = field(default_factory=dict)
    read_task: Optional[asyncio.Task] = None


class MCPMultiplexer:
    """Multiplexes multiple MCP servers into a single interface."""
    
    def __init__(self):
        self.children: dict[str, ChildMCP] = {}
        self.tool_to_child: dict[str, str] = {}  # tool_name -> child_name
        self.server = Server("mcp-multiplexer")
        self._setup_handlers()
    
    def _setup_handlers(self):
        """Set up MCP server handlers."""
        
        @self.server.list_tools()
        async def list_tools() -> list[Tool]:
            """Return all tools from all child MCPs."""
            all_tools = []
            for child_name, child in self.children.items():
                for tool_name, tool_def in child.tools.items():
                    all_tools.append(Tool(
                        name=tool_name,
                        description=tool_def.get("description", ""),
                        inputSchema=tool_def.get("inputSchema", {"type": "object", "properties": {}})
                    ))
            return all_tools
        
        @self.server.call_tool()
        async def call_tool(name: str, arguments: dict) -> list[TextContent]:
            """Route tool call to the appropriate child MCP."""
            if name not in self.tool_to_child:
                return [TextContent(type="text", text=f"Unknown tool: {name}")]
            
            child_name = self.tool_to_child[name]
            child = self.children[child_name]
            
            try:
                result = await self._call_child_tool(child, name, arguments)
                return result
            except Exception as e:
                return [TextContent(type="text", text=f"Error calling {name}: {str(e)}")]
    
    async def _send_request(self, child: ChildMCP, method: str, params: dict = None) -> dict:
        """Send a JSON-RPC request to a child MCP and wait for response."""
        if child.process is None or child.process.stdin is None:
            raise RuntimeError(f"Child {child.name} not running")
        
        child.request_id += 1
        request_id = child.request_id
        
        request = {
            "jsonrpc": "2.0",
            "id": request_id,
            "method": method,
        }
        if params:
            request["params"] = params
        
        # Create future for response
        future = asyncio.get_event_loop().create_future()
        child.pending_requests[request_id] = future
        
        # Send request
        request_line = json.dumps(request) + "\n"
        child.process.stdin.write(request_line.encode())
        await child.process.stdin.drain()
        
        # Wait for response with timeout
        try:
            response = await asyncio.wait_for(future, timeout=120.0)
            return response
        except asyncio.TimeoutError:
            child.pending_requests.pop(request_id, None)
            raise RuntimeError(f"Timeout waiting for response from {child.name}")
    
    async def _read_child_output(self, child: ChildMCP):
        """Continuously read output from child MCP."""
        if child.process is None or child.process.stdout is None:
            return
        
        buffer = b""
        while True:
            try:
                chunk = await child.process.stdout.read(4096)
                if not chunk:
                    break
                
                buffer += chunk
                
                # Process complete lines
                while b"\n" in buffer:
                    line, buffer = buffer.split(b"\n", 1)
                    if not line.strip():
                        continue
                    
                    try:
                        message = json.loads(line.decode())
                        
                        # Handle response
                        if "id" in message and message["id"] in child.pending_requests:
                            future = child.pending_requests.pop(message["id"])
                            if not future.done():
                                future.set_result(message)
                        # Handle notification (log to stderr for debugging)
                        elif "method" in message:
                            pass  # Ignore notifications for now
                    except json.JSONDecodeError:
                        pass  # Ignore non-JSON output
            except Exception as e:
                print(f"Error reading from {child.name}: {e}", file=sys.stderr)
                break
    
    async def _start_child(self, name: str, command: list[str]) -> ChildMCP:
        """Start a child MCP server process."""
        child = ChildMCP(name=name, command=command)
        
        # Set up environment
        env = os.environ.copy()
        
        # Start process
        child.process = await asyncio.create_subprocess_exec(
            *command,
            stdin=asyncio.subprocess.PIPE,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            env=env
        )
        
        # Start reading output in background
        child.read_task = asyncio.create_task(self._read_child_output(child))
        
        # Give it a moment to start
        await asyncio.sleep(0.5)
        
        # Initialize the MCP connection
        init_response = await self._send_request(child, "initialize", {
            "protocolVersion": "2024-11-05",
            "capabilities": {},
            "clientInfo": {
                "name": "mcp-multiplexer",
                "version": "1.0.0"
            }
        })
        
        # Send initialized notification
        initialized_msg = json.dumps({
            "jsonrpc": "2.0",
            "method": "notifications/initialized"
        }) + "\n"
        child.process.stdin.write(initialized_msg.encode())
        await child.process.stdin.drain()
        
        # Get tools list
        tools_response = await self._send_request(child, "tools/list", {})
        
        if "result" in tools_response and "tools" in tools_response["result"]:
            for tool in tools_response["result"]["tools"]:
                tool_name = tool["name"]
                child.tools[tool_name] = tool
                self.tool_to_child[tool_name] = name
        
        self.children[name] = child
        print(f"Started {name} with {len(child.tools)} tools", file=sys.stderr)
        return child
    
    async def _call_child_tool(self, child: ChildMCP, tool_name: str, arguments: dict) -> list[TextContent]:
        """Call a tool on a child MCP."""
        response = await self._send_request(child, "tools/call", {
            "name": tool_name,
            "arguments": arguments
        })
        
        if "error" in response:
            error = response["error"]
            return [TextContent(type="text", text=f"Error: {error.get('message', str(error))}")]
        
        if "result" in response:
            result = response["result"]
            contents = []
            
            # Handle content array
            if "content" in result:
                for item in result["content"]:
                    if item.get("type") == "text":
                        contents.append(TextContent(type="text", text=item.get("text", "")))
                    elif item.get("type") == "image":
                        # Pass through image content
                        contents.append(TextContent(type="text", text=f"[Image: {item.get('mimeType', 'image/png')}]"))
                    else:
                        contents.append(TextContent(type="text", text=json.dumps(item)))
            else:
                contents.append(TextContent(type="text", text=json.dumps(result)))
            
            return contents if contents else [TextContent(type="text", text="OK")]
        
        return [TextContent(type="text", text="No result")]
    
    async def start(self, child_configs: list[tuple[str, list[str]]]):
        """Start the multiplexer with the given child MCP configurations."""
        # Start all children
        for name, command in child_configs:
            try:
                await self._start_child(name, command)
            except Exception as e:
                print(f"Failed to start {name}: {e}", file=sys.stderr)
        
        print(f"Multiplexer ready with {len(self.tool_to_child)} total tools", file=sys.stderr)
        
        # Run the MCP server
        async with stdio_server() as (read_stream, write_stream):
            await self.server.run(
                read_stream,
                write_stream,
                self.server.create_initialization_options()
            )
    
    async def stop(self):
        """Stop all child processes."""
        for child in self.children.values():
            if child.process:
                child.process.terminate()
                try:
                    await asyncio.wait_for(child.process.wait(), timeout=5.0)
                except asyncio.TimeoutError:
                    child.process.kill()
            if child.read_task:
                child.read_task.cancel()


async def main():
    """Main entry point for the multiplexer."""
    # Configure child MCPs
    children = [
        ("playwright", ["npx", "@playwright/mcp", "--browser", "firefox"]),
        ("demo-recorder", ["python", "-m", "recorder.server"]),
    ]
    
    multiplexer = MCPMultiplexer()
    
    try:
        await multiplexer.start(children)
    except KeyboardInterrupt:
        pass
    finally:
        await multiplexer.stop()


def run():
    """Entry point for console script."""
    asyncio.run(main())


if __name__ == "__main__":
    run()








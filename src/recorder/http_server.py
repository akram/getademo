#!/usr/bin/env python3
"""
HTTP/SSE Server for Demo Recorder MCP

Exposes the MCP server over HTTP using Server-Sent Events (SSE) transport.
This allows remote clients to connect to the MCP server over the internet.

Usage:
    python -m recorder.http_server
    # or
    uv run recorder-http
"""

import asyncio
import logging
import os
from contextlib import asynccontextmanager

from starlette.applications import Starlette
from starlette.routing import Route
from starlette.responses import JSONResponse

from mcp.server.sse import SseServerTransport
from recorder.server import server

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# SSE transport instance
sse_transport = SseServerTransport("/messages/")


@asynccontextmanager
async def lifespan(app):
    """Application lifespan context manager."""
    logger.info("Demo Recorder MCP HTTP Server starting...")
    yield
    logger.info("Demo Recorder MCP HTTP Server shutting down...")


async def handle_sse(request):
    """Handle SSE connection for MCP communication."""
    logger.info(f"New SSE connection from {request.client.host}")
    
    async with sse_transport.connect_sse(
        request.scope, request.receive, request._send
    ) as streams:
        await server.run(
            streams[0],
            streams[1],
            server.create_initialization_options()
        )


async def handle_messages(request):
    """Handle incoming MCP messages via POST."""
    await sse_transport.handle_post_message(
        request.scope, request.receive, request._send
    )


async def health_check(request):
    """Health check endpoint."""
    return JSONResponse({
        "status": "healthy",
        "service": "demo-recorder-mcp",
        "version": "0.1.0"
    })


async def info(request):
    """Info endpoint with MCP server details."""
    return JSONResponse({
        "name": "demo-recorder-mcp",
        "description": "MCP server for recording browser demos with video, audio sync, and TTS",
        "transport": "sse",
        "endpoints": {
            "sse": "/sse",
            "messages": "/messages/",
            "health": "/health"
        },
        "tools_count": 13
    })


# Create Starlette app with routes
app = Starlette(
    debug=os.environ.get("DEBUG", "false").lower() == "true",
    lifespan=lifespan,
    routes=[
        Route("/sse", endpoint=handle_sse),
        Route("/messages/", endpoint=handle_messages, methods=["POST"]),
        Route("/health", endpoint=health_check),
        Route("/", endpoint=info),
    ],
)


def main():
    """Run the HTTP server."""
    import uvicorn
    
    host = os.environ.get("MCP_HOST", "0.0.0.0")
    port = int(os.environ.get("MCP_PORT", "8080"))
    
    logger.info(f"Starting Demo Recorder MCP HTTP Server on {host}:{port}")
    logger.info(f"SSE endpoint: http://{host}:{port}/sse")
    logger.info(f"Messages endpoint: http://{host}:{port}/messages/")
    
    uvicorn.run(
        app,
        host=host,
        port=port,
        log_level="info",
        access_log=True
    )


if __name__ == "__main__":
    main()


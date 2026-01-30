#!/usr/bin/env python3
"""
getademo - MCP Server for Demo Recording

Provides tools for:
- Screen recording (start/stop)
- Text-to-speech generation (OpenAI or Edge TTS)
- Video/audio composition (merge, replace audio, trim)
"""

import asyncio
import json
import os
import subprocess
import sys
import tempfile
from datetime import datetime
from pathlib import Path
from typing import Optional

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent

from .protocol import (
    get_protocol,
    get_planning_guide,
    get_setup_guide,
    get_recording_guide,
    get_assembly_guide,
)
from . import window_manager

# Global state for recording
_recording_process: Optional[subprocess.Popen] = None
_recording_path: Optional[Path] = None
_recording_start_time: Optional[datetime] = None


def get_ffmpeg_path() -> str:
    """Find ffmpeg executable."""
    # Common paths
    paths = [
        "/opt/homebrew/bin/ffmpeg",
        "/usr/local/bin/ffmpeg",
        "/usr/bin/ffmpeg",
        "ffmpeg"
    ]
    for path in paths:
        try:
            subprocess.run([path, "-version"], capture_output=True, check=True)
            return path
        except (subprocess.CalledProcessError, FileNotFoundError):
            continue
    raise RuntimeError("ffmpeg not found. Please install: brew install ffmpeg")


def get_screen_capture_args(screen_index: int = 1) -> list[str]:
    """Get platform-specific FULL SCREEN capture arguments for ffmpeg.
    
    Args:
        screen_index: Screen device index for macOS (1=first screen, 2=second screen).
                     Use ffmpeg -f avfoundation -list_devices true -i "" to list devices.
    """
    if sys.platform == "darwin":  # macOS
        # macOS uses AVFoundation - device indices are listed with -list_devices true
        # Typically: 0=FaceTime Camera, 1=Capture screen 0, 2=Capture screen 1
        return [
            "-f", "avfoundation",
            "-capture_cursor", "1",
            "-framerate", "30",
            "-pixel_format", "uyvy422",
            "-i", f"{screen_index}:none",  # Screen index:audio (none = no audio)
        ]
    elif sys.platform == "linux":
        display = os.environ.get("DISPLAY", ":0")
        return [
            "-f", "x11grab",
            "-i", f"{display}.0",
        ]
    elif sys.platform == "win32":
        return [
            "-f", "gdigrab",
            "-i", "desktop",
        ]
    else:
        raise RuntimeError(f"Unsupported platform: {sys.platform}")


def get_region_capture_args(x: int, y: int, width: int, height: int, screen_index: int = 1) -> list[str]:
    """Get platform-specific REGION capture arguments for ffmpeg.
    
    Args:
        x: X coordinate of top-left corner
        y: Y coordinate of top-left corner
        width: Width of capture region
        height: Height of capture region
        screen_index: Screen device index (macOS only)
    """
    if sys.platform == "darwin":  # macOS
        # AVFoundation doesn't support region directly, capture full and crop
        return [
            "-f", "avfoundation",
            "-capture_cursor", "1",
            "-framerate", "30",
            "-pixel_format", "uyvy422",
            "-i", f"{screen_index}:none",
        ], f"crop={width}:{height}:{x}:{y}"  # Returns args and crop filter
    elif sys.platform == "linux":
        display = os.environ.get("DISPLAY", ":0")
        return [
            "-f", "x11grab",
            "-video_size", f"{width}x{height}",
            "-i", f"{display}.0+{x},{y}",
        ], None
    elif sys.platform == "win32":
        return [
            "-f", "gdigrab",
            "-offset_x", str(x),
            "-offset_y", str(y),
            "-video_size", f"{width}x{height}",
            "-i", "desktop",
        ], None
    else:
        raise RuntimeError(f"Unsupported platform: {sys.platform}")


def get_window_capture_args(window_title: str) -> tuple[list[str], Optional[str], Optional[str]]:
    """Get platform-specific WINDOW capture arguments for ffmpeg.
    
    Args:
        window_title: Window title pattern to match
        
    Returns:
        Tuple of (ffmpeg_args, crop_filter, error_message)
        If error_message is set, the other values should be ignored.
    """
    if sys.platform == "darwin":  # macOS
        # Get the CGWindowID for the window
        window_id = window_manager.get_window_id(window_title)
        if not window_id:
            return [], None, f"Window '{window_title}' not found. Use list_windows to see available windows."
        
        # Use screencapture to capture specific window, pipe to ffmpeg
        # Unfortunately, ffmpeg AVFoundation doesn't support window capture directly
        # We'll use a workaround: focus the window and capture full screen
        # Or use region-based capture with window bounds
        try:
            bounds = window_manager.get_window_bounds(window_title)
            # Use region capture with the window's bounds
            args, crop = get_region_capture_args(bounds.x, bounds.y, bounds.width, bounds.height)
            return args, crop, None
        except Exception as e:
            return [], None, f"Could not get window bounds: {e}"
    
    elif sys.platform == "linux":
        # Linux x11grab can capture by window ID
        window_id = window_manager.get_window_id(window_title)
        if not window_id:
            return [], None, f"Window '{window_title}' not found. Use list_windows to see available windows."
        
        # Get window bounds for proper sizing
        try:
            bounds = window_manager.get_window_bounds(window_title)
            display = os.environ.get("DISPLAY", ":0")
            return [
                "-f", "x11grab",
                "-video_size", f"{bounds.width}x{bounds.height}",
                "-i", f"{display}.0+{bounds.x},{bounds.y}",
            ], None, None
        except Exception as e:
            return [], None, f"Could not get window bounds: {e}"
    
    elif sys.platform == "win32":
        # Windows gdigrab supports capture by window title
        return [
            "-f", "gdigrab",
            "-i", f"title={window_title}",
        ], None, None
    
    else:
        return [], None, f"Unsupported platform: {sys.platform}"


# Create the MCP server
server = Server("getademo")


@server.list_tools()
async def list_tools() -> list[Tool]:
    """List available tools."""
    return [
        Tool(
            name="start_recording",
            description="Start recording. Supports multiple capture modes: full screen, specific window by title, or a screen region. Returns immediately while recording runs in background.",
            inputSchema={
                "type": "object",
                "properties": {
                    "output_path": {
                        "type": "string",
                        "description": "Full path where the video will be saved (e.g., /path/to/demo.mp4)"
                    },
                    "capture_mode": {
                        "type": "string",
                        "enum": ["screen", "window", "region"],
                        "description": "What to capture: 'screen' (full screen), 'window' (specific window by title), 'region' (x,y,w,h area). Default: screen",
                        "default": "screen"
                    },
                    "window_title": {
                        "type": "string",
                        "description": "Window title pattern (regex) - required for 'window' mode. E.g., 'Chrome.*', 'Simulator', 'Firefox'"
                    },
                    "capture_region": {
                        "type": "object",
                        "properties": {
                            "x": {"type": "integer", "description": "X coordinate of top-left corner"},
                            "y": {"type": "integer", "description": "Y coordinate of top-left corner"},
                            "width": {"type": "integer", "description": "Width of capture region"},
                            "height": {"type": "integer", "description": "Height of capture region"}
                        },
                        "description": "Screen region to capture - required for 'region' mode. Use get_window_bounds to get values."
                    },
                    "width": {
                        "type": "integer",
                        "description": "Output width in pixels (default: 1920). For region mode, defaults to region width.",
                        "default": 1920
                    },
                    "height": {
                        "type": "integer",
                        "description": "Output height in pixels (default: 1080). For region mode, defaults to region height.",
                        "default": 1080
                    },
                    "fps": {
                        "type": "integer",
                        "description": "Frames per second (default: 30)",
                        "default": 30
                    },
                    "screen_index": {
                        "type": "integer",
                        "description": "Screen device index for 'screen' mode (macOS: 1=screen 0, 2=screen 1; default: 1)",
                        "default": 1
                    }
                },
                "required": ["output_path"]
            }
        ),
        Tool(
            name="stop_recording",
            description="Stop the current screen recording and save the file.",
            inputSchema={
                "type": "object",
                "properties": {},
                "required": []
            }
        ),
        Tool(
            name="recording_status",
            description="Check if recording is in progress and get details.",
            inputSchema={
                "type": "object",
                "properties": {},
                "required": []
            }
        ),
        Tool(
            name="text_to_speech",
            description="Convert text to speech audio file using OpenAI TTS or Edge TTS.",
            inputSchema={
                "type": "object",
                "properties": {
                    "text": {
                        "type": "string",
                        "description": "The text to convert to speech"
                    },
                    "output_path": {
                        "type": "string",
                        "description": "Full path where the audio will be saved (e.g., /path/to/voiceover.mp3)"
                    },
                    "voice": {
                        "type": "string",
                        "description": "Voice to use. OpenAI: alloy, echo, fable, onyx, nova, shimmer. Edge: en-US-AriaNeural, en-US-GuyNeural, etc.",
                        "default": "onyx"
                    },
                    "engine": {
                        "type": "string",
                        "enum": ["openai", "edge"],
                        "description": "TTS engine to use (default: openai if API key available, else edge)",
                        "default": "openai"
                    },
                    "api_key": {
                        "type": "string",
                        "description": "OpenAI API key (optional, uses OPENAI_API_KEY env var if not provided)"
                    }
                },
                "required": ["text", "output_path"]
            }
        ),
        Tool(
            name="replace_video_audio",
            description="Replace the audio track in a video with a new audio file.",
            inputSchema={
                "type": "object",
                "properties": {
                    "video_path": {
                        "type": "string",
                        "description": "Path to the input video file"
                    },
                    "audio_path": {
                        "type": "string",
                        "description": "Path to the new audio file"
                    },
                    "output_path": {
                        "type": "string",
                        "description": "Path for the output video with new audio"
                    },
                    "audio_start_time": {
                        "type": "number",
                        "description": "When to start the audio in the video (seconds, default: 0)",
                        "default": 0
                    },
                    "trim_to_audio": {
                        "type": "boolean",
                        "description": "Trim video to match audio duration exactly (default: true for sync)",
                        "default": True
                    }
                },
                "required": ["video_path", "audio_path", "output_path"]
            }
        ),
        Tool(
            name="merge_audio_tracks",
            description="Merge multiple audio files with specified start times onto a video.",
            inputSchema={
                "type": "object",
                "properties": {
                    "video_path": {
                        "type": "string",
                        "description": "Path to the input video file"
                    },
                    "audio_tracks": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "path": {"type": "string", "description": "Path to audio file"},
                                "start_time": {"type": "number", "description": "Start time in seconds"}
                            },
                            "required": ["path", "start_time"]
                        },
                        "description": "List of audio tracks with their start times"
                    },
                    "output_path": {
                        "type": "string",
                        "description": "Path for the output video"
                    },
                    "keep_original_audio": {
                        "type": "boolean",
                        "description": "Keep the original video audio (default: false)",
                        "default": False
                    }
                },
                "required": ["video_path", "audio_tracks", "output_path"]
            }
        ),
        Tool(
            name="trim_video",
            description="Trim a video to a specific time range.",
            inputSchema={
                "type": "object",
                "properties": {
                    "video_path": {
                        "type": "string",
                        "description": "Path to the input video file"
                    },
                    "output_path": {
                        "type": "string",
                        "description": "Path for the trimmed video"
                    },
                    "start_time": {
                        "type": "number",
                        "description": "Start time in seconds (default: 0)",
                        "default": 0
                    },
                    "end_time": {
                        "type": "number",
                        "description": "End time in seconds (optional, trims to end if not specified)"
                    },
                    "duration": {
                        "type": "number",
                        "description": "Duration in seconds (alternative to end_time)"
                    }
                },
                "required": ["video_path", "output_path"]
            }
        ),
        Tool(
            name="get_media_info",
            description="Get information about a video or audio file (duration, resolution, etc.).",
            inputSchema={
                "type": "object",
                "properties": {
                    "file_path": {
                        "type": "string",
                        "description": "Path to the media file"
                    }
                },
                "required": ["file_path"]
            }
        ),
        Tool(
            name="concatenate_videos",
            description="Concatenate multiple videos into one.",
            inputSchema={
                "type": "object",
                "properties": {
                    "video_paths": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "List of video file paths in order"
                    },
                    "output_path": {
                        "type": "string",
                        "description": "Path for the concatenated video"
                    }
                },
                "required": ["video_paths", "output_path"]
            }
        ),
        Tool(
            name="get_audio_duration",
            description="Get the exact duration of an audio file in seconds. Useful for synchronizing video length with audio.",
            inputSchema={
                "type": "object",
                "properties": {
                    "audio_path": {
                        "type": "string",
                        "description": "Path to the audio file"
                    }
                },
                "required": ["audio_path"]
            }
        ),
        Tool(
            name="adjust_video_to_audio_length",
            description="SPEED UP or SLOW DOWN video to match audio length exactly. Does NOT cut/trim - ALL visual content is preserved. Video longer than audio = speeds up. Video shorter than audio = slows down. MANDATORY for each step's audio-video sync.",
            inputSchema={
                "type": "object",
                "properties": {
                    "video_path": {
                        "type": "string",
                        "description": "Path to the input video file"
                    },
                    "audio_path": {
                        "type": "string",
                        "description": "Path to the audio file (determines target duration)"
                    },
                    "output_path": {
                        "type": "string",
                        "description": "Path for the output video with adjusted speed"
                    },
                    "add_audio": {
                        "type": "boolean",
                        "description": "Merge the audio into the output video (default: true)",
                        "default": True
                    }
                },
                "required": ["video_path", "audio_path", "output_path"]
            }
        ),
        # Phase-based Protocol Tools (recommended)
        Tool(
            name="get_demo_planning_guide",
            description="Phase 1: Learn how to plan and script your demo. Call this FIRST. Returns structure, timing, script writing guidelines, and demo templates. (~200 lines)",
            inputSchema={
                "type": "object",
                "properties": {},
                "required": []
            }
        ),
        Tool(
            name="get_recording_setup_guide",
            description="Phase 2: Pre-recording checklist and setup. Window management, viewport optimization, multi-monitor setup, screen verification. Call after planning. (~250 lines)",
            inputSchema={
                "type": "object",
                "properties": {},
                "required": []
            }
        ),
        Tool(
            name="get_recording_actions_guide",
            description="Phase 3: What to do DURING recording. Interactive actions (scrolling, clicking, typing), pacing, screenshot verification. CRITICAL for engaging demos that aren't boring. (~200 lines)",
            inputSchema={
                "type": "object",
                "properties": {},
                "required": []
            }
        ),
        Tool(
            name="get_video_assembly_guide",
            description="Phase 4: Post-recording assembly. Audio sync, timing verification, concatenation, quality checks, troubleshooting common issues. (~250 lines)",
            inputSchema={
                "type": "object",
                "properties": {},
                "required": []
            }
        ),
        # Deprecated - kept for backwards compatibility
        Tool(
            name="get_demo_protocol",
            description="DEPRECATED: This returns too much info at once. Use phase-based tools instead: get_demo_planning_guide -> get_recording_setup_guide -> get_recording_actions_guide -> get_video_assembly_guide",
            inputSchema={
                "type": "object",
                "properties": {},
                "required": []
            }
        ),
        # Window Management Tools
        Tool(
            name="list_windows",
            description="List all visible windows on the system. Returns window titles, IDs, PIDs, and bounds. Useful for finding the correct window title pattern before recording.",
            inputSchema={
                "type": "object",
                "properties": {},
                "required": []
            }
        ),
        Tool(
            name="focus_window",
            description="Bring a window to the foreground by title pattern. Use before screen recording to ensure the target window is visible. The pattern is a case-insensitive regex.",
            inputSchema={
                "type": "object",
                "properties": {
                    "title_pattern": {
                        "type": "string",
                        "description": "Regex pattern to match window title (e.g., 'Chrome.*', 'Simulator', 'Firefox')"
                    }
                },
                "required": ["title_pattern"]
            }
        ),
        Tool(
            name="get_window_bounds",
            description="Get the position and size of a window by title pattern. Returns x, y, width, height. Useful for region-based recording.",
            inputSchema={
                "type": "object",
                "properties": {
                    "title_pattern": {
                        "type": "string",
                        "description": "Regex pattern to match window title (e.g., 'Chrome.*', 'Simulator')"
                    }
                },
                "required": ["title_pattern"]
            }
        ),
        Tool(
            name="check_window_tools",
            description="Check if window management tools are available on this system. Returns platform info and any missing dependencies.",
            inputSchema={
                "type": "object",
                "properties": {},
                "required": []
            }
        ),
        Tool(
            name="list_screens",
            description="List all available screens/displays with their index, resolution, and position. Use this for multi-monitor setups to find the correct screen_index for recording. On macOS: index 1 is usually the main/built-in display, index 2+ are external displays.",
            inputSchema={
                "type": "object",
                "properties": {},
                "required": []
            }
        ),
    ]


@server.call_tool()
async def call_tool(name: str, arguments: dict) -> list[TextContent]:
    """Handle tool calls."""
    global _recording_process, _recording_path, _recording_start_time
    
    try:
        if name == "start_recording":
            return await _start_recording(arguments)
        
        elif name == "stop_recording":
            return await _stop_recording()
        
        elif name == "recording_status":
            return await _recording_status()
        
        elif name == "text_to_speech":
            return await _text_to_speech(arguments)
        
        elif name == "replace_video_audio":
            return await _replace_video_audio(arguments)
        
        elif name == "merge_audio_tracks":
            return await _merge_audio_tracks(arguments)
        
        elif name == "trim_video":
            return await _trim_video(arguments)
        
        elif name == "get_media_info":
            return await _get_media_info(arguments)
        
        elif name == "concatenate_videos":
            return await _concatenate_videos(arguments)
        
        elif name == "get_audio_duration":
            return await _get_audio_duration_tool(arguments)
        
        elif name == "adjust_video_to_audio_length":
            return await _adjust_video_to_audio_length(arguments)
        
        # Phase-based Protocol Tools
        elif name == "get_demo_planning_guide":
            return [TextContent(type="text", text=get_planning_guide())]
        
        elif name == "get_recording_setup_guide":
            return [TextContent(type="text", text=get_setup_guide())]
        
        elif name == "get_recording_actions_guide":
            return [TextContent(type="text", text=get_recording_guide())]
        
        elif name == "get_video_assembly_guide":
            return [TextContent(type="text", text=get_assembly_guide())]
        
        elif name == "get_demo_protocol":
            # Deprecated - returns notice pointing to new tools
            return [TextContent(type="text", text=get_protocol())]
        
        # Window Management Tools
        elif name == "list_windows":
            return await _list_windows()
        
        elif name == "focus_window":
            return await _focus_window(arguments)
        
        elif name == "get_window_bounds":
            return await _get_window_bounds_tool(arguments)
        
        elif name == "check_window_tools":
            return await _check_window_tools()
        
        elif name == "list_screens":
            return await _list_screens()
        
        else:
            return [TextContent(type="text", text=f"Unknown tool: {name}")]
    
    except Exception as e:
        return [TextContent(type="text", text=f"Error: {str(e)}")]


async def _start_recording(args: dict) -> list[TextContent]:
    """Start recording with support for multiple capture modes."""
    global _recording_process, _recording_path, _recording_start_time
    
    if _recording_process is not None and _recording_process.poll() is None:
        return [TextContent(type="text", text="Recording already in progress. Stop it first.")]
    
    output_path = Path(args["output_path"])
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    capture_mode = args.get("capture_mode", "screen")
    window_title = args.get("window_title")
    capture_region = args.get("capture_region")
    fps = args.get("fps", 30)
    screen_index = args.get("screen_index", 1)
    
    ffmpeg = get_ffmpeg_path()
    capture_args = []
    crop_filter = None
    mode_info = ""
    
    # Determine capture arguments based on mode
    if capture_mode == "window":
        if not window_title:
            return [TextContent(type="text", text="Error: window_title is required for 'window' capture mode.")]
        
        # First, try to focus the window to ensure it's visible
        try:
            window_manager.focus_window(window_title)
            await asyncio.sleep(0.3)  # Brief delay for window to come to front
        except Exception:
            pass  # Continue anyway, window might still be capturable
        
        capture_args, crop_filter, error = get_window_capture_args(window_title)
        if error:
            return [TextContent(type="text", text=f"Window capture error: {error}")]
        
        # Get window bounds for output size
        try:
            bounds = window_manager.get_window_bounds(window_title)
            width = args.get("width", bounds.width)
            height = args.get("height", bounds.height)
            mode_info = f"Window: {window_title}\nWindow size: {bounds.width}x{bounds.height}"
        except Exception:
            width = args.get("width", 1920)
            height = args.get("height", 1080)
            mode_info = f"Window: {window_title}"
    
    elif capture_mode == "region":
        if not capture_region:
            return [TextContent(type="text", text="Error: capture_region is required for 'region' capture mode.")]
        
        try:
            region_x = capture_region["x"]
            region_y = capture_region["y"]
            region_w = capture_region["width"]
            region_h = capture_region["height"]
        except KeyError as e:
            return [TextContent(type="text", text=f"Error: capture_region missing required field: {e}")]
        
        result = get_region_capture_args(region_x, region_y, region_w, region_h, screen_index)
        if isinstance(result, tuple) and len(result) == 2:
            capture_args, crop_filter = result
        else:
            capture_args = result
            crop_filter = None
        
        width = args.get("width", region_w)
        height = args.get("height", region_h)
        mode_info = f"Region: x={region_x}, y={region_y}, w={region_w}, h={region_h}"
    
    else:  # capture_mode == "screen" (default)
        capture_args = get_screen_capture_args(screen_index)
        width = args.get("width", 1920)
        height = args.get("height", 1080)
        mode_info = f"Full screen (screen {screen_index})"
    
    # Build video filter
    video_filters = []
    if crop_filter:
        video_filters.append(crop_filter)
    video_filters.append(f"scale={width}:{height}")
    vf_string = ",".join(video_filters)
    
    # Build command
    cmd = [
        ffmpeg, "-y",
        *capture_args,
        "-vf", vf_string,
        "-c:v", "libx264",
        "-preset", "ultrafast",
        "-crf", "23",
        "-pix_fmt", "yuv420p",
        str(output_path)
    ]
    
    # Start the process
    _recording_process = subprocess.Popen(
        cmd,
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    _recording_path = output_path
    _recording_start_time = datetime.now()
    
    # Wait briefly and check if process started successfully
    await asyncio.sleep(0.5)
    
    if _recording_process.poll() is not None:
        # Process died - get error
        _, stderr = _recording_process.communicate()
        error_msg = stderr.decode() if stderr else "Unknown error"
        _recording_process = None
        _recording_path = None
        _recording_start_time = None
        return [TextContent(
            type="text",
            text=f"Recording failed to start!\n\n"
                 f"Error: {error_msg}\n\n"
                 f"**Troubleshooting:**\n"
                 f"1. Grant Screen Recording permission: System Settings -> Privacy & Security -> Screen Recording\n"
                 f"2. Add the terminal app (Terminal, iTerm, or Cursor) to allowed apps\n"
                 f"3. Restart Cursor after granting permission\n\n"
                 f"Command attempted: {' '.join(cmd)}"
        )]
    
    return [TextContent(
        type="text",
        text=f"Recording started!\n"
             f"Mode: {capture_mode}\n"
             f"{mode_info}\n"
             f"Output: {output_path}\n"
             f"Resolution: {width}x{height} @ {fps}fps\n"
             f"Started at: {_recording_start_time.strftime('%H:%M:%S')}\n\n"
             f"Use 'stop_recording' when done."
    )]


async def _stop_recording() -> list[TextContent]:
    """Stop screen recording."""
    global _recording_process, _recording_path, _recording_start_time
    
    if _recording_process is None:
        return [TextContent(type="text", text="No recording in progress.")]
    
    if _recording_process.poll() is not None:
        return [TextContent(type="text", text="Recording already stopped.")]
    
    duration = (datetime.now() - _recording_start_time).total_seconds() if _recording_start_time else 0
    output_path = _recording_path
    
    # Stop ffmpeg gracefully - multiple approaches for reliability
    stopped = False
    
    # Method 1: Send 'q' to stdin (graceful stop)
    try:
        if _recording_process.stdin:
            _recording_process.stdin.write(b'q')
            _recording_process.stdin.flush()
            # Use asyncio to wait without blocking
            for _ in range(30):  # Wait up to 3 seconds
                await asyncio.sleep(0.1)
                if _recording_process.poll() is not None:
                    stopped = True
                    break
    except (BrokenPipeError, OSError):
        pass  # stdin may be closed
    
    # Method 2: Send SIGINT (Ctrl+C equivalent)
    if not stopped:
        try:
            import signal
            _recording_process.send_signal(signal.SIGINT)
            for _ in range(20):  # Wait up to 2 seconds
                await asyncio.sleep(0.1)
                if _recording_process.poll() is not None:
                    stopped = True
                    break
        except (ProcessLookupError, OSError):
            pass
    
    # Method 3: SIGTERM
    if not stopped:
        try:
            _recording_process.terminate()
            for _ in range(20):  # Wait up to 2 seconds
                await asyncio.sleep(0.1)
                if _recording_process.poll() is not None:
                    stopped = True
                    break
        except (ProcessLookupError, OSError):
            pass
    
    # Method 4: Force kill
    if not stopped:
        try:
            _recording_process.kill()
            await asyncio.sleep(0.5)
        except (ProcessLookupError, OSError):
            pass
    
    # Reset state
    _recording_process = None
    _recording_path = None
    _recording_start_time = None
    
    # Check file size
    try:
        file_size = output_path.stat().st_size / (1024 * 1024) if output_path and output_path.exists() else 0
    except Exception:
        file_size = 0
    
    return [TextContent(
        type="text",
        text=f"Recording stopped!\n"
             f"Output: {output_path}\n"
             f"Duration: {duration:.1f} seconds\n"
             f"File size: {file_size:.1f} MB"
    )]


async def _recording_status() -> list[TextContent]:
    """Get recording status."""
    global _recording_process, _recording_path, _recording_start_time
    
    if _recording_process is None or _recording_process.poll() is not None:
        return [TextContent(type="text", text="No recording in progress.")]
    
    duration = (datetime.now() - _recording_start_time).total_seconds() if _recording_start_time else 0
    
    return [TextContent(
        type="text",
        text=f"Recording in progress\n"
             f"Output: {_recording_path}\n"
             f"Duration: {duration:.1f} seconds\n"
             f"Started: {_recording_start_time.strftime('%H:%M:%S')}"
    )]


async def _text_to_speech(args: dict) -> list[TextContent]:
    """Generate speech from text."""
    text = args["text"]
    output_path = Path(args["output_path"])
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    voice = args.get("voice", "onyx")
    engine = args.get("engine", "openai")
    api_key = args.get("api_key") or os.environ.get("OPENAI_API_KEY")
    
    if engine == "openai":
        if not api_key:
            return [TextContent(type="text", text="OpenAI API key required. Provide api_key or set OPENAI_API_KEY env var.")]
        
        try:
            from openai import OpenAI
            client = OpenAI(api_key=api_key)
            
            response = client.audio.speech.create(
                model="tts-1-hd",
                voice=voice,
                input=text
            )
            response.stream_to_file(str(output_path))
            
        except Exception as e:
            return [TextContent(type="text", text=f"OpenAI TTS error: {str(e)}")]
    
    elif engine == "edge":
        try:
            import edge_tts
            
            communicate = edge_tts.Communicate(text, voice)
            await communicate.save(str(output_path))
            
        except ImportError:
            return [TextContent(type="text", text="edge-tts not installed. Run: pip install edge-tts")]
        except Exception as e:
            return [TextContent(type="text", text=f"Edge TTS error: {str(e)}")]
    
    else:
        return [TextContent(type="text", text=f"Unknown TTS engine: {engine}")]
    
    # Get file info
    file_size = output_path.stat().st_size / 1024 if output_path.exists() else 0
    duration = await _get_audio_duration(output_path)
    
    return [TextContent(
        type="text",
        text=f"Audio generated!\n"
             f"Output: {output_path}\n"
             f"Engine: {engine} ({voice})\n"
             f"Duration: {duration:.1f} seconds\n"
             f"Size: {file_size:.1f} KB\n"
             f"Text length: {len(text)} characters"
    )]


async def _get_audio_duration(path: Path) -> float:
    """Get audio file duration."""
    try:
        ffmpeg = get_ffmpeg_path()
        ffprobe = ffmpeg.replace("ffmpeg", "ffprobe")
        
        result = subprocess.run(
            [ffprobe, "-v", "quiet", "-show_entries", "format=duration",
             "-of", "default=noprint_wrappers=1:nokey=1", str(path)],
            capture_output=True, text=True
        )
        return float(result.stdout.strip())
    except:
        return 0.0


async def _replace_video_audio(args: dict) -> list[TextContent]:
    """Replace video audio with new audio file."""
    video_path = Path(args["video_path"])
    audio_path = Path(args["audio_path"])
    output_path = Path(args["output_path"])
    audio_start = args.get("audio_start_time", 0)
    trim_to_audio = args.get("trim_to_audio", True)
    
    output_path.parent.mkdir(parents=True, exist_ok=True)
    ffmpeg = get_ffmpeg_path()
    
    # Get audio duration if trimming to audio
    audio_duration = None
    if trim_to_audio:
        audio_duration = await _get_audio_duration(audio_path)
    
    base_cmd = [ffmpeg, "-y", "-i", str(video_path), "-i", str(audio_path)]
    
    # Add duration limit if trimming to audio
    if audio_duration:
        base_cmd.extend(["-t", str(audio_duration)])
    
    if audio_start > 0:
        # Delay audio by specified time
        cmd = base_cmd + [
            "-filter_complex", f"[1:a]adelay={int(audio_start * 1000)}|{int(audio_start * 1000)}[a]",
            "-map", "0:v",
            "-map", "[a]",
            "-c:v", "libx264",
            "-preset", "fast",
            "-crf", "23",
            "-c:a", "aac",
            str(output_path)
        ]
    else:
        cmd = base_cmd + [
            "-map", "0:v",
            "-map", "1:a",
            "-c:v", "libx264",
            "-preset", "fast",
            "-crf", "23",
            "-c:a", "aac",
            str(output_path)
        ]
    
    result = subprocess.run(cmd, capture_output=True, text=True)
    
    if result.returncode != 0:
        return [TextContent(type="text", text=f"Error: {result.stderr}")]
    
    file_size = output_path.stat().st_size / (1024 * 1024) if output_path.exists() else 0
    
    return [TextContent(
        type="text",
        text=f"Audio replaced!\n"
             f"Output: {output_path}\n"
             f"Audio start: {audio_start}s\n"
             f"File size: {file_size:.1f} MB"
    )]


async def _merge_audio_tracks(args: dict) -> list[TextContent]:
    """Merge multiple audio tracks onto video."""
    video_path = Path(args["video_path"])
    audio_tracks = args["audio_tracks"]
    output_path = Path(args["output_path"])
    keep_original = args.get("keep_original_audio", False)
    
    output_path.parent.mkdir(parents=True, exist_ok=True)
    ffmpeg = get_ffmpeg_path()
    
    # Build ffmpeg command
    inputs = ["-i", str(video_path)]
    filter_parts = []
    audio_labels = []
    
    for i, track in enumerate(audio_tracks):
        inputs.extend(["-i", track["path"]])
        delay_ms = int(track["start_time"] * 1000)
        label = f"a{i}"
        filter_parts.append(f"[{i+1}:a]adelay={delay_ms}|{delay_ms}[{label}]")
        audio_labels.append(f"[{label}]")
    
    if keep_original:
        audio_labels.insert(0, "[0:a]")
    
    # Mix all audio
    mix_inputs = "".join(audio_labels)
    filter_parts.append(f"{mix_inputs}amix=inputs={len(audio_labels)}:duration=first[aout]")
    
    filter_complex = ";".join(filter_parts)
    
    cmd = [
        ffmpeg, "-y",
        *inputs,
        "-filter_complex", filter_complex,
        "-map", "0:v",
        "-map", "[aout]",
        "-c:v", "copy",
        "-c:a", "aac",
        str(output_path)
    ]
    
    result = subprocess.run(cmd, capture_output=True, text=True)
    
    if result.returncode != 0:
        return [TextContent(type="text", text=f"Error: {result.stderr}")]
    
    return [TextContent(
        type="text",
        text=f"Audio tracks merged!\n"
             f"Output: {output_path}\n"
             f"Tracks merged: {len(audio_tracks)}\n"
             f"Original audio kept: {keep_original}"
    )]


async def _trim_video(args: dict) -> list[TextContent]:
    """Trim video to time range."""
    video_path = Path(args["video_path"])
    output_path = Path(args["output_path"])
    start_time = args.get("start_time", 0)
    end_time = args.get("end_time")
    duration = args.get("duration")
    
    output_path.parent.mkdir(parents=True, exist_ok=True)
    ffmpeg = get_ffmpeg_path()
    
    cmd = [ffmpeg, "-y", "-i", str(video_path), "-ss", str(start_time)]
    
    if end_time is not None:
        cmd.extend(["-to", str(end_time)])
    elif duration is not None:
        cmd.extend(["-t", str(duration)])
    
    cmd.extend(["-c", "copy", str(output_path)])
    
    result = subprocess.run(cmd, capture_output=True, text=True)
    
    if result.returncode != 0:
        return [TextContent(type="text", text=f"Error: {result.stderr}")]
    
    return [TextContent(
        type="text",
        text=f"Video trimmed!\n"
             f"Output: {output_path}\n"
             f"Start: {start_time}s"
    )]


async def _get_media_info(args: dict) -> list[TextContent]:
    """Get media file information."""
    file_path = Path(args["file_path"])
    
    if not file_path.exists():
        return [TextContent(type="text", text=f"File not found: {file_path}")]
    
    ffmpeg = get_ffmpeg_path()
    ffprobe = ffmpeg.replace("ffmpeg", "ffprobe")
    
    cmd = [
        ffprobe, "-v", "quiet",
        "-print_format", "json",
        "-show_format", "-show_streams",
        str(file_path)
    ]
    
    result = subprocess.run(cmd, capture_output=True, text=True)
    
    if result.returncode != 0:
        return [TextContent(type="text", text=f"Error: {result.stderr}")]
    
    info = json.loads(result.stdout)
    fmt = info.get("format", {})
    streams = info.get("streams", [])
    
    duration = float(fmt.get("duration", 0))
    size_mb = int(fmt.get("size", 0)) / (1024 * 1024)
    
    # Find video and audio streams
    video_stream = next((s for s in streams if s.get("codec_type") == "video"), None)
    audio_stream = next((s for s in streams if s.get("codec_type") == "audio"), None)
    
    output = f"Media Info: {file_path.name}\n"
    output += f"Duration: {duration:.1f}s ({duration/60:.1f}m)\n"
    output += f"Size: {size_mb:.1f} MB\n"
    
    if video_stream:
        width = video_stream.get("width", "?")
        height = video_stream.get("height", "?")
        fps = video_stream.get("r_frame_rate", "?")
        codec = video_stream.get("codec_name", "?")
        output += f"Video: {width}x{height} @ {fps} ({codec})\n"
    
    if audio_stream:
        sample_rate = audio_stream.get("sample_rate", "?")
        channels = audio_stream.get("channels", "?")
        codec = audio_stream.get("codec_name", "?")
        output += f"Audio: {sample_rate}Hz, {channels}ch ({codec})\n"
    
    return [TextContent(type="text", text=output)]


async def _concatenate_videos(args: dict) -> list[TextContent]:
    """Concatenate multiple videos."""
    video_paths = [Path(p) for p in args["video_paths"]]
    output_path = Path(args["output_path"])
    
    output_path.parent.mkdir(parents=True, exist_ok=True)
    ffmpeg = get_ffmpeg_path()
    
    # Create concat file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
        for path in video_paths:
            f.write(f"file '{path.absolute()}'\n")
        concat_file = f.name
    
    try:
        cmd = [
            ffmpeg, "-y",
            "-f", "concat",
            "-safe", "0",
            "-i", concat_file,
            "-c", "copy",
            str(output_path)
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode != 0:
            return [TextContent(type="text", text=f"Error: {result.stderr}")]
    
    finally:
        os.unlink(concat_file)
    
    return [TextContent(
        type="text",
        text=f"Videos concatenated!\n"
             f"Output: {output_path}\n"
             f"Videos merged: {len(video_paths)}"
    )]


async def _get_audio_duration_tool(args: dict) -> list[TextContent]:
    """Get audio file duration as a tool."""
    audio_path = Path(args["audio_path"])
    
    if not audio_path.exists():
        return [TextContent(type="text", text=f"File not found: {audio_path}")]
    
    duration = await _get_audio_duration(audio_path)
    
    return [TextContent(
        type="text",
        text=f"Audio Duration\n"
             f"File: {audio_path.name}\n"
             f"Duration: {duration:.3f} seconds ({duration/60:.2f} minutes)"
    )]


async def _adjust_video_to_audio_length(args: dict) -> list[TextContent]:
    """
    Adjust video SPEED to match audio duration exactly.
    
    IMPORTANT: This does NOT cut/trim the video. It speeds up or slows down
    the video so ALL visual content is preserved while matching audio length.
    
    - Video longer than audio -> Speed UP (faster playback)
    - Video shorter than audio -> Slow DOWN (slower playback)
    """
    video_path = Path(args["video_path"])
    audio_path = Path(args["audio_path"])
    output_path = Path(args["output_path"])
    add_audio = args.get("add_audio", True)
    
    if not video_path.exists():
        return [TextContent(type="text", text=f"Video not found: {video_path}")]
    if not audio_path.exists():
        return [TextContent(type="text", text=f"Audio not found: {audio_path}")]
    
    output_path.parent.mkdir(parents=True, exist_ok=True)
    ffmpeg = get_ffmpeg_path()
    ffprobe = ffmpeg.replace("ffmpeg", "ffprobe")
    
    # Get audio duration
    audio_duration = await _get_audio_duration(audio_path)
    if audio_duration <= 0:
        return [TextContent(type="text", text="Could not determine audio duration")]
    
    # Get video duration
    result = subprocess.run(
        [ffprobe, "-v", "quiet", "-show_entries", "format=duration",
         "-of", "default=noprint_wrappers=1:nokey=1", str(video_path)],
        capture_output=True, text=True
    )
    video_duration = float(result.stdout.strip()) if result.stdout.strip() else 0
    
    if video_duration <= 0:
        return [TextContent(type="text", text="Could not determine video duration")]
    
    # Calculate speed factor
    # speed_factor > 1 = speed up (video longer than audio)
    # speed_factor < 1 = slow down (video shorter than audio)
    speed_factor = video_duration / audio_duration
    
    # Determine action description
    if abs(speed_factor - 1.0) < 0.01:
        action = "no change needed"
        speed_change = "1.0x (unchanged)"
    elif speed_factor > 1:
        action = "speed up"
        speed_change = f"{speed_factor:.2f}x faster"
    else:
        action = "slow down"
        speed_change = f"{1/speed_factor:.2f}x slower"
    
    # Build FFmpeg command using setpts filter to adjust video speed
    # setpts=PTS/speed_factor adjusts the presentation timestamps
    # For speed_factor=2, video plays 2x faster (PTS/2 = half the timestamps)
    # For speed_factor=0.5, video plays 2x slower (PTS/0.5 = double the timestamps)
    
    if add_audio:
        cmd = [
            ffmpeg, "-y",
            "-i", str(video_path),
            "-i", str(audio_path),
            "-filter_complex",
            f"[0:v]setpts=PTS/{speed_factor}[v]",
            "-map", "[v]",
            "-map", "1:a",
            "-c:v", "libx264",
            "-preset", "fast",
            "-crf", "23",
            "-c:a", "aac",
            "-shortest",
            str(output_path)
        ]
    else:
        cmd = [
            ffmpeg, "-y",
            "-i", str(video_path),
            "-vf", f"setpts=PTS/{speed_factor}",
            "-c:v", "libx264",
            "-preset", "fast",
            "-crf", "23",
            "-an",  # No audio
            str(output_path)
        ]
    
    result = subprocess.run(cmd, capture_output=True, text=True)
    
    if result.returncode != 0:
        return [TextContent(type="text", text=f"Error: {result.stderr}")]
    
    # Get final duration
    final_duration = await _get_audio_duration(output_path)
    file_size = output_path.stat().st_size / (1024 * 1024) if output_path.exists() else 0
    
    return [TextContent(
        type="text",
        text=f"Video speed adjusted to match audio!\n"
             f"Action: {action}\n"
             f"Speed: {speed_change}\n"
             f"Video: {video_duration:.2f}s -> {final_duration:.2f}s\n"
             f"Audio: {audio_duration:.2f}s\n"
             f"Audio merged: {add_audio}\n"
             f"Output: {output_path}\n"
             f"Size: {file_size:.1f} MB\n"
             f"ALL visual content preserved (no frames cut)"
    )]


# =============================================================================
# Window Management Tool Implementations
# =============================================================================

async def _list_windows() -> list[TextContent]:
    """List all visible windows."""
    try:
        windows = window_manager.list_windows()
        
        if not windows:
            return [TextContent(type="text", text="No visible windows found.")]
        
        output = f"Found {len(windows)} visible windows:\n\n"
        for i, win in enumerate(windows, 1):
            output += f"{i}. {win.title}\n"
            if win.app_name:
                output += f"   App: {win.app_name}\n"
            output += f"   ID: {win.window_id}\n"
            if win.pid:
                output += f"   PID: {win.pid}\n"
            if win.bounds:
                output += f"   Bounds: x={win.bounds.x}, y={win.bounds.y}, "
                output += f"w={win.bounds.width}, h={win.bounds.height}\n"
            output += "\n"
        
        return [TextContent(type="text", text=output)]
    
    except window_manager.DependencyMissingError as e:
        return [TextContent(type="text", text=f"Missing dependencies: {str(e)}")]
    except window_manager.WindowManagerError as e:
        return [TextContent(type="text", text=f"Error listing windows: {str(e)}")]


async def _focus_window(args: dict) -> list[TextContent]:
    """Focus a window by title pattern."""
    title_pattern = args.get("title_pattern")
    if not title_pattern:
        return [TextContent(type="text", text="Error: title_pattern is required")]
    
    try:
        window_manager.focus_window(title_pattern)
        return [TextContent(
            type="text",
            text=f"Window focused successfully!\n"
                 f"Pattern: {title_pattern}\n\n"
                 f"The matching window should now be in the foreground."
        )]
    
    except window_manager.WindowNotFoundError:
        return [TextContent(
            type="text",
            text=f"No window found matching '{title_pattern}'.\n\n"
                 f"Use list_windows to see available windows."
        )]
    except window_manager.DependencyMissingError as e:
        return [TextContent(type="text", text=f"Missing dependencies: {str(e)}")]
    except window_manager.WindowManagerError as e:
        return [TextContent(type="text", text=f"Error focusing window: {str(e)}")]


async def _get_window_bounds_tool(args: dict) -> list[TextContent]:
    """Get window bounds by title pattern."""
    title_pattern = args.get("title_pattern")
    if not title_pattern:
        return [TextContent(type="text", text="Error: title_pattern is required")]
    
    try:
        bounds = window_manager.get_window_bounds(title_pattern)
        return [TextContent(
            type="text",
            text=f"Window bounds for '{title_pattern}':\n\n"
                 f"  x: {bounds.x}\n"
                 f"  y: {bounds.y}\n"
                 f"  width: {bounds.width}\n"
                 f"  height: {bounds.height}\n\n"
                 f"Use these values with capture_mode='region' in start_recording."
        )]
    
    except window_manager.WindowNotFoundError:
        return [TextContent(
            type="text",
            text=f"No window found matching '{title_pattern}'.\n\n"
                 f"Use list_windows to see available windows."
        )]
    except window_manager.DependencyMissingError as e:
        return [TextContent(type="text", text=f"Missing dependencies: {str(e)}")]
    except window_manager.WindowManagerError as e:
        return [TextContent(type="text", text=f"Error getting bounds: {str(e)}")]


async def _check_window_tools() -> list[TextContent]:
    """Check window management tool availability."""
    deps = window_manager.check_dependencies()
    
    output = f"Window Management Tools Status\n"
    output += f"{'=' * 40}\n\n"
    output += f"Platform: {deps['platform']}\n"
    output += f"Available: {'Yes' if deps['available'] else 'No'}\n"
    output += f"Message: {deps['message']}\n"
    
    if deps['missing']:
        output += f"\nMissing tools: {', '.join(deps['missing'])}\n"
        
        if deps['platform'] == 'linux':
            output += f"\nTo install:\n"
            output += f"  Ubuntu/Debian: sudo apt install wmctrl xdotool\n"
            output += f"  Fedora/RHEL:   sudo dnf install wmctrl xdotool\n"
            output += f"  Arch:          sudo pacman -S wmctrl xdotool\n"
    
    return [TextContent(type="text", text=output)]


async def _list_screens() -> list[TextContent]:
    """List available screens/displays for recording."""
    import platform
    
    output = "Available Screens for Recording\n"
    output += "=" * 40 + "\n\n"
    
    system = platform.system().lower()
    
    if system == "darwin":
        # macOS: Use system_profiler to get display info
        try:
            result = subprocess.run(
                ["system_profiler", "SPDisplaysDataType", "-json"],
                capture_output=True, text=True, timeout=10
            )
            
            if result.returncode == 0:
                data = json.loads(result.stdout)
                displays = []
                
                # Parse the JSON to find displays
                for gpu in data.get("SPDisplaysDataType", []):
                    for display in gpu.get("spdisplays_ndrvs", []):
                        display_info = {
                            "name": display.get("_name", "Unknown"),
                            "resolution": display.get("_spdisplays_resolution", "Unknown"),
                            "main": display.get("spdisplays_main") == "spdisplays_yes",
                            "online": display.get("spdisplays_status") == "spdisplays_status_ok"
                        }
                        displays.append(display_info)
                
                if displays:
                    output += "Detected displays:\n\n"
                    for i, d in enumerate(displays, 1):
                        main_marker = " (MAIN)" if d["main"] else ""
                        output += f"  Screen {i}{main_marker}:\n"
                        output += f"    Name: {d['name']}\n"
                        output += f"    Resolution: {d['resolution']}\n"
                        output += f"    Online: {'Yes' if d['online'] else 'No'}\n\n"
                    
                    output += "FFmpeg screen_index mapping:\n"
                    output += "  - screen_index=1: Usually the MAIN display (built-in)\n"
                    output += "  - screen_index=2: Usually the first external display\n"
                    output += "  - screen_index=3: Third display, etc.\n\n"
                    
                    output += "IMPORTANT for multi-monitor setups:\n"
                    output += "  1. Check which screen your target window is on\n"
                    output += "  2. Use the corresponding screen_index in start_recording\n"
                    output += "  3. Or use region-based recording with window bounds\n"
                else:
                    output += "No displays found in system_profiler output.\n"
            else:
                output += f"Error running system_profiler: {result.stderr}\n"
                
        except Exception as e:
            output += f"Error detecting displays: {str(e)}\n"
            
    elif system == "linux":
        # Linux: Use xrandr
        try:
            result = subprocess.run(
                ["xrandr", "--query"],
                capture_output=True, text=True, timeout=10
            )
            
            if result.returncode == 0:
                import re
                lines = result.stdout.strip().split('\n')
                screen_num = 1
                
                for line in lines:
                    # Match connected displays with resolution
                    match = re.match(r'(\S+) connected (?:primary )?(\d+x\d+)', line)
                    if match:
                        name = match.group(1)
                        resolution = match.group(2)
                        is_primary = "primary" in line
                        primary_marker = " (PRIMARY)" if is_primary else ""
                        
                        output += f"  Screen {screen_num}{primary_marker}:\n"
                        output += f"    Name: {name}\n"
                        output += f"    Resolution: {resolution}\n\n"
                        screen_num += 1
                
                output += "For FFmpeg on Linux, use the display name (e.g., ':0.0') or screen offset.\n"
            else:
                output += f"Error running xrandr: {result.stderr}\n"
                
        except FileNotFoundError:
            output += "xrandr not found. Install with: sudo apt install x11-xserver-utils\n"
        except Exception as e:
            output += f"Error detecting displays: {str(e)}\n"
            
    elif system == "windows":
        output += "Windows multi-monitor detection not yet implemented.\n"
        output += "For now, use the Windows display settings to identify screen numbers.\n"
    else:
        output += f"Unsupported platform: {system}\n"
    
    output += "\nRecommendation for reliable multi-monitor recording:\n"
    output += "  Use region-based recording with exact window bounds:\n"
    output += "    1. Get window bounds: get_window_bounds(title_pattern='...')\n"
    output += "    2. Record region: start_recording(capture_mode='region', capture_region={bounds})\n"
    
    return [TextContent(type="text", text=output)]


async def main():
    """Run the MCP server."""
    async with stdio_server() as (read_stream, write_stream):
        await server.run(read_stream, write_stream, server.create_initialization_options())


def run():
    """Entry point."""
    asyncio.run(main())


if __name__ == "__main__":
    run()



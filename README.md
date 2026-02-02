# Demo Recorder MCP

An MCP (Model Context Protocol) server that enables AI agents to create professional demo videos with synchronized voiceover narration. Works with **any website or web application**.

## Features

- **Screen Recording** - Auto-detects browser window in container, captures at 30fps
- **Text-to-Speech** - Generate voiceover using OpenAI TTS (with API key) or Edge TTS (free)
- **Audio-Video Sync** - Adjust video speed to match narration length (preserves all content)
- **Scene-Based Workflow** - Built-in guides enforce short, manageable recordings
- **Container-First** - Includes Playwright browser + virtual display for headless operation

## Quick Start (Container)

```bash
# Build the container
git clone https://github.com/Schimuneck/demo-recorder-mcp.git
cd demo-recorder-mcp
podman build -t demo-recorder-mcp .

# Or use docker
docker build -t demo-recorder-mcp .
```

Add to Cursor MCP settings (`~/.cursor/mcp.json`):

```json
{
  "mcpServers": {
    "demo-recorder": {
      "command": "podman",
      "args": [
        "run", "-i", "--rm",
        "-v", "/path/to/recordings:/app/recordings",
        "-e", "OPENAI_API_KEY=sk-your-api-key-here",
        "demo-recorder-mcp"
      ]
    }
  }
}
```

## How It Works

```
┌─────────────────────────────────────────────────────────────┐
│                   Container (Recommended)                    │
│  ┌───────────────┐  ┌───────────────┐  ┌─────────────────┐  │
│  │    Xvfb       │  │   Playwright  │  │  Demo Recorder  │  │
│  │  DISPLAY=:99  │◄─│    Browser    │  │      MCP        │  │
│  │  2560x1440    │  │   (Firefox)   │  │    (FFmpeg)     │  │
│  └───────────────┘  └───────────────┘  └─────────────────┘  │
│         │                                      │             │
│         └──────────► Screen Capture ◄──────────┘             │
└─────────────────────────────────────────────────────────────┘
```

The container:
1. Starts **Xvfb** with a virtual display
2. Runs **Playwright MCP** (browser renders to virtual display)
3. Runs **Demo Recorder MCP** (FFmpeg captures from virtual display)
4. Both MCPs multiplex through a single connection

## Available Tools

### Recording Tools

| Tool | Description |
|------|-------------|
| `start_recording` | Start video recording (auto-detects browser window) |
| `stop_recording` | Stop recording and save the video file |
| `recording_status` | Check if recording is in progress |

### Audio Tools

| Tool | Description |
|------|-------------|
| `text_to_speech` | Generate voiceover audio (uses OpenAI if API key set, else Edge TTS) |

### Video Editing Tools

| Tool | Description |
|------|-------------|
| `adjust_video_to_audio` | Sync video duration to audio by adjusting playback speed |
| `concatenate_videos` | Join multiple scene videos into final demo |
| `media_info` | Get duration, resolution, and codec info for any media file |

### Protocol Guides

| Tool | Description |
|------|-------------|
| `planning_phase_1` | Demo planning guide - call FIRST before any demo |
| `setup_phase_2` | Browser setup guide - sizing and window verification |
| `recording_phase_3` | Recording actions guide - pacing and interaction patterns |
| `editing_phase_4` | Post-recording guide - audio sync and final assembly |

### Utility Tools

| Tool | Description |
|------|-------------|
| `list_windows` | List visible windows (call after browser_navigate) |
| `window_tools` | Check availability of window management tools |

## Scene-Based Workflow

Demos are recorded as **short scenes (10-30 seconds each)**, not one long video. This enables precise audio-video synchronization.

### Per-Scene Process

```
SCENE N:
1. browser_snapshot()                    # Verify starting position
2. start_recording()                     # START recording
3. browser_wait_for(time=2)              # Viewer sees initial state
4. [ACTION: scroll, click, or type]      # Captured on video!
5. browser_wait_for(time=2)              # Viewer sees result
6. stop_recording()                      # STOP recording
7. text_to_speech("Narration...")        # Generate audio
8. adjust_video_to_audio(...)            # Sync video to audio
9. [Repeat for next scene]
```

### Critical: Actions DURING Recording

**WRONG** (static video):
```python
browser_scroll(400)           # Action NOT recorded
start_recording()
browser_wait_for(time=5)      # Records static page
stop_recording()
```

**CORRECT** (dynamic video):
```python
start_recording()
browser_wait_for(time=2)
browser_scroll(400)           # Action CAPTURED!
browser_wait_for(time=2)
stop_recording()
```

## Complete Example

```python
# === SETUP ===
browser_navigate(url="https://example.com")
browser_resize(width=1920, height=1080)

# === SCENE 1: Homepage Overview ===
browser_snapshot()                              # Verify position

start_recording(output_path="scene1_raw.mp4")   # Start recording
browser_wait_for(time=2)                        # Initial pause
browser_scroll(direction="down", amount=400)    # ACTION CAPTURED
browser_wait_for(time=2)                        # End pause
stop_recording()                                # Stop recording

text_to_speech(
    text="Welcome to our platform. As we scroll down, you can see the key features.",
    output_path="scene1_audio.mp3"
)

adjust_video_to_audio(
    video_path="scene1_raw.mp4",
    audio_path="scene1_audio.mp3",
    output_path="scene1_final.mp4"
)

# === SCENE 2: Click Feature ===
browser_snapshot()

start_recording(output_path="scene2_raw.mp4")
browser_wait_for(time=2)
browser_click(ref="...", element="Learn More")  # ACTION CAPTURED
browser_wait_for(time=3)
stop_recording()

text_to_speech(
    text="Clicking Learn More opens the detailed documentation.",
    output_path="scene2_audio.mp3"
)

adjust_video_to_audio(
    video_path="scene2_raw.mp4",
    audio_path="scene2_audio.mp3",
    output_path="scene2_final.mp4"
)

# === FINAL: Concatenate All Scenes ===
concatenate_videos(
    video_paths=["scene1_final.mp4", "scene2_final.mp4"],
    output_path="demo_final.mp4"
)

media_info(file_path="demo_final.mp4")  # Verify final output
```

## Key Principle: Speed Adjust, Never Cut

When syncing video with audio, the tool uses **speed adjustment**:

- Video longer than audio → **Speeds up** (faster playback)
- Video shorter than audio → **Slows down** (slower playback)
- **ALL visual content is preserved** - no frames are ever cut

Keep scenes short (10-30s) for natural speed adjustments. A 20s video synced to 25s audio plays at comfortable 0.8x speed. A 90s video synced to 45s audio plays at unwatchable 2x speed.

## Text-to-Speech

The `text_to_speech` tool automatically selects the best available engine:

| Engine | When Used | Voice |
|--------|-----------|-------|
| OpenAI TTS | When `OPENAI_API_KEY` is set | "onyx" (deep, authoritative) |
| Edge TTS | Fallback (free, no API key) | "en-US-AriaNeural" |

No configuration needed - just call:
```python
text_to_speech(text="Your narration here", output_path="audio.mp3")
```

## Installation Options

### Option 1: Container (Recommended)

See Quick Start above. Benefits:
- Headless recording works without physical display
- Playwright browser automation included
- Cross-platform (macOS, Linux, Windows)
- No system dependencies to install

### Option 2: From PyPI (Host Mode)

```bash
pip install "demo-recorder-mcp[all]"
```

Requires ffmpeg:
```bash
# macOS
brew install ffmpeg

# Ubuntu/Debian  
sudo apt install ffmpeg

# Windows (Chocolatey)
choco install ffmpeg
```

### Option 3: From Source

```bash
git clone https://github.com/Schimuneck/demo-recorder-mcp.git
cd demo-recorder-mcp
python -m venv .venv
source .venv/bin/activate
pip install -e ".[all]"
```

## Cursor MCP Configuration

### Container (Recommended)

```json
{
  "mcpServers": {
    "demo-recorder": {
      "command": "podman",
      "args": [
        "run", "-i", "--rm",
        "-v", "/path/to/recordings:/app/recordings",
        "-e", "OPENAI_API_KEY=sk-your-api-key-here",
        "demo-recorder-mcp"
      ]
    }
  }
}
```

### Host Mode (Python Package)

```json
{
  "mcpServers": {
    "demo-recorder": {
      "command": "demo-recorder-mcp",
      "env": {
        "OPENAI_API_KEY": "sk-your-api-key-here"
      }
    }
  }
}
```

## Troubleshooting

### Container: Black Screen Recording

1. Ensure browser is navigated first: `browser_navigate(url="...")`
2. The recording auto-detects the browser window
3. Check recording status: `recording_status()`

### Container: No Windows Found

`list_windows()` requires a browser window to exist:
```python
# WRONG: list_windows before browser exists
list_windows()  # Returns empty

# CORRECT: navigate first, then list
browser_navigate(url="https://example.com")
list_windows()  # Returns Firefox window
```

### Host Mode: Screen Recording Permission (macOS)

1. Go to **System Settings → Privacy & Security → Screen Recording**
2. Add **Cursor** (or terminal app) to allowed list
3. Restart Cursor

### Video Out of Sync with Audio

Break demos into shorter scenes (10-30 seconds each). Long recordings require extreme speed adjustments that look unnatural.

## File Organization

```
/app/recordings/
├── scene1_raw.mp4
├── scene1_audio.mp3
├── scene1_final.mp4
├── scene2_raw.mp4
├── scene2_audio.mp3
├── scene2_final.mp4
└── demo_final.mp4
```

## Contributing

Contributions welcome! See [CONTRIBUTING.md](CONTRIBUTING.md).

## License

MIT License - see [LICENSE](LICENSE).

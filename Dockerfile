# Demo Recorder MCP Container
# Combined image with Playwright MCP + demo-recorder MCP
#
# This container includes:
# - Playwright MCP: Browser automation (navigate, click, screenshot, video recording)
# - demo-recorder MCP: Video editing, TTS, media processing
# - Virtual display (Xvfb) for headless operation
#
# Build: podman build -t demo-recorder-mcp .
# Run:   podman run -it --rm -v ./recordings:/app/recordings demo-recorder-mcp

FROM node:20-bookworm AS base

# Install system dependencies for:
# - Playwright Chromium browser
# - FFmpeg for video/audio processing
# - X11/Xvfb for virtual display (headless browser rendering)
# - Window management tools (wmctrl, xdotool)
# - Python 3.11 with pip
RUN apt-get update && apt-get install -y --no-install-recommends \
    # Python
    python3 \
    python3-pip \
    python3-venv \
    # FFmpeg for video/audio processing
    ffmpeg \
    # X11 and virtual framebuffer for headless display
    xvfb \
    x11-utils \
    x11-xserver-utils \
    # Window management tools
    wmctrl \
    xdotool \
    # Minimal window manager (required for wmctrl to work)
    openbox \
    # Chromium dependencies (Playwright needs these)
    libnss3 \
    libnspr4 \
    libatk1.0-0 \
    libatk-bridge2.0-0 \
    libcups2 \
    libdrm2 \
    libxkbcommon0 \
    libxcomposite1 \
    libxdamage1 \
    libxfixes3 \
    libxrandr2 \
    libgbm1 \
    libasound2 \
    libpango-1.0-0 \
    libcairo2 \
    libatspi2.0-0 \
    # Fonts for proper rendering
    fonts-liberation \
    fonts-noto-color-emoji \
    # Additional utilities
    dbus \
    dbus-x11 \
    procps \
    curl \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Set up Python virtual environment
ENV VIRTUAL_ENV=/opt/venv
RUN python3 -m venv $VIRTUAL_ENV
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

# ============================================================
# Install demo-recorder-mcp (Python)
# ============================================================

WORKDIR /opt/recorder

# Copy source files
COPY pyproject.toml README.md LICENSE ./
COPY src/ ./src/

# Install recorder with all TTS engines
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -e ".[all]"

# ============================================================
# Install Playwright MCP (Node.js)
# ============================================================

WORKDIR /app

# Install @playwright/mcp globally and Firefox browser (works on ARM64)
RUN npm install -g @playwright/mcp playwright && \
    npx playwright install firefox && \
    npx playwright install-deps firefox

# Set environment variable for Playwright browser
ENV PLAYWRIGHT_BROWSERS_PATH=/root/.cache/ms-playwright

# ============================================================
# Runtime Configuration
# ============================================================

# Environment variables for display
# Note: Xvfb is taller (1140) to accommodate Firefox window decorations (~60px title bar)
# FFmpeg will capture from y=60 to get just the browser content
ENV DISPLAY=:99
# Extra headroom for window decorations and positioning
ENV XVFB_RESOLUTION=2560x1440x24

# Video server configuration
ENV VIDEO_SERVER_PORT=8080
ENV VIDEO_SERVER_HOST=localhost
ENV RECORDINGS_DIR=/app/recordings

# Copy startup scripts
COPY scripts/start-xvfb.sh /app/start-xvfb.sh
COPY scripts/run-mcp.sh /app/run-mcp.sh
COPY scripts/video-server.py /app/scripts/video-server.py
RUN chmod +x /app/start-xvfb.sh /app/run-mcp.sh

# Create recordings directory
RUN mkdir -p /app/recordings

# Expose video server port
EXPOSE 8080

# Default entrypoint starts Xvfb and then runs the provided command
ENTRYPOINT ["/app/start-xvfb.sh"]

# Default: run multiplexer which exposes all tools (Playwright + demo-recorder)
CMD ["/app/run-mcp.sh", "multi"]




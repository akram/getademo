#!/bin/bash
# Start Xvfb virtual display and video server (silently)
#
# This script:
# 1. Starts Xvfb with the configured resolution
# 2. Starts the video HTTP server to serve recordings
# 3. Executes the provided command (MCP server)
#
# Required for headless browser operation in container.

# Start Xvfb
Xvfb ${DISPLAY} -screen 0 ${XVFB_RESOLUTION} >/dev/null 2>&1 &
XVFB_PID=$!

# Wait for Xvfb to start
sleep 2

# Verify Xvfb is running
if ! kill -0 $XVFB_PID 2>/dev/null; then
    # Only log errors to stderr - MCP expects clean stdout
    echo "ERROR: Xvfb failed to start" >&2
    exit 1
fi

# Create openbox config to disable window decorations and position at 0,0
# This ensures browser viewport size == window size (no title bars eating pixels)
# And windows start at top-left for clean recording capture
mkdir -p /root/.config/openbox
cat > /root/.config/openbox/rc.xml << 'OPENBOX_CONFIG'
<?xml version="1.0" encoding="UTF-8"?>
<openbox_config xmlns="http://openbox.org/3.4/rc">
  <placement>
    <policy>UnderMouse</policy>
  </placement>
  <applications>
    <application class="*">
      <decor>no</decor>
      <maximized>false</maximized>
      <position force="yes">
        <x>0</x>
        <y>0</y>
      </position>
    </application>
  </applications>
</openbox_config>
OPENBOX_CONFIG

# Start openbox window manager (required for wmctrl to detect windows)
# Without a WM, wmctrl cannot list windows (_NET_CLIENT_LIST not set)
openbox >/dev/null 2>&1 &
sleep 1

# Start video server in background (serves recordings via HTTP)
if [ -f /app/scripts/video-server.py ]; then
    python3 /app/scripts/video-server.py &
    VIDEO_SERVER_PID=$!
    echo "Video server started on port ${VIDEO_SERVER_PORT:-8080}" >&2
fi

# Execute the provided command
exec "$@"

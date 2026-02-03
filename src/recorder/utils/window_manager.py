#!/usr/bin/env python3
"""
Window Manager - Cross-platform window management.

Provides platform-agnostic window management functionality:
- List visible windows
- Focus/activate windows by title pattern
- Get window bounds (position and size)

Supports:
- macOS: Uses AppleScript via osascript (built-in)
- Linux: Uses wmctrl/xdotool (requires installation)
- Windows: Uses ctypes with Win32 API (built-in)
"""

import re
import shutil
import subprocess
import sys
from typing import Optional, List

from ..core.types import WindowBounds, WindowInfo


class WindowManagerError(Exception):
    """Base exception for window manager errors."""
    pass


class DependencyMissingError(WindowManagerError):
    """Required dependency is not installed."""
    pass


class WindowNotFoundError(WindowManagerError):
    """No window matching the pattern was found."""
    pass


# =============================================================================
# Platform Detection
# =============================================================================

def get_platform() -> str:
    """Get the current platform identifier."""
    if sys.platform == "darwin":
        return "macos"
    elif sys.platform.startswith("linux"):
        return "linux"
    elif sys.platform == "win32":
        return "windows"
    else:
        return "unknown"


def check_dependencies() -> dict:
    """Check if required dependencies are available for the current platform."""
    platform = get_platform()
    
    if platform == "macos":
        return {
            "platform": platform,
            "available": True,
            "missing": [],
            "message": "macOS: Using built-in AppleScript (osascript)"
        }
    
    elif platform == "linux":
        missing = []
        if not shutil.which("wmctrl"):
            missing.append("wmctrl")
        if not shutil.which("xdotool"):
            missing.append("xdotool")
        
        if missing:
            return {
                "platform": platform,
                "available": False,
                "missing": missing,
                "message": f"Linux: Missing tools: {', '.join(missing)}. "
                          f"Install with: sudo apt install {' '.join(missing)}"
            }
        return {
            "platform": platform,
            "available": True,
            "missing": [],
            "message": "Linux: wmctrl and xdotool available"
        }
    
    elif platform == "windows":
        return {
            "platform": platform,
            "available": True,
            "missing": [],
            "message": "Windows: Using built-in Win32 API (ctypes)"
        }
    
    else:
        return {
            "platform": platform,
            "available": False,
            "missing": ["unknown platform"],
            "message": f"Unsupported platform: {sys.platform}"
        }


# =============================================================================
# macOS Backend
# =============================================================================

def _macos_list_windows_cg() -> List[WindowInfo]:
    """List windows on macOS using CGWindowListCopyWindowInfo (most reliable for Chrome)."""
    script = '''
use framework "Foundation"
use framework "AppKit"
use scripting additions

set windowList to ""
set theWindows to current application's CGWindowListCopyWindowInfo((current application's kCGWindowListOptionOnScreenOnly), 0)

repeat with i from 1 to count of theWindows
    set theWindow to item i of (theWindows as list)
    set ownerName to ""
    set windowName to ""
    set windowID to 0
    set ownerPID to 0
    set boundsStr to "0,0,0,0"
    
    try
        set ownerName to theWindow's kCGWindowOwnerName as text
    end try
    try
        set windowName to theWindow's kCGWindowName as text
    end try
    try
        set windowID to theWindow's kCGWindowNumber as integer
    end try
    try
        set ownerPID to theWindow's kCGWindowOwnerPID as integer
    end try
    try
        set theBounds to theWindow's kCGWindowBounds
        set bX to theBounds's X as integer
        set bY to theBounds's Y as integer
        set bW to theBounds's Width as integer
        set bH to theBounds's Height as integer
        set boundsStr to (bX as text) & "," & (bY as text) & "," & (bW as text) & "," & (bH as text)
    end try
    
    -- Skip windows with no name and small size (likely UI elements)
    if windowName is not "" or ownerName contains "Chrome" or ownerName contains "Chromium" then
        set windowList to windowList & windowID & "||" & ownerPID & "||" & ownerName & "||" & windowName & "||" & boundsStr & linefeed
    end if
end repeat

return windowList
'''
    
    try:
        result = subprocess.run(
            ["osascript", "-e", script],
            capture_output=True, text=True, timeout=15
        )
        
        windows = []
        output = result.stdout.strip()
        
        for line in output.split("\n"):
            line = line.strip()
            if not line or "||" not in line:
                continue
            parts = line.split("||")
            if len(parts) >= 5:
                window_id_str, pid_str, app_name, title, bounds_str = parts[0], parts[1], parts[2], parts[3], parts[4]
                
                # Parse bounds
                try:
                    bounds_parts = bounds_str.split(",")
                    bounds = WindowBounds(
                        x=int(float(bounds_parts[0])),
                        y=int(float(bounds_parts[1])),
                        width=int(float(bounds_parts[2])),
                        height=int(float(bounds_parts[3]))
                    )
                except (ValueError, IndexError):
                    bounds = None
                
                # Skip tiny windows (likely UI chrome elements)
                if bounds and bounds.width < 50 and bounds.height < 50:
                    continue
                
                display_title = title if title else app_name
                windows.append(WindowInfo(
                    title=display_title,
                    window_id=window_id_str,
                    pid=int(pid_str) if pid_str.isdigit() else None,
                    bounds=bounds,
                    app_name=app_name
                ))
        
        return windows
    except Exception:
        return []


def _macos_list_chrome_windows() -> List[WindowInfo]:
    """List Chrome windows by querying Chrome directly (catches Playwright windows)."""
    script = '''
set output to ""
try
    tell application "Google Chrome"
        set windowCount to count of windows
        repeat with i from 1 to windowCount
            set w to window i
            set tabTitles to ""
            try
                set activeTab to active tab of w
                set tabTitles to title of activeTab
            end try
            set winBounds to bounds of w
            set bX to item 1 of winBounds
            set bY to item 2 of winBounds
            set bW to (item 3 of winBounds) - bX
            set bH to (item 4 of winBounds) - bY
            set output to output & i & "||" & "Google Chrome" & "||" & tabTitles & "||" & bX & "," & bY & "," & bW & "," & bH & linefeed
        end repeat
    end tell
end try
return output
'''
    
    try:
        result = subprocess.run(
            ["osascript", "-e", script],
            capture_output=True, text=True, timeout=10
        )
        
        windows = []
        output = result.stdout.strip()
        
        for line in output.split("\n"):
            line = line.strip()
            if not line or "||" not in line:
                continue
            parts = line.split("||")
            if len(parts) >= 4:
                window_idx, app_name, title, bounds_str = parts[0], parts[1], parts[2], parts[3]
                
                try:
                    bounds_parts = bounds_str.split(",")
                    bounds = WindowBounds(
                        x=int(float(bounds_parts[0])),
                        y=int(float(bounds_parts[1])),
                        width=int(float(bounds_parts[2])),
                        height=int(float(bounds_parts[3]))
                    )
                except (ValueError, IndexError):
                    bounds = None
                
                if title:  # Only add if we have a title
                    windows.append(WindowInfo(
                        title=title,
                        window_id=f"chrome:{window_idx}",
                        pid=None,
                        bounds=bounds,
                        app_name=app_name
                    ))
        
        return windows
    except Exception:
        return []


def _macos_list_windows_system_events() -> List[WindowInfo]:
    """List windows on macOS using System Events AppleScript."""
    script = '''
set output to ""
tell application "System Events"
    set procList to every process whose visible is true and background only is false
    repeat with proc in procList
        set procName to name of proc
        set procID to unix id of proc
        try
            set winList to every window of proc
            repeat with win in winList
                try
                    set winTitle to name of win
                    set winPosition to position of win
                    set winSize to size of win
                    set output to output & procID & "||" & procName & "||" & winTitle & "||" & (item 1 of winPosition) & "," & (item 2 of winPosition) & "," & (item 1 of winSize) & "," & (item 2 of winSize) & linefeed
                end try
            end repeat
        end try
    end repeat
end tell
return output
'''
    
    try:
        result = subprocess.run(
            ["osascript", "-e", script],
            capture_output=True, text=True, timeout=15
        )
        
        if result.returncode != 0 and result.stderr:
            if "not allowed" in result.stderr.lower() or "assistive" in result.stderr.lower():
                raise WindowManagerError(
                    "Permission denied. Grant accessibility access:\n"
                    "System Settings -> Privacy & Security -> Accessibility\n"
                    "Add and enable your terminal app (Terminal, iTerm, or Cursor)"
                )
            raise WindowManagerError(f"AppleScript error: {result.stderr}")
        
        windows = []
        output = result.stdout.strip()
        
        for line in output.split("\n"):
            line = line.strip()
            if not line or "||" not in line:
                continue
            parts = line.split("||")
            if len(parts) >= 4:
                pid_str, app_name, title, bounds_str = parts[0], parts[1], parts[2], parts[3]
                try:
                    bounds_parts = bounds_str.split(",")
                    bounds = WindowBounds(
                        x=int(float(bounds_parts[0])),
                        y=int(float(bounds_parts[1])),
                        width=int(float(bounds_parts[2])),
                        height=int(float(bounds_parts[3]))
                    )
                except (ValueError, IndexError):
                    bounds = None
                
                windows.append(WindowInfo(
                    title=title if title else app_name,
                    window_id=f"{pid_str}:{title or app_name}",
                    pid=int(pid_str) if pid_str.isdigit() else None,
                    bounds=bounds,
                    app_name=app_name
                ))
        
        return windows
    except subprocess.TimeoutExpired:
        raise WindowManagerError("Timeout listing windows")
    except WindowManagerError:
        raise
    except Exception as e:
        raise WindowManagerError(f"Failed to list windows: {e}")


def _macos_list_windows() -> List[WindowInfo]:
    """List windows on macOS using multiple methods for best coverage."""
    # Track seen windows by title to avoid duplicates
    seen_titles = set()
    all_windows = []
    
    # Method 1: CGWindowListCopyWindowInfo - best for catching all windows including Chrome
    try:
        cg_windows = _macos_list_windows_cg()
        for win in cg_windows:
            key = (win.app_name, win.title)
            if key not in seen_titles:
                seen_titles.add(key)
                all_windows.append(win)
    except Exception:
        pass
    
    # Method 2: Query Chrome directly - catches Playwright-controlled Chrome windows
    try:
        chrome_windows = _macos_list_chrome_windows()
        for win in chrome_windows:
            # Check if we already have this Chrome window by title
            if not any(w.title == win.title and "Chrome" in (w.app_name or "") for w in all_windows):
                all_windows.append(win)
    except Exception:
        pass
    
    # Method 3: System Events fallback - good for general window management
    if not all_windows:
        try:
            se_windows = _macos_list_windows_system_events()
            for win in se_windows:
                key = (win.app_name, win.title)
                if key not in seen_titles:
                    seen_titles.add(key)
                    all_windows.append(win)
        except Exception:
            pass
    
    # Final fallback: just list running apps
    if not all_windows:
        return _macos_list_windows_fallback()
    
    return all_windows


def _macos_list_windows_fallback() -> List[WindowInfo]:
    """Fallback method using running applications."""
    script = '''
set output to ""
tell application "System Events"
    set appList to name of every application process whose visible is true
    repeat with appName in appList
        set output to output & appName & linefeed
    end repeat
end tell
return output
'''
    try:
        result = subprocess.run(
            ["osascript", "-e", script],
            capture_output=True, text=True, timeout=10
        )
        
        windows = []
        for line in result.stdout.strip().split("\n"):
            app_name = line.strip()
            if app_name:
                windows.append(WindowInfo(
                    title=app_name,
                    window_id=app_name,
                    pid=None,
                    bounds=None,
                    app_name=app_name
                ))
        return windows
    except Exception:
        return []


def _macos_focus_window(title_pattern: str) -> bool:
    """Focus a window on macOS using AppleScript."""
    pattern = re.compile(title_pattern, re.IGNORECASE)
    
    try:
        windows = _macos_list_windows()
    except WindowManagerError:
        windows = []
    
    matching = None
    for win in windows:
        if pattern.search(win.title or '') or (win.app_name and pattern.search(win.app_name)):
            matching = win
            break
    
    if not matching:
        raise WindowNotFoundError(f"No window matching '{title_pattern}'")
    
    escaped_title = matching.title.replace('"', '\\"') if matching.title else ""
    escaped_app = matching.app_name.replace('"', '\\"') if matching.app_name else ""
    
    script = f'''
tell application "System Events"
    set targetProc to first application process whose name is "{escaped_app}"
    set targetWindow to missing value
    repeat with win in windows of targetProc
        if name of win is "{escaped_title}" then
            set targetWindow to win
            exit repeat
        end if
    end repeat
    if targetWindow is not missing value then
        perform action "AXRaise" of targetWindow
        set frontmost of targetProc to true
        return "ok"
    else
        return "window not found"
    end if
end tell
'''
    
    try:
        result = subprocess.run(
            ["osascript", "-e", script],
            capture_output=True, text=True, timeout=5
        )
        if "ok" in result.stdout:
            return True
    except Exception:
        pass
    
    # Fallback: make process frontmost
    if matching.app_name:
        script = f'''
tell application "System Events"
    set targetProc to first application process whose name is "{escaped_app}"
    set frontmost of targetProc to true
end tell
'''
        try:
            subprocess.run(["osascript", "-e", script], capture_output=True, timeout=5)
            return True
        except Exception as e:
            raise WindowManagerError(f"Failed to focus window: {e}")
    
    raise WindowManagerError("Could not focus window")


def _macos_get_window_bounds(title_pattern: str) -> WindowBounds:
    """Get window bounds on macOS."""
    windows = _macos_list_windows()
    pattern = re.compile(title_pattern, re.IGNORECASE)
    
    for win in windows:
        if pattern.search(win.title) or (win.app_name and pattern.search(win.app_name)):
            if win.bounds:
                return win.bounds
            raise WindowManagerError(f"Could not get bounds for window '{win.title}'")
    
    raise WindowNotFoundError(f"No window matching '{title_pattern}'")


def _macos_get_window_id(title_pattern: str) -> Optional[int]:
    """Get CGWindowID for a window on macOS."""
    script = '''
    use framework "Foundation"
    use framework "AppKit"
    use scripting additions

    set windowList to ""
    set theWindows to current application's CGWindowListCopyWindowInfo((current application's kCGWindowListOptionOnScreenOnly), 0)
    
    repeat with i from 1 to count of theWindows
        set theWindow to item i of (theWindows as list)
        set ownerName to theWindow's kCGWindowOwnerName as text
        set windowName to ""
        try
            set windowName to theWindow's kCGWindowName as text
        end try
        set windowID to theWindow's kCGWindowNumber as integer
        set windowList to windowList & windowID & "||" & ownerName & "||" & windowName & "\\n"
    end repeat
    
    return windowList
    '''
    
    try:
        result = subprocess.run(
            ["osascript", "-e", script],
            capture_output=True, text=True, timeout=10
        )
        
        pattern = re.compile(title_pattern, re.IGNORECASE)
        for line in result.stdout.strip().split("\n"):
            if not line or "||" not in line:
                continue
            parts = line.split("||")
            if len(parts) >= 3:
                window_id_str, owner_name, window_name = parts[0], parts[1], parts[2]
                if pattern.search(window_name) or pattern.search(owner_name):
                    return int(window_id_str)
        
        return None
    except Exception:
        return None


def _macos_fullscreen_window(title_pattern: str) -> bool:
    """Make a window fullscreen on macOS using AppleScript."""
    pattern = re.compile(title_pattern, re.IGNORECASE)
    
    try:
        windows = _macos_list_windows()
    except WindowManagerError:
        windows = []
    
    matching = None
    for win in windows:
        if pattern.search(win.title or '') or (win.app_name and pattern.search(win.app_name)):
            matching = win
            break
    
    if not matching:
        raise WindowNotFoundError(f"No window matching '{title_pattern}'")
    
    escaped_app = matching.app_name.replace('"', '\\"') if matching.app_name else ""
    
    # Use System Events to enter fullscreen mode via AXFullScreen button or keyboard shortcut
    script = f'''
tell application "System Events"
    set targetProc to first application process whose name is "{escaped_app}"
    set frontmost of targetProc to true
    delay 0.3
    -- Try to click the fullscreen button (green button)
    try
        set targetWindow to front window of targetProc
        click (first button of targetWindow whose subrole is "AXFullScreenButton")
        return "ok"
    on error
        -- Fallback: use keyboard shortcut Ctrl+Cmd+F
        keystroke "f" using {{control down, command down}}
        return "ok"
    end try
end tell
'''
    
    try:
        result = subprocess.run(
            ["osascript", "-e", script],
            capture_output=True, text=True, timeout=10
        )
        if "ok" in result.stdout:
            return True
        if result.returncode != 0:
            raise WindowManagerError(f"AppleScript error: {result.stderr}")
        return True
    except subprocess.TimeoutExpired:
        raise WindowManagerError("Timeout making window fullscreen")
    except WindowManagerError:
        raise
    except Exception as e:
        raise WindowManagerError(f"Failed to make window fullscreen: {e}")


# =============================================================================
# Linux Backend
# =============================================================================

def _linux_check_deps():
    """Check Linux dependencies are available."""
    deps = check_dependencies()
    if not deps["available"]:
        raise DependencyMissingError(deps["message"])


def _linux_list_windows() -> List[WindowInfo]:
    """List windows on Linux using wmctrl."""
    _linux_check_deps()
    
    try:
        result = subprocess.run(
            ["wmctrl", "-l", "-G", "-p"],
            capture_output=True, text=True, timeout=5
        )
        
        windows = []
        for line in result.stdout.strip().split("\n"):
            if not line:
                continue
            parts = line.split(None, 8)
            if len(parts) >= 9:
                window_id = parts[0]
                pid = int(parts[2]) if parts[2] != "-1" else None
                x, y, w, h = int(parts[3]), int(parts[4]), int(parts[5]), int(parts[6])
                title = parts[8]
                
                windows.append(WindowInfo(
                    title=title,
                    window_id=window_id,
                    pid=pid,
                    bounds=WindowBounds(x=x, y=y, width=w, height=h)
                ))
        
        return windows
    except subprocess.TimeoutExpired:
        raise WindowManagerError("Timeout listing windows")
    except Exception as e:
        raise WindowManagerError(f"Failed to list windows: {e}")


def _linux_focus_window(title_pattern: str) -> bool:
    """Focus a window on Linux using wmctrl."""
    _linux_check_deps()
    
    windows = _linux_list_windows()
    pattern = re.compile(title_pattern, re.IGNORECASE)
    
    matching = None
    for win in windows:
        if pattern.search(win.title):
            matching = win
            break
    
    if not matching:
        raise WindowNotFoundError(f"No window matching '{title_pattern}'")
    
    try:
        subprocess.run(
            ["wmctrl", "-i", "-a", matching.window_id],
            capture_output=True, timeout=5
        )
        return True
    except Exception as e:
        raise WindowManagerError(f"Failed to focus window: {e}")


def _linux_get_window_bounds(title_pattern: str) -> WindowBounds:
    """Get window bounds on Linux."""
    windows = _linux_list_windows()
    pattern = re.compile(title_pattern, re.IGNORECASE)
    
    for win in windows:
        if pattern.search(win.title):
            if win.bounds:
                return win.bounds
            raise WindowManagerError(f"Could not get bounds for window '{win.title}'")
    
    raise WindowNotFoundError(f"No window matching '{title_pattern}'")


def _linux_get_window_id(title_pattern: str) -> Optional[str]:
    """Get X11 window ID on Linux."""
    _linux_check_deps()
    
    try:
        result = subprocess.run(
            ["xdotool", "search", "--name", title_pattern],
            capture_output=True, text=True, timeout=5
        )
        
        window_ids = result.stdout.strip().split("\n")
        if window_ids and window_ids[0]:
            return window_ids[0]
        return None
    except Exception:
        return None


def _linux_fullscreen_window(title_pattern: str) -> bool:
    """Make a window fullscreen on Linux using wmctrl."""
    _linux_check_deps()
    
    windows = _linux_list_windows()
    pattern = re.compile(title_pattern, re.IGNORECASE)
    
    matching = None
    for win in windows:
        if pattern.search(win.title):
            matching = win
            break
    
    if not matching:
        raise WindowNotFoundError(f"No window matching '{title_pattern}'")
    
    try:
        # Remove any existing fullscreen state first, then add it
        # -b add,fullscreen adds the fullscreen state
        subprocess.run(
            ["wmctrl", "-i", "-r", matching.window_id, "-b", "add,fullscreen"],
            capture_output=True, timeout=5
        )
        return True
    except subprocess.TimeoutExpired:
        raise WindowManagerError("Timeout making window fullscreen")
    except Exception as e:
        raise WindowManagerError(f"Failed to make window fullscreen: {e}")


# =============================================================================
# Windows Backend
# =============================================================================

def _windows_list_windows() -> List[WindowInfo]:
    """List windows on Windows using Win32 API."""
    import ctypes
    from ctypes import wintypes
    
    user32 = ctypes.windll.user32
    WNDENUMPROC = ctypes.WINFUNCTYPE(wintypes.BOOL, wintypes.HWND, wintypes.LPARAM)
    
    windows = []
    
    def enum_callback(hwnd, lParam):
        if user32.IsWindowVisible(hwnd):
            length = user32.GetWindowTextLengthW(hwnd)
            if length > 0:
                buffer = ctypes.create_unicode_buffer(length + 1)
                user32.GetWindowTextW(hwnd, buffer, length + 1)
                title = buffer.value
                
                rect = wintypes.RECT()
                user32.GetWindowRect(hwnd, ctypes.byref(rect))
                
                pid = wintypes.DWORD()
                user32.GetWindowThreadProcessId(hwnd, ctypes.byref(pid))
                
                windows.append(WindowInfo(
                    title=title,
                    window_id=str(hwnd),
                    pid=pid.value,
                    bounds=WindowBounds(
                        x=rect.left,
                        y=rect.top,
                        width=rect.right - rect.left,
                        height=rect.bottom - rect.top
                    )
                ))
        return True
    
    user32.EnumWindows(WNDENUMPROC(enum_callback), 0)
    return windows


def _windows_focus_window(title_pattern: str) -> bool:
    """Focus a window on Windows."""
    import ctypes
    
    windows = _windows_list_windows()
    pattern = re.compile(title_pattern, re.IGNORECASE)
    
    matching = None
    for win in windows:
        if pattern.search(win.title):
            matching = win
            break
    
    if not matching:
        raise WindowNotFoundError(f"No window matching '{title_pattern}'")
    
    user32 = ctypes.windll.user32
    hwnd = int(matching.window_id)
    user32.SetForegroundWindow(hwnd)
    user32.BringWindowToTop(hwnd)
    
    return True


def _windows_get_window_bounds(title_pattern: str) -> WindowBounds:
    """Get window bounds on Windows."""
    windows = _windows_list_windows()
    pattern = re.compile(title_pattern, re.IGNORECASE)
    
    for win in windows:
        if pattern.search(win.title):
            if win.bounds:
                return win.bounds
            raise WindowManagerError(f"Could not get bounds for window '{win.title}'")
    
    raise WindowNotFoundError(f"No window matching '{title_pattern}'")


def _windows_get_window_id(title_pattern: str) -> Optional[str]:
    """Get HWND for a window on Windows."""
    windows = _windows_list_windows()
    pattern = re.compile(title_pattern, re.IGNORECASE)
    
    for win in windows:
        if pattern.search(win.title):
            return win.window_id
    
    return None


def _windows_fullscreen_window(title_pattern: str) -> bool:
    """Make a window fullscreen (maximized) on Windows."""
    import ctypes
    
    windows = _windows_list_windows()
    pattern = re.compile(title_pattern, re.IGNORECASE)
    
    matching = None
    for win in windows:
        if pattern.search(win.title):
            matching = win
            break
    
    if not matching:
        raise WindowNotFoundError(f"No window matching '{title_pattern}'")
    
    user32 = ctypes.windll.user32
    hwnd = int(matching.window_id)
    
    # SW_MAXIMIZE = 3
    SW_MAXIMIZE = 3
    user32.ShowWindow(hwnd, SW_MAXIMIZE)
    
    return True


# =============================================================================
# Public API
# =============================================================================

def list_windows() -> List[WindowInfo]:
    """List all visible windows on the system."""
    platform = get_platform()
    
    if platform == "macos":
        return _macos_list_windows()
    elif platform == "linux":
        return _linux_list_windows()
    elif platform == "windows":
        return _windows_list_windows()
    else:
        raise WindowManagerError(f"Unsupported platform: {platform}")


def focus_window(title_pattern: str) -> bool:
    """Bring a window to the foreground by title pattern."""
    platform = get_platform()
    
    if platform == "macos":
        return _macos_focus_window(title_pattern)
    elif platform == "linux":
        return _linux_focus_window(title_pattern)
    elif platform == "windows":
        return _windows_focus_window(title_pattern)
    else:
        raise WindowManagerError(f"Unsupported platform: {platform}")


def get_window_bounds(title_pattern: str) -> WindowBounds:
    """Get the position and size of a window by title pattern."""
    platform = get_platform()
    
    if platform == "macos":
        return _macos_get_window_bounds(title_pattern)
    elif platform == "linux":
        return _linux_get_window_bounds(title_pattern)
    elif platform == "windows":
        return _windows_get_window_bounds(title_pattern)
    else:
        raise WindowManagerError(f"Unsupported platform: {platform}")


def get_window_id(title_pattern: str) -> Optional[str]:
    """Get the platform-specific window identifier."""
    platform = get_platform()
    
    if platform == "macos":
        window_id = _macos_get_window_id(title_pattern)
        return str(window_id) if window_id else None
    elif platform == "linux":
        return _linux_get_window_id(title_pattern)
    elif platform == "windows":
        return _windows_get_window_id(title_pattern)
    else:
        return None


def fullscreen_window(title_pattern: str) -> bool:
    """Make a window fullscreen by title pattern.
    
    On macOS: Uses the native fullscreen mode (green button / Ctrl+Cmd+F)
    On Linux: Uses wmctrl to add fullscreen state
    On Windows: Maximizes the window
    
    Args:
        title_pattern: Regex pattern to match window title or app name
        
    Returns:
        True if successful
        
    Raises:
        WindowNotFoundError: No window matching the pattern
        WindowManagerError: Failed to make window fullscreen
    """
    platform = get_platform()
    
    if platform == "macos":
        return _macos_fullscreen_window(title_pattern)
    elif platform == "linux":
        return _linux_fullscreen_window(title_pattern)
    elif platform == "windows":
        return _windows_fullscreen_window(title_pattern)
    else:
        raise WindowManagerError(f"Unsupported platform: {platform}")

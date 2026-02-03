"""
Window management tools - list and manage windows.
"""

from ..core.config import is_container_environment


def register_window_tools(mcp):
    """Register window management tools with the MCP server."""
    
    @mcp.tool(description="List all windows in the display. Call after browser_navigate().")
    async def list_windows() -> str:
        """List all visible windows."""
        from ..utils.window_manager import (
            list_windows as _list_windows,
            DependencyMissingError,
            WindowManagerError,
        )
        
        try:
            windows = _list_windows()
            
            if not windows:
                return "No visible windows found."
            
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
            
            return output
        
        except DependencyMissingError as e:
            return f"Missing dependencies: {str(e)}"
        except WindowManagerError as e:
            return f"Error listing windows: {str(e)}"
    
    @mcp.tool(description="Check availability of window management tools (wmctrl, xdotool).")
    async def window_tools() -> str:
        """Check window management tool availability."""
        from ..utils.window_manager import check_dependencies
        
        deps = check_dependencies()
        
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
        
        return output
    
    # Only register fullscreen tool in host mode (not available in container)
    if not is_container_environment():
        @mcp.tool(description="Make browser window fullscreen for better demo recording. HOST MODE ONLY. Call after browser_navigate() and list_windows().")
        async def fullscreen_window(window_title: str = None) -> str:
            """Make a window fullscreen by title pattern.
            
            Args:
                window_title: Window title pattern to match (e.g., 'Chrome', 'Firefox').
                             If not provided, will try to auto-detect browser window.
            
            Returns:
                Status message indicating success or failure.
            """
            from ..utils.window_manager import (
                fullscreen_window as _fullscreen_window,
                list_windows as _list_windows,
                WindowNotFoundError,
                WindowManagerError,
                get_platform,
            )
            
            # Auto-detect browser if no title provided
            if not window_title:
                browser_patterns = ["Chrome", "Firefox", "Safari", "Arc", "Brave", "Edge", "Chromium"]
                try:
                    windows = _list_windows()
                    for win in windows:
                        for pattern in browser_patterns:
                            if pattern.lower() in (win.app_name or "").lower() or pattern.lower() in (win.title or "").lower():
                                window_title = win.app_name or pattern
                                break
                        if window_title:
                            break
                except Exception:
                    pass
                
                if not window_title:
                    return "Could not auto-detect browser window. Please provide window_title parameter."
            
            try:
                _fullscreen_window(window_title)
                platform = get_platform()
                
                if platform == "macos":
                    return f"Window '{window_title}' set to fullscreen mode.\nNote: macOS fullscreen animation takes ~1 second. Wait before recording."
                elif platform == "linux":
                    return f"Window '{window_title}' set to fullscreen mode."
                elif platform == "windows":
                    return f"Window '{window_title}' maximized."
                else:
                    return f"Window '{window_title}' fullscreen attempted."
                    
            except WindowNotFoundError as e:
                return f"Window not found: {str(e)}\nTip: Run list_windows() to see available windows."
            except WindowManagerError as e:
                return f"Error: {str(e)}"

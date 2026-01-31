"""
Demo Recording Protocol - Split into 4 Phase-Based Guides

This module contains the demo recording protocol split into focused guides:
1. get_planning_guide() - Phase 1: How to plan your demo
2. get_setup_guide() - Phase 2: Pre-recording setup and verification
3. get_recording_guide() - Phase 3: What to do DURING recording
4. get_assembly_guide() - Phase 4: Post-recording assembly and troubleshooting

The original get_protocol() is deprecated but kept for backwards compatibility.
"""

# =============================================================================
# PHASE 1: PLANNING GUIDE
# =============================================================================

PLANNING_GUIDE = """
# Demo Planning Guide (Phase 1 of 4)

**Call this FIRST** before creating any demo. This guide covers how to structure,
script, and plan your demo for maximum impact.

After planning, call `get_recording_setup_guide` for Phase 2.

---

## Core Principles

### ONE STEP = ONE VIDEO + ONE AUDIO

Each demo step MUST have:
- **Exactly 1 video file** (recording of that step's actions)
- **Exactly 1 audio file** (TTS voiceover for that step)

**WRONG**: Recording the entire demo as one video, then adding voiceover
**RIGHT**: Recording each step separately, syncing each step, then concatenating

### ⚠️ CRITICAL: RECORD FIRST, SCRIPT AFTER (MANDATORY)

**DO NOT generate audio scripts before recording!**

The correct workflow for EACH step is:

```
1. TAKE PRE-SCREENSHOT → See what content will be recorded
2. RECORD THE VIDEO → Perform the actions for this step
3. TAKE POST-SCREENSHOT → See where the recording ended
4. WRITE THE SCRIPT → Based on what the screenshots show
5. GENERATE AUDIO → Using text_to_speech for the script
6. SYNC VIDEO + AUDIO → Using adjust_video_to_audio_length
```

**WHY THIS ORDER MATTERS:**

| Old Way (Script First) | New Way (Record First) |
|------------------------|------------------------|
| Write script guessing what you'll show | Record, then describe what you actually showed |
| Audio doesn't match visuals | Audio perfectly describes the visuals |
| Have to re-record if actions differ | Script naturally matches the recording |
| Disconnect between audio and video | Tight alignment every time |

**The screenshots tell you exactly what to say:**
- PRE-SCREENSHOT: Shows the starting state the viewer sees
- POST-SCREENSHOT: Shows the ending state after your actions
- SCRIPT: Describes the journey from start to end

### USE ONLY MCP TOOLS

**DO NOT** use manual FFmpeg or terminal commands.
**ALWAYS** use the MCP tools provided.

This ensures:
- Consistent behavior across machines
- Reusable workflows for other users
- Proper error handling
- Portability and easy installation

---

## Demo Types - Universal Approach

This protocol works for ANY type of demo:

### Web Application Demos
```
Examples: Google Search, Gmail, GitHub, any SaaS app
Actions: Navigate, search, click, type, show results
```

### Jupyter Notebook Demos
```
Examples: Data science tutorials, ML demos
Actions: Execute cells, scroll to show code/output
```

### Documentation/Tutorial Demos
```
Examples: README walkthroughs, API docs
Actions: Navigate sections, highlight code blocks
```

### Multi-Page Workflow Demos
```
Examples: E-commerce checkout, user registration
Actions: Fill forms, navigate between pages, show confirmations
```

### The Same Tools Work for ALL Types

The getademo MCP provides: recording, audio, video editing
The browser MCP provides: navigation, interaction, verification

**Together they can demo ANYTHING in a browser.**

---

## Demo Structure Planning

Before recording, create a structured plan:

```
Demo: [Title]
├── Step 1: [Description] - [Expected duration: Xs]
├── Step 2: [Description] - [Expected duration: Xs]
├── ...
└── Step N: [Description] - [Expected duration: Xs]

Total Expected Duration: X minutes
```

### Timing Guidelines

| Content Type | Recommended Duration |
|--------------|---------------------|
| Title/intro | 5-10 seconds |
| Simple action | 10-20 seconds |
| Code execution | 15-30 seconds |
| Complex output | 20-40 seconds |
| Summary/conclusion | 10-15 seconds |

---

## Script Writing Guidelines

Write narration scripts that are:

- **Conversational**: Write as if explaining to a colleague
- **Concise**: Aim for 15-30 seconds per step
- **Technical but accessible**: Define terms when first used
- **Action-oriented**: Describe what's happening on screen
- **Paced for viewing**: Allow time for viewers to see the results

### Example Script Structure

```
[Step N: Title]
"Now we [action being performed].
Notice how [key observation].
This is important because [explanation].
The result shows [outcome]."
```

### Voice Selection

- Use **"onyx"** for authoritative, professional tone
- Use **"nova"** for friendly, approachable tone
- Add brief pauses in scripts using "..." for natural rhythm

---

## Quick Start Template (Record First, Script After)

Use this template for each step - note that the script is written AFTER recording:

```
# Demo: [Title]

## Step 1: [Name]

### A. PRE-RECORDING
  - Navigate to: [starting position]
  - Screenshot: step_01_pre.png
  - Verify: [what should be visible at start]

### B. RECORD VIDEO
  - Start recording: step_01_raw.mp4
  - Actions during recording:
    1. [0-2s] WAIT - viewer sees initial state
    2. [2-Xs] [Your actions: scroll, click, type, etc.]
    3. [Final 2s] WAIT - viewer absorbs result
  - Stop recording

### C. POST-RECORDING
  - Screenshot: step_01_post.png
  - Verify: [what should be visible at end]

### D. WRITE SCRIPT (based on screenshots!)
  - Look at step_01_pre.png: What does viewer see at start?
  - Look at step_01_post.png: What does viewer see at end?
  - Write narration describing the journey:
    "Starting from [pre-screenshot content],
     we [action performed],
     and now we can see [post-screenshot content]."

### E. GENERATE AUDIO
  - text_to_speech(text="[your script]", output="step_01_audio.mp3")

### F. SYNC & FINALIZE
  - adjust_video_to_audio_length(video, audio, output="step_01_final.mp4")

[Repeat A-F for each step, then concatenate all step_XX_final.mp4 files]
```

### Example: Writing Script from Screenshots

```
PRE-SCREENSHOT shows:  Google Maps homepage with search bar
POST-SCREENSHOT shows: Red Hat Ireland office with directions panel

SCRIPT (written AFTER recording):
"Let's use Google Maps to find the closest Red Hat office. 
 I'll search for Red Hat offices in the search bar.
 Here we can see the Red Hat Ireland office in Dublin's Temple Bar area,
 with the address and directions panel ready to go."
```

**The screenshots are your guide - describe what they show!**

---

## Visual Must Match Narration

**What the audio says = What the screen shows**

For each step:
1. READ the narration text
2. IDENTIFY what visual content the narration describes
3. PLAN the screen actions to show that exact content
4. CENTER the most relevant content in the viewport

During recording:
- When audio says "let's look at the results" -> results must be visible
- When audio says "notice the feature" -> that feature must be centered
- When audio mentions specific text/code -> that text/code must be on screen

**WRONG**: Audio describes search results while screen shows title
**RIGHT**: Audio describes search results while screen shows and highlights search results

---

## Planning Template Per Step

```
Narration: "[What the audio will say]"
Visual:    "[What must be visible on screen]"
Focus:     "[What should be centered/highlighted]"
Actions:   "[What interactions happen during recording]"
```

---

## Next Steps

After planning your demo:
1. Call `get_recording_setup_guide` for Phase 2 (pre-recording setup)
2. Call `get_recording_actions_guide` for Phase 3 (during recording)
3. Call `get_video_assembly_guide` for Phase 4 (final assembly)
"""


# =============================================================================
# PHASE 2: RECORDING SETUP GUIDE
# =============================================================================

SETUP_GUIDE = """
# Recording Setup Guide (Phase 2 of 4)

**Call this after planning your demo.** This guide covers pre-recording setup,
window management, and MANDATORY verification steps.

After setup, call `get_recording_actions_guide` for Phase 3.

---

## ⚠️ CRITICAL: THE #1 CAUSE OF BAD DEMOS

**NOT verifying what is being recorded BEFORE and AFTER each step.**

You MUST:
1. Take a screenshot BEFORE recording each step
2. EXAMINE the screenshot to verify the content is correct
3. Take a screenshot AFTER recording each step  
4. EXAMINE the screenshot to verify the recording captured the right content
5. If ANYTHING is wrong, DELETE and RE-RECORD

**NEVER start recording without visual confirmation of what will be captured!**

---

## ⚠️ CRITICAL: FULLSCREEN BROWSER SETUP (MANDATORY)

**The browser MUST be in FULLSCREEN mode for consistent recording.**

### ONE-TIME Setup at Demo Start

```
1. CHECK YOUR SCREEN SIZE FIRST (CRITICAL!)
   - Run list_screens() to see your display resolution
   - Note your main screen dimensions (e.g., 1728x1117)
   - Choose viewport size SMALLER than your screen:
     * For 1728-wide screens: use width=1680, height=1050
     * For 1920-wide screens: use width=1920, height=1080

2. NAVIGATE to the target URL using playwright_navigate()
   - Use viewport dimensions that FIT your screen
   - Example: playwright_navigate(url="...", width=1680, height=1050)

3. VERIFY browser is visible: list_windows()
   - Look for "Chrome for Testing" or the page title
   - CHECK the window bounds (x + width must be < screen width)
   - If NOT in list: See "Playwright Visibility" section below

4. GET the exact window title pattern from list_windows()
   - Example: "Cloud Native Agent Platform – Google Chrome for Testing"

5. VERIFY window fits on screen:
   - From list_windows() output, check Bounds: x, y, w, h
   - Ensure: x + w < screen_width (no right cutoff)
   - Ensure: y + h < screen_height (no bottom cutoff)

6. TAKE SCREENSHOT to verify:
   - playwright_screenshot() 
   - Examine: Is the full page visible (not cut off)?
   - Is the browser chrome (tabs, address bar) hidden or minimal?

7. RECORD the window title pattern - you'll use this for ALL steps
```

### NEVER DO THIS

| Bad Practice | Why It's Bad | Correct Approach |
|--------------|--------------|------------------|
| Different window sizes per step | Inconsistent video, zoom issues | Set window size ONCE at start |
| Region-based recording | Captures wrong areas, zoom problems | Use `capture_mode="window"` |
| Not checking window is maximized | Records partial window | Verify with screenshot BEFORE recording |
| Starting recording without screenshot | Unknown what will be captured | ALWAYS screenshot first |

---

## Pre-Recording Checklist

Before starting any demo:

- [ ] **Screen Recording Permission**: Verify macOS System Settings -> Privacy & Security -> Screen Recording has your terminal/Cursor enabled
- [ ] **Window Tools Check**: Run `check_window_tools()` to verify dependencies are installed
- [ ] **Identify Target Window**: Run `list_windows()` to find the correct window title pattern
- [ ] **MULTI-MONITOR CHECK**: Run `list_screens()` to identify your displays
- [ ] **VIEWPORT SIZE CHECK** (CRITICAL - SEE BELOW)
- [ ] **Browser Setup**:
  - Navigate with playwright_navigate(url, width=..., height=...)
  - Verify browser appears in list_windows()
  - Use a clean browser profile or incognito mode
  - Browser should be maximized/fullscreen
  - Close unnecessary tabs
- [ ] **TAKE VERIFICATION SCREENSHOT**:
  - Take screenshot with playwright_screenshot()
  - EXAMINE the screenshot - is the full browser window visible?
  - Is the correct page content showing?
  - DO NOT PROCEED until screenshot shows correct fullscreen content
- [ ] **Desktop Cleanup**: Hide desktop icons, close unrelated applications
- [ ] **Do Not Disturb**: Enable to prevent notification interruptions
- [ ] **Output Directory**: Create a dedicated folder for the demo recordings

---

## ⚠️ CRITICAL: Viewport Size Must Fit Screen (MANDATORY)

**The #2 cause of bad demos: Browser viewport larger than physical screen = content cut off!**

### The Problem

If you set `playwright_navigate(width=1920, height=1080)` but your screen is only 
1728x1117 pixels, the browser window will be LARGER than your screen and the right 
side will be CUT OFF during recording.

### MANDATORY: Check Screen Size BEFORE Setting Viewport

```
1. RUN list_screens() to see your display resolutions:
   
   Example output:
   - Screen 1 (MAIN): 1728 x 1117   <- Your main display
   - Screen 2: 1920 x 1080          <- External monitor
   
2. CHOOSE viewport dimensions SMALLER than your target screen:
   
   | Screen Resolution | Safe Viewport Size |
   |-------------------|-------------------|
   | 1728 x 1117       | 1680 x 1050       |
   | 1920 x 1080       | 1920 x 1080       |
   | 2560 x 1440       | 1920 x 1080       |
   | 1440 x 900        | 1400 x 850        |
   
3. SET viewport to fit your screen:
   playwright_navigate(url="...", width=1680, height=1050)
   
4. VERIFY window fits by checking list_windows() bounds:
   - Window x + width should be LESS than screen width
   - Window y + height should be LESS than screen height
```

### Example Verification

```python
# 1. Check screen size
list_screens()
# Output: Screen 1 (MAIN): 1728 x 1117

# 2. Navigate with SMALLER viewport
playwright_navigate(url="...", width=1680, height=1050)

# 3. Verify window fits
list_windows()
# Look for: Bounds: x=22, y=38, w=1682, h=1079
# Verify: 22 + 1682 = 1704 < 1728 ✅ (fits!)

# 4. If window is TOO BIG (x + width > screen width):
#    Browser will be CUT OFF on the right!
#    Re-navigate with smaller dimensions.
```

### Common Mistakes

| Mistake | Result | Fix |
|---------|--------|-----|
| Using 1920x1080 on a 1728-wide screen | Right 192px cut off | Use 1680x1050 |
| Not checking screen resolution first | Unknown cutoff | Always run list_screens() first |
| Assuming all screens are 1920x1080 | Inconsistent recording | Check YOUR screen size |

### Quick Reference: Safe Viewport Sizes

For most MacBook displays (1728px wide or similar):
- **Recommended:** `width=1680, height=1050`
- **Also safe:** `width=1600, height=900`

For Full HD external monitors (1920x1080):
- **Recommended:** `width=1920, height=1080`

**WHEN IN DOUBT: Use a smaller viewport. A little whitespace is better than cut-off content.**

---

## CRITICAL: Playwright Browser Visibility Issue

**⚠️ MAJOR PITFALL: Playwright browsers may NOT appear in system window lists!**

When using Playwright MCP for browser automation, the Chromium browser it spawns:
- Often does NOT appear in `list_windows()` output on macOS
- May be positioned off-screen or on a different display
- Works correctly internally (screenshots show the right content)
- BUT is NOT visible for screen recording!

### The Problem

You may see this pattern:
```
1. playwright_navigate() -> SUCCESS, page loads
2. playwright_screenshot() -> Shows correct content  
3. list_windows() -> Playwright browser NOT listed!
4. start_recording(screen) -> Records your desktop, NOT Playwright
5. Result: Recording shows the WRONG content!
```

### MANDATORY: Verify Playwright Visibility BEFORE Recording

```
1. After playwright_navigate(), call list_windows()
2. LOOK FOR the Playwright/Chromium window in the list
   - Should appear as "Chromium" or with the page title
3. IF NOT FOUND in window list:
   - The browser is NOT visible on your screen
   - Screen recording WILL NOT capture it
   - DO NOT proceed with recording!
```

### Solutions When Playwright is NOT Visible

**Option 1: Use the user's existing browser (RECOMMENDED)**
```
1. Close Playwright: playwright_close()
2. Ask user to open the URL in their regular Chrome/Firefox
3. Focus that window: focus_window(title_pattern="Chrome.*")
4. Provide click-by-click navigation instructions
5. Record using: capture_mode="window", window_title="Chrome.*"
```

**Option 2: Try relaunching Playwright**
```python
# Close and relaunch with explicit settings
playwright_close()
playwright_navigate(url="...", headless=False, width=1280, height=720)
# Check list_windows() again
# If still not visible, use Option 1
```

**Option 3: Kill all Chromium processes and restart**
```bash
pkill -9 -f Chromium
# Then relaunch Playwright
```

### Signs That Playwright is NOT Being Recorded

- Recording output shows your desktop or another app
- Playwright screenshot shows correct content, but recording doesn't
- Video is "stuck" on one page while Playwright navigated elsewhere
- User reports "nothing is happening" or "page is stuck"

**IF THIS HAPPENS**: Stop immediately, close Playwright, and switch to recording
the user's visible browser instead.

---

## CRITICAL: Multi-Monitor Setup

**IF YOU HAVE MULTIPLE MONITORS, THIS SECTION IS MANDATORY!**

Screen recording defaults to `screen_index=1` which is usually the MAIN/built-in display.
If your target window is on a different display, you WILL record the wrong screen!

### Step 1: Identify your screens
```
list_screens()
```
This shows:
- Screen 1 (MAIN): Usually built-in display
- Screen 2: Usually first external monitor  
- Screen 3+: Additional monitors

### Step 2: Determine which screen your browser is on
- Look at where the browser window is physically located
- OR use `get_window_bounds()` - x coordinates > main display width = external monitor

### Step 3: Use WINDOW mode recording (RECOMMENDED)

**ALWAYS USE WINDOW MODE - It captures the exact window consistently:**
```python
# Get exact window title from list_windows() output
# Example: "Cloud Native Agent Platform – Google Chrome for Testing"
start_recording(
    capture_mode="window",
    window_title="Google Chrome for Testing",  # Pattern from list_windows()
    output_path="...",
    width=1920,
    height=1080
)
```

**Why WINDOW mode is best:**
- Captures ONLY the target window, regardless of other apps
- Consistent frame size across all recording steps
- Works even if window is partially covered
- No zoom issues from incorrect region bounds

**AVOID region-based recording** - it often captures wrong areas:
```python
# DON'T DO THIS - causes inconsistent capture and zoom issues
bounds = get_window_bounds(title_pattern="Chrome.*")
start_recording(capture_mode="region", capture_region={...})  # AVOID!
```

**FALLBACK: Screen mode with focus**
```python
# Only use if window mode doesn't work on your platform
focus_window(title_pattern="Google Chrome for Testing")
# Wait for window to come to front
start_recording(capture_mode="screen", screen_index=1, output_path="...")
```

---

## Ensuring Correct Window is Recorded

**CRITICAL**: Before recording, ensure you're capturing the right window!

### Step 1: List available windows
```python
list_windows()
```
This shows all visible windows with their titles. Look for your browser:
- "Cloud Native Agent Platform – Google Chrome for Testing"
- Or the page title + browser name

**Record this pattern - you'll use it for ALL steps!**

### Step 2: ALWAYS use Window Mode Recording

**Window Mode (MANDATORY for consistent demos):**
```python
start_recording(
    capture_mode="window",
    window_title="Google Chrome for Testing",  # Pattern from list_windows
    output_path="step_N_raw.mp4",
    width=1920,
    height=1080
)
```

Why window mode is essential:
- Captures ONLY the target window, regardless of other apps
- Consistent frame size across ALL steps
- No zoom issues from region coordinate problems
- Works even if window is partially covered

**Fallback: Focus + Screen Mode**
```python
# Only use if window mode doesn't work on your platform
focus_window(title_pattern="Google Chrome for Testing")
# Wait a moment for window to come to front
start_recording(capture_mode="screen", screen_index=1, output_path="...")
```

### Step 3: AVOID Region-Based Recording

**DO NOT use region-based recording** - it causes zoom and framing issues:
```python
# DON'T DO THIS - causes inconsistent capture
bounds = get_window_bounds(title_pattern="Chrome.*")
start_recording(capture_mode="region", capture_region={...})  # AVOID!
```

Region recording problems:
- Window position changes = captures wrong area
- Dimension rounding = inconsistent frame sizes
- Multi-monitor issues = captures wrong screen area

---

## Ensuring Consistent Window Recording

**DO NOT zoom or manipulate the page content.** Just ensure the browser window is properly set up.

### The Simple Rule: Fullscreen Browser + Window Mode Recording

```
1. SET browser to 1920x1080 at start:
   playwright_navigate(url="...", width=1920, height=1080)

2. VERIFY browser is in list_windows()

3. TAKE screenshot and EXAMINE it:
   - Is the full browser window visible?
   - Is the page content showing correctly?
   - Is the window maximized/fullscreen?

4. RECORD using window mode:
   start_recording(capture_mode="window", window_title="...", width=1920, height=1080)

5. SAME window setup for ALL steps - don't change it!
```

### What NOT to Do

| Bad Practice | Why It's Bad |
|--------------|--------------|
| Zooming page content (125%, 150%) | Creates inconsistent video frames |
| Different window sizes per step | Video will have varying zoom levels |
| Region-based recording | Captures wrong areas, zoom issues |
| Not verifying with screenshot | Unknown what's being recorded |
| Manipulating CSS/styles | Unexpected layout changes |

### If Content Doesn't Fill the Window

**ACCEPT IT** - A page with whitespace is better than inconsistent zoom levels.

Only adjust if absolutely necessary:
- Use the app's designed resolution (e.g., 1280x720 for smaller apps)
- Set this ONCE at the start and keep it consistent for ALL steps

---

## MCP Tools Reference

### Recording Tools

| Tool | Purpose |
|------|---------|
| `text_to_speech` | Generate voiceover audio (OpenAI/Edge TTS) |
| `start_recording` | Start recording (supports screen, window, or region modes) |
| `stop_recording` | Stop recording and save file |
| `recording_status` | Check if recording is in progress |
| `adjust_video_to_audio_length` | **KEY TOOL**: Speed up/slow down video to match audio |
| `concatenate_videos` | Join step videos into final demo |
| `get_media_info` | Get duration/resolution info |
| `get_audio_duration` | Get exact audio duration |

### Window Management Tools

| Tool | Purpose |
|------|---------|
| `list_windows` | List all visible windows (titles, IDs, bounds) |
| `focus_window` | Bring a window to the foreground by title pattern |
| `get_window_bounds` | Get window position and size (x, y, width, height) |
| `check_window_tools` | Check if window tools are available on this system |
| `list_screens` | **MULTI-MONITOR**: List all displays with screen_index mapping |

### Recording Capture Modes

| Mode | Description | Recommendation |
|------|-------------|----------------|
| `window` | Capture specific window by title | ✅ **ALWAYS USE THIS** - Consistent framing, no zoom issues |
| `screen` | Capture entire screen | ⚠️ Fallback only - Use with `focus_window()` first |
| `region` | Capture a specific screen area | ❌ **AVOID** - Causes zoom/framing inconsistencies |

### Browser Tools (from Playwright or browser MCP)

| Tool | Purpose |
|------|---------|
| `browser_navigate` / `playwright_navigate` | Go to any URL |
| `browser_snapshot` / `playwright_screenshot` | Get page state / take screenshot |
| `browser_evaluate` / `playwright_evaluate` | Execute JS (scrollIntoView, custom actions) |
| `browser_click` / `playwright_click` | Click elements |
| `browser_type` / `playwright_fill` | Type text |
| `browser_resize` / `playwright_resize` | Set browser dimensions (1920x1080 recommended) |

---

## ⚠️ MANDATORY Verification Workflow

**EVERY step requires screenshot verification BEFORE and AFTER recording.**

### Before Recording Each Step:

```
1. Navigate/scroll to starting position
2. TAKE SCREENSHOT (playwright_screenshot)
3. READ THE SCREENSHOT FILE (use read_file on the PNG)
4. VERIFY:
   ✓ Full browser window visible (not partial)?
   ✓ Correct page/content showing?
   ✓ Window is maximized/fullscreen?
   ✓ No dialogs or overlays blocking content?
5. IF ANY CHECK FAILS:
   - Fix the issue
   - Re-take screenshot
   - Re-verify
6. ONLY start recording when ALL checks pass
```

### After Recording Each Step:

```
1. TAKE SCREENSHOT immediately after stop_recording()
2. READ THE SCREENSHOT FILE
3. VERIFY:
   ✓ Recording ended on expected content?
   ✓ Window still fullscreen (didn't resize)?
   ✓ Correct final state for this step?
4. IF ANY CHECK FAILS:
   - DELETE the raw recording
   - Go back and re-record the step
5. ONLY proceed to audio sync when verification passes
```

### Summary: Screenshot Verification Checklist

For EACH step:
- [ ] Pre-recording screenshot taken
- [ ] Pre-recording screenshot EXAMINED (not just taken!)
- [ ] Pre-recording verification passed
- [ ] Recording completed
- [ ] Post-recording screenshot taken
- [ ] Post-recording screenshot EXAMINED
- [ ] Post-recording verification passed

**NEVER skip screenshot verification. It's the difference between good and terrible demos.**

---

## Next Steps

After setup is complete:
1. Call `get_recording_actions_guide` for Phase 3 (what to do DURING recording)
2. Call `get_video_assembly_guide` for Phase 4 (final assembly)
"""


# =============================================================================
# PHASE 3: RECORDING ACTIONS GUIDE
# =============================================================================

RECORDING_GUIDE = """
# Recording Actions Guide (Phase 3 of 4)

**Call this when you're ready to record.** This guide covers what to do DURING
recording to create engaging, interactive demos.

After recording, call `get_video_assembly_guide` for Phase 4.

---

## CRITICAL: Interactive Demo Actions (NOT Static Screenshots)

**A good demo shows REAL interactions, not still images.**

The #1 mistake is creating boring, static demos where nothing moves. During recording,
you MUST perform actual interactions that viewers can follow.

### What Makes a Demo Engaging

| Boring Demo | Engaging Demo |
|-------------|---------------|
| Static screenshot | Smooth scrolling through content |
| Jump cut to result | Showing the click, then the result |
| Text appears instantly | Typing character by character |
| No cursor movement | Deliberate cursor positioning |
| Rushed transitions | Pauses to let viewer absorb |

---

## Scrolling Patterns

**Slow, deliberate scrolls let viewers follow along:**

```
1. START at the top of the content
2. PAUSE 2-3 seconds (viewer sees initial state)
3. SCROLL slowly (2-3 seconds per scroll)
4. PAUSE at each section for 3-5 seconds
5. SCROLL to next section
6. REPEAT until content is shown
```

### Scroll Methods (in order of reliability)

**JavaScript `scrollIntoView` (MOST RELIABLE):**
```javascript
element.scrollIntoView({ behavior: 'smooth', block: 'start' });
```

**Keyboard Page Down (RELIABLE):**
- Press `PageDown` key for large jumps
- Press `ArrowDown` for fine control

**JavaScript `scrollBy` (LESS RELIABLE):**
```javascript
window.scrollBy({ top: 300, behavior: 'smooth' });
```

**IMPORTANT**: After each scroll, WAIT at least 2 seconds for the animation.

---

## Click Demonstrations

**Show viewers WHAT you're clicking and WHY:**

```
1. MOVE cursor to the element (visible cursor travel)
2. HOVER over the element for 1 second (visual cue)
3. CLICK the element
4. WAIT 2-3 seconds for the result
5. SHOW the result/change that occurred
```

### Example Click Sequence

```python
# During recording:
playwright_hover(selector="button.submit")  # Hover first
# Wait 1 second
playwright_click(selector="button.submit")  # Then click
# Wait 2-3 seconds for result
# Scroll to show the result if needed
```

---

## Form/Input Filling

**Type slowly so viewers can read what's being entered:**

```
1. CLICK the input field
2. PAUSE 1 second
3. TYPE slowly (character by character if possible)
4. PAUSE after typing (show the completed input)
5. MOVE to next field or submit
```

### Slow Typing

If your browser tool supports it:
```python
browser_type(selector="input", text="hello@example.com", slowly=True)
```

Or type with delays:
```python
playwright_fill(selector="input", value="hello@example.com")
# The value appears - pause to let viewer see it
```

---

## Navigation Flow

**Click menu items one at a time, don't jump:**

```
1. SHOW the current page/state
2. PAUSE 2 seconds
3. CLICK the navigation item
4. WAIT for page transition (2-3 seconds)
5. HIGHLIGHT/SCROLL to the new content
6. PAUSE to let viewer see the change
```

---

## Standard In-Recording Action Pattern

For EACH step, follow this pattern:

```
1. START recording
2. WAIT 2-3 seconds (viewer sees initial state)
3. PERFORM first action (scroll/type/click)
4. WAIT for result (animation complete, output visible)
5. FOCUS result (center it in viewport)
6. PAUSE 3-5 seconds (viewer reads the result)
7. (Optional) PERFORM additional actions
8. WAIT 2-3 seconds at end (final state absorption)
9. STOP recording
```

---

## NEVER DO THIS

These mistakes create boring, unprofessional demos:

| Mistake | Why It's Bad | Fix |
|---------|--------------|-----|
| **Static screenshots as video** | No motion, boring | ALWAYS use real screen recording |
| **Rushing through content** | Viewers can't follow | Pause 3-5 seconds on key content |
| **Skipping the interaction** | Just showing before/after | Show the CLICK, the TYPING, the SCROLL |
| **Jerky cursor movements** | Unprofessional | Move cursor smoothly and deliberately |
| **No pauses** | Overwhelming | Pause after EVERY action |
| **Headless browser recording** | Can't record invisible browser | Use a VISIBLE browser window |
| **Recording without checking list_windows()** | Playwright may be invisible | ALWAYS verify browser appears in window list BEFORE recording |
| **Assuming Playwright is visible** | Playwright often runs off-screen | Check list_windows(); if not found, use user's existing browser |

---

## Screenshot Verification (MANDATORY)

### BEFORE Recording Each Step

```
1. TAKE SCREENSHOT of the current browser/app state
2. READ THE SCREENSHOT - actually look at it, don't just take it
3. VERIFY: Is this the correct content for this step?
   - If NO: Navigate/scroll to correct content, take another screenshot, verify again
   - If YES: Proceed to recording
4. NEVER start recording without visual confirmation of correct content
```

### AFTER Recording Each Step

```
1. TAKE SCREENSHOT immediately after stopping recording
2. READ THE SCREENSHOT
3. VERIFY: Did the recording capture the intended content?
   - If NO: DELETE the recording and RE-RECORD the entire step
   - If YES: Proceed to audio sync
```

---

## Per-Step Recording Workflow (MANDATORY - DO NOT SKIP)

⚠️ **THIS IS THE MOST IMPORTANT SECTION** ⚠️

The #1 cause of bad demos is skipping screenshot verification. Follow this EXACT sequence for EACH step:

```
═══════════════════════════════════════════════════════════════════════
STEP A: PRE-RECORDING VERIFICATION (DO NOT SKIP!)
═══════════════════════════════════════════════════════════════════════

1. NAVIGATE/SCROLL to starting position for this step

2. ★★★ TAKE SCREENSHOT ★★★
   - Call playwright_screenshot(name="step_N_pre_verify")
   - This screenshot shows what the recording WILL capture

3. ★★★ EXAMINE THE SCREENSHOT ★★★
   - Actually READ the image file (use read_file on the PNG)
   - Ask yourself: Is this EXACTLY what should be recorded?
   - Is the FULL browser window visible?
   - Is the correct PAGE CONTENT showing?
   - Is the window MAXIMIZED (no partial window)?

4. ★★★ IF ANYTHING IS WRONG - FIX IT ★★★
   - Wrong content? → Navigate/scroll and re-screenshot
   - Partial window? → Maximize browser and re-screenshot
   - Wrong page? → Navigate to correct page and re-screenshot
   - REPEAT until screenshot shows EXACTLY what you want to record

5. ONLY proceed when screenshot verification PASSES

═══════════════════════════════════════════════════════════════════════
STEP B: RECORDING PHASE
═══════════════════════════════════════════════════════════════════════

6. Focus the target window:
   focus_window(title_pattern="Google Chrome for Testing")

7. START recording with WINDOW mode:
   start_recording(
       capture_mode="window",
       window_title="Google Chrome for Testing",  # From list_windows()
       output_path="step_N_raw.mp4",
       width=1920,
       height=1080
   )

8. WAIT 2-3 seconds (viewer sees initial state)

9. EXECUTE IN-RECORDING ACTIONS:
   - SCROLL to reveal content as audio describes it
   - CLICK buttons/links as needed
   - TYPE in input fields slowly
   - WAIT after each action (2 seconds minimum)
   - PAUSE on key information (3-5 seconds)

10. WAIT 2-3 seconds at end (viewer absorbs final state)

11. STOP recording:
    stop_recording()

═══════════════════════════════════════════════════════════════════════
STEP C: POST-RECORDING VERIFICATION (DO NOT SKIP!)
═══════════════════════════════════════════════════════════════════════

12. ★★★ TAKE SCREENSHOT ★★★
    - Call playwright_screenshot(name="step_N_post_verify")

13. ★★★ EXAMINE THE SCREENSHOT ★★★
    - Is this the expected END state for this step?
    - Did the navigation/scrolling work correctly?
    - Is the window still fullscreen (not resized)?

14. ★★★ IF VERIFICATION FAILS ★★★
    - DELETE the raw recording file
    - Go back to STEP A and re-record
    - DO NOT proceed with a bad recording!

15. ONLY proceed to SCRIPT WRITING when post-recording verification PASSES

═══════════════════════════════════════════════════════════════════════
STEP D: WRITE SCRIPT BASED ON SCREENSHOTS (CRITICAL!)
═══════════════════════════════════════════════════════════════════════

16. ★★★ COMPARE PRE AND POST SCREENSHOTS ★★★
    - PRE-SCREENSHOT (step_N_pre_verify.png): Starting state
    - POST-SCREENSHOT (step_N_post_verify.png): Ending state
    - IDENTIFY: What changed? What did the viewer see happen?

17. ★★★ WRITE NARRATION THAT DESCRIBES THE VISUAL JOURNEY ★★★
    Example format:
    "Starting from [describe pre-screenshot],
     we [describe the action you performed],
     and now we can see [describe post-screenshot]."
    
    The script should ONLY describe what is actually visible!

18. ★★★ GENERATE AUDIO FROM YOUR SCRIPT ★★★
    text_to_speech(
        text="[Your script based on screenshots]",
        output_path="step_N_audio.mp3",
        voice="onyx"
    )

═══════════════════════════════════════════════════════════════════════
STEP E: SYNC VIDEO WITH AUDIO
═══════════════════════════════════════════════════════════════════════

19. SYNC the video to match audio duration:
    adjust_video_to_audio_length(
        video_path="step_N_raw.mp4",
        audio_path="step_N_audio.mp3",
        output_path="step_N_final.mp4",
        add_audio=True
    )

20. VERIFY the final video has correct duration and audio
```

### WHY RECORD FIRST, SCRIPT AFTER?

| Problem with Script-First | Solution with Record-First |
|---------------------------|---------------------------|
| Audio says "click the blue button" but button is red | Script describes what you actually see |
| Audio mentions feature not visible on screen | Script only mentions visible content |
| Timing mismatch between audio and visuals | Audio naturally matches recording length |
| Re-record if actions don't match script | Script adapts to whatever you recorded |

**The screenshots tell you EXACTLY what to say. Use them!**

### WHY THIS MATTERS

Without screenshot verification:
- You won't know if the browser was visible
- You won't know if the window was fullscreen
- You won't know if the correct content was showing
- You'll waste time recording bad content
- You'll get inconsistent zoom/framing across steps

**5 seconds of verification prevents 5 minutes of re-work.**

---

## Recording Best Practices

During recording:

- **Move slowly and deliberately** - viewers need time to follow
- **Pause after each action** - let results fully render (2-3 seconds)
- **Keep cursor movements smooth** - avoid jerky motions
- **Center important content** - position key elements in the middle of screen
- **Avoid excessive scrolling** - plan content to fit in viewport when possible
- **Match visual to narration** - show what the audio describes

---

## Failure Recovery

If you recorded the wrong content:
1. **IMMEDIATELY STOP** - do not continue to the next step
2. **DELETE** the bad recording file
3. **NAVIGATE** to the correct content
4. **TAKE SCREENSHOT** to verify correct content
5. **RE-RECORD** the entire step from scratch

Do NOT try to salvage or fix partial/wrong recordings.

---

## Focus the Relevant Content

The most important content must be:
- **Centered** in the viewport (not at edges)
- **Fully visible** (not cut off or partially scrolled)
- **Given time** to be seen (pause 2-3 seconds on key content)

---

## Next Steps

After recording all steps:
1. Call `get_video_assembly_guide` for Phase 4 (sync audio, concatenate, quality check)
"""


# =============================================================================
# PHASE 4: VIDEO ASSEMBLY GUIDE
# =============================================================================

ASSEMBLY_GUIDE = """
# Video Assembly Guide (Phase 4 of 4)

**Call this after recording each step.** This guide covers the complete per-step
workflow: script writing from screenshots, audio generation, synchronization,
and final concatenation.

---

## ⚠️ CRITICAL: Complete Per-Step Workflow

### For EACH step, follow this EXACT sequence:

```
┌─────────────────────────────────────────────────────────────────────┐
│ STEP N WORKFLOW (Repeat for each step)                              │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  1. RECORD VIDEO                                                    │
│     ├── Take PRE-screenshot (see starting state)                   │
│     ├── Record step_N_raw.mp4                                      │
│     └── Take POST-screenshot (see ending state)                    │
│                                                                     │
│  2. WRITE SCRIPT (based on screenshots!)                           │
│     ├── Compare PRE and POST screenshots                           │
│     ├── Describe what viewer sees at start                         │
│     ├── Describe the action/transition                             │
│     └── Describe what viewer sees at end                           │
│                                                                     │
│  3. GENERATE AUDIO                                                  │
│     └── text_to_speech(script) → step_N_audio.mp3                  │
│                                                                     │
│  4. SYNC VIDEO + AUDIO                                              │
│     └── adjust_video_to_audio_length() → step_N_final.mp4          │
│                                                                     │
│  5. PROCEED TO NEXT STEP                                            │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

**DO NOT batch all recordings first, then all scripts, then all audio!**
**Complete each step fully before moving to the next.**

---

## Writing Scripts from Screenshots

### The Screenshot-to-Script Process

```python
# After recording step N, you have:
# - step_N_pre_verify.png  (starting state)
# - step_N_raw.mp4         (the recording)
# - step_N_post_verify.png (ending state)

# READ both screenshots and write script that describes:
# 1. What the viewer sees at the START
# 2. What ACTION happens during the recording
# 3. What the viewer sees at the END

script = '''
Here we can see [describe pre-screenshot content].
Now I'll [describe the action you performed].
As you can see, [describe post-screenshot content].
'''

# Generate audio from the script
text_to_speech(text=script, output_path="step_N_audio.mp3", voice="onyx")
```

### Example: Writing from Screenshots

```
PRE-SCREENSHOT shows:
  - OpenShift Overview page
  - Cluster status: healthy
  - Left sidebar visible

POST-SCREENSHOT shows:
  - Projects list page
  - Multiple projects visible (kagent, agentic-workflows, etc.)
  - Resource usage columns

SCRIPT (written from screenshots):
"From the OpenShift Overview, let's navigate to the Projects section.
 Here we can see all the namespaces in our cluster, including
 AI workloads like kagent and agentic-workflows. Each project
 shows its memory and CPU usage at a glance."
```

---

## Audio-Video Synchronization

### The Golden Rule: SPEED ADJUST, NEVER CUT

To sync video with audio:
- **SPEED UP** the video if it's longer than audio
- **SLOW DOWN** the video if it's shorter than audio
- **NEVER trim/cut** the video - ALL visual content must be preserved

Use `adjust_video_to_audio_length` which automatically speeds up or slows down.

### Per-Step Sync Workflow

For each recorded step (after writing script and generating audio):

```python
# 1. Get the audio duration (from the script you just wrote)
audio_duration = get_audio_duration(audio_path="step_01_audio.mp3")

# 2. Adjust video to match audio length
adjust_video_to_audio_length(
    video_path="step_01_raw.mp4",
    audio_path="step_01_audio.mp3",
    output_path="step_01_final.mp4",
    add_audio=True  # Merge audio into output
)

# 3. Verify the output duration matches audio
final_info = get_media_info(file_path="step_01_final.mp4")
# Duration should match audio_duration
```

---

## Timing Verification Checklist

**BEFORE concatenating, verify each step:**

```
1. CHECK each step video duration matches its audio duration
   - Use get_media_info() on each step_XX_final.mp4
   - Compare to audio duration from text_to_speech output

2. IF video duration differs from audio by more than 0.5s:
   - Re-run adjust_video_to_audio_length
   - Or re-record the step if quality is poor

3. CALCULATE total expected duration:
   - Sum all audio durations
   - Example: 13.5s + 20.0s + 24.2s + 24.6s + 24.2s + 12.7s = 119.2s

4. AFTER concatenation, verify final duration:
   - Should be within 1-2 seconds of expected total
   - If off by more, check individual steps
```

---

## Video Concatenation

After all steps are recorded and synced:

```python
# 1. List all step segments in order
video_paths = [
    "step_01_final.mp4",
    "step_02_final.mp4",
    "step_03_final.mp4",
    # ... all steps
]

# 2. Concatenate into final video
concatenate_videos(
    video_paths=video_paths,
    output_path="final/demo_final.mp4"
)

# 3. Verify final video
get_media_info(file_path="final/demo_final.mp4")
```

---

## Quality Checks

Before delivery, verify:

- [ ] **Audio-video sync**: Audio matches visuals throughout
- [ ] **Content visible**: All text/code is readable
- [ ] **No artifacts**: No glitches, freezes, or corruption
- [ ] **Smooth transitions**: Steps flow naturally
- [ ] **Duration correct**: Total matches expected (sum of audio durations)
- [ ] **Resolution**: 1920x1080 or intended resolution
- [ ] **Audio quality**: Clear voice, no distortion

### Quick Verification

```python
# Check final video properties
info = get_media_info(file_path="final/demo_final.mp4")
# Verify: Duration, Resolution, Video/Audio codecs
```

---

## File Organization

Recommended folder structure:

```
demo_recordings/
├── [demo_name]/
│   ├── steps/
│   │   ├── step_01_raw.mp4      # Raw recording
│   │   ├── step_01_audio.mp3    # TTS audio
│   │   ├── step_01_final.mp4    # Adjusted with audio
│   │   ├── step_02_raw.mp4
│   │   ├── step_02_audio.mp3
│   │   ├── step_02_final.mp4
│   │   └── ...
│   ├── scripts/
│   │   └── voiceover_script.md
│   └── final/
│       └── [demo_name]_final.mp4
```

---

## Common Issues and Fixes

### Recording Issues

| Issue | Solution |
|-------|----------|
| **INCONSISTENT ZOOM/FRAMING** | Browser window wasn't fullscreen for all steps. Set window size ONCE at start, use window-mode recording |
| **PARTIAL WINDOW RECORDED** | Browser wasn't maximized. Take screenshot BEFORE recording to verify fullscreen |
| **DIFFERENT ZOOM LEVELS PER STEP** | Used region-based recording with different bounds. Use `capture_mode="window"` instead |
| **RECORDED WRONG CONTENT** | YOU SKIPPED SCREENSHOT VERIFICATION! Delete recording, take screenshot, verify content, re-record |
| **Recorded a different page/app** | Use `focus_window()` before recording, take screenshot to verify the correct window is focused |
| **Cookie/consent dialog showing** | Handle dialogs BEFORE taking pre-recording screenshot - click accept/dismiss first |
| Recording permission denied | System Settings -> Privacy -> Screen Recording, restart Cursor |
| **Wrong window recorded** | Use `capture_mode="window"` with correct `window_title` pattern |
| **Window not found** | Run `list_windows()` to see exact window titles, adjust pattern |
| **Playwright browser invisible** | Playwright browser not in `list_windows()` = recording will fail! Close Playwright, kill Chromium processes, use user's existing browser |
| **Recording shows desktop/wrong app** | Playwright was running invisibly. Switch to user's visible browser window instead |

### Sync Issues

| Issue | Solution |
|-------|----------|
| Audio too fast/slow | Adjust script text length, regenerate TTS |
| Video too short for audio | Tool will SLOW DOWN video (no frame freeze) |
| Video too long for audio | Tool will SPEED UP video (no cutting) |
| **Final video longer than expected** | Check each step's sync - one might have extra time |
| **Audio cuts off early** | Video was trimmed instead of speed-adjusted - re-sync |

### Visual Issues

| Issue | Solution |
|-------|----------|
| Browser not maximized | Use browser_resize(1920, 1080) or F11 |
| Cursor not visible | Ensure screen_index=1 in start_recording |
| **Scroll not working** | Use `scrollIntoView()` instead of `scrollBy()`, or use PageDown key |
| **Page at wrong position** | Take screenshot to verify BEFORE recording, scroll again if needed |
| **Content not visible after scroll** | Wait 2+ seconds for smooth scroll animation to complete |

### Viewport Issues

| Issue | Solution |
|-------|----------|
| **Inconsistent zoom across steps** | Set browser size ONCE at start, use window-mode recording for ALL steps |
| **Partial window recorded** | Browser wasn't fullscreen. Take screenshot to verify BEFORE recording |
| **Content not filling viewport** | Accept whitespace - it's better than inconsistent zoom. Or use smaller resolution for all steps |
| **Different frame sizes per step** | You used region-based recording. Switch to `capture_mode="window"` |

### Platform-Specific Issues

| Issue | Solution |
|-------|----------|
| **Linux window tools missing** | Run `sudo apt install wmctrl xdotool` (or dnf/pacman equivalent) |
| **Window capture failed** | Fall back to `focus_window()` + `capture_mode="screen"` |
| **Multi-monitor wrong screen** | Use `list_screens()` to find correct screen_index, or use region-based recording |

---

## Error Recovery

### If a Step Recording Fails

When step N fails or has issues:

1. **KEEP** all completed steps (1 to N-1)
2. **DELETE** the failed step N segment
3. **RE-RECORD** step N from scratch
4. **CONTINUE** with step N+1 onwards

### If Re-recording Affects Later Steps

If re-recording step N changes timing or flow:

1. **KEEP** steps 1 to N-1
2. **DISCARD** steps N onwards
3. **RE-RECORD** from step N to the end

---

## The #1 Cause of Failed Demos

**Skipping Screenshot Verification and Inconsistent Window Setup**

If your demo has inconsistent zoom, partial windows, or wrong content, you almost
certainly made one of these mistakes:

### Mistake 1: No Screenshot Verification
1. **Did you take a screenshot BEFORE starting the recording?**
2. **Did you actually READ/EXAMINE the screenshot to verify the content?**
3. **Did you take a screenshot AFTER the recording?**

### Mistake 2: Inconsistent Window Setup
1. **Did you set the browser to fullscreen ONCE at the start?**
2. **Did you use `capture_mode="window"` (not region)?**
3. **Did you use the SAME window_title pattern for all steps?**

### Mistake 3: Using Region-Based Recording
- Region recording (`capture_region=...`) captures EXACT pixel coordinates
- If the window moves or resizes, you capture the WRONG content
- This causes zoom issues and inconsistent framing
- **ALWAYS use `capture_mode="window"` instead**

**The fix is simple**: 
1. Set browser to fullscreen ONCE at demo start
2. Use window-mode recording for ALL steps
3. Take and examine screenshots BEFORE and AFTER each step
This takes 10 seconds and prevents a terrible demo.

---

## Tips for Professional Results

1. **Consistency**: Use the same voice and tone throughout the demo
2. **Pacing**: Add brief pauses in scripts using "..." for natural rhythm
3. **Testing**: Always preview the final video before delivery
4. **Accessibility**: Speak clearly, avoid jargon without explanation

---

## Final Checklist

Before delivering your demo:

- [ ] All steps recorded with real interactions (not static screenshots)
- [ ] Each step synced to its audio duration
- [ ] Final video duration matches expected total
- [ ] Audio is clear and synchronized
- [ ] Content is visible and readable
- [ ] No glitches or artifacts
- [ ] File saved in final/ directory

---

Remember: A good demo tells a story. Each step should build on the previous one,
leading the viewer through the narrative naturally. The voiceover guides their
attention while the visuals provide proof and context.
"""


# =============================================================================
# DEPRECATED: Original Protocol (for backwards compatibility)
# =============================================================================

DEPRECATED_NOTICE = """
# DEPRECATED: get_demo_protocol

This tool returns too much information at once (800+ lines), which can overwhelm agents.

**Use the phase-based tools instead:**

1. **`get_demo_planning_guide`** (Phase 1)
   - How to structure and script your demo
   - Timing guidelines and templates
   - Call this FIRST

2. **`get_recording_setup_guide`** (Phase 2)
   - Pre-recording checklist
   - Window management and viewport optimization
   - Screen verification workflow

3. **`get_recording_actions_guide`** (Phase 3)
   - What to do DURING recording
   - Interactive actions (scrolling, clicking, typing)
   - CRITICAL for engaging, non-boring demos

4. **`get_video_assembly_guide`** (Phase 4)
   - Audio synchronization
   - Video concatenation
   - Quality checks and troubleshooting

**Workflow:**
```
Planning -> Setup -> Recording -> Assembly
```

Each guide is focused (~200 lines) and provides clear next steps.
"""


# =============================================================================
# Public Functions
# =============================================================================

def get_planning_guide() -> str:
    """Phase 1: Return the demo planning guide."""
    return PLANNING_GUIDE


def get_setup_guide() -> str:
    """Phase 2: Return the recording setup guide."""
    return SETUP_GUIDE


def get_recording_guide() -> str:
    """Phase 3: Return the recording actions guide."""
    return RECORDING_GUIDE


def get_assembly_guide() -> str:
    """Phase 4: Return the video assembly guide."""
    return ASSEMBLY_GUIDE


def get_protocol() -> str:
    """DEPRECATED: Return the deprecation notice pointing to new tools."""
    return DEPRECATED_NOTICE

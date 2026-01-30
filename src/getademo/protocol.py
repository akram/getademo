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

## Quick Start Template

Use this template to plan each step:

```
# Demo: [Title]

## Step 1: [Name]

Narration: "[Narration text - what audio will say]"

Pre-recording:
  - Scroll to: [element/heading to find]
  - Verify shows: [what must be visible]
  - Screenshot: (take one to confirm)

In-recording actions:
  1. [0-2s] WAIT - initial view
  2. [2-5s] SCROLL to [target] - reveal content
  3. [5-10s] WAIT - viewer reads
  4. [10-12s] SCROLL to [output] - show results
  5. [12-15s] WAIT - final pause

Expected duration: ~Xs audio

## Step 2: [Name]

Narration: "[Narration text]"

Pre-recording:
  - Scroll to: [element]
  - Verify shows: [content]
  - Screenshot: (take one to confirm)

In-recording actions:
  1. [0-2s] WAIT
  2. [2-Xs] [Actions...]

Expected duration: ~Xs

[Continue for all steps...]
```

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
window management, viewport optimization, and verification.

After setup, call `get_recording_actions_guide` for Phase 3.

---

## Pre-Recording Checklist

Before starting any demo:

- [ ] **Screen Recording Permission**: Verify macOS System Settings -> Privacy & Security -> Screen Recording has your terminal/Cursor enabled
- [ ] **Screen Resolution**: Set to 1920x1080 (Full HD) for best compatibility
- [ ] **Window Tools Check**: Run `check_window_tools()` to verify dependencies are installed
- [ ] **Identify Target Window**: Run `list_windows()` to find the correct window title pattern
- [ ] **MULTI-MONITOR CHECK**: Run `list_screens()` to identify your displays
- [ ] **Browser Setup**:
  - Use a clean browser profile or incognito mode
  - Hide bookmarks bar (Cmd+Shift+B in Chrome)
  - Hide extensions toolbar
  - Set browser to full-screen mode (Cmd+Shift+F or F11)
  - Close unnecessary tabs
- [ ] **Viewport Content Check**:
  - Take screenshot and verify content fills the full viewport
  - If content has empty space on sides, zoom in (125-150%) or adjust CSS
  - Remove max-width constraints if needed: `document.body.style.maxWidth = 'none'`
  - For fixed-width apps, consider recording at the app's optimal resolution
- [ ] **Desktop Cleanup**: Hide desktop icons, close unrelated applications
- [ ] **Do Not Disturb**: Enable to prevent notification interruptions
- [ ] **Output Directory**: Create a dedicated folder for the demo recordings

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

### Step 3: Use the correct recording method

**RECOMMENDED: Region-based recording (most reliable)**
```python
# This captures exactly the window, regardless of which screen it's on
bounds = get_window_bounds(title_pattern="Chrome.*")
start_recording(
    capture_mode="region",
    capture_region={"x": bounds.x, "y": bounds.y, "width": bounds.width, "height": bounds.height},
    output_path="..."
)
```

**ALTERNATIVE: Correct screen_index**
```python
# If browser is on your external monitor (screen 2):
start_recording(
    capture_mode="screen",
    screen_index=2,  # <-- Use the correct screen number!
    output_path="..."
)
```

**WRONG**: Recording screen 1 when browser is on screen 2 = recording wrong content!
**RIGHT**: Either use region-based recording OR correct screen_index

---

## Ensuring Correct Window is Recorded

**CRITICAL**: Before recording, ensure you're capturing the right window!

### 1. List available windows
```python
list_windows()
```
This shows all visible windows with their titles - note the exact title pattern.

### 2. Choose your recording method

**Option A - Window Mode (Recommended)**:
```python
start_recording(capture_mode="window", window_title="Chrome.*", output_path="...")
```
This captures ONLY the matching window, regardless of what's on top.

**Option B - Focus + Screen Mode**:
```python
focus_window(title_pattern="Chrome.*")
# Wait a moment for window to come to front
start_recording(capture_mode="screen", output_path="...")
```
Use this if window mode has issues on your platform.

### 3. Verify bounds (optional)
```python
get_window_bounds(title_pattern="Chrome.*")
```
Returns x, y, width, height - useful for region-based recording.

---

## Viewport Content Optimization

**The web page content MUST fill the entire browser viewport for professional demos.**

Many web applications have responsive layouts that may leave empty space.

### Pre-Recording Browser Optimization

```
1. RESIZE browser viewport to recording resolution (e.g., 1920x1080)
   - Use browser_resize(1920, 1080) or playwright_resize
   
2. TAKE SCREENSHOT and examine it:
   - Does the content fill the full width?
   - Is there excessive whitespace on the sides?
   - Is the navigation/sidebar properly sized?

3. IF content doesn't fill viewport, try these fixes:
   a. ZOOM IN using browser zoom (Cmd/Ctrl + Plus):
      - Execute: document.body.style.zoom = '125%' or '150%'
      - Or press Cmd/Ctrl + Plus multiple times
   
   b. USE CSS to expand content width:
      - Execute: document.querySelector('main').style.maxWidth = '100%'
      - Or: document.body.style.maxWidth = 'none'
   
   c. HIDE unnecessary sidebars/panels if possible:
      - Click collapse buttons
      - Or: document.querySelector('.sidebar').style.display = 'none'
   
   d. ADJUST viewport to match content:
      - If app is designed for 1280px, record at 1280x720 instead

4. TAKE SCREENSHOT again to verify the fix worked

5. ONLY proceed to recording when content fills the viewport properly
```

### Common Viewport Issues and Fixes

| Issue | Solution |
|-------|----------|
| Content has max-width constraint | Execute JS: `document.querySelector('.container').style.maxWidth = 'none'` |
| Large empty margins on sides | Zoom browser to 125% or 150% |
| Sidebar takes too much space | Collapse or hide the sidebar before recording |
| App designed for smaller screens | Record at the app's optimal resolution instead of 1920x1080 |
| Fixed-width layout | Use region-based recording to capture only the content area |
| Login/Auth pages with centered box | Zoom in or record at smaller resolution to fill frame |

### JavaScript Snippets for Common Fixes

**Remove max-width constraints:**
```javascript
document.querySelectorAll('*').forEach(el => {
  if (getComputedStyle(el).maxWidth !== 'none') {
    el.style.maxWidth = 'none';
  }
});
```

**Zoom the page content:**
```javascript
document.body.style.zoom = '125%';  // or '150%' for more zoom
```

**Expand main content area:**
```javascript
const main = document.querySelector('main, .main, #main, .content, #content');
if (main) {
  main.style.maxWidth = '100%';
  main.style.width = '100%';
  main.style.padding = '0 2rem';
}
```

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

| Mode | Description | Use When |
|------|-------------|----------|
| `screen` | Capture entire screen (default) | Recording full desktop, or after using `focus_window` |
| `window` | Capture specific window by title | Recording browser, simulator, or any specific app |
| `region` | Capture a specific screen area | Recording part of screen, use with `get_window_bounds` |

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

## Verification Workflow

**ALWAYS verify before recording:**

```
1. Navigate to target URL
2. Resize browser to 1920x1080
3. Apply zoom/CSS fixes if needed
4. Scroll to target element
5. Wait 2 seconds for animation
6. TAKE SCREENSHOT
7. EXAMINE screenshot - is correct content visible and centered?
8. (IF wrong) -> repeat scroll and verify
9. (IF correct) -> proceed to recording
```

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

## Per-Step Recording Workflow

For EACH step in your demo, follow this EXACT sequence:

```
PRE-RECORDING VERIFICATION (MANDATORY):
1. IDENTIFY target window: list_windows() to get correct title pattern
2. SCROLL/NAVIGATE to starting position
3. *** TAKE SCREENSHOT ***
4. *** READ THE SCREENSHOT - actually examine the image ***
5. *** VERIFY: Is this the CORRECT content for this step? ***
   - If NO: Navigate/scroll to correct content, GOTO step 3
   - If YES: proceed to recording
6. Focus the target window: focus_window(title_pattern="...")

RECORDING PHASE:
7. START recording using start_recording tool
   - PREFERRED: capture_mode="window", window_title="YourApp.*"
   - FALLBACK: focus_window() first, then capture_mode="screen"
8. WAIT 2-3 seconds (viewer sees initial state)
9. EXECUTE IN-RECORDING ACTIONS matching the narration:
   - SCROLL to reveal content as audio describes it
   - CLICK buttons/links as needed
   - TYPE in input fields slowly
   - WAIT after each action (2 seconds minimum)
   - PAUSE on key information (3-5 seconds)
10. WAIT 2-3 seconds at end (viewer absorbs final state)
11. STOP recording using stop_recording tool

POST-RECORDING VERIFICATION (MANDATORY):
12. *** TAKE SCREENSHOT ***
13. *** VERIFY: Did the recording end on the expected content? ***
    - If NO: DELETE the raw recording, GOTO step 2
    - If YES: proceed to audio sync
```

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

**Call this after recording all steps.** This guide covers audio synchronization,
video concatenation, quality checks, and troubleshooting.

---

## Audio-Video Synchronization

### The Golden Rule: SPEED ADJUST, NEVER CUT

To sync video with audio:
- **SPEED UP** the video if it's longer than audio
- **SLOW DOWN** the video if it's shorter than audio
- **NEVER trim/cut** the video - ALL visual content must be preserved

Use `adjust_video_to_audio_length` which automatically speeds up or slows down.

### Per-Step Sync Workflow

For each recorded step:

```python
# 1. Get the audio duration
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
| **RECORDED WRONG CONTENT** | YOU SKIPPED SCREENSHOT VERIFICATION! Delete recording, take screenshot, verify content, re-record |
| **Recorded a different page/app** | Use `focus_window()` before recording, take screenshot to verify the correct window is focused |
| **Cookie/consent dialog showing** | Handle dialogs BEFORE taking pre-recording screenshot - click accept/dismiss first |
| Recording permission denied | System Settings -> Privacy -> Screen Recording, restart Cursor |
| **Wrong window recorded** | Use `capture_mode="window"` with correct `window_title` pattern |
| **Window not found** | Run `list_windows()` to see exact window titles, adjust pattern |

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
| **Content not filling viewport** | Zoom browser (125-150%), remove CSS max-width constraints |
| **Empty space on sides of page** | Execute `document.body.style.zoom = '125%'` or adjust container max-width |
| **Fixed-width web app layout** | Use region-based recording to capture only the content area, or match recording resolution to app design |

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

**Skipping Screenshot Verification**

If you recorded the wrong content (wrong page, wrong app, dialog box, etc.), you almost
certainly skipped one of these critical steps:

1. **Did you take a screenshot BEFORE starting the recording?**
2. **Did you actually READ/EXAMINE the screenshot to verify the content?**
3. **Did you use focus_window() to ensure the correct app is in front?**

**The fix is simple**: ALWAYS take and examine screenshots before and after each recording.
This takes 5 seconds and prevents having to re-do 5 minutes of work.

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

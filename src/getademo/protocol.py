"""
Demo Recording Protocol

This module contains the comprehensive protocol document that agents should read
before creating any demo recording. It covers best practices, step-by-step workflows,
and troubleshooting guidance.

Use the get_demo_protocol tool to retrieve this document.
"""

DEMO_RECORDING_PROTOCOL = """
# Demo Recording Protocol

This document describes the complete workflow for creating professional demo recordings
with synchronized voiceover narration. Follow this protocol to ensure consistent,
high-quality demos.

---

## MANDATORY RULES (NOT SUGGESTIONS)

These are **RULES** that MUST be followed. Failure to follow them will result in
audio-video desync and poor quality demos.

### RULE 0: SCREENSHOT VERIFICATION IS NON-NEGOTIABLE (THE GOLDEN RULE)

**EVERY recording step MUST have screenshot verification BEFORE and AFTER.**

This is the MOST IMPORTANT rule. Failure to follow this rule WILL result in 
recording the wrong content (e.g., a cooking page instead of Google Maps).

#### BEFORE Recording Each Step:
```
1. TAKE SCREENSHOT of the current browser/app state
2. READ THE SCREENSHOT - actually look at it, don't just take it
3. VERIFY: Is this the correct content for this step?
   - If NO: Navigate/scroll to correct content, take another screenshot, verify again
   - If YES: Proceed to recording
4. NEVER start recording without visual confirmation of correct content
```

#### AFTER Recording Each Step:
```
1. TAKE SCREENSHOT immediately after stopping recording
2. READ THE SCREENSHOT
3. VERIFY: Did the recording capture the intended content?
   - If NO: DELETE the recording and RE-RECORD the entire step
   - If YES: Proceed to audio sync
```

#### FAILURE RECOVERY:
If you recorded the wrong content:
1. **IMMEDIATELY STOP** - do not continue to the next step
2. **DELETE** the bad recording file
3. **NAVIGATE** to the correct content
4. **TAKE SCREENSHOT** to verify correct content
5. **RE-RECORD** the entire step from scratch

**WRONG**: Start recording -> hope it captures the right thing -> sync audio
**RIGHT**: Screenshot -> verify correct content -> start recording -> stop -> screenshot -> verify -> sync audio

### RULE 1: ONE STEP = ONE VIDEO + ONE AUDIO

Each demo step MUST have:
- **Exactly 1 video file** (recording of that step's actions)
- **Exactly 1 audio file** (TTS voiceover for that step)

WRONG: Recording the entire demo as one video, then adding voiceover
RIGHT: Recording each step separately, syncing each step, then concatenating

### RULE 2: SPEED ADJUST, NEVER CUT

To sync video with audio:
- **SPEED UP** the video if it's longer than audio
- **SLOW DOWN** the video if it's shorter than audio
- **NEVER trim/cut** the video - ALL visual content must be preserved

Use `adjust_video_to_audio_length` which automatically speeds up or slows down.

### RULE 3: USE ONLY MCP TOOLS

**DO NOT** use manual FFmpeg or terminal commands.
**ALWAYS** use the MCP tools below.

This ensures:
- Consistent behavior across machines
- Reusable workflows for other users
- Proper error handling
- Portability and easy installation

### RULE 4: FULL WALKTHROUGH EACH STEP

During recording, you MUST show the complete action:
- Scroll through content slowly
- Show the action being performed
- Show the result/output
- Pause briefly on important information

WRONG: Start recording -> instantly run cell -> stop recording
RIGHT: Start recording -> scroll to cell -> run cell -> wait for output -> scroll to show output -> pause -> stop recording

### RULE 5: VISUAL MUST MATCH NARRATION

**What the audio says = What the screen shows**

Before recording each step:
1. READ the narration text
2. IDENTIFY what visual content the narration describes
3. PLAN the screen actions to show that exact content
4. CENTER the most relevant content in the viewport

During recording:
- When audio says "let's look at the results" -> results must be visible
- When audio says "notice the vector search" -> vector search output must be centered
- When audio mentions specific text/code -> that text/code must be on screen

WRONG: Audio describes search results while screen shows title
RIGHT: Audio describes search results while screen shows and highlights search results

### RULE 6: FOCUS THE RELEVANT CONTENT

The most important content must be:
- **Centered** in the viewport (not at edges)
- **Fully visible** (not cut off or partially scrolled)
- **Given time** to be seen (pause 2-3 seconds on key content)

Planning template for each step:
```
Narration: "[What the audio will say]"
Visual:    "[What must be visible on screen]"
Focus:     "[What should be centered/highlighted]"
```

### RULE 7: VERIFY POSITION BEFORE AND AFTER RECORDING

**Before starting EVERY step recording:**
1. **SCROLL** to the target section using `scrollIntoView()` or keyboard navigation
2. **TAKE A SCREENSHOT** to verify the correct content is visible
3. **COMPARE** the screenshot to your planned visual - is the right content centered?
4. **ONLY THEN** start recording

**After scrolling DURING recording:**
1. **ASSUME** the scroll may not have worked (browser quirks, timing issues)
2. **USE** reliable scroll methods: `element.scrollIntoView()` or Page Down key
3. **WAIT** 1-2 seconds after scroll for smooth animation to complete
4. **IF** scroll failed (detected by next screenshot), RE-RECORD the entire step

WRONG: Start recording immediately without verifying position
RIGHT: Screenshot -> verify -> start recording -> action -> screenshot -> verify -> stop

### RULE 8: IN-RECORDING ACTIONS ARE MANDATORY

Most demo steps require ACTIONS during recording, not just static viewing:
- **Scrolling** to reveal code, output, or results
- **Typing** to show how to use features
- **Clicking** to demonstrate interactions
- **Waiting** for operations to complete

**These actions ARE the demo** - without them, viewers see nothing happening.

#### Standard In-Recording Action Pattern:

```
1. START recording
2. WAIT 2-3 seconds (let viewer see initial state)
3. PERFORM action (scroll/type/click)
4. WAIT for result (animation complete, output visible)
5. FOCUS result (center it in viewport)
6. PAUSE 3-5 seconds (let viewer read the result)
7. (Optional) SCROLL to show more detail
8. STOP recording
```

#### Scrolling During Recording - BEST PRACTICES:

Use these scroll methods (in order of reliability):

1. **JavaScript `scrollIntoView`** (MOST RELIABLE):
   ```javascript
   element.scrollIntoView({ behavior: 'smooth', block: 'start' });
   ```

2. **Keyboard Page Down** (RELIABLE):
   - Press `PageDown` key for large jumps
   - Press `ArrowDown` for fine control

3. **JavaScript `scrollBy`** (LESS RELIABLE in some contexts):
   ```javascript
   window.scrollBy({ top: 300, behavior: 'smooth' });
   ```

**After each scroll, WAIT at least 2 seconds** for the smooth scroll animation.

#### Typing During Recording:

For demos showing typing:
1. Use `browser_type` with `slowly: true` to show character-by-character
2. WAIT after typing for any autocomplete/feedback
3. Show the result of the typed content

#### Clicking During Recording:

For demos showing clicks:
1. HOVER over the element first (visual cue)
2. WAIT 1 second (viewer sees what will be clicked)
3. CLICK the element
4. WAIT for result

### RULE 9: ENSURE BROWSER CONTENT FILLS THE VIEWPORT

**The web page content MUST fill the entire browser viewport for professional demos.**

Many web applications have responsive layouts that may leave empty space or not utilize
the full screen. Before recording, verify the content fills the viewport properly.

#### Pre-Recording Browser Optimization:

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

#### Common Viewport Issues and Fixes:

| Issue | Solution |
|-------|----------|
| Content has max-width constraint | Execute JS: `document.querySelector('.container').style.maxWidth = 'none'` |
| Large empty margins on sides | Zoom browser to 125% or 150% |
| Sidebar takes too much space | Collapse or hide the sidebar before recording |
| App designed for smaller screens | Record at the app's optimal resolution instead of 1920x1080 |
| Fixed-width layout | Use region-based recording to capture only the content area |
| Login/Auth pages with centered box | Zoom in or record at smaller resolution to fill frame |

#### JavaScript Snippets for Common Fixes:

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

**WRONG**: Recording a page with content only using 60% of the screen width
**RIGHT**: Adjusting zoom/CSS so content fills the viewport, or recording at optimal resolution

---

## MCP Tools Reference

### Recording Tools

| Tool | Purpose |
|------|---------|
| `text_to_speech` | Generate voiceover audio (OpenAI/Edge TTS) |
| `start_recording` | Start recording (supports screen, window, or region modes) |
| `stop_recording` | Stop recording and save file |
| `recording_status` | Check if recording is in progress |
| `adjust_video_to_audio_length` | **KEY TOOL**: Speed up/slow down video to match audio (preserves ALL frames) |
| `concatenate_videos` | Join step videos into final demo |
| `get_media_info` | Get duration/resolution info |
| `get_audio_duration` | Get exact audio duration |
| `get_demo_protocol` | Retrieve this document |

### Window Management Tools

**IMPORTANT**: Use these tools to ensure you're recording the correct window!

| Tool | Purpose |
|------|---------|
| `list_windows` | List all visible windows (titles, IDs, bounds) |
| `focus_window` | Bring a window to the foreground by title pattern |
| `get_window_bounds` | Get window position and size (x, y, width, height) |
| `check_window_tools` | Check if window tools are available on this system |
| `list_screens` | **MULTI-MONITOR**: List all displays with screen_index mapping |

### Recording Capture Modes

The `start_recording` tool supports three capture modes:

| Mode | Description | Use When |
|------|-------------|----------|
| `screen` | Capture entire screen (default) | Recording full desktop, or after using `focus_window` |
| `window` | Capture specific window by title | Recording browser, simulator, or any specific app |
| `region` | Capture a specific screen area | Recording part of screen, use with `get_window_bounds` |

**Recommended workflow for reliable recording:**

1. **For browsers/apps**: Use `capture_mode="window"` with `window_title` pattern
   ```
   start_recording(
     capture_mode="window",
     window_title="Chrome.*",  # or "Firefox", "Simulator", etc.
     output_path="/path/to/video.mp4"
   )
   ```

2. **Focus + Screen (fallback)**: If window capture fails, focus first then record screen
   ```
   focus_window(title_pattern="Chrome.*")
   start_recording(capture_mode="screen", output_path="/path/to/video.mp4")
   ```

3. **Region-based**: For precise control over what's captured
   ```
   bounds = get_window_bounds(title_pattern="MyApp")
   start_recording(
     capture_mode="region",
     capture_region={"x": bounds.x, "y": bounds.y, "width": bounds.width, "height": bounds.height},
     output_path="/path/to/video.mp4"
   )
   ```

### Browser Tools (from cursor-browser-extension MCP)

These tools control the browser and work with ANY website/web app:

| Tool | Purpose |
|------|---------|
| `browser_navigate` | Go to any URL |
| `browser_snapshot` | Get page state and element refs |
| `browser_take_screenshot` | **VERIFY POSITION** - confirm correct content visible |
| `browser_evaluate` | Execute JS (scrollIntoView, custom actions) |
| `browser_press_key` | Keyboard input (PageDown, Enter, shortcuts) |
| `browser_wait_for` | Wait N seconds or for text to appear |
| `browser_click` | Click elements by ref |
| `browser_type` | Type text (use `slowly: true` for visible typing) |
| `browser_hover` | Hover over elements |
| `browser_resize` | Set browser dimensions (1920x1080 recommended) |
| `browser_tabs` | Manage multiple tabs |

### Verification Workflow (works for ANY website)

```
1. browser_navigate -> go to target URL
2. browser_resize -> set to 1920x1080
3. browser_snapshot -> get element references
4. browser_evaluate -> scrollIntoView() to target element
5. browser_wait_for -> 2 seconds for animation
6. browser_take_screenshot -> verify correct content visible
7. (IF wrong) -> repeat scroll and verify
8. (IF correct) -> start_recording
```

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

## Phase 1: Preparation

### 1.1 Pre-Recording Checklist

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
- [ ] **Viewport Content Check** (RULE 9):
  - Take screenshot and verify content fills the full viewport
  - If content has empty space on sides, zoom in (125-150%) or adjust CSS
  - Remove max-width constraints if needed: `document.body.style.maxWidth = 'none'`
  - For fixed-width apps, consider recording at the app's optimal resolution
- [ ] **Desktop Cleanup**: Hide desktop icons, close unrelated applications
- [ ] **Do Not Disturb**: Enable to prevent notification interruptions
- [ ] **Output Directory**: Create a dedicated folder for the demo recordings

### 1.1.0 CRITICAL: Multi-Monitor Setup

**IF YOU HAVE MULTIPLE MONITORS, THIS SECTION IS MANDATORY!**

Screen recording defaults to `screen_index=1` which is usually the MAIN/built-in display.
If your target window is on a different display, you WILL record the wrong screen!

**Step 1: Identify your screens**
```
list_screens()
```
This shows:
- Screen 1 (MAIN): Usually built-in display
- Screen 2: Usually first external monitor  
- Screen 3+: Additional monitors

**Step 2: Determine which screen your browser is on**
- Look at where the browser window is physically located
- OR use `get_window_bounds()` - x coordinates > main display width = external monitor

**Step 3: Use the correct recording method**

**RECOMMENDED: Region-based recording (most reliable)**
```
# This captures exactly the window, regardless of which screen it's on
bounds = get_window_bounds(title_pattern="Chrome.*")
start_recording(
    capture_mode="region",
    capture_region={"x": bounds.x, "y": bounds.y, "width": bounds.width, "height": bounds.height},
    output_path="..."
)
```

**ALTERNATIVE: Correct screen_index**
```
# If browser is on your external monitor (screen 2):
start_recording(
    capture_mode="screen",
    screen_index=2,  # <-- Use the correct screen number!
    output_path="..."
)
```

**WRONG**: Recording screen 1 when browser is on screen 2 = recording wrong content!
**RIGHT**: Either use region-based recording OR correct screen_index

### 1.1.1 Ensuring Correct Window is Recorded

**CRITICAL**: Before recording, ensure you're capturing the right window!

1. **List available windows**:
   ```
   list_windows()
   ```
   This shows all visible windows with their titles - note the exact title pattern.

2. **Choose your recording method**:
   
   **Option A - Window Mode (Recommended)**:
   ```
   start_recording(capture_mode="window", window_title="Chrome.*", output_path="...")
   ```
   This captures ONLY the matching window, regardless of what's on top.
   
   **Option B - Focus + Screen Mode**:
   ```
   focus_window(title_pattern="Chrome.*")
   # Wait a moment for window to come to front
   start_recording(capture_mode="screen", output_path="...")
   ```
   Use this if window mode has issues on your platform.

3. **Verify bounds (optional)**:
   ```
   get_window_bounds(title_pattern="Chrome.*")
   ```
   Returns x, y, width, height - useful for region-based recording.

### 1.2 Demo Structure Planning

Before recording, create a structured plan:

```
Demo: [Title]
├── Step 1: [Description] - [Expected duration: Xs]
├── Step 2: [Description] - [Expected duration: Xs]
├── ...
└── Step N: [Description] - [Expected duration: Xs]

Total Expected Duration: X minutes
```

### 1.3 Script Writing Guidelines

Write narration scripts that are:

- **Conversational**: Write as if explaining to a colleague
- **Concise**: Aim for 15-30 seconds per step
- **Technical but accessible**: Define terms when first used
- **Action-oriented**: Describe what's happening on screen
- **Paced for viewing**: Allow time for viewers to see the results

Example script structure:
```
[Step N: Title]
"Now we [action being performed].
Notice how [key observation].
This is important because [explanation].
The result shows [outcome]."
```

---

## Phase 2: Step-by-Step Recording

### 2.1 Per-Step Workflow

For EACH step in your demo, follow this EXACT sequence:

```
PLANNING PHASE:
1. WRITE the narration text for this step
2. PLAN the visual content:
   - What must be visible when each phrase is spoken?
   - What should be centered/focused?
   - What IN-RECORDING ACTIONS are needed? (scroll, type, click)
3. GENERATE TTS audio using text_to_speech tool
4. NOTE the audio duration (returned by tool)

PRE-RECORDING VERIFICATION (MANDATORY - DO NOT SKIP):
5. IDENTIFY target window: list_windows() to get correct title pattern
6. SCROLL/NAVIGATE to starting position
7. *** TAKE SCREENSHOT ***
8. *** READ THE SCREENSHOT - actually examine the image ***
9. *** VERIFY: Is this the CORRECT content for this step? ***
   - If NO: Navigate/scroll to correct content, GOTO step 7
   - If YES: proceed to recording
10. Focus the target window: focus_window(title_pattern="...")

RECORDING PHASE:
11. START recording using start_recording tool
    - PREFERRED: capture_mode="window", window_title="YourApp.*"
    - FALLBACK: focus_window() first, then capture_mode="screen"
12. WAIT 2-3 seconds (viewer sees initial state)
13. EXECUTE IN-RECORDING ACTIONS matching the narration:
    - SCROLL to reveal content as audio describes it
    - WAIT after each scroll (2 seconds minimum)
    - PAUSE on key information (3-5 seconds)
    - SHOW the results/output
14. WAIT 2-3 seconds at end (viewer absorbs final state)
15. STOP recording using stop_recording tool

POST-RECORDING VERIFICATION (MANDATORY - DO NOT SKIP):
16. *** TAKE SCREENSHOT ***
17. *** READ THE SCREENSHOT - actually examine the image ***
18. *** VERIFY: Did the recording end on the expected content? ***
    - If NO: DELETE the raw recording, GOTO step 6
    - If YES: proceed to audio sync

AUDIO SYNC:
19. ADJUST video speed to match audio using adjust_video_to_audio_length tool
    (This speeds up or slows down - NEVER cuts content)
20. VERIFY: The final duration should match audio duration
21. PROCEED to next step
```

**CRITICAL**: Steps marked with *** are NON-NEGOTIABLE. Skipping them WILL result in
recording the wrong content and wasting time re-doing work.

**IF RECORDING IS WRONG**: 
1. DELETE the bad recording immediately
2. Navigate to correct content
3. Take screenshot to verify
4. RE-RECORD the entire step from scratch
Do NOT try to salvage or fix partial/wrong recordings.

### 2.2 Recording Best Practices

During recording:

- **Move slowly and deliberately** - viewers need time to follow
- **Pause after each action** - let results fully render (2-3 seconds)
- **Keep cursor movements smooth** - avoid jerky motions
- **Center important content** - position key elements in the middle of screen
- **Avoid excessive scrolling** - plan content to fit in viewport when possible

### 2.3 Timing Guidelines

| Content Type | Recommended Duration |
|--------------|---------------------|
| Title/intro | 5-10 seconds |
| Simple action | 10-20 seconds |
| Code execution | 15-30 seconds |
| Complex output | 20-40 seconds |
| Summary/conclusion | 10-15 seconds |

---

## Phase 3: Error Recovery

### 3.1 If a Step Recording Fails

When step N fails or has issues:

1. **KEEP** all completed steps (1 to N-1)
2. **DELETE** the failed step N segment
3. **RE-RECORD** step N from scratch
4. **CONTINUE** with step N+1 onwards

### 3.2 If Re-recording Affects Later Steps

If re-recording step N changes timing or flow that affects later steps:

1. **KEEP** steps 1 to N-1
2. **DISCARD** steps N onwards
3. **RE-RECORD** from step N to the end

### 3.3 Common Issues and Fixes

| Issue | Solution |
|-------|----------|
| **RECORDED WRONG CONTENT** | YOU SKIPPED SCREENSHOT VERIFICATION! Delete recording, take screenshot, verify content, re-record |
| **Recorded a different page/app** | Use `focus_window()` before recording, take screenshot to verify the correct window is focused |
| **Cookie/consent dialog showing** | Handle dialogs BEFORE taking pre-recording screenshot - click accept/dismiss first |
| Recording permission denied | System Settings -> Privacy -> Screen Recording, restart Cursor |
| Audio too fast/slow | Adjust script text length, regenerate TTS |
| Video too short for audio | Tool will SLOW DOWN video (no frame freeze) |
| Video too long for audio | Tool will SPEED UP video (no cutting) |
| Browser not maximized | Use browser_resize(1920, 1080) or F11 |
| Cursor not visible | Ensure screen_index=1 in start_recording |
| **Wrong window recorded** | Use `capture_mode="window"` with correct `window_title` pattern |
| **Window not found** | Run `list_windows()` to see exact window titles, adjust pattern |
| **Linux window tools missing** | Run `sudo apt install wmctrl xdotool` (or dnf/pacman equivalent) |
| **Window capture failed** | Fall back to `focus_window()` + `capture_mode="screen"` |
| **Scroll not working** | Use `scrollIntoView()` instead of `scrollBy()`, or use PageDown key |
| **Page at wrong position** | Take screenshot to verify BEFORE recording, scroll again if needed |
| **Content not visible after scroll** | Wait 2+ seconds for smooth scroll animation to complete |
| **Jupyter notebook scroll issues** | Use `scrollIntoView()` on heading elements, not `window.scrollBy()` |
| **Content not filling viewport** | Zoom browser (125-150%), remove CSS max-width constraints, or record at app's optimal resolution (see RULE 9) |
| **Empty space on sides of page** | Execute `document.body.style.zoom = '125%'` or adjust container max-width |
| **Fixed-width web app layout** | Use region-based recording to capture only the content area, or match recording resolution to app design |

### 3.4 The #1 Cause of Failed Demos: Skipping Screenshot Verification

If you recorded the wrong content (wrong page, wrong app, dialog box, etc.), you almost
certainly skipped one of these critical steps:

1. **Did you take a screenshot BEFORE starting the recording?**
2. **Did you actually READ/EXAMINE the screenshot to verify the content?**
3. **Did you use focus_window() to ensure the correct app is in front?**

**The fix is simple**: ALWAYS take and examine screenshots before and after each recording.
This takes 5 seconds and prevents having to re-do 5 minutes of work.

---

## Phase 4: Final Assembly

### 4.1 Concatenation

After all steps are recorded and adjusted:

```
1. LIST all step segments in order: step_01.mp4, step_02.mp4, ...
2. USE concatenate_videos tool to join them
3. VERIFY final video plays correctly
```

### 4.2 Quality Checks

Before delivery, verify:

- [ ] Audio and video are synchronized throughout
- [ ] All content is visible and readable
- [ ] No recording artifacts or glitches
- [ ] Transitions between steps are smooth
- [ ] Total duration matches expectations

### 4.3 File Organization

Recommended folder structure:
```
demo_recordings/
├── [demo_name]/
│   ├── steps/
│   │   ├── step_01_raw.mp4      # Raw recording
│   │   ├── step_01_audio.mp3    # TTS audio
│   │   ├── step_01_final.mp4    # Adjusted with audio
│   │   ├── step_02_raw.mp4
│   │   └── ...
│   ├── scripts/
│   │   └── voiceover_script.md
│   └── final/
│       └── [demo_name]_final.mp4
```

---

## Quick Start Template

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
  - Screenshot:

In-recording actions:
  1. [0-2s] WAIT
  2. [2-Xs] [Actions...]

Expected duration: ~Xs

[Continue for all steps...]
```

---

## Tips for Professional Results

1. **Voice Selection**: Use "onyx" for authoritative tone, "nova" for friendly tone
2. **Pacing**: Add brief pauses in scripts using "..." for natural rhythm
3. **Emphasis**: Important terms can be emphasized with slightly slower speech
4. **Consistency**: Use the same voice and tone throughout the demo
5. **Accessibility**: Speak clearly, avoid jargon without explanation
6. **Testing**: Always preview the final video before delivery

---

Remember: A good demo tells a story. Each step should build on the previous one,
leading the viewer through the narrative naturally. The voiceover guides their
attention while the visuals provide proof and context.

**The same MCP tools work for ANY website or web application.**
"""


def get_protocol() -> str:
    """Return the demo recording protocol document."""
    return DEMO_RECORDING_PROTOCOL



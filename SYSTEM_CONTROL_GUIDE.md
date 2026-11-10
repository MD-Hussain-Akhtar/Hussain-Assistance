# System Control Feature for ZOYA - Complete Implementation Guide

## Overview
ZOYA now has controlled Windows desktop access with screen awareness and file/app interaction capabilities. All system actions require explicit user confirmation via a confirmation popup.

## Architecture

```
VOICE INPUT
    ↓
INTENT PARSER (Gemini)
    ↓
system_control TOOL CALL
    ↓
CONFIRMATION POPUP (Frontend)
    ↓
SYSTEM_AGENT (Backend)
    ├── Screen Capture (mss + PIL)
    ├── File Operations (pathlib, os)
    ├── App Launcher (subprocess)
    ├── Keyboard/Mouse (pyautogui)
    ├── Volume Control (pycaw)
    └── Brightness Control (screen_brightness_control)
    ↓
WINDOWS OS
```

## Hard Safety Requirements

✅ **All Requirements Implemented:**

1. **Explicit User Confirmation**: Every system action requires user approval via confirmation popup
2. **Permission-Based Access Control**: Three permission flags in settings.json:
   - `system_control` - Enable/disable all system control features
   - `screen_access` - Enable/disable screenshot capture
   - `file_access` - Enable/disable file/folder operations
3. **Single-Frame Screenshots Only**: No continuous recording
4. **Detailed Logging**: Every action logged to `system_agent.log`
5. **Clear Refusals**: If permissions disabled, Zoya refuses with explanation

## Permission Configuration

Edit `backend/settings.json`:

```json
{
  "tool_permissions": {
    "system_control": false,  // ← SET TO true TO ENABLE
    "screen_access": false,   // ← SET TO true FOR SCREENSHOTS
    "file_access": false      // ← SET TO true FOR FILE OPERATIONS
  }
}
```

**Default State**: All disabled (safe by default)

## Supported System Control Actions

### 1. Screen Capture
**When to use**: Zoya needs to see what's on screen

```python
action: "capture_screen"
# Returns: base64-encoded PNG image + timestamp
```

**User command examples**:
- "Meri screen dikha do"
- "What's on my screen right now?"
- "Desktop dekho"

**Requirements**: `screen_access: true`

---

### 2. Open Application
**When to use**: Launch a Windows app

```python
action: "open_app"
params: {
  "app_name": "notepad"  # or "chrome", "calculator", "explorer", etc.
}
```

**Supported apps**:
- `notepad` → notepad.exe
- `explorer` → explorer.exe
- `chrome` → chrome.exe
- `calculator` → calc.exe
- `paint` → mspaint.exe
- `cmd` → cmd.exe
- `powershell` → powershell.exe
- `vscode` → code.exe
- And more...

**User command examples**:
- "Notepad open karo"
- "Chrome kholo"
- "Calculator open karo"

**Requirements**: None (always available, uses confirmation only)

---

### 3. Open File by Path
**When to use**: Open a specific file with default application

```python
action: "open_file"
params: {
  "file_path": "C:/Users/ayush/Documents/report.pdf"
}
```

**User command examples**:
- "Ye file kholo" (with file path provided)
- "Open my resume"
- "Desktop ke PDF ko open kar"

**Requirements**: `file_access: true`

---

### 4. Open Folder
**When to use**: Open a folder in Windows Explorer

```python
action: "open_folder"
params: {
  "folder_path": "C:/Users/ayush/Desktop"
}
```

**User command examples**:
- "Desktop folder open karo"
- "Documents folder kholo"
- "Ye folder open kar"

**Requirements**: `file_access: true`

---

### 5. Find File by Name
**When to use**: Search for a file across common locations

```python
action: "find_file"
params: {
  "file_name": "report.pdf",
  "search_paths": null  # Optional: uses Desktop, Documents, Home if null
}
```

**Search locations** (when search_paths is null):
- `C:/Users/{USER}/Desktop`
- `C:/Users/{USER}/Documents`
- `C:/Users/{USER}`

**User command examples**:
- "Desktop pe jo PDF hai use open karo"
- "My resume find kar aur open kar"
- "Photo find karo"

**Requirements**: `file_access: true`

---

### 6. Type Text
**When to use**: Type text into the currently focused application

```python
action: "type_text"
params: {
  "text": "I am Zoya, your AI assistant",
  "delay": 0.05  # Optional: delay between keystrokes (default 0.05s)
}
```

**User command examples**:
- "Notepad me likho I am Zoya"
- "Type this message"
- "Write my name"

**Requirements**: None (pyautogui must be available)

---

### 7. Control Volume
**When to use**: Set system volume level

```python
action: "control_volume"
params: {
  "level": 50  # 0-100 (percentage)
}
```

**User command examples**:
- "Volume 50 kar do"
- "Sound badha do"
- "Mute karo"  (level: 0)
- "Full volume"  (level: 100)

**Requirements**: None (uses pycaw if available, falls back to nircmd)

---

### 8. Control Brightness
**When to use**: Adjust screen brightness

```python
action: "control_brightness"
params: {
  "level": 75  # 0-100 (percentage)
}
```

**User command examples**:
- "Brightness 30 kar do"
- "Screen bright karo"
- "Itna andhera hai, jyada bright karo"

**Requirements**: `screen_brightness_control` package installed

---

### 9. Click Mouse
**When to use**: Click at specific screen coordinates

```python
action: "click_mouse"
params: {
  "x": 640,
  "y": 480
  # If x,y not provided: clicks at current position
}
```

**Requirements**: None (pyautogui must be available)

---

### 10. Press Key
**When to use**: Simulate keyboard key press

```python
action: "press_key"
params: {
  "key": "enter"  # "tab", "space", "delete", etc.
}
```

**Supported keys**: enter, tab, space, backspace, delete, home, end, pageup, pagedown, etc.

**Requirements**: None (pyautogui must be available)

---

### 11. Get System Capabilities
**When to use**: Check what system control features are available

```python
action: "get_capabilities"
# Returns: {"screenshot": bool, "keyboard": bool, "mouse": bool, ...}
```

---

## Installation & Setup

### Step 1: Install Required Packages

```bash
cd backend
pip install -r requirements.txt
```

Key packages added:
- `pyautogui` - Screen capture, mouse, keyboard control
- `keyboard` - Advanced keyboard handling
- `screen_brightness_control` - Brightness adjustment
- `pycaw` - Volume control
- `mss` - Fast screenshot capture

### Step 2: Enable Permissions (Carefully!)

Edit `backend/settings.json`:

```json
{
  "tool_permissions": {
    "system_control": true,    // ← ENABLE SYSTEM CONTROL
    "screen_access": true,     // ← ENABLE SCREENSHOTS
    "file_access": true        // ← ENABLE FILE ACCESS
  }
}
```

### Step 3: Start the Backend

```bash
cd backend
python server.py
```

Check for logs in `backend/system_agent.log`

### Step 4: Test with Voice Commands

**Try these commands** (requires `system_control: true`):

1. **Simple Screenshot**:
   - "Meri screen dekho"
   - Backend: Captures screenshot, sends base64 to frontend
   - Frontend: Stores in localStorage as `lastScreenshot`

2. **Open Notepad & Type**:
   - "Notepad kholo"
   - (Wait for confirmation popup to appear and approve)
   - "Now type: Hello Zoya"
   - Zoya opens Notepad, then types text into it

3. **Adjust Volume**:
   - "Volume 50 kar do"
   - (Approval required)
   - System volume set to 50%

4. **Brighten Screen**:
   - "Screen bright karo"
   - (Approval required)
   - Brightness increased

5. **Find and Open File**:
   - "Desktop pe jo PDF hai use open karo"
   - (Confirmation required)
   - Zoya finds and opens the PDF

## Confirmation Popup UI

When Zoya wants to perform a system action:

```
┌─────────────────────────────────────────┐
│ ⚠️  AUTHORIZATION REQUIRED               │
│     Desktop Access                       │
├─────────────────────────────────────────┤
│                                          │
│ Zoya wants to: Open application: notepad│
│                                          │
│ ⚠️  This action will control your         │
│     desktop. Make sure you trust this.   │
│                                          │
│ Function: system_control                │
│ Parameters: {...}                       │
│                                          │
│  [DENY REQUEST]  [AUTHORIZE EXECUTION]  │
│                                          │
└─────────────────────────────────────────┘
```

**Color Scheme**:
- 🔴 Orange/Red for dangerous actions (system_control)
- 🔵 Cyan for normal actions
- Clear human-readable descriptions

## Logging & Debugging

All system actions are logged to `backend/system_agent.log`:

```
[SYSTEM_AGENT] 2026-01-27 10:15:32,123 - INFO - System Agent initialized
[SYSTEM_AGENT] 2026-01-27 10:15:35,456 - INFO - Capturing screen...
[SYSTEM_AGENT] 2026-01-27 10:15:36,789 - INFO - Screen captured successfully: 1920x1080
[SYSTEM_AGENT] 2026-01-27 10:15:40,012 - INFO - Opening application: notepad
[SYSTEM_AGENT] 2026-01-27 10:15:41,345 - INFO - Application launched: notepad.exe
[SYSTEM_AGENT] 2026-01-27 10:15:42,678 - INFO - Typing text: Hello Zoya
```

**View logs in real-time**:
```bash
tail -f backend/system_agent.log
```

## Security Considerations

### ✅ What's Implemented

1. **Permission Flags**: Three separate permissions for fine-grained control
2. **Confirmation Required**: Every action needs explicit user approval
3. **No Background Monitoring**: Screenshots only on command
4. **Detailed Logging**: All actions logged for audit trail
5. **Clear Refusals**: User informed if permission denied
6. **Subprocess Isolation**: System actions run in isolated subprocess
7. **Error Handling**: Safe exception handling, no crash-on-error

### ⚠️ Recommendations

1. **Keep system_control: false** by default
2. **Only enable when needed** for specific tasks
3. **Monitor the logs** for unusual activity
4. **Use confirmation popup** as final safety gate
5. **Test in safe environment** before production use
6. **Keep packages updated**: `pip install --upgrade pyautogui screen_brightness_control pycaw`

## User Commands Examples

### Complete Example Flows

**Flow 1: Open Notepad and Write**
```
User: "Notepad open karke likho I am Zoya"
↓
Zoya: "Opening Notepad and will type the message"
↓
[CONFIRMATION POPUP] User clicks "Authorize"
↓
Notepad opens
↓
[CONFIRMATION POPUP] User clicks "Authorize" 
↓
Text typed into Notepad
```

**Flow 2: Screenshot and Show**
```
User: "Meri desktop dekho"
↓
Zoya: "Let me capture your screen"
↓
[CONFIRMATION POPUP] User clicks "Authorize"
↓
Screenshot captured
↓
Zoya: "Here's what I see on your screen"
[Shows screenshot in chat]
```

**Flow 3: Adjust Display**
```
User: "Brightness 30 kar do"
↓
Zoya: "Adjusting brightness to 30%"
↓
[CONFIRMATION POPUP] User clicks "Authorize"
↓
Screen brightness set to 30%
```

**Flow 4: Find and Open File**
```
User: "Desktop pe jo PDF hai use open karo"
↓
Zoya: "Searching for PDF on your desktop"
↓
[CONFIRMATION POPUP showing file path] User clicks "Authorize"
↓
PDF file opened with default application
```

## Troubleshooting

### Issue: Permissions denied even with `system_control: true`

**Solution**: Check all three permission flags:
```json
{
  "system_control": true,
  "screen_access": true,    // ← Also required for screenshots
  "file_access": true       // ← Also required for file operations
}
```

### Issue: Screenshot shows blank/black image

**Solutions**:
1. Make sure `screen_access: true`
2. Check pyautogui installation: `python -c "import pyautogui; print('OK')"`
3. Check mss installation: `python -c "import mss; print('OK')"`
4. Check logs: `tail backend/system_agent.log`

### Issue: Typewriter actions not working

**Solution**:
1. Ensure pyautogui is installed
2. Try with different delay: `"delay": 0.1` (slower)
3. Make sure target app is focused before typing
4. Check for special characters in text (may need HTML encoding)

### Issue: Volume control not working

**Solutions**:
1. For pycaw: `pip install pycaw`
2. For nircmd fallback: Download from nirsoft.net
3. Check Windows audio settings
4. Restart audio service if needed

### Issue: Brightness control not working

**Solution**:
1. Install package: `pip install screen_brightness_control`
2. Note: May not work on some integrated graphics
3. Check monitor has DDC-CI support
4. Try manual brightness first (not all monitors support programmatic control)

## Technical Details

### Files Modified

```
backend/
├── system_agent.py          ← NEW: Main system control module
├── ada.py                   ← MODIFIED: Added system_control handler
├── tools.py                 ← MODIFIED: Registered system_control tool
├── server.py                ← MODIFIED: Added on_system_data callback
└── settings.json            ← MODIFIED: Added permission flags

src/
└── components/
    └── ConfirmationPopup.jsx  ← MODIFIED: Enhanced for system_control

requirements.txt             ← MODIFIED: Added new packages
```

### Key Classes & Functions

**system_agent.py - SystemAgent Class**:
```python
class SystemAgent:
    def capture_screen() -> dict
    def open_app(app_name: str) -> dict
    def open_file(file_path: str) -> dict
    def open_folder(folder_path: str) -> dict
    def find_file(file_name: str, search_paths: list) -> dict
    def type_text(text: str, delay: float) -> dict
    def control_volume(level: int) -> dict
    def control_brightness(level: int) -> dict
    def click_mouse(x: int, y: int) -> dict
    def press_key(key: str) -> dict
    def get_system_capabilities() -> dict
```

### Tool Definition (tools.py)

```python
system_control_tool = {
    "name": "system_control",
    "description": "Controls Windows desktop...",
    "parameters": {
        "action": "open_app|open_file|capture_screen|...",
        "params": {action-specific parameters}
    }
}
```

### Gemini Integration

Gemini's tool use capability automatically:
1. Detects user intent for desktop control
2. Constructs appropriate `system_control` tool call
3. Includes correct action and parameters
4. Example: "Open notepad and type hello" → 
   - Tool 1: `action: "open_app", params: {app_name: "notepad"}`
   - Tool 2: `action: "type_text", params: {text: "hello"}`

## Performance Notes

- **Screenshot**: ~100-200ms (depends on resolution)
- **App Launch**: ~500ms-2s (depends on app)
- **File Search**: ~100ms-5s (depends on depth and number of files)
- **Type Text**: ~50ms per character
- **Volume/Brightness**: <100ms

## Future Enhancements (Optional)

1. **Mouse Movement**: Add `move_mouse` action
2. **Window Management**: Minimize, maximize, close windows
3. **Clipboard Access**: Copy/paste operations
4. **OCR Integration**: Read text from screen
5. **Gesture Recognition**: Detect hand gestures on webcam
6. **App-Specific Scripts**: Custom automation for specific apps
7. **Macro Recording**: Record and replay sequences

## Support & Debugging

**To report issues**:
1. Enable logging: `tail -f backend/system_agent.log`
2. Capture the error message
3. Check frontend console: Press F12 in Electron window
4. Record the voice command you used
5. Check `settings.json` permissions

**Test script**:
```python
# backend/test_system_control.py
from system_agent import get_system_agent

agent = get_system_agent()

# Test capabilities
print(agent.get_system_capabilities())

# Test screenshot
result = agent.capture_screen()
print(f"Screenshot: {result['success']}")

# Test app launch
result = agent.open_app("notepad")
print(f"App launch: {result['success']}")
```

---

**Status**: ✅ COMPLETE & TESTED
**Version**: 1.0
**Last Updated**: January 27, 2026


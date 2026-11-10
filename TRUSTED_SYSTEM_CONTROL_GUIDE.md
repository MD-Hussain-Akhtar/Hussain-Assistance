# TRUSTED SYSTEM CONTROL MODE - Implementation Guide
**Zoya Jarvis-Style Automation with Minimal Popups**

## Overview

Trusted System Control Mode enables Zoya to execute system automation tasks (opening apps, controlling volume, etc.) with **minimal authorization popups**, functioning like Siri or Jarvis while maintaining security. Trust decisions are **persistent** across restarts.

---

## Architecture

### Three Components

#### 1. **TrustedPermissionsManager** (`backend/trusted_permissions.py`)
Handles all trust logic and persistent storage:
- **Enabled/Disabled state** - Controls whether trusted mode is active
- **Allowed Apps** - List of apps that can open without confirmation (e.g., ["chrome", "notepad"])
- **Allowed Actions** - List of system actions allowed without confirmation (e.g., ["open_app", "type_text", "control_volume"])
- **Remember Forever** - Persists trust across application restarts
- **Persistent File** - `trusted_permissions.json` stores all settings

**Action Safety Classification:**
```
SAFE ACTIONS (never require popup if trusted):
- open_app, type_text, control_volume, control_brightness, press_key, click_mouse

DANGEROUS ACTIONS (still require popup even if trusted):
- find_file, open_file, open_folder, capture_screen

ALWAYS REQUIRE POPUP (security-critical):
- execute_shell, delete_file, modify_registry
```

#### 2. **Voice Intent Parser** (`backend/voice_intent_parser.py`)
Processes natural language voice commands to configure trusted mode:

**Supported Voice Intents:**
| Command | Action |
|---------|--------|
| "Zoya, is system ko trust kar lo" | Enable trusted mode |
| "enable trusted mode" | Enable trusted mode |
| "Zoya, future me popup mat dikhana" | Set remember_forever=true |
| "remember forever" | Set remember_forever=true |
| "Zoya, sirf chrome aur notepad allow karo" | Set allowed_apps=["chrome", "notepad"] |
| "allow chrome and notepad" | Set allowed_apps=["chrome", "notepad"] |
| "disable trusted mode" | Disable trusted mode |
| "stop showing popups" | Disable trusted mode |

#### 3. **Backend Integration** (`backend/server.py`, `backend/ada.py`)
- Socket.IO event handlers for frontend control
- Confirmation skip logic at confirmation request time
- Voice intent checking in user input handler

---

## How It Works

### Workflow

```
User says: "Open Chrome"
    ↓
[ADA] Detects system_control tool call
    ↓
[CHECK] Is trusted mode enabled? → YES
    ↓
[CHECK] Is "open_app" in allowed_actions? → YES
    ↓
[CHECK] Is "chrome" in allowed_apps? → YES
    ↓
[CHECK] Is this a "dangerous action"? → NO
    ↓
✅ SKIP CONFIRMATION POPUP
    ↓
🚀 EXECUTE DIRECTLY: chrome.exe opens
    ↓
Toast: "Trusted action executed"
```

### Security Safeguards

1. **Dangerous Actions Always Require Confirmation**
   - File operations (open, find, delete)
   - Screen capture
   - Shell execution
   - Registry modification

2. **Default: Trusted Mode DISABLED**
   - All actions show popups until explicitly enabled
   - No security regression

3. **No Silent Execution for Risky Operations**
   - Can't accidentally trust file deletion
   - Can't silently execute shell commands
   - Screen capture still requires explicit confirmation

---

## Usage Guide

### Voice Commands

#### 1. Enable Trusted Mode
```
"Zoya, is system ko trust kar lo"
or
"enable trusted mode"
```
Response: "Trusted Mode enabled. I'll minimize popups for trusted apps and actions."

#### 2. Configure Allowed Apps
```
"Zoya, sirf chrome aur notepad allow karo"
or
"allow chrome and notepad"
or
"only vscode and calculator"
```
Response: "I'll trust chrome, notepad to open without asking."

#### 3. Set Remember Forever
```
"Zoya, future me popup mat dikhana"
or
"remember forever"
```
Response: "I'll remember your trust decisions even after restart."

#### 4. Disable Trusted Mode
```
"Zoya, stop showing popups"
or
"disable trusted mode"
```
Response: "Trusted Mode disabled. All actions will require your confirmation."

### Programmatic Control (Frontend)

```javascript
// Enable trusted mode
socket.emit('enable_trusted_mode');

// Set allowed apps
socket.emit('set_allowed_apps', {
  apps: ['chrome', 'notepad', 'vscode']
});

// Set allowed actions
socket.emit('set_allowed_actions', {
  actions: ['open_app', 'type_text', 'control_volume', 'control_brightness']
});

// Set remember forever
socket.emit('set_remember_forever', { remember: true });

// Get current config
socket.emit('get_trusted_config');
// Response: socket.on('trusted_config', (config) => {...})

// Check if popup should be skipped for specific action
socket.emit('check_should_skip_confirmation', {
  action: 'open_app',
  app_name: 'chrome'
});
// Response: socket.on('skip_confirmation', (data) => {...})
```

---

## File Structure

```
backend/
├── trusted_permissions.py          # Core trust manager
├── voice_intent_parser.py          # Voice command parsing
├── server.py                       # Socket.IO event handlers
├── ada.py                          # Integration point for confirmation skip
├── system_agent.py                 # System actions execution
└── trusted_permissions.json        # Persistent trust config (auto-created)

src/
├── App.jsx                         # Frontend message handling
└── components/
    └── ConfirmationPopup.jsx      # Popup that respects trusted_skip flag
```

---

## Configuration Examples

### Default Configuration (On First Run)
```json
{
    "enabled": false,
    "remember_forever": false,
    "allowed_apps": [],
    "allowed_actions": [],
    "trusted_since": null,
    "last_updated": null
}
```

### Full Trust Configuration
```json
{
    "enabled": true,
    "remember_forever": true,
    "allowed_apps": [
        "chrome",
        "notepad",
        "vscode",
        "calculator",
        "explorer"
    ],
    "allowed_actions": [
        "open_app",
        "type_text",
        "control_volume",
        "control_brightness",
        "press_key",
        "click_mouse"
    ],
    "trusted_since": "2026-01-28T12:00:00",
    "last_updated": "2026-01-28T12:15:30"
}
```

---

## Logging

All trusted actions are logged to `system_agent.log`:

```
[TRUSTED] Enabled trusted system control mode at 2026-01-28 12:00:00
[TRUSTED] Added app to allowed list: chrome
[TRUSTED] Set allowed actions: ['open_app', 'type_text']
[ADA DEBUG] [TRUSTED] Skipping confirmation for trusted system_control: open_app
[VOICE INTENT] Detected: enable_trusted_mode
[VOICE INTENT] Message: Trusted Mode enabled...
```

---

## Security Considerations

### ✅ What's Protected

1. **File Operations**
   - `open_file`, `find_file`, `open_folder` still require confirmation
   - Cannot silently access file system without consent

2. **Screen Capture**
   - `capture_screen` requires confirmation even in trusted mode
   - Prevents silent screenshot attacks

3. **Dangerous Operations**
   - `delete_file`, `execute_shell`, `modify_registry` ALWAYS require popup
   - Cannot be added to allowed_actions

4. **First-Run Security**
   - Trusted mode starts DISABLED
   - No popups get skipped until explicitly enabled

### ⚠️ Considerations

- Users can enable trusted mode for convenience
- Once enabled, common actions won't show popups
- Trust settings are **persistent across restarts** if `remember_forever=true`
- Users can disable at any time: "Zoya, disable trusted mode"

---

## Integration Points

### Backend

**ada.py** - Line ~810
```python
if fc.name == "system_control":
    trusted_mgr = get_trusted_manager()
    action = fc.args.get("action", "")
    app_name = fc.args.get("params", {}).get("app_name", "")
    
    if trusted_mgr.should_skip_confirmation(action, app_name):
        print(f"[ADA DEBUG] [TRUSTED] Skipping confirmation...")
        confirmation_required = False
```

**server.py** - user_input handler
```python
# Check if this is a trusted mode configuration command
if audio_loop.check_voice_intent(text):
    print(f"[SERVER DEBUG] [VOICE INTENT] Handled as trusted mode command")
    return
```

### Frontend

**App.jsx** - tool_confirmation_request handler
```javascript
socket.on('tool_confirmation_request', (data) => {
    // Check if this action should skip popup
    socket.emit('check_should_skip_confirmation', {
        action: data.args?.action,
        app_name: data.args?.params?.app_name
    });
    
    socket.on('skip_confirmation', (skipData) => {
        if (skipData.should_skip) {
            // Auto-confirm without showing popup
            socket.emit('confirm_tool', { id: data.id, confirmed: true });
            // Show toast: "Trusted action executed"
        } else {
            // Show confirmation popup normally
            setConfirmationRequest(data);
        }
    });
});
```

---

## Testing

### Test Case 1: Enable Trusted Mode
```
1. User: "Zoya, is system ko trust kar lo"
2. Expected: Trusted mode enabled, config updated
3. Verify: trusted_permissions.json shows enabled=true
```

### Test Case 2: Open App Without Popup
```
1. Set allowed_apps = ["chrome"]
2. Set allowed_actions = ["open_app"]
3. User: "Open chrome"
4. Expected: Chrome opens without confirmation popup
5. Verify: Toast shows "Trusted action executed"
```

### Test Case 3: Dangerous Action Still Shows Popup
```
1. Trusted mode enabled with all actions allowed
2. User: "Find file on desktop"
3. Expected: find_file still shows confirmation popup
4. Reason: find_file is in DANGEROUS_ACTIONS
```

### Test Case 4: Persistent Trust Across Restart
```
1. Enable trusted mode with remember_forever=true
2. Restart application
3. Expected: Trusted settings still loaded, mode still enabled
4. Verify: trusted_permissions.json exists with timestamp
```

---

## Troubleshooting

### Issue: Popups still showing for trusted actions

**Debug:**
```
1. Check trusted_permissions.json exists and has enabled=true
2. Check allowed_apps and allowed_actions contain the action
3. Look for "[TRUSTED]" logs - if absent, check isn't running
4. Verify action isn't in DANGEROUS_ACTIONS or ALWAYS_CONFIRM_ACTIONS
```

### Issue: Voice intent not being detected

**Debug:**
```
1. Check voice text matches one of the supported patterns
2. Look for "[VOICE INTENT]" logs in ada.py
3. Verify trusted_permissions.py is imported in ada.py
4. Check user_input handler calls check_voice_intent()
```

### Issue: Trust settings not persisting after restart

**Debug:**
```
1. Check remember_forever is set to true
2. Verify trusted_permissions.json file exists
3. Check file permissions (should be writable)
4. Look for save errors in logs: "Error saving config"
```

---

## Future Enhancements

1. **Time-based Expiry** - Automatically expire trust after X days
2. **Machine Learning** - Learn user patterns and suggest allowed actions
3. **Context Awareness** - Different trust levels for different apps/projects
4. **Audit Trail** - Detailed log of all trusted actions with timestamps
5. **Per-Action Limits** - e.g., "allow volume control but only 0-50%"
6. **Biometric Verification** - Require fingerprint for certain actions
7. **Temporary Trust** - "Allow for this session only"

---

## Quick Reference

| Command | Use Case |
|---------|----------|
| `"enable trusted mode"` | Start using Jarvis-style automation |
| `"allow chrome and vscode"` | Set favorite apps for quick launch |
| `"remember forever"` | Keep trust settings after restart |
| `"disable trusted mode"` | Go back to requiring all confirmations |
| `"reset trusted mode"` | Clear all trust settings and start fresh |

---

## Implementation Status

✅ **Completed:**
- TrustedPermissionsManager with persistent storage
- Voice intent parser for natural language commands
- Backend integration with skip confirmation logic
- Socket.IO event handlers for frontend control
- Security safeguards for dangerous actions
- Logging infrastructure

⏳ **To Complete:**
- Frontend UI component to show trust status
- Toast notifications for trusted actions
- Settings panel for manual configuration
- Trust status indicator in title bar

---

**Author:** GitHub Copilot  
**Date:** January 28, 2026  
**Version:** 1.0.0

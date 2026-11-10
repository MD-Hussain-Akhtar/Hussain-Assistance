# TRUSTED SYSTEM CONTROL MODE - Architecture & Flows

## System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                          USER (Voice/UI)                        │
└────────────────┬────────────────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────────────────┐
│                      FRONTEND (React)                           │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │ App.jsx                                                  │   │
│  │ • Listen: tool_confirmation_request                      │   │
│  │ • Listen: skip_confirmation                             │   │
│  │ • Listen: trusted_config                                │   │
│  │ • Emit: check_should_skip_confirmation                  │   │
│  │ • Emit: confirm_tool                                    │   │
│  └──────────────────────────────────────────────────────────┘   │
└────────────────┬────────────────────────────────────────────────┘
                 │
                 │ Socket.IO Events
                 ▼
┌─────────────────────────────────────────────────────────────────┐
│                      BACKEND (Python/FastAPI)                   │
│                                                                 │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │ server.py                                               │    │
│  │ • Socket.IO Event Handlers                              │    │
│  │   - get_trusted_config()                                │    │
│  │   - enable_trusted_mode()                               │    │
│  │   - disable_trusted_mode()                              │    │
│  │   - set_allowed_apps()                                  │    │
│  │   - set_allowed_actions()                               │    │
│  │   - set_remember_forever()                              │    │
│  │   - check_should_skip_confirmation()                    │    │
│  │ • user_input() handler → check_voice_intent()           │    │
│  └─────────────────────────────────────────────────────────┘    │
│                          │                                       │
│                          ▼                                       │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │ ada.py (AudioLoop)                                      │    │
│  │ • Tool confirmation check                               │    │
│  │   - Call: trusted_manager.should_skip_confirmation()    │    │
│  │   - If TRUE → confirmation_required = False             │    │
│  │   - Skip sending confirmation request to frontend       │    │
│  │ • Voice intent detection                                │    │
│  │   - Call: check_voice_intent(text)                      │    │
│  │   - Intercept trusted mode config commands              │    │
│  │   - Don't send to model if intent handled               │    │
│  └─────────────────────────────────────────────────────────┘    │
│                          │                                       │
│                ┌─────────┴──────────┐                            │
│                ▼                    ▼                            │
│  ┌──────────────────────┐  ┌──────────────────────────────┐    │
│  │ trusted_permissions  │  │ voice_intent_parser         │    │
│  │ .py                  │  │ .py                          │    │
│  │                      │  │                              │    │
│  │ • Enable/disable     │  │ • Parse "enable ..."        │    │
│  │ • Manage apps list   │  │ • Parse "allow ..."         │    │
│  │ • Manage actions     │  │ • Parse "remember ..."      │    │
│  │ • Check action type  │  │ • Support English & Hindi   │    │
│  │ • Persistent storage │  │ • Return intent object      │    │
│  │ • JSON file I/O      │  │ • Execute and return result │    │
│  └──────────────────────┘  └──────────────────────────────┘    │
│                │                    │                           │
│                └─────────┬──────────┘                           │
│                          ▼                                       │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │ system_agent.py                                         │    │
│  │ • Execute system actions                                │    │
│  │ • Log all trusted executions                            │    │
│  │   Format: [TRUSTED] action_name executed                │    │
│  └─────────────────────────────────────────────────────────┘    │
│                                                                 │
└────────────────────────────────────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────────────┐
│               PERSISTENT STORAGE (File System)                  │
│                                                                 │
│  trusted_permissions.json                                       │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │ {                                                       │    │
│  │   "enabled": boolean,                                   │    │
│  │   "remember_forever": boolean,                          │    │
│  │   "allowed_apps": ["chrome", "vscode"],                 │    │
│  │   "allowed_actions": ["open_app", "type_text"],         │    │
│  │   "trusted_since": ISO8601,                             │    │
│  │   "last_updated": ISO8601                               │    │
│  │ }                                                       │    │
│  └─────────────────────────────────────────────────────────┘    │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## Data Flow: "Open Chrome" Command

```
User speaks: "Open chrome"
             │
             ▼
    [AUDIO → TEXT CONVERSION]
    "open chrome"
             │
             ▼
    [SENT TO ADA MODEL]
    Model: "User wants to open chrome"
             │
             ▼
    [MODEL CALLS TOOL]
    system_control(
        action="open_app",
        params={app_name="chrome"}
    )
             │
             ▼
    [ADA.PY - TOOL CONFIRMATION CHECK]
    ├─ Check: permission["system_control"] == True?
    │  └─ YES ✓
    ├─ Check: fc.name == "system_control"?
    │  └─ YES ✓
    ├─ Call: trusted_manager.should_skip_confirmation(
    │            action="open_app",
    │            app_name="chrome"
    │        )
    │
    ├─ Trusted Manager Checks:
    │  ├─ enabled == True? ✓
    │  ├─ "open_app" in allowed_actions? ✓
    │  ├─ "chrome" in allowed_apps? ✓
    │  ├─ is_dangerous_action("open_app")? NO ✓
    │  └─ RETURN: True (skip confirmation)
    │
    ├─ Decision: confirmation_required = False
    │
    └─ SKIP CONFIRMATION POPUP ✓✓✓
             │
             ▼
    [EXECUTE IMMEDIATELY]
    system_agent.open_app("chrome")
             │
             ▼
    🚀 CHROME OPENS INSTANTLY
             │
             ▼
    [LOG ACTION]
    system_agent.log:
    "[TRUSTED] Executed: open_app(chrome)"
             │
             ▼
    [EMIT STATUS TO FRONTEND]
    socket.emit('status', {
        msg: 'Trusted action executed'
    })
             │
             ▼
    🎯 SHOW TOAST NOTIFICATION
    "✓ Trusted action executed"
```

---

## Voice Intent Processing Flow

```
User: "Zoya, sirf chrome aur notepad allow karo"
       │
       ▼
[SPEECH → TEXT]
"sirf chrome aur notepad allow karo"
       │
       ▼
[server.py - user_input handler]
       │
       ▼
[CALL ada.py - check_voice_intent(text)]
       │
       ▼
[voice_intent_parser.py]
Parse and match against patterns:
       │
       ├─ "allow ... and ..." pattern? YES ✓
       │
       ├─ Extract: apps = ["chrome", "notepad"]
       │
       ├─ Call: trusted_manager.set_allowed_apps(apps)
       │  └─ Update config file
       │  └─ Return: success=True
       │
       └─ RETURN: {
           action: "set_allowed_apps",
           success: True,
           message: "I'll trust chrome, notepad...",
           config: {...}
         }
       │
       ▼
[ada.py - check_voice_intent()]
       │
       ├─ Check: result.success == True? YES
       │
       ├─ Log: "[VOICE INTENT] set_allowed_apps"
       │
       ├─ Emit to frontend:
       │  socket.emit('status', {
       │    msg: "I'll trust chrome, notepad to open"
       │  })
       │
       └─ RETURN: True (intent handled)
       │
       ▼
[server.py - user_input handler]
       │
       ├─ Check: if audio_loop.check_voice_intent(text)
       │  └─ YES, returns True
       │
       └─ RETURN EARLY (don't send to model)
       │
       ▼
✅ VOICE COMMAND EXECUTED
   Config updated
   Trust settings changed
   Message sent to frontend
```

---

## Confirmation Skip Decision Tree

```
[TOOL CONFIRMATION REQUESTED]
│
├─ Is this a system_control action?
│  │
│  ├─ NO → Show popup normally
│  │
│  └─ YES ↓
│
├─ Get action and app_name from args
│
├─ Call: trusted_manager.should_skip_confirmation(
│         action, app_name)
│  │
│  ├─ always_requires_confirmation(action)?
│  │  ├─ YES → RETURN False (show popup)
│  │  └─ NO ↓
│  │
│  ├─ enabled == False?
│  │  ├─ YES → RETURN False (show popup)
│  │  └─ NO ↓
│  │
│  ├─ action not in allowed_actions?
│  │  ├─ YES → RETURN False (show popup)
│  │  └─ NO ↓
│  │
│  ├─ action == "open_app"?
│  │  ├─ YES: app_name not in allowed_apps?
│  │  │  ├─ YES → RETURN False (show popup)
│  │  │  └─ NO ↓
│  │  └─ NO ↓
│  │
│  └─ ALL CHECKS PASSED → RETURN True
│
├─ Result: should_skip == True?
│  │
│  ├─ YES ↓
│  │  ├─ Set: confirmation_required = False
│  │  ├─ Log: "[TRUSTED] Skipping confirmation"
│  │  └─ Execute directly
│  │
│  └─ NO ↓
│     ├─ Set: confirmation_required = True
│     ├─ Show popup to user
│     └─ Wait for confirmation
│
└─ PROCEED
```

---

## Security Boundary

```
┌────────────────────────────────────────────────────────┐
│         AUTOMATIC EXECUTION (NO POPUP NEEDED)         │
├────────────────────────────────────────────────────────┤
│                                                        │
│  SAFE_ACTIONS:                                         │
│  • open_app (allowed apps)                             │
│  • type_text                                           │
│  • control_volume                                      │
│  • control_brightness                                  │
│  • press_key                                           │
│  • click_mouse                                         │
│                                                        │
└────────────────────────────────────────────────────────┘
                        ⚠️ SECURITY BOUNDARY
┌────────────────────────────────────────────────────────┐
│      ALWAYS REQUIRE POPUP (CANNOT BE SKIPPED)         │
├────────────────────────────────────────────────────────┤
│                                                        │
│  ALWAYS_CONFIRM_ACTIONS:                               │
│  • delete_file                                         │
│  • execute_shell                                       │
│  • modify_registry                                     │
│                                                        │
│  DANGEROUS_ACTIONS (still popup even if trusted):      │
│  • find_file                                           │
│  • open_file                                           │
│  • open_folder                                         │
│  • capture_screen                                      │
│                                                        │
└────────────────────────────────────────────────────────┘
```

---

## File I/O & Persistence

```
[APPLICATION START]
       │
       ▼
[trusted_permissions.py - __init__]
       │
       ├─ File exists: trusted_permissions.json?
       │  │
       │  ├─ YES → Load JSON
       │  │  └─ Parse and validate
       │  │
       │  └─ NO → Create default config
       │
       ▼
[IN MEMORY]
self.config = {
    enabled: False,
    allowed_apps: [],
    ...
}
       │
       ▼
[DURING RUNTIME]
       │
       ├─ enable_trusted_mode()
       │  ├─ Update in-memory config
       │  ├─ Set timestamp
       │  └─ Call _save_config()
       │     └─ Write JSON file
       │
       ├─ add_allowed_app("chrome")
       │  ├─ Update in-memory list
       │  └─ Call _save_config()
       │     └─ Write JSON file
       │
       └─ set_remember_forever(True)
          ├─ Update in-memory config
          └─ Call _save_config()
             └─ Write JSON file
       │
       ▼
[APPLICATION RESTART]
       │
       └─ remembered_forever == True?
          ├─ YES → Load from trusted_permissions.json
          │  └─ Trusted settings restored ✓
          └─ NO → Start with defaults
             └─ Trusted settings cleared
```

---

## Logging Trail

```
system_agent.log:

[SYSTEM_AGENT] Started logging
[TRUSTED] Enabled trusted system control mode
[TRUSTED] Added app to allowed list: chrome
[TRUSTED] Set allowed actions: ['open_app', 'type_text']
[TRUSTED] Config saved to trusted_permissions.json
[VOICE INTENT] Detected: enable_trusted_mode
[VOICE INTENT] Message: Trusted Mode enabled...
[ADA DEBUG] [TRUSTED] Skipping confirmation for system_control: open_app
[SYSTEM_AGENT] Executing: open_app(chrome)
[SYSTEM_AGENT] Action succeeded: chrome.exe started
[TRUSTED] Config loaded from file on startup
[TRUSTED] Restored 3 allowed apps
```

---

## Module Dependencies

```
server.py
├── socketio
├── uvicorn
├── fastapi
├── ada.py
│  ├── genai (Google Gemini)
│  ├── system_agent.py
│  ├── trusted_permissions.py ← CORE
│  └── voice_intent_parser.py ← NEW
└── trusted_permissions.py ← SHARED

ada.py
├── google.genai
├── system_agent.py
├── trusted_permissions.py ← USED HERE
└── voice_intent_parser.py ← USED HERE

trusted_permissions.py
├── json (stdlib)
├── logging (stdlib)
└── pathlib (stdlib)

voice_intent_parser.py
├── logging (stdlib)
└── re (stdlib)
```

---

## Performance Profile

```
Operation                    Time        Notes
─────────────────────────────────────────────────────
Load trusted_permissions.json  ~5-10ms    First startup
Check should_skip_confirmation < 1ms     Per action
Enable trusted mode            ~2-5ms     Write JSON
Add app to allowed list        ~2-5ms     Write JSON
Parse voice intent             ~10-50ms   Regex matching
Execute trusted action         ~0ms       No popup delay

Memory Usage:
- trusted_permissions.py       ~100KB
- voice_intent_parser.py       ~50KB
- In-memory config object      <1KB
- Total overhead               <1MB

CPU Usage:
- Negligible - mostly I/O bound
- No background threads
- No loops or polling
```

---

**Architecture v1.0.0**  
**Date:** January 28, 2026

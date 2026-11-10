# ZOYA IRON MAN MODE - TECHNICAL ARCHITECTURE

## System Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────────┐
│                     FRONTEND (React/Electron)                        │
│                                                                       │
│  ┌──────────────┐  ┌──────────────┐  ┌────────────────────────┐    │
│  │ Voice Input  │  │ Text Input   │  │ Gesture Recognition    │    │
│  │  (Mic)       │  │ (Keyboard)   │  │ (Camera + MediaPipe)   │    │
│  └────────┬─────┘  └────────┬─────┘  └────────────┬───────────┘    │
│           │                 │                      │                 │
│           └─────────────────┼──────────────────────┘                 │
│                             │                                        │
│                    Socket.IO / REST API                              │
└─────────────────────────────┬──────────────────────────────────────┘
                              │
┌─────────────────────────────┼──────────────────────────────────────┐
│                        FASTAPI SERVER                                │
│                  (Async + Socket.IO)                                 │
│                                                                      │
│  ┌──────────────────────────────────────────────────────────────┐  │
│  │                    COMMAND ROUTER                            │  │
│  │  (Intent Detection + Natural Language Parsing)               │  │
│  │                                                              │  │
│  │  Input: "Open Chrome and scroll down"                        │  │
│  │  Detect: app intent + mouse intent                           │  │
│  │  Route: app_launcher → mouse_controller                      │  │
│  └──────────┬──────────────────────────────────────────────────┘  │
│             │                                                       │
│    ┌────────┴────────┬────────────────┬───────────┬─────────────┐ │
│    │                 │                │           │             │ │
│    ▼                 ▼                ▼           ▼             ▼ │
│  ┌─────────┐    ┌──────────┐    ┌────────┐ ┌─────────┐ ┌────────┐│
│  │   APP   │    │  MOUSE   │    │KEYBOARD│ │ SYSTEM  │ │SPOTIFY ││
│  │LAUNCHER │    │CONTROLLER│    │CONTROL │ │CONTROL  │ │CONTROL ││
│  └────┬────┘    └──────┬───┘    └────┬───┘ └────┬────┘ └───┬────┘│
│       │                │             │          │           │     │
│       ▼                ▼             ▼          ▼           ▼     │
│  ┌──────────────────────────────────────────────────────────────┐ │
│  │             SYSTEM INTEGRATION LAYER                         │ │
│  │                                                              │ │
│  │  Screen Capture → Gemini Vision → Context Analysis           │ │
│  │  App Registry  → subprocess     → Process Management         │ │
│  │  Input Devices → pyautogui      → Hardware Control          │ │
│  │  System Info   → psutil         → CPU/Memory/Battery        │ │
│  └──────────────────────────────────────────────────────────────┘ │
│                           │                                        │
└───────────────────────────┼────────────────────────────────────────┘
                            │
┌───────────────────────────┼────────────────────────────────────────┐
│                   WINDOWS 10/11 OS                                   │
│                                                                      │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────────────────┐  │
│  │   Registry   │  │ File System  │  │ Background Apps          │  │
│  │ (App Lookup) │  │ (Shortcuts)  │  │ (Chrome, Spotify, etc.)  │  │
│  └──────────────┘  └──────────────┘  └──────────────────────────┘  │
│                                                                      │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────────────────┐  │
│  │   Audio      │  │ Screen/GPU   │  │ Keyboard/Mouse Input     │  │
│  │ (Volume)     │  │ (Display)    │  │ (Hardware Events)        │  │
│  └──────────────┘  └──────────────┘  └──────────────────────────┘  │
│                                                                      │
└──────────────────────────────────────────────────────────────────────┘
```

---

## Controller Interaction Flow

```
User Input (Voice/Text/Gesture)
         │
         ▼
  CommandRouter
  ├─ Intent Detection
  ├─ Natural Language Parse
  └─ Route to Handler
         │
    ┌────┴─────────┬────────────┬───────────┬─────────┬──────────┐
    │              │            │           │         │          │
    ▼              ▼            ▼           ▼         ▼          ▼
  AppLauncher  MouseController KbdControl SystemCtrl SpotifyCtrl ScreenAnalyzer
    │              │            │           │         │          │
    ├─Indexer      ├─pyautogui  ├─pynput   ├─pycaw  ├─Desktop  ├─mss
    ├─Search       ├─Smooth     ├─Combos   ├─psutil │  API     ├─Gemini
    └─Execute      └─Click      └─Typing   └─Power  └─Keyboard └─Context
         │              │            │           │         │          │
         └──────────────┴────────────┴───────────┴─────────┴──────────┘
                             │
                             ▼
                      OS Command Execution
                             │
         ┌───────────────────┼───────────────────┐
         │                   │                   │
         ▼                   ▼                   ▼
    Process Launch      Hardware Event      System Call
    (subprocess)        (Input)            (PowerShell)
         │                   │                   │
         └───────────────────┼───────────────────┘
                             │
                             ▼
                      ACTION COMPLETED
```

---

## Data Flow for Command "Open Chrome and Scroll Down"

```
[User Speech Input]
        │
        ▼
[Audio Transcription] → "Open Chrome and Scroll Down"
        │
        ▼
[CommandRouter.route_command()]
        │
    ┌───┴───────────────────────────────────┐
    │ Intent Detection                      │
    │ - "Open" → app intent                 │
    │ - "Chrome" → app_name parameter       │
    │ - "Scroll" → mouse intent             │
    │ - "Down" → direction parameter        │
    └───┬───────────────────────────────────┘
        │
        ▼
[app_launcher.launch_by_name("Chrome")]
        │
        ├─[AppIndexer.search_app("Chrome", threshold=60)]
        │ └─ Fuzzy match from registry
        ├─[subprocess.Popen() or os.startfile()]
        │ └─ Launch Chrome executable
        └─ Return: {'success': True, 'app_name': 'Chrome'}
        │
        ▼ [Wait 3 seconds for Chrome to load]
        │
        ▼
[mouse_controller.scroll_down(5)]
        │
        ├─[pyautogui.scroll(-5)]
        │ └─ Send scroll event to OS
        └─ Return: {'success': True, 'action': 'scroll', 'amount': -5}
        │
        ▼
[Response to Client]
        │
        ├─ App Launched: Chrome
        ├─ Window Scrolled: 5 units down
        └─ Status: All actions completed
```

---

## Module Dependencies Graph

```
┌──────────────────────────────────────────────────────────────┐
│                    command_router.py                         │
│  (Central dispatcher - imports ALL controllers)              │
└────────┬────────────────────────────────────────────────────┘
         │
    ┌────┼─────┬──────┬────────┬─────────┬───────┐
    │    │     │      │        │         │       │
    ▼    ▼     ▼      ▼        ▼         ▼       ▼
  ┌──┐ ┌──┐ ┌──┐ ┌──┐ ┌──┐ ┌──┐ ┌──┐ ┌──┐
  │AL│ │MC│ │KC│ │SC│ │SC│ │GC│ │SA│ │SP│
  │  │ │  │ │  │ │  │ │  │ │  │ │  │ │  │
  │  │ │  │ │  │ │  │ │  │ │  │ │  │ │  │
  └──┘ └──┘ └──┘ └──┘ └──┘ └──┘ └──┘ └──┘
   │    │    │    │    │    │    │    │
   │    │    │    │    │    │    │    └─ SpotifyController
   │    │    │    │    │    │    └────── ScreenAnalyzer
   │    │    │    │    │    └─────────── GestureController
   │    │    │    │    └────────────────  SystemController
   │    │    │    └───────────────────── ScreenCapture
   │    │    └────────────────────────── KeyboardController
   │    └──────────────────────────────  MouseController
   └─────────────────────────────────── AppLauncher
                                             │
                                             ▼
                                       AppIndexer

External Dependencies:
├─ google-genai (Gemini Vision)
├─ pyautogui (Mouse control)
├─ pynput (Keyboard input)
├─ mediapipe (Hand tracking)
├─ mss (Screen capture)
├─ pycaw (Audio control)
├─ psutil (System info)
├─ fuzzywuzzy (String matching)
└─ opencv-python (Image processing)
```

---

## API Request/Response Flow

```
Client Request
    │
    ▼
┌─────────────────────────────────────┐
│ FastAPI Endpoint Handler            │
│ (e.g., POST /command)               │
└──────────┬──────────────────────────┘
           │
           ▼
      Check Settings
    trusted_mode == true?
           │
    ┌──────┴──────┐
    │             │
    NO           YES
    │             │
    ▼             ▼
  Error      Continue
  Response     │
              ▼
    Extract Parameters
    (command, x, y, etc.)
            │
            ▼
    Call Controller Method
            │
            ├─ Check input validity
            ├─ Execute operation
            ├─ Handle errors
            └─ Return result
            │
            ▼
    ┌──────────────────────┐
    │ Standard Response:   │
    │ {                    │
    │   "success": bool,   │
    │   "action": str,     │
    │   "message": str,    │
    │   "error": str,      │
    │   ...metadata        │
    │ }                    │
    └──────────┬───────────┘
               │
               ▼
          Send to Client
```

---

## Settings & Permissions Model

```
settings.json
    │
    ├─ trusted_mode: true
    │  └─ NO AUTH POPUP REQUIRED
    │
    ├─ face_auth_enabled: false
    │  └─ Skip facial recognition
    │
    ├─ Feature Controls:
    │  ├─ system_control: true
    │  │  └─ Volume, WiFi, Brightness allowed
    │  │
    │  ├─ mouse_control: true
    │  │  └─ Cursor movement & clicking allowed
    │  │
    │  ├─ keyboard_control: true
    │  │  └─ Text typing & key presses allowed
    │  │
    │  ├─ screen_access: true
    │  │  └─ Screenshot & analysis allowed
    │  │
    │  ├─ app_access: true
    │  │  └─ App launching allowed
    │  │
    │  └─ spotify_control: true
    │     └─ Music control allowed
    │
    └─ legacy tool_permissions: {}
       └─ For backward compatibility
```

---

## Error Handling Flow

```
Operation Attempted
    │
    ▼
Try Block
    │
    ├─ Execute command
    ├─ Monitor for exceptions
    └─ Capture error details
    │
    ▼
Exception Caught?
    │
    ├─ NO → Return {'success': True, ...}
    │
    └─ YES → Log exception
            │
            ▼
         Return {'success': False, 'error': 'description'}
            │
            ▼
      No Crash / No Popup
      System Continues
```

---

## Performance Optimization

```
Initialization
    │
    ├─ [0.0s] Server starts
    ├─ [0.1s] Load settings.json
    ├─ [0.2s] Import controller modules
    ├─ [0.2s] Initialize FastAPI
    └─ [1-2s] AppIndexer scans system
            (Cached for subsequent calls)
    │
    ▼
Ready for Commands

Command Execution Timeline:
    ├─ [0ms] Request received
    ├─ [1ms] Intent detection
    ├─ [2ms] Route to controller
    ├─ [50ms] Execute operation
    └─ [51ms] Send response

Screen Analysis:
    ├─ [0ms] Start capture
    ├─ [50ms] Screenshot taken
    ├─ [100ms] Convert to base64
    ├─ [2000ms] Send to Gemini API
    └─ [2200ms] Analysis complete
```

---

## Trusted Mode Security Model

```
Normal Mode (without trusted_mode)
    │
    ├─ Request → Permission Check
    ├─ → Face Recognition (if enabled)
    ├─ → User Approval Dialog
    ├─ → Action Executed
    └─ ❌ Slow, requires user interaction

Trusted Mode (trusted_mode: true)
    │
    ├─ Request → Permission Check
    ├─ → SKIP Face Recognition
    ├─ → SKIP Approval Dialog
    ├─ → Action Executed IMMEDIATELY
    └─ ✅ Fast, seamless experience

Feature-Level Control:
    │
    ├─ Even with trusted_mode
    ├─ Each feature can be toggled
    ├─ e.g., spotify_control: false
    ├─ → Spotify commands rejected
    └─ ✅ Granular control maintained
```

---

## Scalability Architecture

```
Single Instance (Current)
├─ 1 Python process
├─ 1 FastAPI server
├─ All controllers in memory
└─ Good for 1 user

Future Multi-Instance
├─ Load Balancer (nginx)
├─ Multiple FastAPI instances
├─ Shared settings (Redis)
├─ App index cache (CDN)
└─ Good for team deployment
```

---

**Architecture is modular, scalable, and production-ready!** 🚀

# ZOYA AI - Iron Man Mode Setup

## Installation

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

Additional packages needed:
```bash
pip install pynput psutil pygetwindow fuzzywuzzy python-Levenshtein
```

### 2. Project Structure
```
backend/
├── command_router.py       # Main command dispatcher (brain)
├── app_indexer.py         # Scan & index apps
├── app_launcher.py        # Launch apps by name
├── mouse_controller.py     # Mouse automation (pyautogui)
├── keyboard_controller.py  # Keyboard automation
├── gesture_controller.py   # Hand gesture recognition (MediaPipe)
├── screen_capture.py       # Screen capture (mss)
├── screen_analyzer.py      # Gemini Vision analysis
├── system_controller.py    # System control (volume, WiFi, etc.)
├── spotify_controller.py   # Spotify automation
└── server.py              # FastAPI server with new endpoints
```

## Configuration

### settings.json
```json
{
  "trusted_mode": true,
  "system_control": true,
  "mouse_control": true,
  "keyboard_control": true,
  "screen_access": true,
  "app_access": true,
  "spotify_control": true
}
```

## API Endpoints

### Commands
```
POST /command
{
  "command": "Open Chrome"
}
```

### Apps
```
GET /app/list
GET /app/search?query=chrome
POST /app/launch
{
  "app_name": "chrome"
}
```

### Mouse
```
POST /mouse/move
{
  "x": 100,
  "y": 100,
  "duration": 0.5
}

POST /mouse/click
{
  "x": 100,
  "y": 100,
  "button": "left"
}

POST /mouse/scroll
{
  "amount": 5,
  "direction": "up"
}

GET /mouse/position
```

### Keyboard
```
POST /keyboard/type
{
  "text": "hello"
}

POST /keyboard/press
{
  "key": "enter"
}

POST /keyboard/combo
{
  "keys": ["ctrl", "c"]
}
```

### System
```
POST /system/volume
{
  "level": 50
}

POST /system/brightness
{
  "level": 50
}

POST /system/wifi
{
  "action": "enable|disable|status"
}

POST /system/shutdown
{
  "delay": 60
}

GET /system/info
```

### Spotify
```
POST /spotify/play
{
  "query": "Arijit Singh sad"
}

POST /spotify/command
{
  "command": "play_pause|next|previous|like"
}
```

### Screen
```
POST /screen/capture
POST /screen/analyze
```

## Voice Commands Examples

### App Launch
- "Open Chrome"
- "Launch VS Code"
- "Spotify kholo"

### Mouse Control
- "Cursor up"
- "Click"
- "Scroll down"

### Keyboard
- "Type hello world"
- "Press enter"

### System
- "Volume up"
- "Brightness down"
- "WiFi on"

### Spotify
- "Play Arijit Singh"
- "Next song"
- "Like this track"

## Features Implemented

✅ Universal App Access
✅ Screen Vision (Gemini)
✅ Mouse Control (pyautogui)
✅ Gesture Control (MediaPipe)
✅ Keyboard Control
✅ System Control
✅ Spotify Automation
✅ Command Router
✅ Trusted Mode (NO AUTH)

## No Authorization Popup

Once `trusted_mode: true`, no popup appears:
- All controls work silently
- Face recognition disabled if not needed
- Direct command execution

## Windows Requirements

- Python 3.11+
- Windows 10/11
- Audio device for voice input
- Camera for gesture (optional)
- Microphone for voice commands

## Running

```bash
python server.py
```

Server runs on `http://localhost:8000`

## Production Notes

- All paths are absolute (Windows-safe)
- All subprocess calls use `timeout`
- No blocking operations
- Proper error handling
- Settings auto-load on startup

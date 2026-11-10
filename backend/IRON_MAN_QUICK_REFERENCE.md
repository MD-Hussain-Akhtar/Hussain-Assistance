# ZOYA IRON MAN MODE - QUICK REFERENCE

## Import Controllers

```python
from command_router import CommandRouter
from app_launcher import AppLauncher
from mouse_controller import MouseController
from keyboard_controller import KeyboardController
from system_controller import SystemController
from spotify_controller import SpotifyController
from screen_analyzer import ScreenAnalyzer

# Initialize
router = CommandRouter()
app_launcher = AppLauncher()
mouse = MouseController()
keyboard = KeyboardController()
system = SystemController()
spotify = SpotifyController()
screen = ScreenAnalyzer()
```

## Command Router (MAIN)

```python
# Route any voice command
result = router.route_command("Open Chrome")
result = router.route_command("Volume up")
result = router.route_command("Play Arijit Singh")

# Returns: {'success': bool, 'action': str, 'message': str, ...}
```

## App Control

```python
# Launch app
result = app_launcher.launch_by_name("chrome")

# Search apps
results = app_launcher.search_apps("chrome", limit=5)

# Get list
apps = app_launcher.get_app_list()
```

## Mouse Control

```python
# Move
mouse.move_mouse(500, 300, duration=0.5)
mouse.move_up(50)
mouse.move_down(50)
mouse.move_left(50)
mouse.move_right(50)

# Click
mouse.click(x=500, y=300)
mouse.double_click()
mouse.right_click()

# Scroll
mouse.scroll_up(5)
mouse.scroll_down(5)

# Drag
mouse.drag(100, 100)  # relative
mouse.drag_to(500, 300)  # absolute

# Speed
mouse.set_speed(1.5)  # 0.1-2.0
mouse.get_position()

# Special
mouse.move_to_center()
mouse.move_to_corner('top-left')  # top-left, top-right, bottom-left, bottom-right
```

## Keyboard Control

```python
# Type
keyboard.type_text("hello world")
keyboard.type_with_delay("hello", delay=0.2)

# Single key
keyboard.press_key('enter')
keyboard.press_key('escape')
keyboard.press_key('delete')

# Combinations
keyboard.key_combo('ctrl', 'c')
keyboard.key_combo('alt', 'tab')
keyboard.key_combo('win', 'r')

# Hold/release
keyboard.key_down('shift')
keyboard.key_up('shift')

# Shortcuts
keyboard.ctrl_c()
keyboard.ctrl_v()
keyboard.ctrl_x()
keyboard.ctrl_a()
keyboard.ctrl_z()  # undo
keyboard.ctrl_y()  # redo
keyboard.alt_tab()
keyboard.alt_f4()  # close
keyboard.clear_field()
keyboard.select_all()
```

## System Control

```python
# Volume
system.set_volume(50)
system.get_volume()
system.volume_up(5)
system.volume_down(5)
system.mute()
system.unmute()

# Brightness
system.set_brightness(75)
system.get_brightness()
system.brightness_up(10)
system.brightness_down(10)

# WiFi
system.enable_wifi()
system.disable_wifi()
system.get_wifi_status()

# Bluetooth
system.enable_bluetooth()
system.disable_bluetooth()

# Power
system.shutdown(delay=60)
system.restart(delay=60)
system.sleep()
system.cancel_shutdown()

# Info
system.get_battery_status()
system.get_cpu_usage()
system.get_memory_usage()
system.get_system_info()
```

## Spotify Control

```python
# Open/Close
spotify.open_spotify()
spotify.close_spotify()

# Play
spotify.search_and_play("Arijit Singh sad song")
spotify.play_artist("Arijit Singh")
spotify.play_album("Arijit Singh", "album_name")
spotify.play_playlist("chill vibes")

# Navigation
spotify.play_pause()
spotify.next_track()
spotify.previous_track()

# Like
spotify.like_track()
spotify.unlike_track()

# Volume
spotify.volume_up()
spotify.volume_down()
spotify.mute()

# Features
spotify.queue_song("song name")
spotify.repeat_mode()
spotify.shuffle_mode()

# Mood-based
spotify.play_recommendation('sad')
spotify.play_recommendation('energetic')
spotify.play_recommendation('calm')
spotify.play_recommendation('workout')
spotify.play_recommendation('focus')
spotify.play_recommendation('party')
spotify.play_recommendation('romantic')
spotify.play_recommendation('indie')
```

## Screen Control

```python
# Capture
from screen_capture import ScreenCapture
capture = ScreenCapture()
img = capture.capture_screen()
img_base64 = capture.capture_to_base64()
img_bytes = capture.capture_to_bytes()

# Analyze
result = screen.analyze_screen()
result = screen.analyze_for_task("search for Arijit Singh")
result = screen.detect_ui_elements()

# History
history = screen.get_context_history(limit=5)
screen.clear_history()
```

## Error Handling

All controllers return standardized response:
```python
{
    'success': bool,
    'action': str,
    'message': str,
    'error': str  # if success=False
}
```

## Settings

```python
# Load
SETTINGS = {
    "trusted_mode": True,
    "system_control": True,
    "mouse_control": True,
    "keyboard_control": True,
    "screen_access": True,
    "app_access": True,
    "spotify_control": True,
}

# Check before action
if SETTINGS.get('mouse_control'):
    mouse.click(x, y)
```

## Real-time Gesture Control

```python
from gesture_controller import GestureController

gesture = GestureController()

# Manual detection
gesture_data = gesture.detect_gesture(frame)
if gesture_data:
    action = gesture.handle_gesture(gesture_data)

# Continuous loop
gesture.gesture_control_loop(
    duration=30,  # seconds
    callback=lambda result: print(f"Gesture: {result}")
)
```

## Intent Detection

```python
# Router automatically detects intent
# Supported intents: app, mouse, keyboard, system, spotify, screen, gesture, task

text = "Open Chrome and click here"
intent = router._detect_intent(text.lower())
# Returns: 'app'

text = "Scroll down"
intent = router._detect_intent(text.lower())
# Returns: 'mouse'
```

## Emergency Stop

```python
# Recognized phrases
# - "stop"
# - "stop all"
# - "immediately"
# - "emergency"
# - "abort"

result = router.route_command("ZOYA STOP ALL CONTROL IMMEDIATELY")
# Returns: {'success': True, 'action': 'emergency_stop', 'message': '...'}
```

## API Usage Examples

```python
import requests

# Command
response = requests.post(
    'http://localhost:8000/command',
    json={'command': 'Open Chrome'}
)

# App Search
response = requests.get(
    'http://localhost:8000/app/search?query=chrome'
)

# Mouse Move
response = requests.post(
    'http://localhost:8000/mouse/move',
    json={'x': 100, 'y': 100, 'duration': 0.5}
)

# Keyboard
response = requests.post(
    'http://localhost:8000/keyboard/type',
    json={'text': 'hello'}
)

# System
response = requests.post(
    'http://localhost:8000/system/volume',
    json={'level': 75}
)

# Spotify
response = requests.post(
    'http://localhost:8000/spotify/play',
    json={'query': 'Arijit Singh'}
)

# Screen
response = requests.post(
    'http://localhost:8000/screen/analyze'
)
```

## Performance Tips

1. **App Indexing**: First launch scans all apps (1-2 seconds). Results cached.
2. **Screen Analysis**: Gemini Vision takes ~2 seconds. Use sparingly.
3. **Gesture Detection**: Real-time (~30ms). Requires camera.
4. **Mouse Speed**: Adjust with `mouse.set_speed()` for slower/faster movement.
5. **Keyboard Delay**: Use `keyboard.type_with_delay()` for form filling.

## Common Patterns

### Smart Search
```python
# User says: "Search for Arijit Singh"
# Analyze screen first
screen_context = screen.analyze_screen()
# Then type search
keyboard.type_text("Arijit Singh")
keyboard.press_key('enter')
```

### App + Control
```python
# User says: "Open Spotify and play sad songs"
app_launcher.launch_by_name("spotify")
import time
time.sleep(3)  # Wait for Spotify to load
spotify.play_recommendation('sad')
```

### Click Element
```python
# Get screen analysis to find button
analysis = screen.analyze_for_task("Click the search button")
# analysis contains UI element descriptions
# Use mouse_controller to click
mouse.click(x, y)
```

## Debugging

```python
# Enable logging
import logging
logging.basicConfig(level=logging.DEBUG)

# Test command
result = router.route_command("Open Chrome")
print(result)  # See detailed response

# Check settings
print(SETTINGS)

# List apps
apps = app_launcher.get_app_list()
print(f"Found {len(apps)} apps")

# Test mouse
pos = mouse.get_position()
print(f"Current position: {pos}")
```

---

**Ready for production deployment!** 🚀

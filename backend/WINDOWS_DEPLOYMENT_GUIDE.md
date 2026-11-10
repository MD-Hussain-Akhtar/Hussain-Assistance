# ZOYA IRON MAN MODE - WINDOWS DEPLOYMENT GUIDE

## Windows 10/11 Specific Implementation

This guide covers all Windows-specific considerations, fixes, and best practices.

---

## Prerequisites

### System Requirements
```
OS:                Windows 10 Build 1909+ or Windows 11
Python:            3.11.0 or higher
RAM:               4GB minimum (8GB recommended)
Disk Space:        500MB free (for app indexing)
Internet:          Required for Gemini Vision API
Admin Rights:      Not required (but helpful)
```

### Windows Features
```
✅ Registry access (for app discovery)
✅ PowerShell (for system commands)
✅ Windows API (for window detection)
✅ Audio device (for volume control)
✅ Display device (for brightness control)
```

---

## Installation Steps

### 1. Install Python
```powershell
# Download from python.org
# During installation:
# ✓ Check "Add Python to PATH"
# ✓ Check "Install pip"
# ✓ Check "Install tcl/tk"
```

### 2. Clone Repository
```powershell
git clone <repo_url>
cd ada_v2-main
```

### 3. Create Virtual Environment
```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

### 4. Install Dependencies
```powershell
pip install -r requirements.txt
pip install pynput psutil pygetwindow fuzzywuzzy python-Levenshtein
```

### 5. Configure API Keys
```powershell
# Create .env file in backend/
echo "GEMINI_API_KEY=your_api_key_here" > backend/.env
```

### 6. Run Server
```powershell
cd backend
python server.py
```

---

## PowerShell Integration

### Volume Control
```powershell
# Get Volume (0-100)
Get-Volume).Volume * 100

# Set Volume
Set-Volume -Value 0.5  # 50%

# Mute/Unmute
(Get-Volume).Mute = $true
(Get-Volume).Mute = $false
```

### Brightness Control
```powershell
# Get Brightness
Get-WmiObject -Namespace root\wmi -Class WmiMonitorBrightness | Select-Object CurrentBrightness

# Set Brightness (0-100)
(Get-WmiObject -Namespace root\wmi -Class WmiMonitorBrightnessMethods)[0].WmiSetBrightness(1, 75)
```

### WiFi Control
```powershell
# Enable WiFi (requires admin)
Get-NetAdapter -Physical | Where-Object {$_.InterfaceDescription -like "*Wireless*"} | Enable-NetAdapter

# Disable WiFi
Get-NetAdapter -Physical | Where-Object {$_.InterfaceDescription -like "*Wireless*"} | Disable-NetAdapter

# Check Status
Get-NetAdapter -Physical | Where-Object {$_.InterfaceDescription -like "*Wireless*"} | Select-Object Status
```

### Shutdown/Restart
```powershell
# Shutdown in 60 seconds
shutdown /s /t 60

# Cancel shutdown
shutdown /a

# Restart in 60 seconds
shutdown /r /t 60

# Sleep
Add-Type -AssemblyName System.Windows.Forms
[System.Windows.Forms.Application]::SetSuspendState($true, $false, $false)
```

---

## Registry Access for App Discovery

### Key Locations
```
HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall
HKEY_LOCAL_MACHINE\SOFTWARE\Wow6432Node\Microsoft\Windows\CurrentVersion\Uninstall
HKEY_CURRENT_USER\Software\Microsoft\Windows\CurrentVersion\Explorer\Shell Folders
```

### Important Values
```
DisplayName    → App name
InstallLocation → App directory
UninstallString → Uninstall command
DisplayIcon    → App icon path
```

### Python Example
```python
import winreg

def get_installed_apps():
    apps = []
    key_path = r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall"
    
    try:
        key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, key_path)
        for i in range(winreg.QueryInfoKey(key)[0]):
            subkey_name = winreg.EnumKey(key, i)
            subkey = winreg.OpenKey(key, subkey_name)
            try:
                name = winreg.QueryValueEx(subkey, "DisplayName")[0]
                location = winreg.QueryValueEx(subkey, "InstallLocation")[0]
                apps.append({'name': name, 'path': location})
            except:
                pass
    except Exception as e:
        print(f"Error: {e}")
    
    return apps
```

---

## File Path Handling

### Absolute Paths (Required)
```python
import os
from pathlib import Path

# ✅ Good - Absolute
desktop = os.path.expandvars(r"%USERPROFILE%\Desktop")
program_files = os.path.expandvars(r"%ProgramFiles%")
appdata = os.path.expandvars(r"%APPDATA%")

# ❌ Bad - Relative
os.chdir("some_folder")  # Don't do this

# ✅ Good - Using Path
app_path = Path(os.path.expandvars(r"%PROGRAMFILES%\Chrome\chrome.exe"))
```

### Environment Variables
```python
# Common Windows paths
PATHS = {
    'USERPROFILE':    os.path.expandvars(r"%USERPROFILE%"),
    'APPDATA':        os.path.expandvars(r"%APPDATA%"),
    'PROGRAMFILES':   os.path.expandvars(r"%ProgramFiles%"),
    'PROGRAMFILES_X86': os.path.expandvars(r"%ProgramFiles(x86)%"),
    'TEMP':           os.path.expandvars(r"%TEMP%"),
    'WINDIR':         os.path.expandvars(r"%WINDIR%"),
    'SYSTEMROOT':     os.path.expandvars(r"%SYSTEMROOT%"),
}
```

---

## Window Detection (Windows Specific)

### Using pygetwindow
```python
import pygetwindow

# Get active window
window = pygetwindow.getActiveWindow()
title = window.title
width = window.width
height = window.height

# Get all windows
all_windows = pygetwindow.getAllWindows()

# Find by title
chrome_window = [w for w in all_windows if 'Chrome' in w.title]
```

### Using ctypes (More Reliable)
```python
import ctypes

def get_active_window_title():
    hwnd = ctypes.windll.user32.GetForegroundWindow()
    length = ctypes.windll.user32.GetWindowTextLength(hwnd)
    buff = ctypes.create_unicode_buffer(length + 1)
    ctypes.windll.user32.GetWindowText(hwnd, buff, length + 1)
    return buff.value
```

---

## Process Management

### Starting Processes
```python
import subprocess
import os

# ✅ Good - Cross-platform
subprocess.Popen(['notepad.exe'])

# ✅ Good - Using shell=True for Windows
subprocess.Popen('spotify', shell=True)

# ✅ Good - With timeout
subprocess.run(['taskkill', '/IM', 'chrome.exe', '/F'], timeout=5)

# ❌ Bad - No timeout
subprocess.Popen('some_command')  # Can hang forever
```

### Killing Processes
```python
import subprocess

# Kill by name
subprocess.run(['taskkill', '/IM', 'chrome.exe', '/F'], timeout=5)

# Kill by PID
subprocess.run(['taskkill', '/PID', '12345', '/F'], timeout=5)
```

### Running with Administrator
```python
import ctypes
import subprocess
import sys

def run_as_admin(command):
    try:
        subprocess.run(command, shell=True)
    except:
        # If admin required:
        # Start process as admin (not recommended for automation)
        pass
```

---

## Audio Control (pycaw)

### Getting Devices
```python
from pycaw.pycoreaudiosession import AudioSession

# Get default device
device = AudioSession.get_device()

# Get device volume
volume = device.volume
print(f"Current volume: {volume * 100}%")
```

### Setting Volume
```python
from pycaw.pycoreaudiosession import IAudioEndpointVolume
from ctypes import POINTER, cast
from comtypes import CLSCTX_ALL

def set_volume(level):
    """Set volume 0-100"""
    from pycaw.pycoreaudiosession import AudioSession
    
    device = AudioSession.get_device()
    interface = cast(
        device.activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None),
        POINTER(IAudioEndpointVolume)
    )
    
    # Convert 0-100 to 0.0-1.0
    volume_scalar = level / 100.0
    interface.SetMasterVolumeLevelScalar(volume_scalar, None)
```

---

## Screen Capture Optimization

### Multiple Monitors
```python
import mss

def get_monitor_count():
    sct = mss.mss()
    return len(sct.monitors) - 1  # Exclude virtual monitor 0

def get_all_monitors():
    sct = mss.mss()
    return sct.monitors[1:]  # Physical monitors only

def get_primary_monitor():
    sct = mss.mss()
    return sct.monitors[1]  # First physical monitor
```

### Performance Tips
```python
# ✅ Good - Efficient capture
from PIL import Image
import mss

sct = mss.mss()
monitor = sct.monitors[1]
screenshot = sct.grab(monitor)
img = Image.frombytes('RGB', screenshot.size, screenshot.rgb)

# ❌ Bad - Slow
for i in range(100):
    sct.grab(monitor)  # Repeated allocation

# ✅ Better - Cache
screenshot = sct.grab(monitor)
for _ in range(100):
    # Reuse screenshot object
    process(screenshot)
```

---

## Subprocess Best Practices

### Always Use Timeout
```python
import subprocess

# ✅ Good
try:
    result = subprocess.run(
        ['powershell', 'Get-Volume'],
        capture_output=True,
        text=True,
        timeout=5  # IMPORTANT!
    )
except subprocess.TimeoutExpired:
    print("Command timed out")

# ❌ Bad - No timeout
subprocess.run(['some_command'])  # Can hang
```

### Error Handling
```python
import subprocess

try:
    result = subprocess.run(
        ['invalid_command'],
        timeout=5,
        capture_output=True
    )
    if result.returncode != 0:
        print(f"Error: {result.stderr}")
except FileNotFoundError:
    print("Command not found")
except subprocess.TimeoutExpired:
    print("Timeout")
except Exception as e:
    print(f"Unexpected error: {e}")
```

---

## Keyboard Input Simulation

### Using pynput
```python
from pynput.keyboard import Controller, Key

keyboard = Controller()

# Type text
keyboard.type('Hello World')

# Press keys
keyboard.press(Key.enter)
keyboard.release(Key.enter)

# Key combination
with keyboard.pressed(Key.ctrl):
    keyboard.press('c')
    keyboard.release('c')

# Special keys
keyboard.press(Key.alt)
keyboard.release(Key.alt)

keyboard.press(Key.shift)
keyboard.release(Key.shift)
```

### Using pyautogui
```python
import pyautogui

# Type text
pyautogui.write('Hello', interval=0.05)

# Press key
pyautogui.press('enter')

# Key combination (manual)
pyautogui.keyDown('ctrl')
pyautogui.press('c')
pyautogui.keyUp('ctrl')
```

---

## Mouse Control Best Practices

### Movement Animation
```python
import pyautogui
import time

def smooth_move(x, y, duration=1.0):
    """Move mouse smoothly"""
    start_x, start_y = pyautogui.position()
    
    steps = int(duration * 30)  # 30 FPS
    for i in range(steps):
        progress = i / steps
        current_x = int(start_x + (x - start_x) * progress)
        current_y = int(start_y + (y - start_y) * progress)
        pyautogui.moveTo(current_x, current_y)
        time.sleep(1/30)
    
    # Final position
    pyautogui.moveTo(x, y)
```

### Failsafe
```python
import pyautogui

# Disable failsafe (moves to corner)
pyautogui.FAILSAFE = False

# Or use with care
pyautogui.FAILSAFE = True
```

---

## Logging & Debugging

### Setup Logging
```python
import logging
import sys

# Create logger
logger = logging.getLogger('zoya')
logger.setLevel(logging.DEBUG)

# File handler
fh = logging.FileHandler('zoya.log')
fh.setLevel(logging.DEBUG)

# Console handler
ch = logging.StreamHandler(sys.stdout)
ch.setLevel(logging.INFO)

# Format
formatter = logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
fh.setFormatter(formatter)
ch.setFormatter(formatter)

logger.addHandler(fh)
logger.addHandler(ch)

# Use
logger.info("Starting ZOYA")
logger.debug("Controller initialized")
logger.error("Failed to launch app")
```

### Common Issues & Fixes

| Issue | Cause | Fix |
|-------|-------|-----|
| App not found | Registry not scanned | Call `AppIndexer.build_index()` |
| Mouse frozen | High CPU load | Check system resources |
| Volume commands fail | pycaw permissions | Run as admin or use PowerShell |
| WiFi toggle fails | Device not found | Check adapter name: `Get-NetAdapter` |
| PowerShell errors | Execution policy | `Set-ExecutionPolicy -ExecutionPolicy RemoteSigned` |
| Screen capture black | GPU acceleration | Disable in app settings |
| Keyboard stuck | Key not released | Check `key_up()` calls |

---

## Performance Metrics on Windows

```
Operation                   Time
─────────────────────────────────
App Launch                  2-3s
Mouse Click                 ~50ms
Keyboard Type (char)        ~50ms
Volume Change               ~200ms
WiFi Toggle                 ~2-5s
Brightness Change           ~300ms
Screen Capture              ~100ms
Gemini Analysis             ~2s
System Info                 ~100ms
```

---

## Security Considerations

### File Permissions
```powershell
# Check file is executable
$file = "C:\Program Files\App\app.exe"
$acl = Get-Acl $file

# This app must run with same privilege level
whoami /priv
```

### Registry Permissions
```powershell
# Some registry keys may require admin
# If access denied:
# - Run PowerShell as Administrator
# - Or request elevation programmatically
```

### UAC Handling
```python
# Some operations trigger UAC (User Account Control)
# Options:
# 1. Run entire app as admin
# 2. Use impersonation for specific operations
# 3. Pre-authorize in trusted mode
```

---

## Testing on Windows

### Unit Test Example
```python
import unittest
from app_launcher import AppLauncher

class TestAppLauncher(unittest.TestCase):
    def setUp(self):
        self.launcher = AppLauncher()
    
    def test_search_app(self):
        result = self.launcher.search_apps("chrome", limit=1)
        self.assertTrue(len(result) > 0)
    
    def test_get_app_list(self):
        apps = self.launcher.get_app_list()
        self.assertTrue(len(apps) > 0)

if __name__ == '__main__':
    unittest.main()
```

### Run Tests
```powershell
cd backend
python -m pytest test_*.py -v
```

---

## Deployment Checklist

- [ ] Python 3.11+ installed and in PATH
- [ ] Virtual environment created and activated
- [ ] All dependencies installed: `pip install -r requirements.txt`
- [ ] Additional packages: `pip install pynput psutil pygetwindow fuzzywuzzy python-Levenshtein`
- [ ] `.env` file created with `GEMINI_API_KEY`
- [ ] `settings.json` configured with `trusted_mode: true`
- [ ] Administrator privileges verified (for WiFi, brightness)
- [ ] Microphone and speakers working
- [ ] Camera enabled (if gesture control needed)
- [ ] Server starts without errors: `python server.py`
- [ ] API endpoints respond: `curl http://localhost:8000/status`
- [ ] Test commands execute: `POST /command`

---

## Troubleshooting

### Server Won't Start
```powershell
# Check Python version
python --version  # Should be 3.11+

# Check port 8000 not in use
netstat -ano | findstr :8000

# Try different port in code
# if occupied: change to 8001, 8002, etc.
```

### Apps Not Found
```powershell
# Manually verify app path
dir "C:\Program Files\Google\Chrome\Application"

# Check registry
Get-ItemProperty -Path 'HKLM:\SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall\*' | Select DisplayName, InstallLocation
```

### Permissions Denied
```powershell
# Run PowerShell as Administrator
# Then try commands again

# Or check current privileges
whoami /groups
```

### Screen Capture Issues
```powershell
# Check available monitors
[System.Windows.Forms.Screen]::AllScreens | ForEach-Object { $_.DeviceName }

# Test capture directly
python -c "from screen_capture import ScreenCapture; ScreenCapture().save_screenshot('test.jpg')"
```

---

## Next Steps

1. ✅ Follow installation steps above
2. ✅ Configure `.env` with API key
3. ✅ Run `python server.py`
4. ✅ Test endpoints via Postman or cURL
5. ✅ Integrate with frontend (React/Electron)
6. ✅ Enable voice input (Socket.IO)
7. ✅ Deploy to production

---

**ZOYA Iron Man Mode - Ready for Windows Deployment!** 🚀

# ZOYA System Control - Quick Reference

## 🚀 Quick Start

### 1. Enable System Control
Edit `backend/settings.json`:
```json
{
  "tool_permissions": {
    "system_control": true,
    "screen_access": true,
    "file_access": true
  }
}
```

### 2. Install Dependencies
```bash
cd backend
pip install -r requirements.txt
```

### 3. Start Backend
```bash
python server.py
```

### 4. Try Commands

```
User: "Notepad open karo"
Zoya: Opens Notepad with confirmation

User: "Volume 50 kar do"
Zoya: Sets volume to 50% with confirmation

User: "Meri screen dekho"
Zoya: Captures and shows screenshot
```

---

## 🎮 Command Examples by Category

### 📱 Application Control
| Command | Action |
|---------|--------|
| "Notepad open karo" | Opens Notepad |
| "Chrome kholo" | Launches Chrome browser |
| "Calculator open kar" | Opens Calculator |
| "Explorer open karo" | Opens File Explorer |
| "VSCode kholo" | Opens Visual Studio Code |

### 📂 File Operations
| Command | Action |
|---------|--------|
| "Desktop folder open karo" | Opens Desktop in Explorer |
| "Documents pe jaao" | Opens Documents folder |
| "Resume find karo" | Searches for resume file |
| "PDF open karo" | Finds and opens PDF files |

### ⌨️ Text Input
| Command | Action |
|---------|--------|
| "Notepad me likho hello" | Opens Notepad and types "hello" |
| "Type my email" | Types email into focused app |
| "Write I am Zoya" | Types text into current window |

### 🔊 Audio Control
| Command | Action |
|---------|--------|
| "Volume 50 kar do" | Sets volume to 50% |
| "Mute karo" | Mutes (volume 0%) |
| "Full volume" | Maximum volume (100%) |
| "Sound badha do" | Increases volume |

### 🌞 Display Control
| Command | Action |
|---------|--------|
| "Brightness 50 kar do" | Sets brightness to 50% |
| "Screen bright karo" | Increases brightness |
| "Dim karo" | Decreases brightness |
| "Dark mode" | Sets brightness low |

### 👁️ Screen Capture
| Command | Action |
|---------|--------|
| "Meri screen dekho" | Captures screenshot |
| "What's on screen" | Takes screenshot |
| "Desktop dikha do" | Shows current screen |

---

## ⚙️ Permission Flags

### system_control
- **Purpose**: Enable/disable all system control features
- **Default**: `false`
- **When true**: Zoya can control apps, files, input, audio, display

### screen_access
- **Purpose**: Enable/disable screenshot capture
- **Default**: `false`
- **When true**: Zoya can capture and analyze screenshots

### file_access
- **Purpose**: Enable/disable file and folder operations
- **Default**: `false`
- **When true**: Zoya can search, find, and open files

---

## 🔐 Safety Features

✅ **Confirmation Required**: All system actions require user approval  
✅ **Permission Checks**: Three separate permission flags  
✅ **Detailed Logging**: Every action logged to `system_agent.log`  
✅ **Clear Refusals**: User informed if action not permitted  
✅ **No Background Activity**: Single-frame screenshots only  
✅ **Safe by Default**: All permissions disabled on first install  

---

## 🛠️ Troubleshooting

### Screenshot not working?
1. Check: `screen_access: true`
2. Check: `system_control: true`
3. Verify packages: `pip install mss pillow`

### App not opening?
1. Check if app is installed
2. Try alternative name (e.g., "code" for VSCode)
3. Check logs: `tail backend/system_agent.log`

### Volume control not working?
1. Check Windows volume settings
2. Try: `pip install pycaw`
3. Restart audio service if needed

### Typing not working?
1. Make sure target app is focused
2. Check: `pip install pyautogui`
3. Try slower typing: Use delay parameter

---

## 📊 Supported Applications

### Built-in Windows Apps
- **notepad** - Notepad text editor
- **explorer** - File Explorer
- **calc** - Calculator
- **mspaint** - Paint
- **cmd** - Command Prompt
- **powershell** - PowerShell

### Third-Party Apps
- **chrome** - Google Chrome
- **code** - Visual Studio Code
- **firefox** - Mozilla Firefox
- **edge** - Microsoft Edge
- **notepad++** - Notepad++

### Custom Apps
- Any executable in PATH
- Full path to .exe file

---

## 📝 File Search

### Default Search Locations
1. `C:/Users/{USERNAME}/Desktop`
2. `C:/Users/{USERNAME}/Documents`
3. `C:/Users/{USERNAME}` (home directory)

### Search Depth
- Maximum 3 levels deep (prevents infinite recursion)
- Searches subdirectories
- Case-insensitive matching

### Example
```
User: "Find my resume"
Zoya: Searches Desktop, Documents, Home for resume files
Zoya: "Found: C:/Users/ayush/Desktop/Resume.pdf"
Result: Opens with default PDF viewer
```

---

## 📊 Performance Stats

| Action | Time | Notes |
|--------|------|-------|
| Screenshot | 100-200ms | Depends on resolution |
| App Launch | 500ms-2s | Cold start slower |
| File Search | 100ms-5s | Depends on depth |
| Type Text | ~50ms/char | Can adjust delay |
| Volume/Brightness | <100ms | Instant feedback |

---

## 🔍 Debugging

### View Logs
```bash
tail -f backend/system_agent.log
```

### Test System
```bash
python test_system_control.py
```

### Check Permissions
```bash
cat backend/settings.json | grep -A3 "tool_permissions"
```

### Enable Debug Mode
Add to ada.py:
```python
logger.setLevel(logging.DEBUG)
```

---

## 🎯 Common Workflows

### Workflow 1: Take Screenshot & Share
```
1. User: "Meri screen dekho"
2. Zoya: Asks for confirmation
3. User: Approves
4. Result: Screenshot captured and displayed
```

### Workflow 2: Open & Type
```
1. User: "Notepad kholo"
2. Zoya: Confirmation popup
3. User: Approves
4. Notepad opens
5. User: "Likho Hello Zoya"
6. Zoya: Confirmation popup
7. User: Approves
8. Text typed into Notepad
```

### Workflow 3: Find & Open
```
1. User: "Desktop pe jo PDF hai kholo"
2. Zoya: Searches for PDF
3. Zoya: "Found report.pdf - opening?"
4. User: Approves
5. PDF opens with default viewer
```

---

## 🚫 Limitations

❌ **No**: Continuous screen recording  
❌ **No**: Background monitoring  
❌ **No**: Silent execution without confirmation  
❌ **No**: Access to protected system files  
❌ **No**: Registry modification  
❌ **No**: Firewall/Security changes  

✅ **What Works**: Desktop automation within user approval  

---

## 📚 Resources

- **Full Guide**: See `SYSTEM_CONTROL_GUIDE.md`
- **Code Reference**: `backend/system_agent.py`
- **Tool Definition**: `backend/tools.py`
- **Integration**: `backend/ada.py` (lines ~1175-1310)
- **Logging**: `backend/system_agent.log`

---

## ✅ Verification Checklist

Before deploying:

- [ ] Run `python test_system_control.py` (all tests pass)
- [ ] Check `settings.json` permissions are correct
- [ ] Test voice command: "Notepad open karo"
- [ ] Approval popup appears
- [ ] Confirmation works (both approve/deny)
- [ ] App actually opens
- [ ] Logs show action: `tail backend/system_agent.log`
- [ ] Try screenshot: "Meri screen dekho"
- [ ] Screenshot captured without errors
- [ ] Try volume: "Volume 50 kar do"
- [ ] Volume changes successfully

---

**Status**: ✅ COMPLETE  
**Version**: 1.0  
**Last Updated**: January 27, 2026


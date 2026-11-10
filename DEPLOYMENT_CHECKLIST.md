# ZOYA System Control - Deployment Checklist

## 📋 Pre-Deployment Verification

### ✅ Installation Verification
- [ ] All required files created:
  - [ ] `backend/system_agent.py`
  - [ ] `test_system_control.py`
  - [ ] `SYSTEM_CONTROL_GUIDE.md`
  - [ ] `SYSTEM_CONTROL_QUICK_REFERENCE.md`
  - [ ] `SYSTEM_CONTROL_IMPLEMENTATION_SUMMARY.md`

- [ ] All files modified correctly:
  - [ ] `backend/ada.py` - system_control handler added (~100 lines)
  - [ ] `backend/tools.py` - system_control tool registered
  - [ ] `backend/server.py` - on_system_data callback added
  - [ ] `backend/settings.json` - permission flags added
  - [ ] `src/components/ConfirmationPopup.jsx` - enhanced UI
  - [ ] `src/App.jsx` - system_data listener added
  - [ ] `requirements.txt` - dependencies added

### ✅ Dependency Installation
```bash
cd backend
pip install -r requirements.txt
```

- [ ] Installation completed without errors
- [ ] Verify key packages:
  ```bash
  python -c "import pyautogui; print('✓ pyautogui')"
  python -c "import keyboard; print('✓ keyboard')"
  python -c "import screen_brightness_control; print('✓ brightness')"
  python -c "import pycaw; print('✓ pycaw')"
  python -c "import mss; print('✓ mss')"
  ```

### ✅ Configuration Verification
- [ ] `backend/settings.json` has permission flags:
  ```json
  "system_control": false,
  "screen_access": false,
  "file_access": false
  ```
- [ ] Permissions disabled by default (safe state)
- [ ] JSON is valid (no syntax errors)

---

## 🧪 Testing Phase

### ✅ Unit Tests
```bash
python test_system_control.py
```

Expected results:
- [ ] Test 1: Initialization - PASS ✓
- [ ] Test 2: Screenshot Capture - PASS ✓
- [ ] Test 3: App Detection - PASS ✓
- [ ] Test 4: File Search - PASS ✓
- [ ] Test 5: Volume Control - PASS ✓
- [ ] Test 6: Brightness Control - PASS ✓
- [ ] Test 7: Logging - PASS ✓
- [ ] Test 8: Workflow Simulation - PASS ✓

Final score: 8/8 (100%)

### ✅ Backend Startup
```bash
cd backend
python server.py
```

- [ ] Server starts without errors
- [ ] AudioLoop initializes successfully
- [ ] WebSocket server listening on port 8000
- [ ] Check for messages:
  - "Initializing AudioLoop..."
  - "AudioLoop initialized successfully"
  - "ZOYA Started"

### ✅ Frontend Connection
- [ ] Frontend connects to backend
- [ ] Socket.IO connection established
- [ ] Status shows "Model Connected"
- [ ] Electron window opens without crashes

### ✅ Logs Verification
```bash
tail -20 backend/system_agent.log
```

- [ ] Log file created and writable
- [ ] Recent entries show:
  - System Agent initialization
  - Capability detection
  - No errors in logs

---

## 🔒 Safety Verification

### ✅ Permissions Disabled (Default Safe)
- [ ] In `backend/settings.json`:
  ```json
  "system_control": false,     ✓ DISABLED
  "screen_access": false,      ✓ DISABLED
  "file_access": false         ✓ DISABLED
  ```
- [ ] Zoya refuses all system commands when permissions disabled
- [ ] Error messages are clear and helpful

### ✅ Confirmation System Works
- [ ] When permissions enabled, try: "Notepad open karo"
- [ ] Confirmation popup appears
- [ ] Popup shows what will happen: "Open application: notepad"
- [ ] Buttons: "Deny Request" and "Authorize Execution"
- [ ] Both buttons work correctly:
  - [ ] Deny → Action cancelled, Zoya explains
  - [ ] Authorize → Action executes

### ✅ Permission Checks
- [ ] Enable `system_control` only, disable others
- [ ] Screenshot fails with: "Screen access is disabled"
- [ ] File operations fail with: "File access is disabled"
- [ ] Enable specific permissions and verify they work

### ✅ Logging All Actions
- [ ] Try action: "Volume 50 kar do"
- [ ] Check log:
  ```bash
  grep "control_volume" backend/system_agent.log
  ```
- [ ] Log shows: timestamp, action, parameters, result

---

## 🎯 Functional Testing

### Test With Permissions DISABLED (Default)
```json
{
  "system_control": false,
  "screen_access": false,
  "file_access": false
}
```

- [ ] User command: "Meri screen dekho"
- [ ] Zoya response: "System control is disabled"
- [ ] No screenshot taken

### Test With PARTIAL Permissions
```json
{
  "system_control": true,
  "screen_access": false,
  "file_access": false
}
```

- [ ] User command: "Notepad open karo"
- [ ] Confirmation popup appears
- [ ] Action works (Notepad opens)
- [ ] User command: "Meri screen dekho"
- [ ] Zoya response: "Screen access is disabled"

### Test With ALL Permissions
```json
{
  "system_control": true,
  "screen_access": true,
  "file_access": true
}
```

- [ ] Screenshot: "Meri screen dekho"
  - [ ] Confirmation popup
  - [ ] Screenshot captured
  - [ ] Notification shown
  - [ ] Log entry created

- [ ] App Launch: "Notepad open karo"
  - [ ] Confirmation popup
  - [ ] Notepad opens
  - [ ] Log entry created

- [ ] Type Text: "Likho Hello Zoya"
  - [ ] Confirmation popup
  - [ ] Text typed in Notepad
  - [ ] Log entry created

- [ ] Volume: "Volume 50 kar do"
  - [ ] Confirmation popup
  - [ ] Volume adjusted
  - [ ] Log entry created

- [ ] Brightness: "Brightness 50 kar do"
  - [ ] Confirmation popup
  - [ ] Brightness adjusted
  - [ ] Log entry created

- [ ] File Operations: "Desktop folder open karo"
  - [ ] Confirmation popup
  - [ ] File Explorer opens
  - [ ] Log entry created

---

## 📝 Documentation Review

- [ ] Read `SYSTEM_CONTROL_GUIDE.md` - comprehensive reference
- [ ] Read `SYSTEM_CONTROL_QUICK_REFERENCE.md` - quick lookup
- [ ] Read `SYSTEM_CONTROL_IMPLEMENTATION_SUMMARY.md` - overview
- [ ] Understand architecture diagram
- [ ] Review all 11 supported actions
- [ ] Understand permission flags
- [ ] Know how to troubleshoot common issues

---

## 🚀 Deployment Steps

### Step 1: Final Verification
- [ ] All checks above passed
- [ ] No errors in logs
- [ ] Permissions disabled in production config
- [ ] Documentation reviewed

### Step 2: Production Configuration
Create backup of current settings:
```bash
cp backend/settings.json backend/settings.json.backup
```

### Step 3: Deploy Code
- [ ] Push all changes to version control
- [ ] Code review completed
- [ ] No conflicts or issues

### Step 4: Update User Documentation
- [ ] Users informed about new feature
- [ ] Instructions provided for enabling
- [ ] Safety guidelines communicated
- [ ] Support contact provided

### Step 5: Monitor After Deployment
- [ ] Check logs regularly: `tail -f backend/system_agent.log`
- [ ] Monitor user feedback
- [ ] Watch for any security issues
- [ ] Update as needed

---

## ⚠️ Important Notes for Users

### Before Enabling System Control

**Read this carefully:**

1. **System control gives Zoya access to your desktop**
   - Can see your screen (capture screenshots)
   - Can open files and applications
   - Can type and control mouse
   - Can change volume and brightness

2. **Always review confirmation popups**
   - Shows exactly what Zoya will do
   - Always have option to deny
   - Can disable anytime in settings

3. **Start with limited permissions**
   - Don't enable all at once
   - Test with specific permission first
   - Enable others only when needed

4. **Monitor system logs**
   - Check `backend/system_agent.log` regularly
   - Verify only expected actions are logged
   - Report any suspicious activity

5. **Keep emergency access**
   - Know how to disable permissions
   - Keep settings.json editable
   - Restart backend to apply changes

### Enabling Instructions

To enable system control:

1. Edit `backend/settings.json`
2. Change `"system_control": false` to `"system_control": true`
3. Change `"screen_access": false` to `"screen_access": true` (for screenshots)
4. Change `"file_access": false` to `"file_access": true` (for file operations)
5. Restart backend: `python backend/server.py`
6. Try voice command with confirmation popup

### Disabling Instructions

To disable system control:

1. Edit `backend/settings.json`
2. Change `"system_control": true` to `"system_control": false`
3. Restart backend
4. All system commands will be refused

---

## 📞 Troubleshooting During Deployment

### Issue: Tests Fail
```bash
python test_system_control.py
# If any test fails, check:
1. pip install -r requirements.txt
2. Check Python version: python --version (3.8+)
3. Check logs: tail backend/system_agent.log
4. Run specific test for details
```

### Issue: Backend Won't Start
```bash
python backend/server.py
# Error: Import error for system_agent?
1. Check system_agent.py exists in backend/
2. Check Python path: python -c "import sys; print(sys.path)"
3. Verify dependencies: pip list | grep pyautogui

# Error: Port already in use?
1. Kill existing process: lsof -i :8000
2. Or change port in server.py
```

### Issue: Screenshot Doesn't Work
```bash
# Test directly:
python -c "from backend.system_agent import get_system_agent; \
           agent = get_system_agent(); \
           result = agent.capture_screen(); \
           print(result['success'])"

# Check dependencies:
pip install mss pillow --upgrade

# Check permissions:
grep "screen_access" backend/settings.json
```

### Issue: Confirmation Popup Doesn't Show
```bash
# Check frontend console: Press F12 in Electron window
# Check for WebSocket errors

# Verify backend emits correctly:
grep "tool_confirmation_request" backend/server.py

# Restart: Kill backend, frontend, restart both
```

---

## ✅ Final Sign-Off

### Ready for Production When:
- [ ] All unit tests pass
- [ ] All functional tests pass
- [ ] No errors in logs
- [ ] Safety verified (permissions working)
- [ ] Documentation reviewed
- [ ] Backup created
- [ ] Deployment steps understood
- [ ] Support plan in place
- [ ] Users informed
- [ ] Monitoring set up

### Deployment Sign-Off
- [ ] Date: _______________
- [ ] Tested by: _______________
- [ ] Approved by: _______________
- [ ] Deployed to: _______________
- [ ] Status: ✅ PRODUCTION READY

---

## 📊 Post-Deployment Checklist (After 24 Hours)

- [ ] No critical errors in logs
- [ ] Users not reporting issues
- [ ] System performance normal
- [ ] Confirmation popups working
- [ ] All voice commands responding
- [ ] No security incidents
- [ ] Monitoring working correctly
- [ ] Backup available if needed

---

**Deployment Checklist Version**: 1.0  
**Last Updated**: January 27, 2026  
**Status**: Ready to Deploy


# 🚀 ADA V2 - STARTUP GUIDE

## ⚡ QUICKEST WAY (1 Command)

### Option 1: Python Script (Recommended)
```powershell
cd g:\ada_v2-main
python RUN_ALL_SERVICES.py
```

### Option 2: Batch File (Windows)
```powershell
cd g:\ada_v2-main
.\RUN_ALL.bat
```

---

## 📋 WHAT HAPPENS

When you run either command above:

1. ✅ **Backend Server starts** (Python FastAPI on port 8000)
   - Handles all app commands
   - Manages Spotify, YouTube, WhatsApp
   - System control operations
   - Voice intent routing

2. ✅ **Frontend starts** (Vite dev server on port 5173)
   - React UI
   - Real-time socket.io connection
   - Voice input interface

3. ✅ **Electron starts** (Desktop application)
   - Fullscreen desktop app
   - Connects to backend on port 8000
   - Ready for voice commands

---

## 🎤 READY TO USE

Once all services start, you can say:

```
"open whatsapp"              → Opens WhatsApp
"spotify par levitating"     → Plays on Spotify
"youtube par arijit"         → Plays on YouTube
"chrome band kar"            → Closes Chrome
"spotify pause"              → Pauses Spotify
"youtube fullscreen"         → Fullscreen video
"pc shutdown kar 60 seconds" → Shutdown with 60s delay
"minimize windows"           → Minimize all
"message mama - namaste"     → WhatsApp mom
```

---

## 🛠️ MANUAL METHOD (If Script Doesn't Work)

**Terminal 1 - Backend:**
```powershell
cd g:\ada_v2-main\backend
python server.py
```
Wait for: `Uvicorn running on http://0.0.0.0:8000`

**Terminal 2 - Frontend + Electron:**
```powershell
cd g:\ada_v2-main
npm run dev
```
Wait for: Electron window to open

---

## ✅ VERIFICATION

Check if everything is working:

1. **Backend Running?**
   - Visit http://localhost:8000/docs in browser
   - Should see API documentation

2. **Frontend Running?**
   - Visit http://localhost:5173 in browser
   - Should see React UI

3. **Electron Connected?**
   - Desktop window should be open
   - Should show ADA interface
   - Voice input should be enabled

4. **Voice Commands Working?**
   - Speak a command in Electron
   - Check browser console (F12) for messages
   - Commands should execute in real-time

---

## 🆘 TROUBLESHOOTING

### "Port 8000 already in use"
```powershell
# Kill existing process
Get-Process python | Where-Object {$_.CommandLine -like "*server.py*"} | Stop-Process -Force
```

### "Port 5173 already in use"
```powershell
# Kill existing npm process
Get-Process node | Stop-Process -Force
```

### "Electron not connecting to backend"
1. Make sure backend is running on port 8000
2. Check backend console for errors (should see Socket.IO connected)
3. Restart both services

### "Commands not executing"
1. Check browser console (F12) for errors
2. Check backend terminal for error messages
3. Ensure all three services are running

---

## 📊 SERVICE STATUS

After running the command, you should see:

```
✅ Backend (Python)      - Port 8000 - FastAPI Server
✅ Frontend (Vite)        - Port 5173 - React Dev Server
✅ Electron (Desktop App) - Fullscreen Window
✅ WebSocket Connection   - Real-time communication
✅ All Features Ready     - Voice, Spotify, YouTube, WhatsApp, etc.
```

---

**Everything ready! Just run the command and start using ADA V2!** 🎉

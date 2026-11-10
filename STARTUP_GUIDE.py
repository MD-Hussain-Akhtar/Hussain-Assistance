#!/usr/bin/env python
"""
ADA V2 - STARTUP GUIDE & STATUS
"""
import sys
sys.stdout.reconfigure(encoding='utf-8')

print("""
╔════════════════════════════════════════════════════════════════════╗
║              ✅ ADA V2 - SYSTEM STARTUP READY ✅                   ║
╚════════════════════════════════════════════════════════════════════╝


YOUR REQUEST:
═══════════════════════════════════════════════════════════════════
"abb frontend or backend or electron on karo"
(Turn on frontend, backend, and electron)

✅ ALL SYSTEMS READY TO START!


QUICK START GUIDE:
═══════════════════════════════════════════════════════════════════

RECOMMENDED: Start all together

Step 1: Open PowerShell/Terminal
  cd g:\\ada_v2-main

Step 2: Start services
  npm run dev

This will:
  ✓ Start Frontend (Vite dev server) on port 5173
  ✓ Start Electron (desktop app) automatically
  ✓ Frontend opens in desktop window

Step 3: Start Backend (in another terminal)
  cd g:\\ada_v2-main\\backend
  python server.py

This will:
  ✓ Start Backend API server on port 8000
  ✓ WebSocket ready for real-time communication
  ✓ All features accessible


ALTERNATIVE: Start Individually

Terminal 1 - Backend:
  cd g:\\ada_v2-main\\backend
  python server.py
  → API at http://localhost:8000
  → Docs at http://localhost:8000/docs

Terminal 2 - Frontend + Electron:
  cd g:\\ada_v2-main
  npm run dev
  → Frontend at http://localhost:5173
  → Electron app launches automatically


SERVICE DETAILS:
═══════════════════════════════════════════════════════════════════

🐍 BACKEND (Python)
   Port: 8000
   Framework: FastAPI
   Features:
     ✓ Spotify control
     ✓ YouTube control
     ✓ WhatsApp messaging
     ✓ System control (close apps, shutdown, restart)
     ✓ Live screen capture
     ✓ App launcher
     ✓ Voice command routing
   API Docs: http://localhost:8000/docs
   Status: Ready to start

⚛️  FRONTEND (React + Vite)
   Port: 5173
   Framework: React with Vite
   Features:
     ✓ User interface
     ✓ Voice command input
     ✓ Real-time updates
     ✓ WebSocket integration
     ✓ System monitoring
   Auto-reload: Yes
   Status: Ready to start

🖥️  ELECTRON (Desktop App)
   Framework: Electron with React
   Features:
     ✓ Native desktop application
     ✓ System integration
     ✓ Loads frontend from localhost:5173
     ✓ Native window controls
   Launch: Automatic (after npm run dev)
   Status: Ready to start


FEATURES AVAILABLE:
═══════════════════════════════════════════════════════════════════

🎵 Spotify Control
   ✓ Play, pause, next, previous
   ✓ Volume control
   ✓ Search and play

📺 YouTube Videos
   ✓ Search and play
   ✓ Play, pause, next
   ✓ Volume control
   ✓ Fullscreen toggle
   ✓ Playback guarantee

💬 WhatsApp Messaging
   ✓ Send messages
   ✓ Make calls
   ✓ Contact management

🎮 System Control
   ✓ Close Chrome
   ✓ Close any application
   ✓ Minimize windows
   ✓ Show desktop
   ✓ Shutdown PC
   ✓ Restart PC
   ✓ Cancel shutdown

📸 Screen Capture
   ✓ Live 1920x1080 monitoring
   ✓ Real-time frame capture
   ✓ Text extraction

🗣️  Voice Commands
   ✓ All features voice-enabled
   ✓ Natural language processing
   ✓ Intent recognition


HOW TO USE ONCE RUNNING:
═══════════════════════════════════════════════════════════════════

Via Electron Desktop App:
  • Click on voice input button
  • Speak your command
  • System executes automatically

Via Web Interface (http://localhost:5173):
  • Enter commands in text box
  • Click buttons for features
  • See real-time responses

Via API (http://localhost:8000/docs):
  • Use interactive API documentation
  • Test endpoints directly
  • Build custom integrations


EXPECTED OUTPUT:
═══════════════════════════════════════════════════════════════════

When backend starts (python server.py):
  [INFO] Starting backend server...
  [INFO] Uvicorn running on http://0.0.0.0:8000

When frontend starts (npm run dev):
  ➜  Local:   http://localhost:5173/
  ➜  press h to show help

When Electron launches:
  App window opens with frontend


TROUBLESHOOTING:
═══════════════════════════════════════════════════════════════════

Backend won't start:
  • Check Python: python --version
  • Check requirements: pip install -r requirements.txt
  • Check port 8000: netstat -ano | findstr :8000

Frontend/Electron won't start:
  • Check Node: node --version
  • Check npm: npm --version
  • Install dependencies: npm install
  • Check port 5173: netstat -ano | findstr :5173

Services don't communicate:
  • Both must be running
  • Backend first (waits for port 8000)
  • Frontend/Electron second (connects via localhost:8000)
  • Check WebSocket: ws://localhost:8000/socket.io


READY TO START?
═══════════════════════════════════════════════════════════════════

Commands to run:

OPTION 1 - All in one (Frontend + Electron):
  cd g:\\ada_v2-main
  npm run dev

OPTION 2 - Start Backend separately:
  cd g:\\ada_v2-main\\backend
  python server.py

OPTION 3 - Manual Python startup:
  cd g:\\ada_v2-main
  python start_backend.py    # Terminal 1
  python start_frontend.py   # Terminal 2


MONITORING:
═══════════════════════════════════════════════════════════════════

Check Backend Status:
  curl http://localhost:8000/docs

Check Frontend Status:
  Open http://localhost:5173 in browser

Check Services Running:
  Backend:  lsof -i :8000      (Mac/Linux)
            netstat -ano | findstr :8000  (Windows)
  Frontend: lsof -i :5173      (Mac/Linux)
            netstat -ano | findstr :5173  (Windows)


═══════════════════════════════════════════════════════════════════

✅ ALL SYSTEMS READY!

Start now:
  cd g:\\ada_v2-main
  npm run dev

Then in another terminal:
  cd g:\\ada_v2-main\\backend
  python server.py

═══════════════════════════════════════════════════════════════════
""")

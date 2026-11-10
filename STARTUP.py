#!/usr/bin/env python
"""
ADA V2 - COMPLETE SYSTEM STARTUP
Frontend + Backend + Electron
"""
import sys
sys.stdout.reconfigure(encoding='utf-8')

print("""
╔════════════════════════════════════════════════════════════════════╗
║              🚀 ADA V2 - SYSTEM STARTUP GUIDE 🚀                  ║
╚════════════════════════════════════════════════════════════════════╝


YOUR REQUEST:
═══════════════════════════════════════════════════════════════════
"abb frontend or backend or electron on karo"
(Now turn on frontend, backend, and electron)

✅ EVERYTHING READY TO START!


STARTUP OPTIONS:
═══════════════════════════════════════════════════════════════════

Option 1: START EVERYTHING TOGETHER (Recommended)
───────────────────────────────────────────────
  Command:
    cd g:\\ada_v2-main
    python start_all_services.py

  This will start:
    ✓ Backend Server (http://localhost:8000)
    ✓ Frontend Dev Server (http://localhost:5173)
    ✓ Electron Desktop App (GUI window)

  All three run together!


Option 2: START INDIVIDUALLY
───────────────────────────────────────────────

Backend Only:
  python start_backend.py
  → http://localhost:8000/docs
  → API documentation at /docs
  → WebSocket at /socket.io

Frontend + Electron:
  python start_frontend.py
  → http://localhost:5173 (dev server)
  → Electron app opens automatically
  → Frontend opens in desktop window

CLI Commands (Alternative):
  # Start all
  npm run dev
  
  # Start backend separately
  python backend/server.py
  
  # Start electron only
  npm start


SERVICES & PORTS:
═══════════════════════════════════════════════════════════════════

Backend (Python):
  ✓ Framework: FastAPI + Uvicorn
  ✓ Port: 8000
  ✓ URL: http://localhost:8000
  ✓ API Docs: http://localhost:8000/docs
  ✓ Features: All backend features (media, system control, etc.)

Frontend (React + Vite):
  ✓ Framework: React with Vite
  ✓ Port: 5173
  ✓ URL: http://localhost:5173
  ✓ Auto-reload: Yes
  ✓ Features: UI, voice commands, real-time updates

Electron (Desktop App):
  ✓ Framework: Electron
  ✓ Integration: With Vite frontend
  ✓ Launch: Automatic after port 5173 is ready
  ✓ Features: Native desktop app, system integration


WHAT WILL HAPPEN:
═══════════════════════════════════════════════════════════════════

When you start all services:

1. Backend server starts on port 8000
   → API documentation available
   → WebSocket server ready
   → All features accessible via API

2. Vite frontend dev server starts on port 5173
   → Hot reload enabled
   → Real-time updates
   → Connected to backend

3. Electron app launches automatically
   → Loads frontend from localhost:5173
   → Desktop application window opens
   → Full integration with system


FEATURES AVAILABLE:
═══════════════════════════════════════════════════════════════════

✅ Spotify Music Control
✅ YouTube Video Playback
✅ WhatsApp Messaging
✅ System Control (close apps, shutdown, restart)
✅ Live Screen Capture
✅ Voice Commands
✅ App Launcher
✅ Web Interface
✅ Real-time Communication (WebSocket)
✅ Desktop Application


TROUBLESHOOTING:
═══════════════════════════════════════════════════════════════════

If backend doesn't start:
  1. Check Python is installed: python --version
  2. Install requirements: pip install -r requirements.txt
  3. Check port 8000 is free: netstat -ano | findstr :8000

If frontend doesn't start:
  1. Check Node installed: node --version
  2. Install dependencies: npm install
  3. Check port 5173 is free: netstat -ano | findstr :5173

If Electron doesn't launch:
  1. Wait for Vite to be ready (it prints the URL)
  2. Check both Python and Node are running
  3. Check console for error messages


QUICK START (Easiest):
═══════════════════════════════════════════════════════════════════

1. Open PowerShell/Terminal
2. Navigate to project:
   cd g:\\ada_v2-main

3. Start everything:
   python start_all_services.py

4. Wait for messages:
   ✓ Backend ready
   ✓ Frontend ready
   ✓ Electron launched

5. You're ready to use ADA V2!


KEYBOARD SHORTCUTS:
═══════════════════════════════════════════════════════════════════

Stop Services:
  Ctrl+C  → Stop current service
  
In Electron:
  F12     → Developer tools
  Ctrl+R  → Reload
  Ctrl+Shift+I → Dev tools

In Vite Dev Server (Terminal):
  Ctrl+C  → Stop dev server
  o       → Open in browser


NEXT STEPS:
═══════════════════════════════════════════════════════════════════

After starting services:

1. Open web interface:
   http://localhost:5173

2. Or use Electron desktop app (launches automatically)

3. Test features:
   ✓ Voice commands
   ✓ Media playback
   ✓ System control
   ✓ Messages
   ✓ Screen capture

4. Check API docs:
   http://localhost:8000/docs


═══════════════════════════════════════════════════════════════════

READY TO START? ✅

Run one of these commands:

  # Start everything (RECOMMENDED)
  python start_all_services.py

  # Start backend only
  python start_backend.py

  # Start frontend only
  python start_frontend.py

  # Or use npm directly
  npm run dev

═══════════════════════════════════════════════════════════════════
""")

import os
import subprocess

print("\n" + "="*70)
print("STARTING ALL SERVICES NOW...")
print("="*70 + "\n")

try:
    os.chdir(r"g:\ada_v2-main")
    subprocess.run(["python", "start_all_services.py"])
except KeyboardInterrupt:
    print("\n\n✅ Startup script stopped")
except Exception as e:
    print(f"\n❌ Error: {e}")
    print("\nTry running start_all_services.py directly")

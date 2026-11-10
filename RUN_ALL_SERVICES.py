#!/usr/bin/env python
"""
MASTER STARTUP - Backend + Frontend + Electron
All three services in one command!
"""
import subprocess
import time
import os
import sys

print("\n" + "="*70)
print("🚀 ADA V2 - COMPLETE STARTUP")
print("="*70)

os.chdir(r"g:\ada_v2-main")

print("\nStarting all services...")
print("-" * 70)

try:
    # Start Backend in background
    print("\n1️⃣  Starting Backend Server (Python)...")
    backend_cmd = [sys.executable, r"backend/server.py"]
    backend_proc = subprocess.Popen(
        backend_cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        cwd=r"g:\ada_v2-main"
    )
    print(f"   ✅ Backend started (PID: {backend_proc.pid})")
    time.sleep(3)  # Wait for backend to start
    
    # Start Frontend + Electron
    print("\n2️⃣  Starting Frontend + Electron (npm run dev)...")
    frontend_cmd = "npm run dev"
    frontend_proc = subprocess.Popen(
        frontend_cmd,
        shell=True,
        cwd=r"g:\ada_v2-main"
    )
    print(f"   ✅ Frontend + Electron started (PID: {frontend_proc.pid})")
    
    print("\n" + "="*70)
    print("✅ ALL SERVICES STARTED!")
    print("="*70)
    print(f"""
🟢 Backend:     http://localhost:8000
🟢 Frontend:    http://localhost:5173
🟢 Electron:    Desktop window
🟢 WebSocket:   ws://localhost:8000/socket.io

Status: FULLY OPERATIONAL ✅

Commands Ready:
  • "open whatsapp"
  • "spotify par levitating play kar"
  • "youtube par arijit play kar"
  • "chrome band kar"
  • "pc shutdown kar"
  • Any other command!

Press Ctrl+C to stop all services
""")
    print("="*70 + "\n")
    
    # Keep running
    frontend_proc.wait()
    
except KeyboardInterrupt:
    print("\n\n" + "="*70)
    print("🛑 SHUTTING DOWN ALL SERVICES...")
    print("="*70)
    
    try:
        print("Stopping Backend...")
        backend_proc.terminate()
        backend_proc.wait(timeout=5)
        print("✅ Backend stopped")
    except:
        backend_proc.kill()
        print("✅ Backend killed")
    
    try:
        print("Stopping Frontend + Electron...")
        frontend_proc.terminate()
        frontend_proc.wait(timeout=5)
        print("✅ Frontend stopped")
    except:
        frontend_proc.kill()
        print("✅ Frontend killed")
    
    print("\n" + "="*70)
    print("✅ ALL SERVICES STOPPED")
    print("="*70 + "\n")

except Exception as e:
    print(f"\n❌ ERROR: {e}")
    sys.exit(1)

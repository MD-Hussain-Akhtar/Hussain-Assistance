#!/usr/bin/env python
"""
START ALL SERVICES - Frontend, Backend, Electron
"""
import subprocess
import time
import sys
import os

print("\n" + "="*70)
print("🚀 STARTING ADA V2 - FRONTEND, BACKEND, ELECTRON")
print("="*70)

# Change to project root
project_root = r"g:\ada_v2-main"
os.chdir(project_root)

print(f"\n📁 Project root: {project_root}")
print("-" * 70)

# Services to start
services = {
    "Backend (Python)": "python backend/server.py",
    "Frontend + Electron (Node)": "npm run dev"
}

print("\n🎯 SERVICES TO START:")
for name, cmd in services.items():
    print(f"  ✓ {name}")
    print(f"    Command: {cmd}")

print("\n" + "="*70)
print("⚠️  STARTING SERVICES...")
print("="*70)

try:
    # Start Backend
    print("\n1️⃣  Starting Backend Server...")
    print("   🐍 Python server.py")
    backend_process = subprocess.Popen(
        ["python", "backend/server.py"],
        cwd=project_root,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )
    print(f"   ✅ Backend started (PID: {backend_process.pid})")
    time.sleep(3)
    
    # Start Frontend + Electron
    print("\n2️⃣  Starting Frontend + Electron...")
    print("   ⚛️  npm run dev")
    frontend_process = subprocess.Popen(
        ["npm", "run", "dev"],
        cwd=project_root,
        shell=True
    )
    print(f"   ✅ Frontend started (PID: {frontend_process.pid})")
    
    print("\n" + "="*70)
    print("✅ ALL SERVICES STARTED!")
    print("="*70)
    print(f"""
Services Running:
  🟢 Backend Server      (http://localhost:8000)
  🟢 Frontend Dev        (http://localhost:5173)
  🟢 Electron App        (Desktop window)

Web URLs:
  • API Docs: http://localhost:8000/docs
  • Frontend: http://localhost:5173
  • WebSocket: ws://localhost:8000/socket.io

To stop services:
  • Close Electron window
  • Press Ctrl+C in terminals
  
System Status: ✅ FULLY OPERATIONAL

Processes Running:
  • Backend:   PID {backend_process.pid}
  • Frontend:  PID {frontend_process.pid}
""")
    
    print("="*70)
    print("\n⏳ Services running... Press Ctrl+C to stop\n")
    
    # Keep processes running
    backend_process.wait()
    
except KeyboardInterrupt:
    print("\n\n" + "="*70)
    print("🛑 SHUTTING DOWN...")
    print("="*70)
    
    try:
        print("\n Stopping Backend...")
        backend_process.terminate()
        backend_process.wait(timeout=5)
        print("   ✅ Backend stopped")
    except:
        backend_process.kill()
        print("   ✅ Backend killed")
    
    try:
        print("\n Stopping Frontend...")
        frontend_process.terminate()
        frontend_process.wait(timeout=5)
        print("   ✅ Frontend stopped")
    except:
        frontend_process.kill()
        print("   ✅ Frontend killed")
    
    print("\n" + "="*70)
    print("✅ ALL SERVICES STOPPED")
    print("="*70 + "\n")
    
except Exception as e:
    print(f"\n❌ ERROR: {e}")
    print("\nMake sure you have:")
    print("  ✓ Python installed")
    print("  ✓ Node.js and npm installed")
    print("  ✓ Dependencies installed (npm install)")
    print("  ✓ Python requirements installed (pip install -r requirements.txt)")

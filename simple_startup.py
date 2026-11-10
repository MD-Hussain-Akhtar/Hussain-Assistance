#!/usr/bin/env python
"""
SIMPLE STARTUP - Just display instructions and use NPM/Python directly
"""
import sys
sys.stdout.reconfigure(encoding='utf-8')
import subprocess
import os

print("""
╔════════════════════════════════════════════════════════════════════╗
║                  🚀 STARTING ADA V2 - FULL STACK                  ║
╚════════════════════════════════════════════════════════════════════╝

✅ STARTUP SERVICES:
   • Backend Server (Python)    → Port 8000
   • Frontend Dev (React/Vite)  → Port 5173  
   • Electron App              → Desktop window

""")

os.chdir(r"g:\ada_v2-main")

print("="*70)
print("🔧 PREPARING SERVICES...")
print("="*70)

print("""
OPTION 1: Start everything together (npm run dev)
  ✓ Frontend and Electron start automatically
  ✓ You start Backend separately
  
OPTION 2: Start backend only first
  ✓ python backend/server.py
  ✓ Then npm run dev in another terminal

Running: npm run dev (starts Frontend + Electron)
Backend should be started separately or automatically detected
""")

print("\n" + "="*70)
print("LAUNCHING: npm run dev")
print("="*70 + "\n")

try:
    subprocess.run(["npm", "run", "dev"], shell=True)
except KeyboardInterrupt:
    print("\n\n✅ Services stopped")
except Exception as e:
    print(f"\n❌ Error: {e}")
    print("\nFallback - Try running these commands in separate terminals:")
    print("  1. python backend/server.py")
    print("  2. npm run dev")

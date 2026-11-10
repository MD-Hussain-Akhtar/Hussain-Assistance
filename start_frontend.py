#!/usr/bin/env python
"""Start Frontend + Electron"""
import subprocess
import sys
import os

print("\n" + "="*70)
print("⚛️  STARTING FRONTEND + ELECTRON")
print("="*70)

os.chdir(r"g:\ada_v2-main")

print("\n📌 Frontend + Electron:")
print("   Frontend: http://localhost:5173")
print("   Electron App: Desktop window")
print("   Build tool: Vite")
print("\n" + "-"*70)

try:
    subprocess.run(["npm", "run", "dev"], shell=True)
except KeyboardInterrupt:
    print("\n\n✅ Frontend/Electron stopped")
except Exception as e:
    print(f"\n❌ Error: {e}")
    print("\nMake sure you have:")
    print("  1. Node.js installed")
    print("  2. Dependencies: npm install")

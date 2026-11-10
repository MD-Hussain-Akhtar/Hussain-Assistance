#!/usr/bin/env python
"""Start Backend Server Only"""
import subprocess
import sys
import os

print("\n" + "="*70)
print("🐍 STARTING BACKEND SERVER")
print("="*70)

os.chdir(r"g:\ada_v2-main")

print("\n📌 Backend Server:")
print("   Port: 8000")
print("   API Docs: http://localhost:8000/docs")
print("   WebSocket: ws://localhost:8000/socket.io")
print("\n" + "-"*70)

try:
    subprocess.run(["python", "backend/server.py"])
except KeyboardInterrupt:
    print("\n\n✅ Backend stopped")
except Exception as e:
    print(f"\n❌ Error: {e}")
    print("\nMake sure you have installed requirements:")
    print("  pip install -r requirements.txt")

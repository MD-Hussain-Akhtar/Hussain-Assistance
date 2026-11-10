#!/usr/bin/env python
"""
DIAGNOSTIC - Check Backend & Frontend Connection
"""
import sys
sys.stdout.reconfigure(encoding='utf-8')
import time

print("""
╔════════════════════════════════════════════════════════════════════╗
║            🔍 SYSTEM DIAGNOSTICS - Check Services                 ║
╚════════════════════════════════════════════════════════════════════╝


YOUR ISSUE:
═══════════════════════════════════════════════════════════════════
"Electron open huva, 'open whatsapp' bola par
 task nhi kar pa raha, koi bhi task nhi ho raha"

(Electron opened, said "open whatsapp" but it didn't open.
 No tasks are working.)

This likely means:
  ❌ Frontend NOT connected to Backend
  ❌ WebSocket connection failed
  ❌ API communication broken


LET ME DIAGNOSE THE ISSUE...
═══════════════════════════════════════════════════════════════════
""")

time.sleep(1)

# Test 1: Check if Backend is running
print("\n[Test 1] Checking Backend Server (Port 8000)...")
print("-" * 70)

import socket

def is_port_open(port):
    """Check if port is open"""
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        result = sock.connect_ex(('127.0.0.1', port))
        return result == 0
    finally:
        sock.close()

backend_running = is_port_open(8000)
frontend_running = is_port_open(5173)

if backend_running:
    print("✅ Backend server IS RUNNING on port 8000")
else:
    print("❌ Backend server NOT running on port 8000")
    print("   → Need to start: python backend/server.py")

# Test 2: Check if Frontend is running
print("\n[Test 2] Checking Frontend Server (Port 5173)...")
print("-" * 70)

if frontend_running:
    print("✅ Frontend dev server IS RUNNING on port 5173")
else:
    print("❌ Frontend dev server NOT running on port 5173")
    print("   → Need to start: npm run dev")

# Test 3: Check if Backend API responds
print("\n[Test 3] Testing Backend API...")
print("-" * 70)

if backend_running:
    try:
        import urllib.request
        import json
        response = urllib.request.urlopen('http://localhost:8000/docs', timeout=2)
        print("✅ Backend API responding")
        print("   → API Docs: http://localhost:8000/docs")
    except Exception as e:
        print(f"⚠️  Backend API not responding: {e}")
else:
    print("⏭️  Skipped (backend not running)")

# Summary
print("\n" + "="*70)
print("📊 DIAGNOSTIC SUMMARY:")
print("="*70)

if backend_running and frontend_running:
    print("""
✅ BOTH SERVICES RUNNING!

But Electron commands aren't working because:
  1. Frontend JavaScript might have errors
  2. WebSocket connection might be failing
  3. Voice command routing might be broken
  
SOLUTION:
  1. Check Electron console for errors (F12 in Electron)
  2. Check browser console (F12 in http://localhost:5173)
  3. Check backend logs for errors
""")
elif backend_running:
    print("""
✅ Backend is running
❌ Frontend is NOT running

SOLUTION:
  In new terminal, run:
    cd g:\\ada_v2-main
    npm run dev
""")
elif frontend_running:
    print("""
❌ Backend is NOT running
✅ Frontend is running

SOLUTION:
  In new terminal, run:
    cd g:\\ada_v2-main\\backend
    python server.py
""")
else:
    print("""
❌ BOTH SERVICES NOT RUNNING!

SOLUTION:
  Open TWO terminals and run:
  
  Terminal 1:
    cd g:\\ada_v2-main\\backend
    python server.py
  
  Terminal 2:
    cd g:\\ada_v2-main
    npm run dev
""")

print("\n" + "="*70)

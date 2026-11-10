#!/usr/bin/env python
"""Test WhatsApp launch through system"""
import time
import sys
sys.path.insert(0, 'g:\\ada_v2-main\\backend')

from app_launcher import AppLauncher

print("=" * 50)
print("TESTING WHATSAPP LAUNCH")
print("=" * 50)

launcher = AppLauncher()

# Test 1: Direct app launch
print("\n[TEST 1] Launching WhatsApp Desktop...")
result = launcher.launch_common_app('whatsapp')
print(f"Result: {result}")
print("Waiting 3 seconds for app to open...")
time.sleep(3)

# Test 2: Check if process exists
import subprocess
try:
    ps_check = subprocess.check_output(
        ['powershell', '-Command', 'Get-Process | Where-Object { $_.ProcessName -like "*whatsapp*" } | Select-Object ProcessName'],
        text=True
    )
    if ps_check.strip():
        print("\n✅ SUCCESS: WhatsApp process is running!")
        print(ps_check)
    else:
        print("\n⚠️  No WhatsApp process found yet (may be initializing)")
except:
    print("\n⚠️  Could not check process")

print("\n" + "=" * 50)
print("TEST COMPLETE")
print("=" * 50)

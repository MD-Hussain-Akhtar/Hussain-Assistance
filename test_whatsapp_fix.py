#!/usr/bin/env python
"""Test WhatsApp launcher fix"""
import sys
import time
sys.path.insert(0, 'g:\\ada_v2-main\\backend')

from app_launcher import AppLauncher

print("Testing WhatsApp launcher...")
launcher = AppLauncher()
result = launcher.launch_common_app('whatsapp')
print(f"Launch result: {result}")
time.sleep(3)
print("WhatsApp should have opened now")

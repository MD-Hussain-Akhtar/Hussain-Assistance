#!/usr/bin/env python
"""Test WhatsApp launch"""
import sys
import os

# Add parent to path
sys.path.insert(0, os.path.dirname(__file__))

from app_launcher import AppLauncher

print("Testing WhatsApp launch...")
launcher = AppLauncher()
result = launcher.launch_common_app('whatsapp')
print("Result:", result)

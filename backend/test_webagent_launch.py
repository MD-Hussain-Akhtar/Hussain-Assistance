#!/usr/bin/env python
"""Test WebAgent launch"""
import sys
import os

# Add parent to path
sys.path.insert(0, os.path.dirname(__file__))

from app_launcher import AppLauncher

print("Testing WebAgent launch...")
launcher = AppLauncher()
result = launcher.launch_common_app('webagent')
print("Result:", result)
print("\nStatus:", "✅ SUCCESS" if result.get('success') else "⚠️ Not found")

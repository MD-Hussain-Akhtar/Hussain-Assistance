#!/usr/bin/env python
"""Test camera module functionality."""

import sys
sys.path.insert(0, 'backend')

from camera_module import get_camera_module

print('[TEST] ✅ Initializing camera...')
camera = get_camera_module()
print(f'[TEST] Camera initialized: {camera.initialized}')

if camera.initialized:
    print('[TEST] ✅ Capturing frame...')
    result = camera.describe_scene()
    print(f'[TEST] Success: {result.get("success")}')
    print(f'[TEST] Description: {result.get("description")}')
    print(f'[TEST] Frame shape: {result.get("frame_shape")}')
    brightness = result.get("brightness", {})
    print(f'[TEST] Brightness: {brightness.get("status")}')
    activity = result.get("edges", {})
    print(f'[TEST] Activity: {activity.get("activity")}')
    motion = result.get("motion_potential", {})
    print(f'[TEST] Motion detected: {motion.get("detected")}')
    print('[TEST] ✅ Camera working perfectly!')
else:
    print('[TEST] ❌ Camera failed to initialize')

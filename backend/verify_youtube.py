#!/usr/bin/env python
"""Verify YouTube video is actually playing"""
from media_controller import MediaController
import time
import pygetwindow as gw

mc = MediaController()

print("\n🎬 STARTING YOUTUBE VIDEO TEST")
print("-" * 50)

# Play video
result = mc.youtube_play("honey singh mundian to bach ke")
print(f"Function Result: {result}")

# Wait for Chrome to open and load
time.sleep(8)

# Check Chrome window
print("\n📌 Checking Chrome Window:")
try:
    chrome_windows = gw.getWindowsWithTitle("Chrome")
    for w in chrome_windows:
        print(f"  ✅ Found: {w.title}")
        
    youtube_windows = gw.getWindowsWithTitle("YouTube")
    for w in youtube_windows:
        print(f"  ✅ YouTube Page Found: {w.title}")
        
except Exception as e:
    print(f"  Error checking windows: {e}")

print("\n✅ TEST COMPLETE - Check Chrome window if video is playing")

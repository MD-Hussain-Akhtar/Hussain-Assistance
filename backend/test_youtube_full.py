#!/usr/bin/env python
"""Test YouTube video play - full flow with debugging"""
from media_controller import MediaController
import time

mc = MediaController()

print("=" * 60)
print("🎥 YOUTUBE VIDEO PLAY TEST")
print("=" * 60)

query = "honey singh mundian to bach ke"
print(f"\n1️⃣ Query: {query}")
print("2️⃣ Opening Chrome...")

try:
    # Call youtube_play
    result = mc.youtube_play(query)
    
    print(f"\n3️⃣ Initial Result: {result}")
    
    # Wait and check if window is active
    time.sleep(2)
    print(f"4️⃣ Checking Chrome window...")
    
    import pygetwindow as gw
    windows = gw.getWindowsWithTitle("YouTube")
    if windows:
        print(f"   ✅ YouTube window found: {windows[0].title}")
        print(f"   Window size: {windows[0].size}")
    else:
        print(f"   ⚠️ YouTube window not found")
    
    # Try to check if video is playing by looking for pause button
    time.sleep(3)
    print(f"\n5️⃣ Video should be playing now...")
    print(f"   If you see a video in Chrome - SUCCESS! ✅")
    print(f"   If you only see search results - FAILED ❌")
    
    print("\n" + "=" * 60)
    print("TEST COMPLETE")
    print("=" * 60)
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()

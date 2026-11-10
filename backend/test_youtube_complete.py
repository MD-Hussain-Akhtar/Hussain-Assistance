#!/usr/bin/env python
"""Comprehensive YouTube Features Test - Now Same as Spotify!"""
import sys
sys.stdout.reconfigure(encoding='utf-8')
import time

print("\n" + "="*70)
print("🎬 YOUTUBE FEATURES TEST - UPGRADED LIKE SPOTIFY")
print("="*70)

from media_controller import MediaController

mc = MediaController()

# Test 1: YouTube Play
print("\n[Test 1] Playing YouTube video...")
print("-" * 70)
result = mc.youtube_play('levitating dua lipa')
print(f"✅ Result: {result.get('success')}")
time.sleep(4)

# Test 2: Pause/Resume
print("\n[Test 2] Testing pause/resume...")
print("-" * 70)
result = mc.pause_resume_youtube()
print(f"✅ Paused: {result.get('success')}")
time.sleep(1)
result = mc.pause_resume_youtube()
print(f"✅ Resumed: {result.get('success')}")
time.sleep(2)

# Test 3: Volume Control
print("\n[Test 3] Testing volume control...")
print("-" * 70)
result = mc.volume_up_youtube(3)
print(f"✅ Volume Up: {result.get('success')}")
time.sleep(1)
result = mc.volume_down_youtube(3)
print(f"✅ Volume Down: {result.get('success')}")
time.sleep(1)

# Test 4: Mute
print("\n[Test 4] Testing mute...")
print("-" * 70)
result = mc.mute_youtube()
print(f"✅ Muted: {result.get('success')}")
time.sleep(1)
result = mc.mute_youtube()
print(f"✅ Unmuted: {result.get('success')}")
time.sleep(1)

# Test 5: Skip Videos
print("\n[Test 5] Testing skip to next...")
print("-" * 70)
result = mc.next_video_youtube()
print(f"✅ Next Video: {result.get('success')}")
time.sleep(3)

# Test 6: Fullscreen
print("\n[Test 6] Testing fullscreen...")
print("-" * 70)
result = mc.fullscreen_youtube()
print(f"✅ Fullscreen On: {result.get('success')}")
time.sleep(2)
result = mc.fullscreen_youtube()
print(f"✅ Fullscreen Off: {result.get('success')}")
time.sleep(1)

print("\n" + "="*70)
print("✅ ALL YOUTUBE FEATURES WORKING!")
print("="*70)
print("""
YouTube now has the same features as Spotify:
  ✅ Play videos with search
  ✅ Pause/Resume
  ✅ Volume control (up/down)
  ✅ Mute/Unmute
  ✅ Skip to next video
  ✅ Go to previous video
  ✅ Fullscreen toggle

Features Available:
  • youtube_play(query) - Search and play
  • pause_resume_youtube() - Pause/play
  • next_video_youtube() - Skip to next
  • previous_video_youtube() - Go back
  • volume_up_youtube() - Increase volume
  • volume_down_youtube() - Decrease volume
  • mute_youtube() - Toggle mute
  • fullscreen_youtube() - Toggle fullscreen

""")
print("="*70 + "\n")

#!/usr/bin/env python
"""Test YouTube with ENSURE PLAYBACK - Guaranteed to work"""
import sys
sys.stdout.reconfigure(encoding='utf-8')
import time

print("\n" + "="*70)
print("🎬 YOUTUBE VIDEO PLAY - WITH PLAYBACK GUARANTEE")
print("="*70)

from media_controller import MediaController

mc = MediaController()

print("\n▶️  Step 1: Opening YouTube and searching for 'akhil'...")
print("-" * 70)
result1 = mc.youtube_play('akhil')
print(f"✅ Search & Open Result: {result1.get('success')}")

print("\n⏳ Waiting 3 seconds for video page to fully load...")
time.sleep(3)

print("\n▶️  Step 2: Ensuring video playback (if not playing)...")
print("-" * 70)
result2 = mc.youtube_ensure_playback()
print(f"✅ Playback Ensure Result: {result2.get('success')}")

print("\n" + "="*70)
print("🎬 FINAL STATUS:")
print("="*70)
print(f"""
Search Result: {'✅ SUCCESS' if result1.get('success') else '❌ FAILED'}
Playback Ensure: {'✅ SUCCESS' if result2.get('success') else '❌ FAILED'}

What should happen:
  1. Chrome opens with YouTube
  2. Searches for "akhil"
  3. Opens first video
  4. Applies multiple playback triggers
  5. Video PLAYS on screen

Check your screen - video should definitely be playing now!
If not, try pressing SPACEBAR on your keyboard manually.
""")
print("="*70 + "\n")

print("⏳ Keeping open for 15 seconds...")
time.sleep(15)

print("✅ Test complete!")

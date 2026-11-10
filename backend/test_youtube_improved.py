#!/usr/bin/env python
"""Test YouTube Play - Improved Version"""
import sys
sys.stdout.reconfigure(encoding='utf-8')
import time

print("\n" + "="*70)
print("🎬 IMPROVED YOUTUBE TEST")
print("="*70)

from media_controller import MediaController

mc = MediaController()

print("\n▶️  Testing improved YouTube playback...")
print("-" * 70)

result = mc.youtube_play('akhil')

print(f"\n✅ Result:")
print(f"   Success: {result.get('success')}")
print(f"   Status: {result.get('status')}")
print(f"   Query: {result.get('query')}")

print("\n" + "="*70)
print("📺 IMPROVEMENTS MADE:")
print("="*70)
print("""
New Features:
  ✓ Extra wait time (8 seconds) for full page load
  ✓ Tab navigation to first video (more reliable)
  ✓ Escape key to ensure focus
  ✓ Multiple play methods:
    - Spacebar (universal)
    - 'j' key (activates player)
    - 'k' key (YouTube play)
    - Spacebar again (final play)
  ✓ Better timing between actions

Result:
  Video should now actually PLAY on your screen!
""")
print("="*70 + "\n")

print("⏳ Waiting 12 seconds to let video fully load and play...")
time.sleep(12)

print("\n✅ Test complete!")
print("Check your screen - video should be playing now!")

#!/usr/bin/env python
"""Test YouTube - Play Akhil Song and Verify"""
import sys
sys.stdout.reconfigure(encoding='utf-8')
import time

print("\n" + "="*70)
print("🎬 TESTING YOUTUBE - AKHIL SONG")
print("="*70)

from media_controller import MediaController

mc = MediaController()

print("\n▶️  Playing: Akhil Song on YouTube...")
print("-" * 70)

result = mc.youtube_play('akhil')

print(f"\n✅ Result:")
print(f"   Success: {result.get('success')}")
print(f"   Status: {result.get('status')}")
print(f"   Query: {result.get('query')}")
print(f"   Action: {result.get('action')}")

print("\n" + "="*70)
print("📺 CHECK YOUR SCREEN:")
print("="*70)
print("""
You should see:
  ✓ Chrome window opened
  ✓ YouTube search results
  ✓ First Akhil video playing
  ✓ Video controls visible
  ✓ Audio playing

If all above are visible, YouTube is WORKING! ✅
""")
print("="*70)

# Keep window open
print("\n⏳ Keeping window open for 15 seconds...")
time.sleep(15)

print("\n✅ Test complete! Check if video is playing.")

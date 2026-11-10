#!/usr/bin/env python
"""Simple test of YouTube video play fix"""
import sys
sys.stdout.reconfigure(encoding='utf-8')
import time

print("\n" + "="*70)
print("TESTING YOUTUBE FIX - IMPROVED VERSION")
print("="*70)

from media_controller import MediaController

# Create instance
mc = MediaController()

# Test it
print("\n📺 Testing: youtube_play('akhil')")
print("-" * 70)

result = mc.youtube_play('akhil')

print(f"\n✅ Test Complete!")
print(f"   Success: {result.get('success')}")
print(f"   Status: {result.get('status')}")
print(f"   Query: {result.get('query')}")

print("\n" + "="*70)
print("📸 CHECK YOUR SCREEN NOW:")
print("="*70)
print("""
You should see:
  1. Chrome window opened
  2. YouTube search results for "akhil"
  3. First video should start playing automatically
  4. Video should show in the center with video controls visible

If video is playing, the fix worked! ✅
If video is NOT playing, we need more debugging. ❌
""")
print("="*70 + "\n")

# Keep script running to show results
time.sleep(10)
print("Test window can now be closed.")

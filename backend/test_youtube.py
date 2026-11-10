#!/usr/bin/env python
"""
Test YouTube feature - open and play a song
"""
import sys
sys.path.insert(0, 'backend')

from media_controller import get_media_controller

print("="*60)
print("Testing YouTube Feature")
print("="*60)
print("\nOpening YouTube and playing a song...\n")

controller = get_media_controller()

print("[1] Playing 'arijit singh' on YouTube...")
result = controller.youtube_play('arijit singh')

print(f"\n[RESULT]")
print(f"  Success: {result.get('success')}")
print(f"  Status: {result.get('status')}")
print(f"  Query: {result.get('query')}\n")

if result.get('success'):
    print("✅ YouTube opened and playing!")
    print("\nYou should see:")
    print("  • Chrome window opening")
    print("  • YouTube search results for 'arijit singh'")
    print("  • First video playing automatically")
else:
    print("⚠️  YouTube playback issue")
    print(f"  Error: {result.get('error')}")

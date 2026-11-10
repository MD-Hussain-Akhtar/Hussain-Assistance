#!/usr/bin/env python
"""
Test Spotify feature - open and play Akhil song
"""
import sys
sys.path.insert(0, 'backend')

from media_controller import get_media_controller

print("="*60)
print("Testing Spotify Feature")
print("="*60)
print("\nOpening Spotify and playing Akhil song...\n")

controller = get_media_controller()

print("[1] Playing 'akhil' on Spotify...")
result = controller.spotify_play('akhil')

print(f"\n[RESULT]")
print(f"  Success: {result.get('success')}")
print(f"  Status: {result.get('status')}")
print(f"  Query: {result.get('query')}\n")

if result.get('success'):
    print("✅ Spotify opened and playing!")
    print("\nYou should see:")
    print("  • Spotify window opening")
    print("  • Search for 'akhil'")
    print("  • First track playing")
    print("  • Song playing in background")
else:
    print("⚠️  Spotify playback issue")
    print(f"  Error: {result.get('error')}")

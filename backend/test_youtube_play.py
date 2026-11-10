#!/usr/bin/env python
"""Open YouTube and play a song"""
import sys
import os

# Add parent to path
sys.path.insert(0, os.path.dirname(__file__))

from media_controller import get_media_controller

print("=" * 60)
print("OPENING YOUTUBE AND PLAYING SONG")
print("=" * 60)

media = get_media_controller()

print("\n🎵 Playing song on YouTube...")
result = media.youtube_play("arijit singh")

print(f"\nResult: {result}")
print(f"Status: {'✅ SUCCESS' if result.get('success') else '⚠️ FAILED'}")

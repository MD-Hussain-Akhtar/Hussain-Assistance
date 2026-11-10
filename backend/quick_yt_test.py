#!/usr/bin/env python
"""Quick YouTube Test"""
import sys
sys.stdout.reconfigure(encoding='utf-8')

from media_controller import MediaController

mc = MediaController()

print("\n📺 Testing YouTube - Arijit Singh")
result = mc.youtube_play('arijit singh')
print(f"\n✅ Success: {result.get('success')}")
print(f"✅ Status: {result.get('status')}")
print(f"✅ Query: {result.get('query')}")

print("\n🎬 Video should be playing now!")

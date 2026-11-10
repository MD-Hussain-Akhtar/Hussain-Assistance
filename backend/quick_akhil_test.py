#!/usr/bin/env python
"""Quick Akhil Test - Check YouTube"""
import sys
sys.stdout.reconfigure(encoding='utf-8')

from media_controller import MediaController

print("\n📺 YouTube Test: Akhil Song")
print("-" * 50)

mc = MediaController()
result = mc.youtube_play('akhil')

print(f"✅ Status: {result.get('success')}")
print(f"✅ Playing: {result.get('query')}")
print(f"✅ Result: {result.get('status')}")

print("\n🎵 Akhil song video should be playing now!")
print("   Check your screen - video should be visible\n")

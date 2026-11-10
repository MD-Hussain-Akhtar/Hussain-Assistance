#!/usr/bin/env python
"""Test YouTube Video Play - Akhil Song"""
import sys
sys.stdout.reconfigure(encoding='utf-8')
from media_controller import MediaController

mc = MediaController()

print("\n" + "="*60)
print("TESTING YOUTUBE VIDEO PLAY - AKHIL SONG")
print("="*60)

print("\n1. Opening Chrome with YouTube search...")
print("2. Searching for: Akhil")
print("3. Clicking first video result...")
print("4. Auto-playing video...")

result = mc.youtube_play('akhil')

print("\nRESULT:")
print(f"  Success: {result.get('success')}")
print(f"  Action: {result.get('action')}")
print(f"  Query: {result.get('query')}")
print(f"  Status: {result.get('status')}")

print("\n" + "="*60)
print("CHECK YOUR CHROME WINDOW - VIDEO SHOULD BE PLAYING!")
print("="*60 + "\n")

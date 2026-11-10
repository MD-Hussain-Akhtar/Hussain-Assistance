#!/usr/bin/env python
"""Fix YouTube Video Play - Debug and Test"""
import sys
sys.stdout.reconfigure(encoding='utf-8')
from vision_analyzer import VisionAnalyzer
from media_controller import MediaController
import time

print("\n" + "="*70)
print("YOUTUBE VIDEO PLAY - DEBUGGING AND FIXING")
print("="*70)

# Check screen first
print("\n[Step 1] Capturing live screen...")
va = VisionAnalyzer()
img = va.capture_screen()
if img is not None:
    print(f"✅ Screen captured: {img.shape[1]}x{img.shape[0]} pixels")
    print("✅ Screen monitoring is ACTIVE")
else:
    print("❌ Screen capture failed")

print("\n[Step 2] Testing YouTube video play...")
print("Query: 'akhil'")
print("Opening Chrome + YouTube search...")

mc = MediaController()

# Test with direct play
result = mc.youtube_play('akhil')

print(f"\n[Step 3] Result:")
print(f"  Success: {result.get('success')}")
print(f"  Status: {result.get('status')}")
print(f"  Action: {result.get('action')}")

print("\n[Step 4] Checking screen after video play...")
time.sleep(3)
img2 = va.capture_screen()
if img2 is not None:
    print(f"✅ Screen still active: {img2.shape[1]}x{img2.shape[0]} pixels")

print("\n" + "="*70)
print("CHECK YOUR SCREEN:")
print("  1. Look for Chrome window")
print("  2. Look for YouTube")
print("  3. Look for video playing")
print("\nIf video is NOT playing, the issue might be:")
print("  • Chrome window not focused")
print("  • Keyboard shortcuts not working")
print("  • Page not fully loaded")
print("="*70 + "\n")

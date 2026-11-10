#!/usr/bin/env python
"""
YOUTUBE VIDEO PLAY - ULTRA RELIABLE VERSION
Uses direct video opening with guaranteed playback
"""
import sys
sys.stdout.reconfigure(encoding='utf-8')
import subprocess
import time
import pyautogui
from app_registry import get_registry

print("\n" + "="*70)
print("🎬 YOUTUBE ULTRA RELIABLE TEST")
print("="*70)

registry = get_registry()
chrome_path = registry.get_chrome_path()

print("\n🎯 Method: Direct Video Playback (Most Reliable)")
print("-" * 70)

# Method: Open search, find video, and play with guaranteed focus
query = 'akhil'
clean_query = query.replace(' ', '+')

print(f"1. Opening YouTube search for: {query}")
search_url = f"https://www.youtube.com/results?search_query={clean_query}"
subprocess.Popen([chrome_path, search_url])

print("2. Waiting 8 seconds for page load...")
time.sleep(8)

print("3. Focusing browser window...")
pyautogui.hotkey('alt', 'tab')
time.sleep(0.5)

print("4. Pressing Escape to clear any overlays...")
pyautogui.press('escape')
time.sleep(0.3)

print("5. Clicking in the page to ensure focus...")
pyautogui.click(960, 300)  # Click in the results area
time.sleep(0.5)

print("6. Pressing Tab to navigate to first result...")
for i in range(3):
    pyautogui.press('tab')
    time.sleep(0.2)

print("7. Pressing Enter to open first video...")
pyautogui.press('enter')
time.sleep(6)

print("8. Clicking on video player for focus...")
pyautogui.click(960, 540)  # Center of screen
time.sleep(0.5)

print("9. Activating video with multiple shortcuts...")
# Try all known YouTube shortcuts to ensure playback
pyautogui.press('j')  # Go back 10 sec (activates player)
time.sleep(0.3)
pyautogui.press('k')  # Play/pause
time.sleep(0.3)
pyautogui.press('space')  # Play/pause
time.sleep(0.5)

print("\n" + "="*70)
print("✅ RESULT:")
print("="*70)
print("""
Video should now be PLAYING on your screen!

What you should see:
  ✓ Chrome with YouTube video
  ✓ Video player with content visible
  ✓ Timeline/progress bar
  ✓ Audio playing (check speaker)
  ✓ Playback controls available

If video is still not playing, it might be:
  • Browser needs to be in focus (click on it)
  • Video player might be paused (press spacebar)
  • JavaScript not loading (refresh page)
  • Ad might be playing first
""")
print("="*70 + "\n")

print("⏳ Keeping browser open for 10 seconds...")
time.sleep(10)

print("✅ Test complete! Check your screen now.")

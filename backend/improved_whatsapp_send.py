#!/usr/bin/env python
"""
Improved WhatsApp message sender with better timing and debugging
"""
import pyautogui
import time
import sys

# Disable fail-safe
pyautogui.FAILSAFE = False
pyautogui.PAUSE = 0.1

print("=== IMPROVED WhatsApp Message Test ===\n")

contact_name = 'papa'
message = 'hello'

try:
    print(f"[1] Focusing WhatsApp window...")
    # Try Alt+Tab to switch to WhatsApp
    pyautogui.hotkey('alt', 'tab')
    print("    ✓ Alt+Tab executed")
    time.sleep(2)  # LONGER wait for window switch
    
    print(f"\n[2] Opening new chat (Ctrl+N)...")
    pyautogui.hotkey('ctrl', 'n')
    print("    ✓ Ctrl+N executed")
    time.sleep(2)  # Wait for new chat dialog to open
    
    print(f"\n[3] Typing contact name: '{contact_name}'...")
    # Use write() instead of typewrite() for better compatibility
    pyautogui.write(contact_name)
    print("    ✓ Contact name typed")
    time.sleep(1.5)  # Wait for autocomplete
    
    print(f"\n[4] Selecting first contact (Down + Enter)...")
    pyautogui.press('down')
    print("    ✓ Down pressed")
    time.sleep(0.5)
    
    pyautogui.press('enter')
    print("    ✓ Enter pressed (selecting contact)")
    time.sleep(2)  # Wait for chat to open
    
    print(f"\n[5] Typing message: '{message}'...")
    pyautogui.write(message)
    print("    ✓ Message typed")
    time.sleep(1)
    
    print(f"\n[6] Sending message (Enter)...")
    pyautogui.press('enter')
    print("    ✓ Enter pressed (sending)")
    time.sleep(2)  # Wait for send to complete
    
    print(f"\n✅ TEST COMPLETE!")
    print(f"   Message to {contact_name}: '{message}'")
    print(f"   Check WhatsApp window - message should appear in chat")
    
except Exception as e:
    print(f"\n❌ ERROR: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

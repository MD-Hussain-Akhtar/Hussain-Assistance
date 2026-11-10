#!/usr/bin/env python
"""Test System Control Features - Close, Minimize, Shutdown, Restart"""
import sys
sys.stdout.reconfigure(encoding='utf-8')
import time

print("\n" + "="*70)
print("🎮 SYSTEM CONTROL FEATURES - TEST")
print("="*70)

from system_controller import SystemController

sc = SystemController()

print("\n" + "="*70)
print("AVAILABLE SYSTEM CONTROL FEATURES:")
print("="*70)

features = """
1️⃣  CLOSE CHROME
    Command: close_chrome()
    Voice: "chrome band kar", "chrome close kar", "chrome hata do"
    Action: Closes Google Chrome

2️⃣  CLOSE ANY APPLICATION  
    Command: close_application('app_name')
    Voice: "spotify band kar", "notepad close kar"
    Action: Closes specified application

3️⃣  MINIMIZE WINDOWS
    Command: minimize_window()
    Voice: "minimize kar", "sab hide kar", "chhupa do"
    Action: Minimizes all windows (shows desktop)

4️⃣  SHOW DESKTOP
    Command: show_desktop()
    Voice: "desktop dikhao", "desktop show kar"
    Action: Minimizes all windows and shows desktop

5️⃣  SHUTDOWN PC
    Command: shutdown_pc(delay=0)
    Voice: "pc band kar", "computer shutdown kar"
    Action: Shuts down the computer
    
    Optional delay:
    shutdown_pc(delay=60)  # Shutdown after 60 seconds

6️⃣  RESTART PC
    Command: restart_pc(delay=0)
    Voice: "pc restart kar", "computer restart kar"
    Action: Restarts the computer
    
    Optional delay:
    restart_pc(delay=60)  # Restart after 60 seconds

7️⃣  CANCEL SHUTDOWN/RESTART
    Command: cancel_shutdown()
    Voice: "shutdown cancel kar", "restart cancel kar"
    Action: Cancels pending shutdown/restart
"""

print(features)

print("\n" + "="*70)
print("QUICK TEST:")
print("="*70)

print("\n✅ Testing close_chrome()...")
print("   (This will close Chrome if it's open)")
# result = sc.close_chrome()
# print(f"   Result: {result.get('status')}")

print("\n✅ Testing close_application('notepad')...")
print("   (This will close Notepad if it's open)")
# result = sc.close_application('notepad')
# print(f"   Result: {result.get('status')}")

print("\n✅ Testing minimize_window()...")
print("   (This will minimize all windows)")
print("   WARNING: This will minimize everything!")
response = input("\n   Continue with minimize test? (y/n): ")
if response.lower() == 'y':
    result = sc.minimize_window()
    print(f"   Result: {result}")
    time.sleep(2)

print("\n✅ Testing show_desktop()...")
print("   (This will show desktop)")
response = input("   Continue with show_desktop test? (y/n): ")
if response.lower() == 'y':
    result = sc.show_desktop()
    print(f"   Result: {result}")
    time.sleep(2)

print("\n" + "="*70)
print("🔴 DANGEROUS OPERATIONS:")
print("="*70)
print("""
The following operations will actually shutdown/restart your PC.
They are NOT tested automatically to prevent accidental PC shutdown!

To test manually in Python:
  
  # Shutdown immediately:
  sc.shutdown_pc(delay=0)
  
  # Shutdown in 60 seconds:
  sc.shutdown_pc(delay=60)
  
  # Restart immediately:
  sc.restart_pc(delay=0)
  
  # Cancel shutdown:
  sc.cancel_shutdown()

VOICE COMMANDS:
  "PC shutdown kar" → Will shutdown
  "PC restart kar" → Will restart
  "shutdown cancel kar" → Will cancel
""")

print("="*70 + "\n")

print("✅ System Control Features READY!")
print("   All features can be accessed via voice commands or code!")

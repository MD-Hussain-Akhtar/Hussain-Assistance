import subprocess
import time
import sys

print("=== WhatsApp Launch & Message Test ===\n")

# Import and use the same launcher
from app_launcher import AppLauncher

print("[1] Launching WhatsApp via AppLauncher...")
launcher = AppLauncher()
result = launcher.launch_whatsapp_desktop()
print(f"    Result: {result}")

time.sleep(3)

# Check if WhatsApp opened
print("\n[2] Checking if WhatsApp is running...")
proc = subprocess.run(['tasklist'], capture_output=True, text=True)
if 'WhatsApp' in proc.stdout:
    print("    ✓ WhatsApp process found!")
else:
    print("    ✗ WhatsApp process NOT found in tasklist")
    print("    Tasklist output (sample):")
    for line in proc.stdout.splitlines()[:5]:
        print(f"      {line}")

time.sleep(2)

# Try to send message
print("\n[3] Attempting to send message to Papa...")
try:
    from whatsapp_v2 import WhatsAppMessenger
    wa = WhatsAppMessenger()
    msg_result = wa.quick_message('papa', 'hello')
    print(f"    Result: {msg_result}")
    if msg_result.get('success'):
        print("    ✓ Message sent!")
    else:
        print(f"    ✗ Message failed: {msg_result.get('error')}")
except Exception as e:
    print(f"    ✗ Exception: {e}")
    import traceback
    traceback.print_exc()

print("\n=== Test Complete ===")

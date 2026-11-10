from app_launcher import AppLauncher

print("Using Electron's AppLauncher to launch WhatsApp...")
launcher = AppLauncher()
result = launcher.launch_whatsapp_desktop()
print("Launch result:", result)

import time
time.sleep(4)

print("\nNow attempting to send message...")
from whatsapp_v2 import WhatsAppMessenger
wa = WhatsAppMessenger()
msg_result = wa.quick_message('papa', 'hello')
print("Message result:", msg_result)

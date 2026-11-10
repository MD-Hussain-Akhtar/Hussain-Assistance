import ctypes
import time
import os

appid = "5319275A.WhatsAppDesktop_cv1g1gvanyjgm!WhatsApp"

print("[WHATSAPP] Attempting to launch via WinAPI (ShellExecute)...")
try:
    # Use ctypes to call ShellExecuteW directly
    shell32 = ctypes.windll.shell32
    # ShellExecuteW(hwnd, operation, file, parameters, directory, show_command)
    # file: "shell:appsFolder\{appid}"
    uri = f"shell:appsFolder\\{appid}"
    result = shell32.ShellExecuteW(None, "open", uri, None, None, 1)  # 1 = SW_SHOW
    print(f"ShellExecuteW result code: {result}")
    if result > 32:
        print("[SUCCESS] ShellExecute launched app successfully")
    else:
        print(f"[ERROR] ShellExecute failed with code {result}")
except Exception as e:
    print(f"[ERROR] Failed to use WinAPI: {e}")

print("\nWaiting 3 seconds...")
time.sleep(3)

# Check process
print("\nChecking if WhatsApp is running...")
os.system("tasklist | findstr /I WhatsApp")

print("\nNow sending message to Papa...")
from whatsapp_v2 import WhatsAppMessenger
wa = WhatsAppMessenger()
result = wa.quick_message('papa', 'hello')
print("Result:", result)

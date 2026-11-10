import subprocess
import time

# Use the exact same AppID that Electron/Zoya uses for WhatsApp
appid = "5319275A.WhatsAppDesktop_cv1g1gvanyjgm!WhatsApp"

ps_cmd = f'''
[Windows.System.Launcher,Windows.System,ContentType=WindowsRuntime] | Out-Null
[Windows.System.LauncherOptions,Windows.System,ContentType=WindowsRuntime] | Out-Null
$uri = [Windows.Foundation.Uri]("shell:appsFolder\\{appid}")
[Windows.System.Launcher]::LaunchUriAsync($uri) | Out-Null
Write-Host "WhatsApp launched"
'''

print("[WHATSAPP] Launching via PowerShell (same method as Electron)...")
try:
    proc = subprocess.run(
        ["powershell", "-NoProfile", "-Command", ps_cmd],
        capture_output=True,
        text=True,
        timeout=10
    )
    print("Exit code:", proc.returncode)
    if proc.stdout:
        print("Output:", proc.stdout)
    if proc.stderr:
        print("Error output:", proc.stderr)
except Exception as e:
    print(f"Failed to run PowerShell: {e}")

print("\nWaiting 3 seconds for WhatsApp to appear...")
time.sleep(3)

# Check if WhatsApp process is running
try:
    result = subprocess.run(["tasklist"], capture_output=True, text=True)
    if "WhatsApp" in result.stdout:
        print("[SUCCESS] WhatsApp is running on desktop!")
    else:
        print("[INFO] WhatsApp process not found in tasklist")
except Exception as e:
    print(f"Could not check tasklist: {e}")

print("\nNow attempting to send message to Papa...")
from whatsapp_v2 import WhatsAppMessenger
wa = WhatsAppMessenger()
result = wa.quick_message('papa', 'hello')
print("Message result:", result)

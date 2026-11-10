import subprocess
import time
import json
import os

print('=== Launching WhatsApp via Store AppID ===\n')

# The correct AppID for Microsoft Store WhatsApp
app_id = '5319275A.WhatsAppDesktop_cv1g1gvanyjgm!WhatsApp'
ps_cmd = f'''
try {{
    [Windows.System.Launcher,Windows.System,ContentType=WindowsRuntime] | Out-Null
    [Windows.System.LauncherOptions,Windows.System,ContentType=WindowsRuntime] | Out-Null
    $uri = [Windows.Foundation.Uri]("shell:appsFolder\\{app_id}")
    [Windows.System.Launcher]::LaunchUriAsync($uri) | Out-Null
    Write-Host "WhatsApp launched successfully"
}} catch {{
    Write-Host "Failed to launch WhatsApp: $_"
}}
'''

try:
    print('Executing PowerShell launch command...')
    subprocess.Popen(['powershell', '-NoProfile', '-Command', ps_cmd])
    print('✓ Command issued')
    print('⏳ Waiting 5 seconds for app to start...')
    time.sleep(5)
except Exception as e:
    print(f'✗ Error: {e}')
    import sys
    sys.exit(1)

# Verify WhatsApp is running
print('\n=== Verifying WhatsApp is running ===')
try:
    proc = subprocess.run(['tasklist'], capture_output=True, text=True)
    if 'WhatsApp' in proc.stdout:
        print('✓ WhatsApp process found in tasklist')
        
        # Save to app_paths for future use
        print('\n=== Saving path reference ===')
        app_paths = {}
        if os.path.exists('app_paths.json'):
            try:
                with open('app_paths.json', 'r') as f:
                    app_paths = json.load(f)
            except:
                pass
        
        app_paths['WhatsApp'] = f'shell:appsFolder\\{app_id}'
        with open('app_paths.json', 'w') as f:
            json.dump(app_paths, f, indent=2)
        print('✓ Saved to app_paths.json')
        
        # Now try sending message
        print('\n=== Sending message to Papa ===')
        time.sleep(2)  # Give time for UI to settle
        from whatsapp_v2 import WhatsAppMessenger
        wa = WhatsAppMessenger()
        result = wa.quick_message('papa', 'hello')
        print(f'Message result: {result}')
    else:
        print('✗ WhatsApp process not found in tasklist')
        print('Check if WhatsApp window is visible on screen.')
except Exception as e:
    print(f'Error: {e}')

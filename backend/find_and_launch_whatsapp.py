import os
import json
import subprocess
import time
from pathlib import Path

print('=== Finding WhatsApp.exe ===\n')

# Search locations for Microsoft Store and traditional installs
search_paths = [
    Path(os.path.expanduser('~\\AppData\\Local\\WhatsApp')),
    Path(os.path.expanduser('~\\AppData\\Local\\Microsoft\\WindowsApps')),
    Path('C:\\Program Files\\WhatsApp'),
    Path('C:\\Program Files (x86)\\WhatsApp'),
    Path(os.path.expanduser('~\\AppData\\Roaming\\WhatsApp')),
]

found_path = None

for search_dir in search_paths:
    if not search_dir.exists():
        continue
    try:
        print(f'Searching {search_dir}...')
        for exe_file in search_dir.rglob('WhatsApp.exe'):
            found_path = str(exe_file)
            print(f'✓ Found: {found_path}')
            break
        if found_path:
            break
    except Exception as e:
        print(f'  Error: {e}')

if not found_path:
    print('\n✗ WhatsApp.exe not found in standard locations.')
    print('Trying fallback: searching entire AppData\\Local...')
    try:
        appdata = Path(os.path.expanduser('~\\AppData\\Local'))
        for exe_file in appdata.rglob('WhatsApp.exe'):
            found_path = str(exe_file)
            print(f'✓ Found: {found_path}')
            break
    except Exception as e:
        print(f'Fallback search error: {e}')

if found_path:
    print(f'\n=== Saving to app_paths.json ===')
    # Load or create app_paths.json
    app_paths = {}
    if os.path.exists('app_paths.json'):
        try:
            with open('app_paths.json', 'r') as f:
                app_paths = json.load(f)
        except Exception:
            pass
    
    app_paths['WhatsApp'] = found_path
    with open('app_paths.json', 'w') as f:
        json.dump(app_paths, f, indent=2)
    print(f'✓ Saved WhatsApp path to app_paths.json')
    
    print(f'\n=== Launching WhatsApp ===')
    try:
        subprocess.Popen([found_path], shell=False)
        print('✓ Launch command issued.')
        print('⏳ Waiting 4 seconds for app to load...')
        time.sleep(4)
    except Exception as e:
        print(f'✗ Failed to launch: {e}')
        found_path = None

if found_path:
    print(f'\n=== Checking if WhatsApp is running ===')
    try:
        proc = subprocess.run(['tasklist'], capture_output=True, text=True)
        if 'WhatsApp' in proc.stdout:
            print('✓ WhatsApp process found in tasklist')
            
            print(f'\n=== Sending message to Papa ===')
            from whatsapp_v2 import WhatsAppMessenger
            wa = WhatsAppMessenger()
            result = wa.quick_message('papa', 'hello')
            print(f'Result: {result}')
        else:
            print('✗ WhatsApp not found in running processes')
    except Exception as e:
        print(f'Error: {e}')
else:
    print('\n✗ Could not locate WhatsApp.exe')
    print('Please ensure WhatsApp Desktop is installed from the Microsoft Store.')

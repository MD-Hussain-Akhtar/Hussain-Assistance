import os
import json
import time
import subprocess
from app_registry import get_registry

print('--- Media App Diagnostic ---')
reg = get_registry()

# Show cached registry entries if present
if os.path.exists('app_paths.json'):
    try:
        with open('app_paths.json','r') as f:
            print('\nCached app_paths:')
            print(json.dumps(json.load(f), indent=2))
    except Exception as e:
        print('Could not read app_paths.json:', e)
else:
    print('\nNo app_paths.json found.')

# Query registry for Spotify and WhatsApp
spotify_path = reg.get_spotify_path()
whatsapp_path = reg.get_app_path('WhatsApp')

print(f'\nget_spotify_path() -> {spotify_path}')
print(f'get_app_path("WhatsApp") -> {whatsapp_path}')

# Helper to try launching
def try_launch(path, name):
    if not path:
        print(f'No path for {name}, skipping launch')
        return False
    if not os.path.exists(path):
        print(f'Path for {name} does not exist on disk: {path}')
        return False
    try:
        print(f'Launching {name} -> {path}')
        subprocess.Popen([path], shell=False)
        time.sleep(2)
        return True
    except Exception as e:
        print(f'Failed to launch {name}: {e}')
        return False

launched_spotify = try_launch(spotify_path, 'Spotify')
launched_whatsapp = try_launch(whatsapp_path, 'WhatsApp')

# List processes to confirm
print('\nListing running processes for Spotify and WhatsApp:')
try:
    proc = subprocess.run(['tasklist'], capture_output=True, text=True)
    out = proc.stdout.lower()
    lines = [l for l in out.splitlines() if 'spotify' in l or 'whatsapp' in l]
    if lines:
        for l in lines:
            print(' ', l)
    else:
        print('  No Spotify or WhatsApp processes found in tasklist output')
except Exception as e:
    print('Could not run tasklist:', e)

print('\nDiagnostic complete.')

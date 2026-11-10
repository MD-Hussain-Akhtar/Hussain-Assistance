import time
import subprocess

try:
    import pygetwindow as gw
    import pyautogui
except Exception as e:
    print('ERROR importing dependencies:', e)
    raise


def check_process():
    out = subprocess.run(['tasklist','/FI','IMAGENAME eq Spotify.exe'], capture_output=True, text=True)
    return 'Spotify.exe' in out.stdout


def get_spotify_window():
    wins = gw.getWindowsWithTitle('Spotify')
    return wins[0] if wins else None


print('== Spotify Playback Check ==')
proc = check_process()
print('Spotify process running:', proc)

w = get_spotify_window()
if not w:
    print('Spotify window not found.')
else:
    print('Spotify window title (before):', repr(w.title))
    try:
        w.activate()
        time.sleep(0.6)
    except Exception as e:
        print('Could not activate window:', e)

    # Try to start playback using media key
    print('Sending media play/pause key...')
    try:
        pyautogui.press('playpause')
    except Exception as e:
        print('pyautogui press playpause failed:', e)
        try:
            pyautogui.hotkey('fn','playpause')
        except Exception:
            pass

    time.sleep(2.5)
    w2 = get_spotify_window()
    print('Spotify window title (after):', repr(w2.title) if w2 else None)
    contains_akhil = 'akhil' in w2.title.lower() if w2 and w2.title else False
    print("Window title contains 'Akhil'?:", contains_akhil)

print('Done')

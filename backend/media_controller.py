"""
Media Controller - Simplified for Spotify and YouTube playback
"""
import subprocess
import time
import pyautogui
import pygetwindow as gw
from app_registry import get_registry
from typing import Optional, Dict


class MediaController:
    def __init__(self):
        self.registry = get_registry()
        pyautogui.FAILSAFE = True
        pyautogui.PAUSE = 0.05
    
    def launch_app(self, app_name: str) -> bool:
        """Launch application directly"""
        try:
            if app_name.lower() == "spotify":
                path = self.registry.get_spotify_path()
            elif app_name.lower() in ["chrome", "google chrome"]:
                path = self.registry.get_chrome_path()
            elif app_name.lower() == "edge":
                path = self.registry.get_edge_path()
            else:
                path = self.registry.get_app_path(app_name)
            
            if not path:
                return False
            
            subprocess.Popen(path)
            time.sleep(1)
            return True
        except:
            return False
    
    def focus_window(self, window_title_partial: str) -> Optional[object]:
        """Focus window by partial title match"""
        try:
            windows = gw.getWindowsWithTitle(window_title_partial)
            if windows:
                window = windows[0]
                window.activate()
                time.sleep(0.5)
                return window
        except:
            pass
        return None
    
    def spotify_play(self, query: str) -> Dict:
        """Search and play music on Spotify"""
        try:
            print(f"[SPOTIFY] Playing: {query}")
            
            # Launch Spotify if not running
            if not self.focus_window("Spotify"):
                print(f"[SPOTIFY] Launching Spotify...")
                if not self.launch_app("Spotify"):
                    return {"success": False, "error": "Spotify not found"}
                time.sleep(5)  # Wait for Spotify to fully load
                if not self.focus_window("Spotify"):
                    time.sleep(3)
                    self.focus_window("Spotify")
            
            print(f"[SPOTIFY] Searching for: {query}")
            time.sleep(1)
            
            # IMPROVED: Open search with Ctrl+L
            pyautogui.hotkey('ctrl', 'l')
            time.sleep(0.8)  # Wait for search box to activate
            
            # Select all and clear previous search
            pyautogui.hotkey('ctrl', 'a')
            time.sleep(0.2)
            
            # Type query with proper interval (0.08 per character, like WhatsApp fix)
            print(f"[SPOTIFY] Typing query: {query}")
            pyautogui.typewrite(query, interval=0.08)
            time.sleep(1)
            
            # Press Enter to search
            print(f"[SPOTIFY] Searching...")
            pyautogui.press('enter')
            time.sleep(3)  # Wait for search results
            
            # IMPORTANT: First tab press gets focus on search results
            # Then press down and enter to select first track
            print(f"[SPOTIFY] Selecting first result...")
            pyautogui.press('tab')
            time.sleep(0.5)
            
            # Press down to go to first track
            pyautogui.press('down')
            time.sleep(0.3)
            
            # Press enter to play the track
            print(f"[SPOTIFY] Playing track...")
            pyautogui.press('enter')
            time.sleep(2)  # Wait for playback to start
            
            print(f"[SPOTIFY] ✓ Track should now be playing!")
            return {"success": True, "action": "spotify_play", "query": query, "status": "now playing"}
            
        except Exception as e:
            print(f"[SPOTIFY ERROR] {e}")
            return {"success": False, "error": str(e)}
    
    def youtube_play(self, query: str) -> Dict:
        try:
            import pywhatkit
            print(f"[YouTube] Playing: {query}")
            pywhatkit.playonyt(query)
            return {"success": True, "message": f"YouTube pe '{query}' play kar diya"}
        except Exception as e:
            print(f"[YouTube] Error: {e}")
            return {"success": False, "error": str(e)}
    
    def open_app(self, app_name: str) -> Dict:
        """Open application"""
        try:
            if self.launch_app(app_name):
                return {"success": True, "action": "open_app", "app": app_name}
            return {"success": False, "error": f"{app_name} not found"}
        except Exception as e:
            return {"success": False, "error": str(e)}


_controller = None

def get_media_controller() -> MediaController:
    global _controller
    if _controller is None:
        _controller = MediaController()
    return _controller

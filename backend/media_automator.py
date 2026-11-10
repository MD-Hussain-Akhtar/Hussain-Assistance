import subprocess
import time
import os
import json
from typing import Dict, Optional
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('MediaAutomator')


class SpotifyAutomator:
    def __init__(self, exe_path: Optional[str] = None):
        self.exe_path = exe_path or self._find_spotify()
        self.is_running = False

    def _find_spotify(self) -> Optional[str]:
        """Find Spotify executable"""
        common_paths = [
            os.path.expanduser(r'~\AppData\Roaming\Spotify\Spotify.exe'),
            r'C:\Program Files\Spotify\Spotify.exe',
            r'C:\Program Files (x86)\Spotify\Spotify.exe',
        ]
        for path in common_paths:
            if os.path.exists(path):
                return path
        return None

    def launch(self) -> Dict:
        """Launch Spotify"""
        try:
            if not self.exe_path:
                return {'success': False, 'error': 'Spotify not found'}

            subprocess.Popen([self.exe_path], shell=False)
            self.is_running = True
            time.sleep(3)
            return {'success': True, 'action': 'spotify_launched'}
        except Exception as e:
            logger.error(f"Spotify launch failed: {e}")
            return {'success': False, 'error': str(e)}

    def search_and_play(self, query: str) -> Dict:
        """Search for song and play (requires Spotify Web API or automation)"""
        try:
            from ui_automator import get_ui_automator
            automator = get_ui_automator()

            # Open search with Ctrl+L
            automator.key_combo('ctrl', 'l')
            time.sleep(0.5)
            automator.type_text(query)
            time.sleep(0.3)
            automator.press_key('enter')
            time.sleep(1)

            return {'success': True, 'action': 'spotify_search', 'query': query}
        except Exception as e:
            logger.error(f"Spotify search failed: {e}")
            return {'success': False, 'error': str(e)}

    def play_pause(self) -> Dict:
        """Toggle play/pause"""
        try:
            from ui_automator import get_ui_automator
            automator = get_ui_automator()
            automator.press_key('space')
            return {'success': True, 'action': 'spotify_play_pause'}
        except Exception as e:
            logger.error(f"Play/pause failed: {e}")
            return {'success': False, 'error': str(e)}

    def next_track(self) -> Dict:
        """Skip to next track"""
        try:
            from ui_automator import get_ui_automator
            automator = get_ui_automator()
            automator.key_combo('ctrl', 'right')
            return {'success': True, 'action': 'spotify_next'}
        except Exception as e:
            logger.error(f"Next track failed: {e}")
            return {'success': False, 'error': str(e)}

    def previous_track(self) -> Dict:
        """Skip to previous track"""
        try:
            from ui_automator import get_ui_automator
            automator = get_ui_automator()
            automator.key_combo('ctrl', 'left')
            return {'success': True, 'action': 'spotify_previous'}
        except Exception as e:
            logger.error(f"Previous track failed: {e}")
            return {'success': False, 'error': str(e)}

    def set_volume(self, level: int) -> Dict:
        """Set volume (0-100) via Spotify UI"""
        try:
            # Not directly controllable via keyboard; requires system audio
            return {'success': False, 'error': 'Use system volume control'}
        except Exception as e:
            return {'success': False, 'error': str(e)}


class YouTubeAutomator:
    def __init__(self, browser_exe: Optional[str] = None):
        self.browser_exe = browser_exe or self._find_chrome()

    def _find_chrome(self) -> Optional[str]:
        """Find Chrome/Edge executable"""
        common_paths = [
            r'C:\Program Files\Google\Chrome\Application\chrome.exe',
            r'C:\Program Files (x86)\Google\Chrome\Application\chrome.exe',
            r'C:\Program Files\Microsoft\Edge\Application\msedge.exe',
        ]
        for path in common_paths:
            if os.path.exists(path):
                return path
        return None

    def open_youtube(self) -> Dict:
        """Open YouTube"""
        try:
            if not self.browser_exe:
                return {'success': False, 'error': 'Chrome/Edge not found'}

            subprocess.Popen([self.browser_exe, 'https://youtube.com'], shell=False)
            time.sleep(3)
            return {'success': True, 'action': 'youtube_opened'}
        except Exception as e:
            logger.error(f"YouTube open failed: {e}")
            return {'success': False, 'error': str(e)}

    def open_studio(self) -> Dict:
        """Open YouTube Studio (for uploads)"""
        try:
            if not self.browser_exe:
                return {'success': False, 'error': 'Chrome/Edge not found'}

            subprocess.Popen([self.browser_exe, 'https://studio.youtube.com'], shell=False)
            time.sleep(5)
            return {'success': True, 'action': 'youtube_studio_opened'}
        except Exception as e:
            logger.error(f"YouTube Studio open failed: {e}")
            return {'success': False, 'error': str(e)}

    def search_video(self, query: str) -> Dict:
        """Search for video on YouTube"""
        try:
            from ui_automator import get_ui_automator
            from vision_analyzer import get_vision_analyzer
            automator = get_ui_automator()
            vision = get_vision_analyzer()

            # Wait for page load
            time.sleep(2)

            # Click search box
            vision.capture_screen()
            search_box = vision.find_text('search', exact=False)
            if search_box:
                automator.click(search_box.cx, search_box.cy)
                time.sleep(0.3)
                automator.type_text(query)
                time.sleep(0.3)
                automator.press_key('enter')
                time.sleep(2)

            return {'success': True, 'action': 'youtube_search', 'query': query}
        except Exception as e:
            logger.error(f"YouTube search failed: {e}")
            return {'success': False, 'error': str(e)}

    def upload_video(self, file_path: str, title: str, description: str, tags: str = '') -> Dict:
        """Upload video to YouTube"""
        try:
            from ui_automator import get_ui_automator
            from vision_analyzer import get_vision_analyzer
            automator = get_ui_automator()
            vision = get_vision_analyzer()

            # Ensure YouTube Studio is open
            self.open_studio()
            time.sleep(3)

            # Click create button
            vision.capture_screen()
            create_btn = vision.find_text('create', exact=False)
            if create_btn:
                automator.click(create_btn.cx, create_btn.cy)
                time.sleep(1)

            # Click upload
            vision.capture_screen()
            upload_btn = vision.find_text('upload', exact=False)
            if upload_btn:
                automator.click(upload_btn.cx, upload_btn.cy)
                time.sleep(1)

            # Select file
            automator.type_text_fast(file_path)
            automator.press_key('enter')
            time.sleep(2)

            # Fill title
            vision.capture_screen()
            title_field = vision.find_input_field('title')
            if title_field:
                automator.fill_input_field(title_field, title)
                time.sleep(0.3)

            # Fill description
            desc_field = vision.find_input_field('description')
            if desc_field:
                automator.fill_input_field(desc_field, description)
                time.sleep(0.3)

            # Add tags if provided
            if tags:
                tags_field = vision.find_input_field('tags')
                if tags_field:
                    automator.fill_input_field(tags_field, tags)
                    time.sleep(0.3)

            # Click publish
            vision.capture_screen()
            publish_btn = vision.find_text('publish', exact=False)
            if publish_btn:
                automator.click(publish_btn.cx, publish_btn.cy)
                time.sleep(2)

            return {'success': True, 'action': 'youtube_uploaded', 'title': title}
        except Exception as e:
            logger.error(f"YouTube upload failed: {e}")
            return {'success': False, 'error': str(e)}

    def handle_popups(self) -> Dict:
        """Handle common YouTube popups (Agree, Skip, etc.)"""
        try:
            from vision_analyzer import get_vision_analyzer
            from ui_automator import get_ui_automator
            vision = get_vision_analyzer()
            automator = get_ui_automator()

            vision.capture_screen()
            buttons = vision.detect_buttons()

            for btn in buttons:
                if any(x in btn['text'].lower() for x in ['agree', 'accept', 'ok', 'yes', 'skip']):
                    automator.click(btn['x'], btn['y'])
                    time.sleep(0.5)
                    return {'success': True, 'popup_handled': btn['text']}

            return {'success': False, 'error': 'No popup found'}
        except Exception as e:
            logger.error(f"Popup handling failed: {e}")
            return {'success': False, 'error': str(e)}


class ChromeAutomator:
    def __init__(self, exe_path: Optional[str] = None):
        self.exe_path = exe_path or self._find_chrome()

    def _find_chrome(self) -> Optional[str]:
        common_paths = [
            r'C:\Program Files\Google\Chrome\Application\chrome.exe',
            r'C:\Program Files (x86)\Google\Chrome\Application\chrome.exe',
        ]
        for path in common_paths:
            if os.path.exists(path):
                return path
        return None

    def launch(self, url: str = 'about:blank') -> Dict:
        """Launch Chrome with optional URL"""
        try:
            if not self.exe_path:
                return {'success': False, 'error': 'Chrome not found'}

            subprocess.Popen([self.exe_path, url], shell=False)
            time.sleep(3)
            return {'success': True, 'action': 'chrome_launched', 'url': url}
        except Exception as e:
            logger.error(f"Chrome launch failed: {e}")
            return {'success': False, 'error': str(e)}

    def open_url(self, url: str) -> Dict:
        """Open URL in Chrome (or existing window)"""
        try:
            from ui_automator import get_ui_automator
            automator = get_ui_automator()

            # Try Ctrl+L to focus address bar
            automator.key_combo('ctrl', 'l')
            time.sleep(0.3)
            automator.type_text(url)
            automator.press_key('enter')
            time.sleep(2)

            return {'success': True, 'action': 'url_opened', 'url': url}
        except Exception as e:
            logger.error(f"Open URL failed: {e}")
            return {'success': False, 'error': str(e)}


_spotify = None
_youtube = None
_chrome = None


def get_spotify_automator() -> SpotifyAutomator:
    global _spotify
    if _spotify is None:
        _spotify = SpotifyAutomator()
    return _spotify


def get_youtube_automator() -> YouTubeAutomator:
    global _youtube
    if _youtube is None:
        _youtube = YouTubeAutomator()
    return _youtube


def get_chrome_automator() -> ChromeAutomator:
    global _chrome
    if _chrome is None:
        _chrome = ChromeAutomator()
    return _chrome

import subprocess
import time
from mouse_controller import MouseController
from keyboard_controller import KeyboardController

class SpotifyController:
    def __init__(self):
        self.mouse = MouseController()
        self.keyboard = KeyboardController()
        self.spotify_process = None
        
    def open_spotify(self):
        """Open Spotify desktop app"""
        try:
            subprocess.Popen('spotify')
            time.sleep(5)  # Wait for Spotify to load
            return {'success': True, 'action': 'spotify_opened'}
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def close_spotify(self):
        """Close Spotify app"""
        try:
            subprocess.run(['taskkill', '/IM', 'spotify.exe', '/F'], timeout=5)
            return {'success': True, 'action': 'spotify_closed'}
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def search_and_play(self, query):
        """Search for song and play"""
        try:
            # Open search with Ctrl+L
            self.keyboard.key_combo('ctrl', 'l')
            time.sleep(0.5)
            
            # Type search query
            self.keyboard.type_text(query, interval=0.05)
            time.sleep(0.5)
            
            # Press Enter to search
            self.keyboard.press_key('enter')
            time.sleep(1)
            
            # Press Enter again to play first result
            self.keyboard.press_key('enter')
            time.sleep(0.5)
            
            return {'success': True, 'action': 'play', 'query': query}
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def play_artist(self, artist_name):
        """Search and play artist"""
        try:
            query = f"artist:{artist_name}"
            return self.search_and_play(query)
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def play_album(self, artist_name, album_name):
        """Search and play album"""
        try:
            query = f"artist:{artist_name} album:{album_name}"
            return self.search_and_play(query)
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def play_playlist(self, playlist_name):
        """Search and play playlist"""
        try:
            self.keyboard.key_combo('ctrl', 'l')
            time.sleep(0.5)
            self.keyboard.type_text(f"playlist:{playlist_name}", interval=0.05)
            time.sleep(0.5)
            self.keyboard.press_key('enter')
            time.sleep(1)
            return {'success': True, 'action': 'playlist', 'playlist': playlist_name}
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def play_pause(self):
        """Toggle play/pause"""
        try:
            self.keyboard.press_key('space')
            return {'success': True, 'action': 'play_pause'}
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def next_track(self):
        """Skip to next track"""
        try:
            self.keyboard.key_combo('ctrl', 'right')
            return {'success': True, 'action': 'next_track'}
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def previous_track(self):
        """Go to previous track"""
        try:
            self.keyboard.key_combo('ctrl', 'left')
            return {'success': True, 'action': 'previous_track'}
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def volume_up(self):
        """Increase Spotify volume"""
        try:
            self.keyboard.key_combo('shift', 'up')
            return {'success': True, 'action': 'volume_up'}
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def volume_down(self):
        """Decrease Spotify volume"""
        try:
            self.keyboard.key_combo('shift', 'down')
            return {'success': True, 'action': 'volume_down'}
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def mute(self):
        """Mute Spotify"""
        try:
            self.keyboard.key_combo('shift', 'mute')
            return {'success': True, 'action': 'mute'}
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def like_track(self):
        """Like current track"""
        try:
            self.keyboard.key_combo('ctrl', 'l')
            return {'success': True, 'action': 'like_track'}
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def unlike_track(self):
        """Unlike current track"""
        try:
            self.keyboard.key_combo('ctrl', 'u')
            return {'success': True, 'action': 'unlike_track'}
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def queue_song(self, query):
        """Add song to queue"""
        try:
            self.keyboard.key_combo('ctrl', 'q')
            time.sleep(0.5)
            self.keyboard.type_text(query, interval=0.05)
            time.sleep(0.5)
            self.keyboard.press_key('enter')
            return {'success': True, 'action': 'queue_song', 'query': query}
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def repeat_mode(self):
        """Cycle repeat mode"""
        try:
            self.keyboard.key_combo('ctrl', 'h')
            return {'success': True, 'action': 'repeat_mode'}
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def shuffle_mode(self):
        """Toggle shuffle mode"""
        try:
            self.keyboard.key_combo('ctrl', 's')
            return {'success': True, 'action': 'shuffle_mode'}
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def focused_listening(self):
        """Enable focused listening mode"""
        try:
            # This would require API access, but Ctrl+I might work
            self.keyboard.key_combo('ctrl', 'i')
            return {'success': True, 'action': 'focused_listening'}
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def play_recommendation(self, mood='energetic'):
        """Play recommendation based on mood"""
        moods = {
            'energetic': 'energetic upbeat songs',
            'sad': 'sad emotional songs',
            'calm': 'calm relaxing songs',
            'workout': 'high energy workout songs',
            'focus': 'focus concentration songs',
            'party': 'party dance songs',
            'romantic': 'romantic love songs',
            'indie': 'indie alternative songs'
        }
        
        query = moods.get(mood.lower(), mood)
        
        try:
            return self.search_and_play(query)
        except Exception as e:
            return {'success': False, 'error': str(e)}

import pyautogui
import time

class KeyboardController:
    def __init__(self):
        pyautogui.FAILSAFE = False
        self.key_map = {
            'enter': 'return',
            'escape': 'esc',
            'delete': 'delete',
            'backspace': 'backspace',
            'tab': 'tab',
            'space': 'space',
            'capslock': 'capslock',
            'shift': 'shift',
            'ctrl': 'ctrl',
            'alt': 'alt',
            'win': 'win',
        }
        
    def type_text(self, text, interval=0.05):
        """Type text character by character"""
        try:
            pyautogui.write(text, interval=interval)
            return {'success': True, 'text': text}
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def press_key(self, key):
        """Press a single key"""
        try:
            key = self.key_map.get(key.lower(), key.lower())
            pyautogui.press(key)
            return {'success': True, 'key': key}
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def press_keys(self, keys, interval=0.1):
        """Press multiple keys sequentially"""
        try:
            for key in keys:
                key = self.key_map.get(key.lower(), key.lower())
                pyautogui.press(key)
                time.sleep(interval)
            return {'success': True, 'keys': keys}
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def key_down(self, key):
        """Hold key down"""
        try:
            key = self.key_map.get(key.lower(), key.lower())
            pyautogui.keyDown(key)
            return {'success': True, 'key': key, 'action': 'down'}
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def key_up(self, key):
        """Release key"""
        try:
            key = self.key_map.get(key.lower(), key.lower())
            pyautogui.keyUp(key)
            return {'success': True, 'key': key, 'action': 'up'}
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def key_combo(self, *keys):
        """Press key combination (e.g., Ctrl+C)"""
        try:
            mapped_keys = [self.key_map.get(k.lower(), k.lower()) for k in keys]
            
            # Press all keys down
            for key in mapped_keys:
                pyautogui.keyDown(key)
            
            time.sleep(0.1)
            
            # Release all keys
            for key in reversed(mapped_keys):
                pyautogui.keyUp(key)
            
            return {'success': True, 'combo': ' + '.join(mapped_keys)}
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def ctrl_c(self):
        """Press Ctrl+C"""
        return self.key_combo('ctrl', 'c')
    
    def ctrl_v(self):
        """Press Ctrl+V"""
        return self.key_combo('ctrl', 'v')
    
    def ctrl_x(self):
        """Press Ctrl+X"""
        return self.key_combo('ctrl', 'x')
    
    def ctrl_a(self):
        """Press Ctrl+A"""
        return self.key_combo('ctrl', 'a')
    
    def ctrl_z(self):
        """Press Ctrl+Z"""
        return self.key_combo('ctrl', 'z')
    
    def ctrl_y(self):
        """Press Ctrl+Y"""
        return self.key_combo('ctrl', 'y')
    
    def alt_tab(self):
        """Press Alt+Tab"""
        return self.key_combo('alt', 'tab')
    
    def alt_f4(self):
        """Press Alt+F4"""
        return self.key_combo('alt', 'f4')
    
    def win_key(self):
        """Press Windows key"""
        return self.press_key('win')
    
    def send_keys(self, key_sequence):
        """Send key sequence (space-separated keys)"""
        try:
            keys = key_sequence.split()
            return self.press_keys(keys)
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def clear_field(self):
        """Clear current field (Ctrl+A + Delete)"""
        try:
            self.key_combo('ctrl', 'a')
            time.sleep(0.1)
            self.press_key('delete')
            return {'success': True, 'action': 'clear_field'}
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def select_all(self):
        """Select all (Ctrl+A)"""
        return self.key_combo('ctrl', 'a')
    
    def copy(self):
        """Copy (Ctrl+C)"""
        return self.ctrl_c()
    
    def paste(self):
        """Paste (Ctrl+V)"""
        return self.ctrl_v()
    
    def cut(self):
        """Cut (Ctrl+X)"""
        return self.ctrl_x()
    
    def undo(self):
        """Undo (Ctrl+Z)"""
        return self.ctrl_z()
    
    def redo(self):
        """Redo (Ctrl+Y)"""
        return self.ctrl_y()
    
    def switch_window(self):
        """Switch window (Alt+Tab)"""
        return self.alt_tab()
    
    def close_window(self):
        """Close window (Alt+F4)"""
        return self.alt_f4()
    
    def open_run(self):
        """Open Run dialog (Win+R)"""
        return self.key_combo('win', 'r')
    
    def open_search(self):
        """Open Search (Win+S)"""
        return self.key_combo('win', 's')
    
    def lock_screen(self):
        """Lock screen (Win+L)"""
        return self.key_combo('win', 'l')
    
    def type_with_delay(self, text, delay=0.1):
        """Type text with custom delay between characters"""
        try:
            pyautogui.write(text, interval=delay)
            return {'success': True, 'text': text}
        except Exception as e:
            return {'success': False, 'error': str(e)}

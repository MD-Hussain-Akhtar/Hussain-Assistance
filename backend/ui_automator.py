import pyautogui
import time
from typing import Optional, Tuple
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('UIAutomator')


class UIAutomator:
    def __init__(self):
        pyautogui.FAILSAFE = True
        pyautogui.PAUSE = 0.05
        self.last_mouse_pos = (0, 0)

    def get_mouse_position(self) -> Tuple[int, int]:
        pos = pyautogui.position()
        self.last_mouse_pos = pos
        return pos

    def move_mouse(self, x: int, y: int, duration: float = 0.3, smooth: bool = True):
        """Move mouse to position smoothly"""
        try:
            if smooth:
                pyautogui.moveTo(x, y, duration=duration)
            else:
                pyautogui.moveTo(x, y)
            self.last_mouse_pos = (x, y)
            time.sleep(0.1)
            return {'success': True, 'x': x, 'y': y}
        except Exception as e:
            logger.error(f"Move mouse failed: {e}")
            return {'success': False, 'error': str(e)}

    def click(self, x: int, y: int, button: str = 'left', delay: float = 0.1):
        """Click at position"""
        try:
            pyautogui.click(x, y, button=button)
            time.sleep(delay)
            return {'success': True, 'action': 'click', 'x': x, 'y': y}
        except Exception as e:
            logger.error(f"Click failed: {e}")
            return {'success': False, 'error': str(e)}

    def double_click(self, x: int, y: int, delay: float = 0.1):
        """Double-click at position"""
        try:
            pyautogui.doubleClick(x, y)
            time.sleep(delay)
            return {'success': True, 'action': 'double_click', 'x': x, 'y': y}
        except Exception as e:
            logger.error(f"Double-click failed: {e}")
            return {'success': False, 'error': str(e)}

    def right_click(self, x: int, y: int, delay: float = 0.1):
        """Right-click at position"""
        try:
            pyautogui.click(x, y, button='right')
            time.sleep(delay)
            return {'success': True, 'action': 'right_click', 'x': x, 'y': y}
        except Exception as e:
            logger.error(f"Right-click failed: {e}")
            return {'success': False, 'error': str(e)}

    def drag_and_drop(self, x1: int, y1: int, x2: int, y2: int, duration: float = 0.5):
        """Drag from (x1,y1) to (x2,y2)"""
        try:
            pyautogui.drag(x2 - x1, y2 - y1, duration=duration, button='left')
            time.sleep(0.1)
            return {'success': True, 'action': 'drag', 'from': (x1, y1), 'to': (x2, y2)}
        except Exception as e:
            logger.error(f"Drag failed: {e}")
            return {'success': False, 'error': str(e)}

    def scroll(self, x: int, y: int, direction: str = 'down', amount: int = 5):
        """Scroll at position"""
        try:
            pyautogui.moveTo(x, y)
            if direction.lower() == 'down':
                pyautogui.scroll(-amount)
            elif direction.lower() == 'up':
                pyautogui.scroll(amount)
            time.sleep(0.2)
            return {'success': True, 'action': 'scroll', 'direction': direction, 'amount': amount}
        except Exception as e:
            logger.error(f"Scroll failed: {e}")
            return {'success': False, 'error': str(e)}

    def type_text(self, text: str, interval: float = 0.05):
        """Type text character by character"""
        try:
            for char in text:
                pyautogui.typewrite(char)
                time.sleep(interval)
            time.sleep(0.1)
            return {'success': True, 'action': 'type', 'text': text[:50]}
        except Exception as e:
            logger.error(f"Type text failed: {e}")
            return {'success': False, 'error': str(e)}

    def type_text_fast(self, text: str):
        """Type text fast using clipboard"""
        try:
            import subprocess
            # Copy to clipboard (Windows)
            p = subprocess.Popen(['clip'], stdin=subprocess.PIPE, shell=True)
            p.communicate(text.encode('utf-8'))
            # Paste
            pyautogui.hotkey('ctrl', 'v')
            time.sleep(0.2)
            return {'success': True, 'action': 'type_fast', 'text': text[:50]}
        except Exception as e:
            logger.error(f"Type text fast failed: {e}")
            return {'success': False, 'error': str(e)}

    def press_key(self, key: str):
        """Press a single key"""
        try:
            pyautogui.press(key)
            time.sleep(0.05)
            return {'success': True, 'action': 'press_key', 'key': key}
        except Exception as e:
            logger.error(f"Press key failed: {e}")
            return {'success': False, 'error': str(e)}

    def key_combo(self, *keys):
        """Press key combination (e.g., ctrl+c, alt+tab)"""
        try:
            pyautogui.hotkey(*keys)
            time.sleep(0.1)
            return {'success': True, 'action': 'key_combo', 'keys': keys}
        except Exception as e:
            logger.error(f"Key combo failed: {e}")
            return {'success': False, 'error': str(e)}

    def click_on_text(self, text_box, offset_x: int = 0, offset_y: int = 0):
        """Click on a text box returned by vision analyzer"""
        try:
            x = text_box.cx + offset_x
            y = text_box.cy + offset_y
            return self.click(x, y)
        except Exception as e:
            logger.error(f"Click on text failed: {e}")
            return {'success': False, 'error': str(e)}

    def fill_input_field(self, text_box, text: str, clear: bool = True):
        """Click on input field and fill with text"""
        try:
            self.click(text_box.cx, text_box.cy)
            time.sleep(0.2)
            if clear:
                self.key_combo('ctrl', 'a')
                time.sleep(0.05)
            self.type_text(text)
            return {'success': True, 'action': 'fill_field', 'text': text[:50]}
        except Exception as e:
            logger.error(f"Fill input field failed: {e}")
            return {'success': False, 'error': str(e)}


_automator = None


def get_ui_automator() -> UIAutomator:
    global _automator
    if _automator is None:
        _automator = UIAutomator()
    return _automator

import pyautogui
import time
import math

class MouseController:
    def __init__(self):
        pyautogui.FAILSAFE = False
        self.speed = 0.5  # Movement speed multiplier
        self.current_x = 0
        self.current_y = 0
        self._update_position()
        
    def _update_position(self):
        """Update current mouse position"""
        self.current_x, self.current_y = pyautogui.position()
    
    def move_mouse(self, x, y, duration=0.5, smooth=True):
        """Move mouse to absolute position"""
        try:
            if smooth:
                pyautogui.moveTo(x, y, duration=duration * self.speed)
            else:
                pyautogui.moveTo(x, y)
            self._update_position()
            return {'success': True, 'x': x, 'y': y}
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def move_relative(self, dx, dy, duration=0.5, smooth=True):
        """Move mouse relative to current position"""
        try:
            new_x = self.current_x + dx
            new_y = self.current_y + dy
            
            if smooth:
                pyautogui.moveTo(new_x, new_y, duration=duration * self.speed)
            else:
                pyautogui.moveTo(new_x, new_y)
            
            self._update_position()
            return {'success': True, 'x': new_x, 'y': new_y}
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def move_up(self, pixels=50, duration=0.5):
        """Move cursor up"""
        return self.move_relative(0, -pixels, duration)
    
    def move_down(self, pixels=50, duration=0.5):
        """Move cursor down"""
        return self.move_relative(0, pixels, duration)
    
    def move_left(self, pixels=50, duration=0.5):
        """Move cursor left"""
        return self.move_relative(-pixels, 0, duration)
    
    def move_right(self, pixels=50, duration=0.5):
        """Move cursor right"""
        return self.move_relative(pixels, 0, duration)
    
    def click(self, x=None, y=None, button='left', clicks=1, interval=0.1):
        """Click mouse button"""
        try:
            if x is not None and y is not None:
                self.move_mouse(x, y, duration=0.2)
            
            pyautogui.click(button=button, clicks=clicks, interval=interval)
            return {'success': True, 'action': 'click', 'button': button}
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def double_click(self, x=None, y=None, interval=0.1):
        """Double click"""
        try:
            if x is not None and y is not None:
                self.move_mouse(x, y, duration=0.2)
            
            pyautogui.click(clicks=2, interval=interval)
            return {'success': True, 'action': 'double_click'}
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def right_click(self, x=None, y=None):
        """Right click"""
        try:
            if x is not None and y is not None:
                self.move_mouse(x, y, duration=0.2)
            
            pyautogui.rightClick()
            return {'success': True, 'action': 'right_click'}
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def drag(self, x, y, duration=0.5, button='left'):
        """Drag mouse from current position to x, y"""
        try:
            pyautogui.drag(x, y, duration=duration * self.speed, button=button)
            self._update_position()
            return {'success': True, 'action': 'drag'}
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def drag_to(self, x, y, duration=0.5, button='left'):
        """Drag to absolute position"""
        try:
            pyautogui.drag(
                x - self.current_x, 
                y - self.current_y, 
                duration=duration * self.speed, 
                button=button
            )
            self._update_position()
            return {'success': True, 'action': 'drag_to', 'x': x, 'y': y}
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def scroll(self, amount=5, x=None, y=None):
        """Scroll up (positive) or down (negative)"""
        try:
            if x is not None and y is not None:
                pyautogui.moveTo(x, y)
                self._update_position()
            
            pyautogui.scroll(amount)
            return {'success': True, 'action': 'scroll', 'amount': amount}
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def scroll_up(self, amount=5):
        """Scroll up"""
        return self.scroll(amount=amount)
    
    def scroll_down(self, amount=5):
        """Scroll down"""
        return self.scroll(amount=-amount)
    
    def get_position(self):
        """Get current mouse position"""
        self._update_position()
        return {'x': self.current_x, 'y': self.current_y}
    
    def set_speed(self, speed):
        """Set movement speed (0.1 - 2.0)"""
        self.speed = max(0.1, min(2.0, speed))
        return {'speed': self.speed}
    
    def move_to_center(self):
        """Move to center of screen"""
        try:
            screen_width, screen_height = pyautogui.size()
            center_x = screen_width // 2
            center_y = screen_height // 2
            return self.move_mouse(center_x, center_y)
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def move_to_corner(self, corner='top-left'):
        """Move to screen corner"""
        try:
            screen_width, screen_height = pyautogui.size()
            
            corners = {
                'top-left': (0, 0),
                'top-right': (screen_width - 1, 0),
                'bottom-left': (0, screen_height - 1),
                'bottom-right': (screen_width - 1, screen_height - 1),
            }
            
            x, y = corners.get(corner, (0, 0))
            return self.move_mouse(x, y)
        except Exception as e:
            return {'success': False, 'error': str(e)}

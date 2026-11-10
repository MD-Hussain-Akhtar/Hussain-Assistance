import mss
import base64
import io
from PIL import Image
import time

class ScreenCapture:
    def __init__(self):
        self.sct = mss.mss()
        self.last_frame = None
        
    def capture_screen(self, monitor=1):
        """Capture screen as PIL Image"""
        try:
            monitor_info = self.sct.monitors[monitor]
            screenshot = self.sct.grab(monitor_info)
            
            img = Image.frombytes('RGB', screenshot.size, screenshot.rgb)
            self.last_frame = img
            return img
        except Exception as e:
            print(f"Error capturing screen: {e}")
            return None
    
    def capture_to_base64(self, monitor=1):
        """Capture screen and return as base64"""
        try:
            img = self.capture_screen(monitor)
            if not img:
                return None
            
            buffered = io.BytesIO()
            img.save(buffered, format="JPEG", quality=85)
            img_str = base64.b64encode(buffered.getvalue()).decode()
            return img_str
        except Exception as e:
            print(f"Error converting to base64: {e}")
            return None
    
    def capture_to_bytes(self, monitor=1):
        """Capture screen as bytes"""
        try:
            img = self.capture_screen(monitor)
            if not img:
                return None
            
            buffered = io.BytesIO()
            img.save(buffered, format="JPEG", quality=85)
            return buffered.getvalue()
        except Exception as e:
            print(f"Error capturing to bytes: {e}")
            return None
    
    def get_active_window(self):
        """Get active window name (Windows specific)"""
        try:
            import pygetwindow
            window = pygetwindow.getActiveWindow()
            if window:
                return window.title
            return None
        except:
            try:
                import ctypes
                hwnd = ctypes.windll.user32.GetForegroundWindow()
                length = ctypes.windll.user32.GetWindowTextLength(hwnd)
                buff = ctypes.create_unicode_buffer(length + 1)
                ctypes.windll.user32.GetWindowText(hwnd, buff, length + 1)
                return buff.value
            except:
                return None
    
    def get_all_monitors(self):
        """Get list of all monitors"""
        return self.sct.monitors[1:]  # Skip monitor 0 (virtual combined)
    
    def continuous_capture(self, interval=0.5, callback=None):
        """Capture screen continuously"""
        try:
            while True:
                frame = self.capture_screen()
                if callback:
                    callback(frame)
                time.sleep(interval)
        except KeyboardInterrupt:
            print("Capture stopped")
    
    def capture_region(self, x, y, width, height):
        """Capture specific region of screen"""
        try:
            monitor = {
                'top': y,
                'left': x,
                'width': width,
                'height': height
            }
            screenshot = self.sct.grab(monitor)
            img = Image.frombytes('RGB', screenshot.size, screenshot.rgb)
            return img
        except Exception as e:
            print(f"Error capturing region: {e}")
            return None
    
    def save_screenshot(self, filepath):
        """Save last captured screenshot"""
        if self.last_frame:
            self.last_frame.save(filepath)
            return True
        return False

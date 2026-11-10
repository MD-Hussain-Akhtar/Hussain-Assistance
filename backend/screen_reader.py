"""Screen reader utilities: capture screen and perform OCR.

This module provides a single `ScreenReader` class with a `read_screen`
method that captures the screen (or a region) and returns extracted text
via Tesseract OCR. It also includes a few small helpers used elsewhere
in the backend. All operations are best-effort and return safe defaults
on failure so imports won't crash the server.
"""

import io
import time
import os
from typing import Optional, Dict, Any
from PIL import Image
import mss
import pytesseract


class ScreenReader:
    def __init__(self, tesseract_path: Optional[str] = None):
        """Initialize ScreenReader.

        tesseract_path: optional path to tesseract executable. If omitted,
        the module will rely on system PATH.
        """
        if tesseract_path and os.path.exists(tesseract_path):
            pytesseract.pytesseract.tesseract_cmd = tesseract_path

        # mss instance used for grabbing the screen
        try:
            self.sct = mss.mss()
        except Exception:
            self.sct = None

    def _get_monitor(self, region: Optional[Dict[str, int]] = None) -> Optional[Dict[str, int]]:
        if not self.sct:
            return None
        if region:
            return {
                "left": int(region.get("left", 0)),
                "top": int(region.get("top", 0)),
                "width": int(region.get("width", 0)),
                "height": int(region.get("height", 0)),
            }
        # primary monitor
        try:
            return self.sct.monitors[0]
        except Exception:
            return None

    def read_screen(self, region: Optional[Dict[str, int]] = None) -> Dict[str, Any]:
        """Capture the screen (or a region) and return OCR text.

        Returns: {success: bool, text: str} or {success: False, error: str}
        """
        try:
            monitor = self._get_monitor(region)
            if not monitor:
                return {"success": False, "error": "screen capture unavailable"}

            sshot = self.sct.grab(monitor)
            img = Image.frombytes("RGB", sshot.size, sshot.rgb)

            # small delay to stabilize capture on some systems
            time.sleep(0.12)

            text = pytesseract.image_to_string(img)
            return {"success": True, "text": text.strip()}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def capture_image_bytes(self, region: Optional[Dict[str, int]] = None) -> Optional[bytes]:
        """Return a PNG-encoded bytes of the captured region (or None on failure)."""
        try:
            monitor = self._get_monitor(region)
            if not monitor:
                return None

            sshot = self.sct.grab(monitor)
            img = Image.frombytes("RGB", sshot.size, sshot.rgb)
            buf = io.BytesIO()
            img.save(buf, format="PNG")
            return buf.getvalue()
        except Exception:
            return None

    def get_active_window_info(self) -> Dict[str, str]:
        """Best-effort: return active window title/process name."""
        try:
            import pygetwindow as gw

            window = gw.getActiveWindow()
            if not window:
                return {"title": "Unknown", "process": "Unknown"}

            title = window.title or ""
            process = "Unknown"
            if "-" in title:
                process = title.split("-")[-1].strip()

            return {"title": title, "process": process}
        except Exception:
            return {"title": "Unknown", "process": "Unknown"}

    def get_active_browser_url(self) -> Optional[str]:
        """Attempt to OCR the top part of the active window to find a URL.

        This is a best-effort helper and may return None if not available.
        """
        try:
            from PIL import ImageGrab

            info = self.get_active_window_info()
            title = info.get("title", "").lower()
            if not title:
                return None

            # only attempt for common browsers
            if "chrome" not in title and "edge" not in title and "firefox" not in title:
                return None

            # capture a thin strip from the top of the active window (best-effort)
            try:
                import pygetwindow as gw

                w = gw.getActiveWindow()
                if not w:
                    return None
                left, top, right = w.left, w.top, w.right
                bbox = (left, top, right, top + 80)
                img = ImageGrab.grab(bbox=bbox)
            except Exception:
                return None

            text = pytesseract.image_to_string(img)
            if "http" in text:
                for line in text.splitlines():
                    if "http" in line:
                        return line.strip()
            return None
        except Exception:
            return None


_reader: Optional[ScreenReader] = None


def get_screen_reader() -> ScreenReader:
    global _reader
    if _reader is None:
        _reader = ScreenReader()
    return _reader

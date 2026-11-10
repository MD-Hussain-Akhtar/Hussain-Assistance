"""Minimal screen reader: capture primary monitor and OCR using pytesseract."""
import time
import os
from typing import Optional, Dict
from PIL import Image
import mss
import pytesseract


class ScreenReader:
    def __init__(self, tesseract_path: Optional[str] = None):
        if tesseract_path and os.path.exists(tesseract_path):
            pytesseract.pytesseract.tesseract_cmd = tesseract_path
        self.sct = mss.mss()

    def read_screen(self, region: Optional[Dict[str, int]] = None) -> Dict:
        try:
            if region:
                monitor = {
                    "left": int(region.get("left", 0)),
                    "top": int(region.get("top", 0)),
                    "width": int(region.get("width", 0)),
                    "height": int(region.get("height", 0)),
                }
            else:
                monitor = self.sct.monitors[0]

            sshot = self.sct.grab(monitor)
            img = Image.frombytes("RGB", sshot.size, sshot.rgb)
            time.sleep(0.12)
            text = pytesseract.image_to_string(img)
            return {"success": True, "text": text.strip()}
        except Exception as e:
            return {"success": False, "error": str(e)}


_reader = None


def get_screen_reader() -> ScreenReader:
    global _reader
    if _reader is None:
        _reader = ScreenReader()
    return _reader

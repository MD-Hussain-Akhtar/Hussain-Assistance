import pytesseract
import cv2
from PIL import Image, ImageDraw
import mss
import numpy as np
from typing import List, Dict, Tuple, Optional
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('VisionAnalyzer')


class TextBox:
    def __init__(self, text: str, x: int, y: int, w: int, h: int, confidence: float):
        self.text = text
        self.x = x
        self.y = y
        self.w = w
        self.h = h
        self.confidence = confidence
        self.cx = x + w // 2
        self.cy = y + h // 2

    def contains_point(self, px: int, py: int) -> bool:
        return self.x <= px <= self.x + self.w and self.y <= py <= self.y + self.h

    def to_dict(self) -> dict:
        return {
            'text': self.text,
            'x': self.x, 'y': self.y, 'w': self.w, 'h': self.h,
            'cx': self.cx, 'cy': self.cy,
            'confidence': self.confidence
        }


class VisionAnalyzer:
    def __init__(self):
        self.sct = mss.mss()
        self.last_screenshot = None
        self.last_boxes = []

    def capture_screen(self) -> Optional[np.ndarray]:
        try:
            mon = self.sct.monitors[1]
            screenshot = self.sct.grab(mon)
            img = np.array(screenshot)
            img = cv2.cvtColor(img, cv2.COLOR_BGRA2BGR)
            self.last_screenshot = img
            return img
        except Exception as e:
            logger.error(f"Capture failed: {e}")
            return None

    def extract_text_boxes(self, image: Optional[np.ndarray] = None) -> List[TextBox]:
        """Extract text and their bounding boxes using pytesseract"""
        if image is None:
            image = self.last_screenshot
        if image is None:
            image = self.capture_screen()
        if image is None:
            return []

        try:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            data = pytesseract.image_to_data(gray, output_type=pytesseract.Output.DICT)

            boxes = []
            for i in range(len(data['text'])):
                if int(data['conf'][i]) > 30:
                    text = data['text'][i].strip()
                    if text:
                        box = TextBox(
                            text=text,
                            x=int(data['left'][i]),
                            y=int(data['top'][i]),
                            w=int(data['width'][i]),
                            h=int(data['height'][i]),
                            confidence=float(data['conf'][i]) / 100.0
                        )
                        boxes.append(box)

            self.last_boxes = boxes
            return boxes
        except Exception as e:
            logger.error(f"OCR extraction failed: {e}")
            return []

    def find_text(self, keyword: str, exact: bool = False) -> Optional[TextBox]:
        """Find a text box containing keyword"""
        if not self.last_boxes:
            self.extract_text_boxes()

        keyword_lower = keyword.lower()
        for box in self.last_boxes:
            text_lower = box.text.lower()
            if exact:
                if text_lower == keyword_lower:
                    return box
            else:
                if keyword_lower in text_lower:
                    return box
        return None

    def find_all_text(self, keyword: str) -> List[TextBox]:
        """Find all text boxes containing keyword"""
        if not self.last_boxes:
            self.extract_text_boxes()

        keyword_lower = keyword.lower()
        results = []
        for box in self.last_boxes:
            if keyword_lower in box.text.lower():
                results.append(box)
        return results

    def detect_buttons(self) -> List[Dict]:
        """Detect clickable button-like regions"""
        if self.last_screenshot is None:
            self.capture_screen()

        buttons = []
        for box in self.last_boxes:
            if box.h >= 20 and box.w >= 40:
                if any(kw in box.text.lower() for kw in ['ok', 'yes', 'no', 'cancel', 'submit', 'login', 'sign', 'next', 'skip', 'close', 'save']):
                    buttons.append({
                        'text': box.text,
                        'x': box.cx,
                        'y': box.cy,
                        'rect': (box.x, box.y, box.w, box.h)
                    })
        return buttons

    def find_input_field(self, label: Optional[str] = None) -> Optional[TextBox]:
        """Find input field, optionally by label"""
        if not self.last_boxes:
            self.extract_text_boxes()

        for i, box in enumerate(self.last_boxes):
            if label:
                if label.lower() in box.text.lower():
                    if i + 1 < len(self.last_boxes):
                        return self.last_boxes[i + 1]
            if any(kw in box.text.lower() for kw in ['email', 'password', 'username', 'search', 'query', 'input']):
                return box

        return None

    def describe_screen(self) -> Dict:
        """Analyze screen and return description"""
        if self.last_screenshot is None:
            self.capture_screen()

        boxes = self.extract_text_boxes()
        buttons = self.detect_buttons()

        text_content = ' '.join([b.text for b in boxes])[:500]

        return {
            'text_count': len(boxes),
            'button_count': len(buttons),
            'text_content': text_content,
            'buttons': buttons,
            'boxes': [b.to_dict() for b in boxes[:20]]
        }

    def draw_boxes(self, output_path: str = 'screen_marked.png', highlight_text: Optional[str] = None):
        """Draw OCR boxes on screenshot for debugging"""
        if self.last_screenshot is None:
            return

        img = self.last_screenshot.copy()

        for box in self.last_boxes:
            color = (0, 255, 0)
            if highlight_text and highlight_text.lower() in box.text.lower():
                color = (0, 0, 255)

            cv2.rectangle(img, (box.x, box.y), (box.x + box.w, box.y + box.h), color, 1)
            cv2.putText(img, box.text[:15], (box.x, box.y - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.4, color, 1)

        cv2.imwrite(output_path, img)
        logger.info(f"Marked screenshot saved to {output_path}")


_analyzer = None


def get_vision_analyzer() -> VisionAnalyzer:
    global _analyzer
    if _analyzer is None:
        _analyzer = VisionAnalyzer()
    return _analyzer

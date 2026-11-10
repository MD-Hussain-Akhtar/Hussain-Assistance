"""
Camera Module: Capture video frames from webcam and provide descriptions.
This replaces Tesseract-based screen reading with real camera vision.
"""

import cv2
import numpy as np
import logging
from typing import Optional, Dict, Tuple
from datetime import datetime
import threading

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('CameraModule')


class CameraModule:
    """Real-time camera capture and frame analysis."""
    
    def __init__(self, camera_index: int = 0):
        """Initialize camera with index (0 = default camera)."""
        self.camera_index = camera_index
        self.cap = None
        self.last_frame = None
        self.is_running = False
        self.frame_lock = threading.Lock()
        self.initialized = False
        
    def initialize(self) -> bool:
        """Initialize camera connection."""
        try:
            self.cap = cv2.VideoCapture(self.camera_index)
            if not self.cap.isOpened():
                logger.error(f"Failed to open camera at index {self.camera_index}")
                return False
            
            # Set resolution
            self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
            self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
            self.cap.set(cv2.CAP_PROP_FPS, 30)
            
            # Read first frame to verify
            ret, frame = self.cap.read()
            if ret:
                with self.frame_lock:
                    self.last_frame = frame
                logger.info("✅ Camera initialized successfully")
                self.initialized = True
                return True
            return False
        except Exception as e:
            logger.error(f"Camera initialization error: {e}")
            return False
    
    def capture_frame(self) -> Optional[np.ndarray]:
        """Capture single frame from camera."""
        try:
            if not self.cap or not self.cap.isOpened():
                self.initialize()
            
            ret, frame = self.cap.read()
            if ret:
                with self.frame_lock:
                    self.last_frame = frame
                return frame
            return None
        except Exception as e:
            logger.error(f"Frame capture error: {e}")
            return None
    
    def get_last_frame(self) -> Optional[np.ndarray]:
        """Get last captured frame."""
        with self.frame_lock:
            return self.last_frame.copy() if self.last_frame is not None else None
    
    def analyze_frame(self, frame: Optional[np.ndarray] = None) -> Dict:
        """Analyze frame and extract features."""
        if frame is None:
            frame = self.capture_frame()
        
        if frame is None:
            return {
                'success': False,
                'error': 'No frame available',
                'description': 'Camera not responding'
            }
        
        try:
            analysis = {
                'success': True,
                'timestamp': datetime.now().isoformat(),
                'frame_shape': frame.shape,
                'brightness': self._analyze_brightness(frame),
                'edges': self._count_edges(frame),
                'color_distribution': self._analyze_colors(frame),
                'motion_potential': self._detect_motion(frame),
            }
            
            # Generate natural description
            description = self._generate_description(analysis)
            analysis['description'] = description
            
            return analysis
        except Exception as e:
            logger.error(f"Frame analysis error: {e}")
            return {
                'success': False,
                'error': str(e),
                'description': f'Analysis failed: {str(e)}'
            }
    
    def _analyze_brightness(self, frame: np.ndarray) -> Dict:
        """Analyze brightness levels."""
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        brightness = np.mean(gray)
        return {
            'level': brightness,
            'status': 'bright' if brightness > 150 else 'dark' if brightness < 100 else 'moderate'
        }
    
    def _count_edges(self, frame: np.ndarray) -> Dict:
        """Detect edges and count activity."""
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        edges = cv2.Canny(gray, 100, 200)
        edge_count = np.count_nonzero(edges)
        return {
            'count': int(edge_count),
            'density': float(edge_count / edges.size),
            'activity': 'high' if edge_count > 50000 else 'moderate' if edge_count > 20000 else 'low'
        }
    
    def _analyze_colors(self, frame: np.ndarray) -> Dict:
        """Analyze color distribution."""
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        h, s, v = cv2.split(hsv)
        
        return {
            'dominant_hue': int(np.mean(h)),
            'saturation': float(np.mean(s) / 255),
            'brightness': float(np.mean(v) / 255),
        }
    
    def _detect_motion(self, frame: np.ndarray) -> Dict:
        """Detect if there's motion in frame."""
        if self.last_frame is None:
            return {'detected': False, 'confidence': 0}
        
        try:
            diff = cv2.absdiff(self.last_frame, frame)
            gray_diff = cv2.cvtColor(diff, cv2.COLOR_BGR2GRAY)
            motion_pixels = np.count_nonzero(gray_diff > 30)
            motion_percentage = (motion_pixels / gray_diff.size) * 100
            
            return {
                'detected': motion_percentage > 5,
                'percentage': float(motion_percentage),
                'confidence': min(motion_percentage / 20, 1.0)
            }
        except Exception:
            return {'detected': False, 'confidence': 0}
    
    def _generate_description(self, analysis: Dict) -> str:
        """Generate natural language description of frame."""
        parts = []
        
        # Brightness description
        brightness = analysis.get('brightness', {}).get('status', 'unknown')
        if brightness == 'bright':
            parts.append("Yaha bahot aiyajala h")  # It's very bright here
        elif brightness == 'dark':
            parts.append("Yaha kaafi andhera h")  # It's quite dark here
        else:
            parts.append("Normal chamak h")  # Normal lighting
        
        # Activity description
        activity = analysis.get('edges', {}).get('activity', 'low')
        if activity == 'high':
            parts.append("bohat kuch chal raha h")  # A lot is happening
        elif activity == 'moderate':
            parts.append("kuch activity h")  # Some activity
        else:
            parts.append("sab shant h")  # Everything is calm
        
        # Motion detection
        motion = analysis.get('motion_potential', {}).get('detected', False)
        if motion:
            parts.append("motion dekh raha hu")  # I see motion
        
        description = ", ".join(parts)
        return description if description else "Camera feed normal hai"  # Camera feed is normal
    
    def describe_scene(self) -> Dict:
        """Complete scene description with all details."""
        frame = self.capture_frame()
        if frame is None:
            return {
                'success': False,
                'error': 'Camera not available',
                'description': 'Camera se connect nahi ho paya'
            }
        
        return self.analyze_frame(frame)
    
    def close(self):
        """Close camera connection."""
        if self.cap:
            self.cap.release()
            logger.info("Camera closed")
    
    def __del__(self):
        """Cleanup on deletion."""
        self.close()


# Global camera instance
_camera = None


def get_camera_module() -> CameraModule:
    """Get or create singleton camera module."""
    global _camera
    if _camera is None:
        _camera = CameraModule()
        _camera.initialize()
    return _camera


def describe_camera_view() -> Dict:
    """Quick function to describe what camera sees."""
    camera = get_camera_module()
    return camera.describe_scene()

"""
Face Expression Analysis
Detects emotion from facial expressions using MediaPipe Face Landmarker.
"""

import logging
import numpy as np
from typing import Tuple, Optional
from collections import deque

logger = logging.getLogger("FACE_EMOTION")


class FaceEmotionDetector:
    """Detects emotion from facial expressions."""
    
    # Face landmark indices (MediaPipe)
    MOUTH_LEFT = 61
    MOUTH_RIGHT = 291
    MOUTH_TOP = 13
    MOUTH_BOTTOM = 14
    
    LEFT_EYE_LEFT = 33
    LEFT_EYE_RIGHT = 133
    LEFT_EYE_TOP = 159
    LEFT_EYE_BOTTOM = 145
    
    RIGHT_EYE_LEFT = 362
    RIGHT_EYE_RIGHT = 263
    RIGHT_EYE_TOP = 386
    RIGHT_EYE_BOTTOM = 374
    
    LEFT_BROW_INNER = 105
    LEFT_BROW_OUTER = 33
    RIGHT_BROW_INNER = 334
    RIGHT_BROW_OUTER = 263
    
    def __init__(self, smoothing_window: int = 5):
        """
        Initialize face emotion detector.
        
        Args:
            smoothing_window: Number of frames to smooth over
        """
        self.smoothing_window = smoothing_window
        self.emotion_history = deque(maxlen=smoothing_window)
        self.last_emotion = "neutral"
        self.last_confidence = 0.0
    
    def analyze_face(self, face_landmarks) -> Tuple[str, float]:
        """
        Analyze face landmarks for emotion.
        
        Args:
            face_landmarks: MediaPipe face landmarks (478 points)
        
        Returns:
            Tuple of (emotion, confidence) where confidence is 0.0-1.0
        """
        try:
            if face_landmarks is None or len(face_landmarks) < 478:
                return "neutral", 0.0
            
            # Extract facial measurements
            mouth_openness = self._calculate_mouth_openness(face_landmarks)
            mouth_shape = self._calculate_mouth_shape(face_landmarks)
            eye_openness_left = self._calculate_eye_openness(face_landmarks, 'left')
            eye_openness_right = self._calculate_eye_openness(face_landmarks, 'right')
            brow_position = self._calculate_brow_position(face_landmarks)
            
            eye_openness = (eye_openness_left + eye_openness_right) / 2
            
            # Classify emotion
            emotion, confidence = self._classify_emotion(
                mouth_openness, mouth_shape, eye_openness, brow_position
            )
            
            # Smooth with history
            self.emotion_history.append((emotion, confidence))
            smoothed_emotion, smoothed_confidence = self._smooth_emotion()
            
            self.last_emotion = smoothed_emotion
            self.last_confidence = smoothed_confidence
            
            logger.debug(
                f"Face analysis: mouth={mouth_openness:.2f}, "
                f"eyes={eye_openness:.2f}, brow={brow_position:.2f} "
                f"→ {emotion} ({confidence:.2f})"
            )
            
            return smoothed_emotion, smoothed_confidence
            
        except Exception as e:
            logger.warning(f"Face emotion analysis error: {e}")
            return "neutral", 0.0
    
    def _calculate_mouth_openness(self, landmarks) -> float:
        """Calculate how open the mouth is (0-1)."""
        try:
            top = landmarks[self.MOUTH_TOP]
            bottom = landmarks[self.MOUTH_BOTTOM]
            
            # Distance between top and bottom of mouth
            distance = np.sqrt((top[0] - bottom[0])**2 + (top[1] - bottom[1])**2)
            
            # Normalize (typical range 0.005-0.05)
            openness = np.clip(distance / 0.05, 0, 1)
            return openness
            
        except Exception:
            return 0.0
    
    def _calculate_mouth_shape(self, landmarks) -> float:
        """
        Calculate mouth shape.
        Returns: positive for smile, negative for frown, 0 for neutral
        """
        try:
            # Left and right mouth corners
            left = landmarks[self.MOUTH_LEFT]
            right = landmarks[self.MOUTH_RIGHT]
            top = landmarks[self.MOUTH_TOP]
            
            # Calculate angle from mouth center to corners
            center_x = (left[0] + right[0]) / 2
            center_y = (left[1] + right[1]) / 2
            
            left_angle = np.arctan2(left[1] - center_y, left[0] - center_x)
            right_angle = np.arctan2(right[1] - center_y, right[0] - center_x)
            top_angle = np.arctan2(top[1] - center_y, top[0] - center_x)
            
            # Smile: corners go up (positive angle)
            # Frown: corners go down (negative angle)
            smile_score = (left_angle + right_angle) / 2
            
            # Normalize to -1 to 1 range
            smile_normalized = np.clip(smile_score / 1.5, -1, 1)
            
            return smile_normalized
            
        except Exception:
            return 0.0
    
    def _calculate_eye_openness(self, landmarks, eye: str) -> float:
        """
        Calculate how open an eye is (0-1).
        
        Args:
            eye: 'left' or 'right'
        """
        try:
            if eye == 'left':
                top = landmarks[self.LEFT_EYE_TOP]
                bottom = landmarks[self.LEFT_EYE_BOTTOM]
                left = landmarks[self.LEFT_EYE_LEFT]
                right = landmarks[self.LEFT_EYE_RIGHT]
            else:  # right
                top = landmarks[self.RIGHT_EYE_TOP]
                bottom = landmarks[self.RIGHT_EYE_BOTTOM]
                left = landmarks[self.RIGHT_EYE_LEFT]
                right = landmarks[self.RIGHT_EYE_RIGHT]
            
            # Vertical distance (openness)
            vertical = np.sqrt((top[0] - bottom[0])**2 + (top[1] - bottom[1])**2)
            
            # Horizontal distance (width)
            horizontal = np.sqrt((left[0] - right[0])**2 + (left[1] - right[1])**2)
            
            # Eye aspect ratio (typical range 0.1-0.3)
            if horizontal > 0:
                ratio = vertical / horizontal
                openness = np.clip(ratio / 0.3, 0, 1)
                return openness
            
            return 0.5
            
        except Exception:
            return 0.5
    
    def _calculate_brow_position(self, landmarks) -> float:
        """
        Calculate brow position.
        Returns: positive for raised brows (surprised), negative for furrowed (angry/sad)
        """
        try:
            left_inner = landmarks[self.LEFT_BROW_INNER]
            left_outer = landmarks[self.LEFT_BROW_OUTER]
            right_inner = landmarks[self.RIGHT_BROW_INNER]
            right_outer = landmarks[self.RIGHT_BROW_OUTER]
            
            # Y position of brows (lower = raised, higher = furrowed)
            left_y = (left_inner[1] + left_outer[1]) / 2
            right_y = (right_inner[1] + right_outer[1]) / 2
            avg_brow_y = (left_y + right_y) / 2
            
            # Typical range: 0.1-0.3 (normalized coordinates)
            # Raised: 0.1 (low y), Furrowed: 0.3 (high y)
            brow_position = np.clip((avg_brow_y - 0.1) / 0.2, 0, 1)
            
            # Convert to -1 to 1 (negative = raised, positive = furrowed)
            return (1 - brow_position) * 2 - 1
            
        except Exception:
            return 0.0
    
    def _classify_emotion(
        self,
        mouth_openness: float,
        mouth_shape: float,
        eye_openness: float,
        brow_position: float
    ) -> Tuple[str, float]:
        """
        Classify emotion based on facial measurements.
        
        Returns:
            Tuple of (emotion_name, confidence_score)
        """
        emotions_scores = {}
        
        # SMILE: mouth open, corners up, eyes open
        emotions_scores['happy'] = (
            max(mouth_shape, 0) * 0.5 +  # positive mouth shape
            eye_openness * 0.3 +
            (1 - abs(mouth_openness)) * 0.2  # can be smile or laugh
        ) if mouth_shape > 0.3 else 0.0
        
        # SAD: mouth shape down (frown), eyes slightly closed, brows down
        emotions_scores['sad'] = (
            min(mouth_shape, 0) * -0.5 +  # negative mouth shape
            (1 - eye_openness) * 0.3 +
            min(brow_position, 0) * -0.2
        ) if mouth_shape < -0.2 else 0.0
        
        # ANGRY: brows furrowed, mouth shape down, eyes open
        emotions_scores['angry'] = (
            min(brow_position, 0) * -0.5 +  # negative = furrowed
            eye_openness * 0.3 +
            min(mouth_shape, 0) * -0.2
        ) if brow_position < -0.3 else 0.0
        
        # SURPRISED: eyes very open, brows raised, mouth open
        emotions_scores['surprised'] = (
            eye_openness * 0.4 +
            max(brow_position, 0) * 0.4 +
            mouth_openness * 0.2
        ) if eye_openness > 0.7 and brow_position > 0.3 else 0.0
        
        # TIRED: eyes closed/closing, neutral mouth, relaxed brows
        emotions_scores['tired'] = (
            (1 - eye_openness) * 0.7 +
            (1 - abs(mouth_shape)) * 0.2 +
            (1 - abs(brow_position)) * 0.1
        ) if eye_openness < 0.4 else 0.0
        
        # CALM/NEUTRAL: balanced features
        emotions_scores['neutral'] = (
            (1 - abs(mouth_shape)) * 0.4 +
            (1 - abs(brow_position)) * 0.3 +
            abs(eye_openness - 0.6) * 0.3
        )
        
        # Find best emotion
        best_emotion = max(emotions_scores, key=emotions_scores.get)
        confidence = emotions_scores[best_emotion]
        
        # Clip confidence to 0-1
        confidence = np.clip(confidence, 0, 1)
        
        return best_emotion, confidence
    
    def _smooth_emotion(self) -> Tuple[str, float]:
        """Smooth emotion detection over history."""
        if not self.emotion_history:
            return "neutral", 0.0
        
        # Get most common emotion and average confidence
        emotions = [e[0] for e in self.emotion_history]
        confidences = [e[1] for e in self.emotion_history]
        
        # Weighted average (recent frames weighted more)
        weights = np.linspace(0.5, 1.5, len(emotions))
        weighted_emotions = {}
        
        for emotion, confidence, weight in zip(emotions, confidences, weights):
            if emotion not in weighted_emotions:
                weighted_emotions[emotion] = 0
            weighted_emotions[emotion] += confidence * weight
        
        # Normalize by weight sum
        total_weight = sum(weights)
        for emotion in weighted_emotions:
            weighted_emotions[emotion] /= total_weight
        
        best_emotion = max(weighted_emotions, key=weighted_emotions.get)
        avg_confidence = weighted_emotions[best_emotion]
        
        return best_emotion, min(avg_confidence, 1.0)

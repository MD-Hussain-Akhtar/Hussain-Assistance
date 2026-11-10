"""
Emotion Engine
Orchestrates voice and face emotion detection with fusion logic.
"""

import logging
import numpy as np
from typing import Tuple, Optional
from .emotion_state import EmotionState, EmotionStateManager
from .voice_emotion import VoiceEmotionDetector
from .face_emotion import FaceEmotionDetector

logger = logging.getLogger("EMOTION_ENGINE")


class EmotionEngine:
    """
    Unified emotion detection engine combining voice and face analysis.
    
    Weights:
    - Voice: 60%
    - Face: 40%
    """
    
    VOICE_WEIGHT = 0.60
    FACE_WEIGHT = 0.40
    CONFIDENCE_THRESHOLD = 0.50
    
    # Emotion categories
    EMOTIONS = {
        'neutral', 'happy', 'sad', 'tired', 'stressed', 'angry', 'calm', 'surprised'
    }
    
    def __init__(self, enable_voice: bool = True, enable_face: bool = True):
        """
        Initialize emotion engine.
        
        Args:
            enable_voice: Enable voice emotion detection
            enable_face: Enable face emotion detection
        """
        self.enable_voice = enable_voice
        self.enable_face = enable_face
        
        self.voice_detector = VoiceEmotionDetector() if enable_voice else None
        self.face_detector = FaceEmotionDetector() if enable_face else None
        self.state_manager = EmotionStateManager()
        
        logger.info(
            f"Emotion Engine initialized: "
            f"voice={enable_voice}, face={enable_face}"
        )
    
    def analyze(
        self,
        audio_chunk: Optional[np.ndarray] = None,
        face_landmarks: Optional[list] = None
    ) -> EmotionState:
        """
        Analyze emotion from available sources and return fused result.
        
        Args:
            audio_chunk: Audio samples for voice analysis (numpy array)
            face_landmarks: Face landmarks from MediaPipe for face analysis
        
        Returns:
            EmotionState object with combined emotion and confidence
        """
        voice_emotion = "neutral"
        voice_confidence = 0.0
        face_emotion = "neutral"
        face_confidence = 0.0
        
        # Voice analysis
        if self.enable_voice and audio_chunk is not None:
            try:
                voice_emotion, voice_confidence = self.voice_detector.analyze_audio_chunk(
                    audio_chunk
                )
            except Exception as e:
                logger.warning(f"Voice emotion analysis failed: {e}")
        
        # Face analysis
        if self.enable_face and face_landmarks is not None:
            try:
                face_emotion, face_confidence = self.face_detector.analyze_face(
                    face_landmarks
                )
            except Exception as e:
                logger.warning(f"Face emotion analysis failed: {e}")
        
        # Fuse emotions
        fused_emotion, fused_confidence = self._fuse_emotions(
            voice_emotion, voice_confidence,
            face_emotion, face_confidence
        )
        
        # Create emotion state
        emotion_state = EmotionState(
            emotion=fused_emotion,
            confidence=fused_confidence,
            voice_emotion=voice_emotion,
            voice_confidence=voice_confidence,
            face_emotion=face_emotion,
            face_confidence=face_confidence
        )
        
        # Update state manager
        self.state_manager.update_state(emotion_state)
        
        return emotion_state
    
    def _fuse_emotions(
        self,
        voice_emotion: str,
        voice_confidence: float,
        face_emotion: str,
        face_confidence: float
    ) -> Tuple[str, float]:
        """
        Fuse voice and face emotions using weighted averaging.
        
        Logic:
        1. If only one source is available, use that
        2. If both available, weight by configured ratios
        3. Apply confidence threshold
        
        Returns:
            Tuple of (fused_emotion, fused_confidence)
        """
        # Handle cases where one or both sources are unavailable
        if voice_confidence == 0.0 and face_confidence == 0.0:
            return "neutral", 0.0
        
        if voice_confidence == 0.0:
            final_emotion = face_emotion
            final_confidence = face_confidence
        elif face_confidence == 0.0:
            final_emotion = voice_emotion
            final_confidence = voice_confidence
        else:
            # Both sources available - weight them
            # Create emotion score vectors
            voice_scores = self._emotion_to_vector(voice_emotion, voice_confidence)
            face_scores = self._emotion_to_vector(face_emotion, face_confidence)
            
            # Weighted combination
            combined_scores = {}
            for emotion in self.EMOTIONS:
                voice_score = voice_scores.get(emotion, 0)
                face_score = face_scores.get(emotion, 0)
                combined_scores[emotion] = (
                    voice_score * self.VOICE_WEIGHT +
                    face_score * self.FACE_WEIGHT
                )
            
            # Select best emotion
            final_emotion = max(combined_scores, key=combined_scores.get)
            final_confidence = combined_scores[final_emotion]
        
        # Apply confidence threshold
        if final_confidence < self.CONFIDENCE_THRESHOLD:
            return "neutral", 0.0
        
        return final_emotion, np.clip(final_confidence, 0, 1)
    
    def _emotion_to_vector(self, emotion: str, confidence: float) -> dict:
        """
        Convert emotion with confidence to score vector across all emotions.
        Applies some semantic smoothing (e.g., angry and stressed are related).
        """
        scores = {e: 0.0 for e in self.EMOTIONS}
        
        if confidence == 0.0:
            return scores
        
        # Main emotion score
        scores[emotion] = confidence
        
        # Semantic relationships for smoothing
        relationships = {
            'happy': ['calm'],
            'sad': ['tired'],
            'tired': ['sad', 'calm'],
            'stressed': ['angry'],
            'angry': ['stressed'],
            'calm': ['happy', 'neutral'],
            'surprised': ['happy'],
            'neutral': ['calm'],
        }
        
        # Apply decay to related emotions
        if emotion in relationships:
            decay = confidence * 0.3  # 30% decay to related emotions
            for related in relationships[emotion]:
                scores[related] += decay
        
        return scores
    
    def get_current_state(self) -> EmotionState:
        """Get current emotion state."""
        return self.state_manager.get_state()
    
    def reset(self):
        """Reset emotion state to neutral."""
        self.state_manager.reset()
        if self.voice_detector:
            self.voice_detector.last_emotion = "neutral"
            self.voice_detector.last_confidence = 0.0
        if self.face_detector:
            self.face_detector.last_emotion = "neutral"
            self.face_detector.last_confidence = 0.0
        logger.info("Emotion engine reset")
    
    def set_emotion_source_enabled(self, source: str, enabled: bool):
        """Enable/disable emotion source at runtime."""
        if source == 'voice':
            self.enable_voice = enabled
            logger.info(f"Voice emotion detection: {'enabled' if enabled else 'disabled'}")
        elif source == 'face':
            self.enable_face = enabled
            logger.info(f"Face emotion detection: {'enabled' if enabled else 'disabled'}")

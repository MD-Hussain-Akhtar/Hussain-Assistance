"""
Voice Emotion Analysis
Detects emotion from speech tone using audio features.
Analyzes: pitch, energy, speech rate, and spectral characteristics.
"""

import logging
import numpy as np
from typing import Tuple, Optional
from collections import deque

logger = logging.getLogger("VOICE_EMOTION")


class VoiceEmotionDetector:
    """Detects emotion from voice characteristics."""
    
    # Audio processing constants
    SAMPLE_RATE = 16000
    ANALYSIS_WINDOW = 2.0  # seconds of audio to analyze
    SAMPLES_PER_WINDOW = int(SAMPLE_RATE * ANALYSIS_WINDOW)
    
    # Feature thresholds (calibrated for typical speech)
    PITCH_RANGE_LOW = 80    # Hz
    PITCH_RANGE_HIGH = 300  # Hz
    ENERGY_THRESHOLD = -40  # dB
    
    # Emotion mappings based on acoustic features
    EMOTION_MAPPINGS = {
        'happy': {'pitch': 'high', 'energy': 'high', 'rate': 'fast'},
        'calm': {'pitch': 'medium', 'energy': 'medium', 'rate': 'slow'},
        'sad': {'pitch': 'low', 'energy': 'low', 'rate': 'slow'},
        'tired': {'pitch': 'low', 'energy': 'low', 'rate': 'very_slow'},
        'stressed': {'pitch': 'high', 'energy': 'high', 'rate': 'very_fast'},
        'angry': {'pitch': 'high', 'energy': 'very_high', 'rate': 'fast'},
    }
    
    def __init__(self):
        self.audio_buffer = deque(maxlen=self.SAMPLES_PER_WINDOW)
        self.last_emotion = "neutral"
        self.last_confidence = 0.0
    
    def analyze_audio_chunk(self, audio_data: np.ndarray) -> Tuple[str, float]:
        """
        Analyze audio chunk for emotion.
        
        Args:
            audio_data: numpy array of audio samples (16-bit PCM)
        
        Returns:
            Tuple of (emotion, confidence) where confidence is 0.0-1.0
        """
        try:
            # Convert to float and normalize
            if audio_data.dtype != np.float32:
                audio_float = audio_data.astype(np.float32) / 32768.0
            else:
                audio_float = audio_data
            
            # Add to buffer
            for sample in audio_float:
                self.audio_buffer.append(sample)
            
            # Only analyze if buffer is full
            if len(self.audio_buffer) < self.SAMPLES_PER_WINDOW * 0.5:
                return self.last_emotion, self.last_confidence
            
            # Extract acoustic features
            buffer_array = np.array(list(self.audio_buffer))
            
            # Skip silent segments
            if self._is_silent(buffer_array):
                return "neutral", 0.0
            
            pitch = self._estimate_pitch(buffer_array)
            energy = self._calculate_energy(buffer_array)
            speech_rate = self._estimate_speech_rate(buffer_array)
            
            # Classify emotion based on features
            emotion, confidence = self._classify_emotion(pitch, energy, speech_rate)
            
            # Update cache
            self.last_emotion = emotion
            self.last_confidence = confidence
            
            logger.debug(
                f"Voice analysis: pitch={pitch:.1f}Hz, "
                f"energy={energy:.1f}dB, rate={speech_rate:.2f} "
                f"→ {emotion} ({confidence:.2f})"
            )
            
            return emotion, confidence
            
        except Exception as e:
            logger.warning(f"Voice emotion analysis error: {e}")
            return "neutral", 0.0
    
    def _is_silent(self, audio: np.ndarray, threshold_db: float = -40) -> bool:
        """Check if audio segment is silent."""
        energy_db = self._calculate_energy(audio)
        return energy_db < threshold_db
    
    def _estimate_pitch(self, audio: np.ndarray) -> float:
        """
        Estimate fundamental frequency (pitch) using autocorrelation.
        Returns pitch in Hz.
        """
        try:
            # Simple autocorrelation-based pitch detection
            autocorr = np.correlate(audio, audio, mode='full')
            autocorr = autocorr[len(autocorr)//2:]
            autocorr = autocorr / autocorr[0]
            
            # Find first peak in valid pitch range
            min_period = int(self.SAMPLE_RATE / self.PITCH_RANGE_HIGH)
            max_period = int(self.SAMPLE_RATE / self.PITCH_RANGE_LOW)
            
            if len(autocorr) > max_period:
                autocorr_slice = autocorr[min_period:max_period]
                if len(autocorr_slice) > 0:
                    peak_idx = np.argmax(autocorr_slice)
                    if autocorr_slice[peak_idx] > 0.5:  # Confidence threshold
                        period = peak_idx + min_period
                        pitch = self.SAMPLE_RATE / period
                        return np.clip(pitch, self.PITCH_RANGE_LOW, self.PITCH_RANGE_HIGH)
            
            return 150.0  # Default middle pitch
            
        except Exception:
            return 150.0
    
    def _calculate_energy(self, audio: np.ndarray) -> float:
        """Calculate energy (loudness) in dB."""
        try:
            # RMS energy
            rms = np.sqrt(np.mean(audio ** 2))
            
            # Convert to dB (using 0.1 as reference)
            db = 20 * np.log10(rms + 1e-10)
            return np.clip(db, -80, 0)
            
        except Exception:
            return -40.0
    
    def _estimate_speech_rate(self, audio: np.ndarray) -> float:
        """
        Estimate speech rate using zero-crossing rate.
        Returns normalized rate (0.0 to 1.0 where 1.0 = very fast).
        """
        try:
            # Zero-crossing rate
            zero_crossings = np.sum(np.abs(np.diff(np.sign(audio)))) / 2
            zcr = zero_crossings / len(audio)
            
            # Normalize (typical speech has ZCR 0.0-0.1)
            normalized_rate = np.clip(zcr * 10, 0.0, 1.0)
            return normalized_rate
            
        except Exception:
            return 0.5
    
    def _classify_emotion(self, pitch: float, energy: float, rate: float) -> Tuple[str, float]:
        """
        Classify emotion based on extracted features.
        
        Returns:
            Tuple of (emotion_name, confidence_score)
        """
        # Define feature ranges (normalized 0-1)
        pitch_norm = (pitch - self.PITCH_RANGE_LOW) / (self.PITCH_RANGE_HIGH - self.PITCH_RANGE_LOW)
        pitch_norm = np.clip(pitch_norm, 0, 1)
        
        energy_norm = (energy + 40) / 40  # -40dB to 0dB → 0 to 1
        energy_norm = np.clip(energy_norm, 0, 1)
        
        # Decision tree for emotion classification
        emotions_scores = {}
        
        # Happy: high pitch, high energy, fast rate
        emotions_scores['happy'] = (
            pitch_norm * 0.4 +
            energy_norm * 0.4 +
            rate * 0.2
        ) if pitch_norm > 0.6 and energy_norm > 0.6 else 0.0
        
        # Stressed: very high pitch, high energy, very fast rate
        emotions_scores['stressed'] = (
            pitch_norm * 0.3 +
            energy_norm * 0.3 +
            rate * 0.4
        ) if pitch_norm > 0.7 and rate > 0.7 else 0.0
        
        # Angry: high pitch, very high energy, fast rate
        emotions_scores['angry'] = (
            pitch_norm * 0.3 +
            energy_norm * 0.5 +
            rate * 0.2
        ) if pitch_norm > 0.6 and energy_norm > 0.7 else 0.0
        
        # Calm: medium pitch, medium energy, slow rate
        emotions_scores['calm'] = (
            (1 - abs(pitch_norm - 0.5)) * 0.4 +
            (1 - abs(energy_norm - 0.5)) * 0.4 +
            (1 - rate) * 0.2
        ) if 0.4 < pitch_norm < 0.6 and rate < 0.3 else 0.0
        
        # Sad: low pitch, low energy, slow rate
        emotions_scores['sad'] = (
            (1 - pitch_norm) * 0.3 +
            (1 - energy_norm) * 0.3 +
            (1 - rate) * 0.4
        ) if pitch_norm < 0.4 and energy_norm < 0.4 else 0.0
        
        # Tired: low pitch, low energy, very slow rate
        emotions_scores['tired'] = (
            (1 - pitch_norm) * 0.3 +
            (1 - energy_norm) * 0.4 +
            (1 - rate) * 0.3
        ) if pitch_norm < 0.4 and energy_norm < 0.3 and rate < 0.2 else 0.0
        
        # Find emotion with highest score
        best_emotion = max(emotions_scores, key=emotions_scores.get)
        confidence = emotions_scores[best_emotion]
        
        # If all scores are very low, default to neutral
        if confidence < 0.3:
            return "neutral", 0.0
        
        return best_emotion, min(confidence, 1.0)

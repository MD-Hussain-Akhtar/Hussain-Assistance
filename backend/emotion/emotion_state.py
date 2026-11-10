"""
Emotion State Management
Tracks and persists emotion state during runtime.
"""

import json
import logging
from dataclasses import dataclass, asdict
from datetime import datetime
from pathlib import Path
from typing import Optional

logger = logging.getLogger("EMOTION_AI")


@dataclass
class EmotionState:
    """Represents current emotional state with confidence scores."""
    
    emotion: str  # neutral, happy, sad, tired, stressed, angry, calm
    confidence: float  # 0.0 to 1.0
    voice_emotion: Optional[str] = None
    voice_confidence: float = 0.0
    face_emotion: Optional[str] = None
    face_confidence: float = 0.0
    timestamp: str = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now().isoformat()
    
    def to_dict(self):
        """Convert to dictionary for serialization."""
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: dict):
        """Create from dictionary."""
        return cls(**data)
    
    def is_neutral(self) -> bool:
        """Check if emotion is neutral or below confidence threshold."""
        return self.emotion == "neutral" or self.confidence < 0.5


class EmotionStateManager:
    """Manages emotion state persistence and runtime tracking."""
    
    def __init__(self, state_file: str = "backend/emotion/emotion_state.json"):
        self.state_file = Path(state_file)
        self.current_state = EmotionState(
            emotion="neutral",
            confidence=0.0,
            timestamp=datetime.now().isoformat()
        )
        self._load_state()
    
    def update_state(self, new_state: EmotionState):
        """Update current emotion state."""
        self.current_state = new_state
        self._save_state()
        logger.info(
            f"Emotion updated: {new_state.emotion} "
            f"(confidence: {new_state.confidence:.2f})"
        )
    
    def get_state(self) -> EmotionState:
        """Get current emotion state."""
        return self.current_state
    
    def _save_state(self):
        """Save state to persistent storage."""
        try:
            self.state_file.parent.mkdir(parents=True, exist_ok=True)
            with open(self.state_file, 'w') as f:
                json.dump(self.current_state.to_dict(), f, indent=2)
        except Exception as e:
            logger.warning(f"Failed to save emotion state: {e}")
    
    def _load_state(self):
        """Load state from persistent storage."""
        try:
            if self.state_file.exists():
                with open(self.state_file, 'r') as f:
                    data = json.load(f)
                    self.current_state = EmotionState.from_dict(data)
                    logger.info(f"Loaded emotion state: {self.current_state.emotion}")
        except Exception as e:
            logger.warning(f"Failed to load emotion state: {e}")
            self.current_state = EmotionState(
                emotion="neutral",
                confidence=0.0,
                timestamp=datetime.now().isoformat()
            )
    
    def reset(self):
        """Reset emotion state to neutral."""
        self.current_state = EmotionState(
            emotion="neutral",
            confidence=0.0,
            timestamp=datetime.now().isoformat()
        )
        self._save_state()
        logger.info("Emotion state reset to neutral")

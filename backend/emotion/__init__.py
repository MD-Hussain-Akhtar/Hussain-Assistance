"""
Emotion AI Module for ADA V2
Detects and responds to user emotions through voice tone and face expressions.
"""

from .emotion_engine import EmotionEngine
from .emotion_state import EmotionState

__all__ = ["EmotionEngine", "EmotionState"]

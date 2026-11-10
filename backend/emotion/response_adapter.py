"""
Response Style Adapter
Adapts Zoya's response style based on detected emotion.
"""

import logging
from typing import Dict, Optional
from .emotion_state import EmotionState

logger = logging.getLogger("RESPONSE_ADAPTER")


class ResponseStyleAdapter:
    """
    Adapts response characteristics based on detected emotion.
    Does NOT change actions, only communication style.
    """
    
    # Style profiles for each emotion
    STYLE_PROFILES = {
        'neutral': {
            'tone': 'professional',
            'energy': 'medium',
            'sentence_length': 'medium',
            'response_speed': 'normal',
            'temperature': 0.7,
            'characteristics': [
                'Clear and straightforward',
                'Professional tone',
                'Direct communication',
            ]
        },
        
        'happy': {
            'tone': 'enthusiastic',
            'energy': 'high',
            'sentence_length': 'varied',
            'response_speed': 'faster',
            'temperature': 0.8,
            'characteristics': [
                'Enthusiastic and upbeat',
                'Encouraging language',
                'Exclamation marks!',
                'Positive framing',
            ]
        },
        
        'calm': {
            'tone': 'soothing',
            'energy': 'low',
            'sentence_length': 'short',
            'response_speed': 'slower',
            'temperature': 0.6,
            'characteristics': [
                'Relaxed and gentle',
                'Reassuring tone',
                'Simple language',
                'Meditative pacing',
            ]
        },
        
        'sad': {
            'tone': 'supportive',
            'energy': 'low',
            'sentence_length': 'short',
            'response_speed': 'slower',
            'temperature': 0.6,
            'characteristics': [
                'Compassionate and understanding',
                'Supportive language',
                'Validation of feelings',
                'Gentle encouragement',
            ]
        },
        
        'tired': {
            'tone': 'soothing',
            'energy': 'low',
            'sentence_length': 'short',
            'response_speed': 'slower',
            'temperature': 0.6,
            'characteristics': [
                'Calm and restorative',
                'Supportive tone',
                'Short, clear sentences',
                'No overwhelming information',
            ]
        },
        
        'stressed': {
            'tone': 'reassuring',
            'energy': 'medium',
            'sentence_length': 'medium',
            'response_speed': 'normal',
            'temperature': 0.7,
            'characteristics': [
                'Calm and grounding',
                'Step-by-step guidance',
                'Reassuring language',
                'Breaking down complex tasks',
            ]
        },
        
        'angry': {
            'tone': 'understanding',
            'energy': 'low',
            'sentence_length': 'medium',
            'response_speed': 'slower',
            'temperature': 0.6,
            'characteristics': [
                'Respectful and understanding',
                'Acknowledging frustration',
                'Problem-solving focus',
                'Patient explanation',
            ]
        },
        
        'surprised': {
            'tone': 'engaging',
            'energy': 'high',
            'sentence_length': 'varied',
            'response_speed': 'faster',
            'temperature': 0.75,
            'characteristics': [
                'Curious and engaged',
                'Dynamic responses',
                'Interest in details',
                'Eager to help',
            ]
        },
    }
    
    # System prompt prefixes for each emotion
    SYSTEM_PROMPT_PREFIXES = {
        'neutral': 'Be clear, professional, and helpful.',
        
        'happy': (
            'The user is happy! Be enthusiastic, encouraging, and upbeat. '
            'Use positive language and exclamation marks where appropriate. '
            'Match their positive energy!'
        ),
        
        'calm': (
            'The user is calm and relaxed. Maintain a soothing tone. '
            'Keep responses short and simple. Use meditative, gentle language. '
            'Avoid overwhelming information.'
        ),
        
        'sad': (
            'The user is sad. Be compassionate, understanding, and supportive. '
            'Validate their feelings. Use gentle, encouraging language. '
            'Offer help without being pushy.'
        ),
        
        'tired': (
            'The user is tired. Be calm and restorative. Keep responses short and clear. '
            'Provide supportive, gentle guidance. Avoid overwhelming them. '
            'Suggest rest when appropriate.'
        ),
        
        'stressed': (
            'The user is stressed. Be calm and reassuring. Break down tasks into steps. '
            'Use step-by-step guidance. Help them feel grounded and in control. '
            'Focus on solutions, not problems.'
        ),
        
        'angry': (
            'The user is frustrated or angry. Be respectful and understanding. '
            'Acknowledge their frustration. Focus on solving the problem. '
            'Be patient and clear in your explanations.'
        ),
        
        'surprised': (
            'The user is surprised or curious! Be engaging and dynamic. '
            'Match their curiosity with detailed, interesting responses. '
            'Be eager and helpful.'
        ),
    }
    
    def __init__(self):
        """Initialize the response adapter."""
        self.current_style = self.STYLE_PROFILES['neutral'].copy()
    
    def adapt_to_emotion(self, emotion_state: EmotionState) -> Dict:
        """
        Adapt response style based on emotion state.
        
        Args:
            emotion_state: EmotionState object with detected emotion
        
        Returns:
            Dictionary with:
            - style: Style profile
            - system_prompt_prefix: Prompt prefix for Gemini
            - instructions: List of communication guidelines
        """
        if emotion_state.confidence < 0.5:
            emotion = 'neutral'
        else:
            emotion = emotion_state.emotion
        
        # Get style profile
        style = self.STYLE_PROFILES.get(emotion, self.STYLE_PROFILES['neutral']).copy()
        self.current_style = style
        
        # Build adapted response config
        config = {
            'emotion': emotion,
            'confidence': emotion_state.confidence,
            'style': style,
            'system_prompt_prefix': self.SYSTEM_PROMPT_PREFIXES.get(
                emotion,
                self.SYSTEM_PROMPT_PREFIXES['neutral']
            ),
            'instructions': style.get('characteristics', []),
            'gemini_config': {
                'temperature': style.get('temperature', 0.7),
            }
        }
        
        logger.debug(f"Adapted response style to emotion: {emotion}")
        
        return config
    
    def get_adapted_system_prompt(
        self,
        base_system_prompt: str,
        emotion_state: EmotionState
    ) -> str:
        """
        Augment system prompt with emotion-aware instructions.
        
        Args:
            base_system_prompt: Original system prompt for Zoya
            emotion_state: Current emotion state
        
        Returns:
            Augmented system prompt
        """
        config = self.adapt_to_emotion(emotion_state)
        prefix = config['system_prompt_prefix']
        
        # Append emotion-aware instructions
        augmented = f"{prefix}\n\n{base_system_prompt}"
        
        return augmented
    
    def get_response_delay(self, emotion_state: EmotionState) -> float:
        """
        Get recommended response delay based on emotion.
        Stressed/tired users benefit from slightly slower responses.
        
        Args:
            emotion_state: Current emotion state
        
        Returns:
            Delay in seconds (0.0 to 2.0)
        """
        if emotion_state.confidence < 0.5:
            return 0.0
        
        emotion = emotion_state.emotion
        
        delays = {
            'calm': 0.5,
            'tired': 0.8,
            'sad': 0.5,
            'stressed': 0.3,
            'angry': 0.5,
            'neutral': 0.0,
            'happy': 0.0,
            'surprised': 0.0,
        }
        
        return delays.get(emotion, 0.0)
    
    def get_response_length_hint(self, emotion_state: EmotionState) -> str:
        """
        Get hint about optimal response length.
        
        Args:
            emotion_state: Current emotion state
        
        Returns:
            'short', 'medium', or 'long'
        """
        if emotion_state.confidence < 0.5:
            return 'medium'
        
        emotion = emotion_state.emotion
        
        lengths = {
            'calm': 'short',
            'tired': 'short',
            'sad': 'short',
            'stressed': 'medium',
            'angry': 'medium',
            'neutral': 'medium',
            'happy': 'medium',
            'surprised': 'medium',
        }
        
        return lengths.get(emotion, 'medium')
    
    @staticmethod
    def get_context_for_frontend(emotion_state: EmotionState) -> Dict:
        """
        Get emotion context to send to frontend.
        
        Args:
            emotion_state: Current emotion state
        
        Returns:
            Dictionary suitable for JSON serialization
        """
        return {
            'emotion': emotion_state.emotion,
            'confidence': float(emotion_state.confidence),
            'voice_emotion': emotion_state.voice_emotion,
            'voice_confidence': float(emotion_state.voice_confidence),
            'face_emotion': emotion_state.face_emotion,
            'face_confidence': float(emotion_state.face_confidence),
            'timestamp': emotion_state.timestamp,
        }

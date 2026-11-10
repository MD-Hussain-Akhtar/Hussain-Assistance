# Emotion AI Feature Guide

## Overview

**Emotional Awareness** (Emotion AI) is a new ADA V2 feature that enables Zoya to detect and respond to user emotions. This feature analyzes both voice tone and facial expressions to understand emotional context and adapt response styles accordingly.

### Goal
> Zoya should not only follow commands, but also detect and respond to user emotions with appropriate tone, pacing, and energy level.

---

## Architecture

### Module Structure

```
backend/emotion/
├── __init__.py                  # Module exports
├── emotion_state.py             # Emotion state management
├── voice_emotion.py             # Voice tone analysis
├── face_emotion.py              # Face expression analysis  
├── emotion_engine.py            # Main orchestrator
└── response_adapter.py          # Response style adaptation
```

### Design Principles

1. **Modular**: Emotion detection is completely isolated from core ADA logic
2. **Optional**: Can be enabled/disabled via settings without affecting functionality
3. **Non-blocking**: Emotion analysis runs asynchronously, never blocks audio processing
4. **Graceful Degradation**: If emotion detection fails, system continues normally
5. **Privacy-Respecting**: All processing is local; no emotion data sent to cloud

---

## Core Components

### 1. Voice Emotion Detector (`voice_emotion.py`)

**Purpose**: Analyzes live microphone audio to detect emotional state

**Detected Emotions**:
- `happy` - High pitch, high energy, fast speech rate
- `calm` - Medium pitch, medium energy, slow speech rate
- `sad` - Low pitch, low energy, slow speech rate
- `tired` - Low pitch, low energy, very slow speech rate
- `stressed` - High pitch, high energy, very fast speech rate
- `angry` - High pitch, very high energy, fast speech rate
- `neutral` - Balanced features, low confidence

**Technical Approach**:
- Analyzes audio features in real-time:
  - **Pitch** (fundamental frequency, 80-300 Hz)
  - **Energy** (loudness, -40 to 0 dB)
  - **Speech Rate** (zero-crossing rate, normalized 0-1)
- Uses decision tree classification
- Outputs emotion with confidence score (0-1)

**Key Methods**:
```python
detector = VoiceEmotionDetector()
emotion, confidence = detector.analyze_audio_chunk(audio_numpy_array)
# Returns: ("happy", 0.85)
```

### 2. Face Emotion Detector (`face_emotion.py`)

**Purpose**: Analyzes facial expressions to detect emotional state

**Detected Emotions**:
- `happy` - Smile, open eyes, relaxed brows
- `sad` - Frown, slightly closed eyes, downturned brows
- `angry` - Furrowed brows, open eyes, downturned mouth
- `tired` - Closed/closing eyes, relaxed features
- `surprised` - Very open eyes, raised brows, open mouth
- `calm` - Neutral expression, balanced features
- `neutral` - Low confidence classification

**Technical Approach**:
- Uses MediaPipe Face Landmarker (478 landmarks)
- Analyzes key regions:
  - **Mouth**: Openness, shape (smile vs frown)
  - **Eyes**: Aspect ratio (open vs closed)
  - **Eyebrows**: Position (raised vs furrowed)
- Applies temporal smoothing (5-frame window)
- Outputs emotion with confidence score (0-1)

**Key Methods**:
```python
detector = FaceEmotionDetector()
emotion, confidence = detector.analyze_face(face_landmarks_list)
# Returns: ("happy", 0.72)
```

### 3. Emotion Engine (`emotion_engine.py`)

**Purpose**: Orchestrates voice and face analysis with fusion logic

**Emotion Fusion**:
- Voice emotion: **60% weight**
- Face emotion: **40% weight**
- Confidence threshold: **0.50** (below = neutral)

**Algorithm**:
```
1. Analyze voice emotion (if enabled)
2. Analyze face emotion (if enabled)
3. Create emotion score vectors
4. Apply weighted combination
5. Select best emotion above threshold
6. Apply semantic smoothing
```

**Example**:
```
Voice: happy (0.8)     → happy scores: 0.8
Face:  calm (0.6)      → calm scores: 0.6
Combined: (0.8×0.6 + 0.6×0.4) = 0.72 (happy wins)
```

**Key Methods**:
```python
engine = EmotionEngine(enable_voice=True, enable_face=True)

# Analyze emotion
emotion_state = engine.analyze(
    audio_chunk=audio_array,
    face_landmarks=landmarks
)
# Returns: EmotionState(emotion="happy", confidence=0.72, ...)

# Get current state
state = engine.get_current_state()

# Control sources at runtime
engine.set_emotion_source_enabled('voice', True)
engine.set_emotion_source_enabled('face', False)
```

### 4. Response Style Adapter (`response_adapter.py`)

**Purpose**: Adapts Zoya's response style based on detected emotion

**Adaptation Styles**:

| Emotion | Tone | Energy | Sentence Length | Speed |
|---------|------|--------|-----------------|-------|
| **neutral** | Professional | Medium | Medium | Normal |
| **happy** | Enthusiastic | High | Varied | Faster |
| **calm** | Soothing | Low | Short | Slower |
| **sad** | Supportive | Low | Short | Slower |
| **tired** | Restorative | Low | Short | Slower |
| **stressed** | Reassuring | Medium | Medium | Normal |
| **angry** | Understanding | Low | Medium | Slower |
| **surprised** | Engaging | High | Varied | Faster |

**System Prompt Augmentation**:
Each emotion has a custom system prompt prefix:

```python
# Example for tired emotion
prefix = """The user is tired. Be calm and restorative. 
Keep responses short and clear. Provide supportive, 
gentle guidance. Avoid overwhelming them. 
Suggest rest when appropriate."""
```

**Key Methods**:
```python
adapter = ResponseStyleAdapter()

# Adapt to emotion state
config = adapter.adapt_to_emotion(emotion_state)
# Returns:
# {
#     'emotion': 'happy',
#     'confidence': 0.72,
#     'style': {...style profile...},
#     'system_prompt_prefix': '...',
#     'instructions': ['Enthusiastic...', 'Encouraging...'],
#     'gemini_config': {'temperature': 0.8}
# }

# Get adapted system prompt
prompt = adapter.get_adapted_system_prompt(base_prompt, emotion_state)

# Get response characteristics
delay = adapter.get_response_delay(emotion_state)  # 0-2 seconds
length = adapter.get_response_length_hint(emotion_state)  # short/medium/long
```

### 5. Emotion State Management (`emotion_state.py`)

**Purpose**: Tracks and persists emotion state during runtime

**State Structure**:
```python
@dataclass
class EmotionState:
    emotion: str              # Main emotion (happy, sad, etc)
    confidence: float         # 0.0 to 1.0
    voice_emotion: str        # Emotion from voice analysis
    voice_confidence: float   # Voice confidence
    face_emotion: str         # Emotion from face analysis
    face_confidence: float    # Face confidence
    timestamp: str            # ISO format timestamp
```

**Persistence**:
- Emotion state saved to `backend/emotion/emotion_state.json`
- Auto-loads on startup
- Resets to neutral on system restart
- Thread-safe updates

**Key Methods**:
```python
manager = EmotionStateManager()

# Get current state
state = manager.get_state()

# Update state
new_state = EmotionState(emotion="happy", confidence=0.8)
manager.update_state(new_state)

# Reset to neutral
manager.reset()
```

---

## Integration with ADA V2

### 1. Backend Integration (`ada.py`)

**Initialization**:
```python
# In AudioLoop.__init__
self.emotion_engine = EmotionEngine(
    enable_voice=emotion_voice_enabled,
    enable_face=emotion_face_enabled
)
self.response_adapter = ResponseStyleAdapter()
```

**Audio Analysis**:
```python
# In listen_audio() - runs for each audio chunk
if self.emotion_engine and self.emotion_engine.enable_voice:
    audio_array = np.frombuffer(data, dtype=np.int16)
    asyncio.create_task(self._analyze_user_emotion(audio_array))
```

**Emotion Update Method**:
```python
async def _analyze_user_emotion(self, audio_chunk):
    """Analyzes user emotion (non-blocking)"""
    emotion_state = self.emotion_engine.analyze(
        audio_chunk=audio_chunk,
        face_landmarks=None  # Can add face landmarks from video
    )
    
    # Emit to frontend
    if self.on_emotion_update:
        emotion_context = ResponseStyleAdapter.get_context_for_frontend(emotion_state)
        self.on_emotion_update(emotion_context)
```

**Getting Emotion State**:
```python
# Public method to retrieve current emotion
emotion_data = audio_loop.get_current_emotion()
# Returns: {emotion, confidence, voice_emotion, face_emotion, timestamp}
```

### 2. Configuration (`settings.json`)

**Enable/Disable Emotion AI**:
```json
{
    "emotion_ai_enabled": true,
    "emotion_sources": {
        "voice": true,
        "face": true
    }
}
```

**Settings Effects**:
- `emotion_ai_enabled: false` → Entire system disabled, minimal overhead
- `emotion_sources.voice: false` → Only face analysis
- `emotion_sources.face: false` → Only voice analysis

---

## Usage Examples

### Basic Usage

```python
from emotion.emotion_engine import EmotionEngine
from emotion.response_adapter import ResponseStyleAdapter
import numpy as np

# Initialize
engine = EmotionEngine(enable_voice=True, enable_face=True)
adapter = ResponseStyleAdapter()

# Analyze audio
audio_data = np.frombuffer(mic_audio, dtype=np.int16)
emotion_state = engine.analyze(audio_chunk=audio_data)

# Get response style
config = adapter.adapt_to_emotion(emotion_state)
print(f"User is {emotion_state.emotion}")
print(f"Respond with: {config['system_prompt_prefix']}")
```

### Advanced Usage - Custom Integration

```python
# Monitor emotion over time
for audio_chunk in live_audio_stream:
    state = engine.analyze(audio_chunk=audio_chunk)
    
    # Log emotion changes
    if state.confidence > 0.7:  # High confidence
        logger.info(f"User emotion: {state.emotion}")
    
    # Adapt UI based on emotion
    if state.emotion == 'stressed':
        show_calming_visuals()
        reduce_response_latency()
    elif state.emotion == 'happy':
        show_celebratory_animation()
```

---

## Configuration Guide

### settings.json

```json
{
    "emotion_ai_enabled": true,
    "emotion_sources": {
        "voice": true,
        "face": true
    }
}
```

### Runtime Control

```python
# Disable voice emotion at runtime
audio_loop.emotion_engine.set_emotion_source_enabled('voice', False)

# Check current emotion
current = audio_loop.get_current_emotion()
print(current['emotion'], current['confidence'])

# Reset emotion state
audio_loop.emotion_engine.reset()
```

---

## Technical Details

### Voice Emotion Algorithm

**Feature Extraction** (per audio chunk):
1. Pitch estimation using autocorrelation
2. Energy calculation (RMS in dB)
3. Speech rate via zero-crossing rate

**Classification Decision Tree**:
```
IF pitch > 0.6 AND energy > 0.6 THEN happy
IF pitch > 0.7 AND rate > 0.7 THEN stressed
IF pitch > 0.6 AND energy > 0.7 THEN angry
IF pitch < 0.4 AND energy < 0.4 AND rate < 0.2 THEN tired
IF pitch < 0.4 AND energy < 0.4 THEN sad
...
ELSE neutral
```

### Face Emotion Algorithm

**Landmark Measurements**:
1. Mouth openness (top-bottom distance)
2. Mouth shape (corners up/down angle)
3. Eye openness (vertical/horizontal ratio)
4. Brow position (vertical location)

**Temporal Smoothing**:
- 5-frame sliding window
- Weighted average (recent frames weighted more)
- Reduces false positives from micro-expressions

### Emotion Fusion

**Score Vector Creation**:
```python
# Create emotion probability distributions
voice_vector = {
    'happy': 0.8,
    'calm': 0.1,
    'sad': 0.05,
    'tired': 0.05,
    ...
}

face_vector = {
    'happy': 0.4,
    'calm': 0.3,
    'neutral': 0.3,
    ...
}

# Weighted combination
combined = {}
for emotion in all_emotions:
    combined[emotion] = (
        voice_vector[emotion] * 0.6 +
        face_vector[emotion] * 0.4
    )
```

---

## Performance & Optimization

### Performance Metrics

| Operation | Time | Blocking |
|-----------|------|----------|
| Voice analysis per chunk | ~2ms | No (async task) |
| Face analysis per frame | ~5ms | No (async task) |
| Emotion fusion | <1ms | No |
| State persistence | ~10ms | No (background) |

### Memory Usage

- VoiceEmotionDetector: ~2 MB (buffer)
- FaceEmotionDetector: ~500 KB (history)
- EmotionEngine: ~1 MB (managers + state)
- **Total**: ~3.5 MB overhead

### Optimization Tips

1. **Reduce analysis frequency**: Skip emotion analysis for silent periods
2. **Batch processing**: Analyze 5 chunks together for efficiency
3. **Disable unused sources**: Set face emotion to False if camera not available
4. **Clear history**: Reset state periodically for long sessions

---

## Error Handling & Debugging

### Common Issues

**Issue**: Emotion AI crashes on startup
```python
# Fix: Enable with error handling in ada.py
try:
    self.emotion_engine = EmotionEngine(...)
except Exception as e:
    print(f"Emotion AI failed to initialize: {e}")
    self.emotion_engine = None
```

**Issue**: All emotions detected as "neutral"
```python
# Diagnosis:
# 1. Check confidence threshold (default 0.50)
# 2. Verify audio input is active
# 3. Check feature extraction (pitch, energy, rate)
```

**Issue**: Face emotion not updating
```python
# Ensure:
# 1. Camera is enabled (video_mode='camera')
# 2. face_auth_enabled or camera accessible
# 3. Landmarks detected successfully
```

### Debug Logging

Enable debug output:
```python
import logging
logging.basicConfig(level=logging.DEBUG)

# View emotion analysis logs
logger = logging.getLogger("EMOTION_AI")
logger.setLevel(logging.DEBUG)
```

---

## Testing Emotion AI

### Manual Testing

```python
# Test voice emotion with sample audio
import numpy as np
from emotion.voice_emotion import VoiceEmotionDetector

detector = VoiceEmotionDetector()

# High pitch, high energy (happy)
happy_sample = np.sin(np.linspace(0, 200, 16000))
emotion, confidence = detector.analyze_audio_chunk(happy_sample)
assert emotion == "happy", f"Expected happy, got {emotion}"

# Low pitch, low energy (sad)
sad_sample = np.sin(np.linspace(0, 50, 16000))
emotion, confidence = detector.analyze_audio_chunk(sad_sample)
assert emotion in ["sad", "tired"], f"Expected sad/tired, got {emotion}"
```

### Automated Testing

```bash
# Run test suite (if available)
python -m pytest backend/emotion/tests/ -v
```

---

## Best Practices

### ✅ DO

- Enable emotion AI selectively (toggle in settings)
- Use emotion state for UI hints, not actions
- Combine with other signals (context, tools)
- Log emotion changes for debugging
- Reset state on session restart

### ❌ DON'T

- Use emotion to override explicit user commands
- Trigger system actions based solely on emotion
- Expose raw emotion scores to user without context
- Train on personal emotion data
- Assume emotion detection is 100% accurate

---

## Future Enhancements

1. **Prosody Analysis**: Intonation patterns for nuanced emotion
2. **Multimodal Fusion**: Combine text sentiment + voice + face
3. **Emotion Transition Tracking**: Detect emotional shifts
4. **Personalized Models**: Calibrate per user
5. **Real-time Feedback**: Show confidence to user
6. **Emotion History**: Track mood patterns over time

---

## Architecture Diagram

```
┌─────────────────────────────────────────────────┐
│           ADA V2 Emotion AI System              │
├─────────────────────────────────────────────────┤
│                                                 │
│  Audio Input (Mic)        Video Input (Camera) │
│        │                           │            │
│        ▼                           ▼            │
│  ┌──────────────┐      ┌─────────────────┐    │
│  │ Voice Audio  │      │ Face Landmarks  │    │
│  │  (16kHz)     │      │   (478 points)  │    │
│  └──────────────┘      └─────────────────┘    │
│        │                           │            │
│        ▼                           ▼            │
│  ┌──────────────────┐  ┌─────────────────┐    │
│  │ Voice Emotion    │  │ Face Emotion    │    │
│  │ Detector         │  │ Detector        │    │
│  │ (pitch, energy,  │  │ (mouth, eyes,   │    │
│  │  rate)           │  │  brows)         │    │
│  └────────┬─────────┘  └────────┬────────┘    │
│           │                     │             │
│           └──────────┬──────────┘             │
│                      ▼                        │
│            ┌──────────────────────┐           │
│            │  Emotion Engine      │           │
│            │  - Fusion Logic      │           │
│            │  - Confidence Scoring│           │
│            │  - State Persistence │           │
│            └──────────┬───────────┘           │
│                       ▼                       │
│            ┌──────────────────────┐           │
│            │ Response Adapter     │           │
│            │ - Style Profiles     │           │
│            │ - System Prompt      │           │
│            │ - Response Pacing    │           │
│            └──────────┬───────────┘           │
│                       │                       │
│              ┌────────┴────────┐              │
│              ▼                 ▼              │
│         Zoya Response      Frontend UI        │
│         (Adapted tone)     (Emotion badge)    │
│                                               │
└─────────────────────────────────────────────────┘
```

---

## API Reference

### EmotionEngine

```python
class EmotionEngine:
    def __init__(self, enable_voice=True, enable_face=True)
    def analyze(self, audio_chunk=None, face_landmarks=None) -> EmotionState
    def get_current_state(self) -> EmotionState
    def reset(self)
    def set_emotion_source_enabled(self, source: str, enabled: bool)
```

### ResponseStyleAdapter

```python
class ResponseStyleAdapter:
    def adapt_to_emotion(self, emotion_state: EmotionState) -> Dict
    def get_adapted_system_prompt(self, base_prompt: str, emotion_state: EmotionState) -> str
    def get_response_delay(self, emotion_state: EmotionState) -> float
    def get_response_length_hint(self, emotion_state: EmotionState) -> str
    @staticmethod
    def get_context_for_frontend(emotion_state: EmotionState) -> Dict
```

### VoiceEmotionDetector

```python
class VoiceEmotionDetector:
    def analyze_audio_chunk(self, audio_data: np.ndarray) -> Tuple[str, float]
```

### FaceEmotionDetector

```python
class FaceEmotionDetector:
    def analyze_face(self, face_landmarks) -> Tuple[str, float]
```

---

## Support & Troubleshooting

For issues or questions:

1. Check logs in `backend/emotion/` directory
2. Review emotion state: `audio_loop.get_current_emotion()`
3. Test individual components in isolation
4. Disable emotion AI to confirm it's not the culprit
5. Open an issue with logs and audio samples

---

**Last Updated**: January 28, 2026  
**Emotion AI Version**: 1.0  
**ADA V2 Compatibility**: v2.0+

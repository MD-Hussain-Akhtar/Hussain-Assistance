# Half-Duplex Voice Architecture Implementation

## Overview
Successfully implemented a half-duplex voice architecture for ZOYA where the microphone automatically pauses when ADA speaks and resumes when ADA finishes. This eliminates feedback loops at the architectural level rather than through filtering.

## Architecture

### Full-Duplex (Previous - Problematic)
```
User Speaking → STT → Model
      ↓
    (Model processes simultaneously)
      ↓
Model Speaking → TTS → Speaker
      ↓
Speaker Output → Microphone (ECHO!) → STT → Back to Model (LOOP!)
```

### Half-Duplex (New - Fixed)
```
User Speaking (Mic ON) → STT → Model
      ↓
Model Processes
      ↓
Model Speaking (Mic PAUSED) → TTS → Speaker
      ↓
Speaker Finishes
      ↓
User Speaking (Mic RESUMED) → STT → Model
```

## Implementation Details

### 1. Backend State Management (`backend/ada.py`)

**State Variables Added (Lines 245-250):**
```python
self.assistant_speaking = False         # Track if ADA is currently speaking
self._ada_output_started = False        # Prevent multiple pause calls
self._ada_output_text = ""              # Accumulate ADA's full output
```

**Control Method Added (Lines 331-350):**
```python
def set_assistant_speaking(self, speaking):
    """
    HALF-DUPLEX VOICE CONTROL
    When ADA starts speaking: Pause microphone input
    When ADA finishes: Resume microphone input
    """
    # Pauses microphone when speaking=True
    # Resumes microphone when speaking=False
    # Emits state change to frontend via callback
```

**Auto-Pause Trigger (Lines 733-738):**
- Located in `receive_audio()` → `output_transcription` handler
- When ADA first starts speaking (detects output_transcription delta):
  - Calls `set_assistant_speaking(True)`
  - Sets `_ada_output_started = True` (prevents repeated pauses)
  - Accumulates output text in `_ada_output_text`

**Auto-Resume Trigger (Lines 1175-1179):**
- Located at end of `async for response in turn:` loop
- When response loop completes (turn is done):
  - Calls `set_assistant_speaking(False)` if currently speaking
  - Resets `_ada_output_started = False` for next turn
  - Clears `_ada_output_text` for next turn

### 2. Backend Event Emission (`backend/server.py`)

**New Callback Function (Lines 268-271):**
```python
def on_assistant_speaking(data):
    """Emit assistant speaking state to frontend via Socket.IO"""
    speaking = data.get('speaking', False)
    asyncio.create_task(sio.emit('assistant_speaking', {'speaking': speaking}))
```

**Callback Signature Updated (Line 215):**
- Added `on_assistant_speaking=None` parameter to AudioLoop.__init__()
- Callback is invoked whenever state changes in ada.py

**Callback Wired (Line 324):**
- AudioLoop instantiation now passes `on_assistant_speaking=on_assistant_speaking`

### 3. Frontend State Tracking (`src/App.jsx`)

**New Socket Event Listener (Lines 495-508):**
```jsx
socket.on('assistant_speaking', (data) => {
    const isSpeaking = data.speaking;
    console.log(`[HALF-DUPLEX] ADA is ${isSpeaking ? 'SPEAKING' : 'DONE SPEAKING'}`);
    
    // Visual feedback (optional UI updates)
    if (isSpeaking) {
        console.log("[HALF-DUPLEX] Microphone DISABLED");
    } else {
        console.log("[HALF-DUPLEX] Microphone ENABLED");
    }
});
```

## Flow Sequence

### Scenario: Normal Conversation

1. **User Speaks**
   - Microphone is ON (default state)
   - STT captures user input
   - Socket emits 'transcription' event with sender='User'
   - Model receives user input

2. **Model Processes and Responds**
   - Model starts generating response
   - First output_transcription delta arrives
   - Backend detects output_transcription → calls `set_assistant_speaking(True)`
   - Microphone is PAUSED (set_paused=True)
   - Backend emits 'assistant_speaking' event with speaking=True
   - Frontend receives event → logs mic disabled state

3. **Model Finishes Speaking**
   - Response loop `async for response in turn:` completes
   - Backend executes code after loop:
     - Checks `if self.assistant_speaking: self.set_assistant_speaking(False)`
     - Microphone is RESUMED (set_paused=False)
     - Backend emits 'assistant_speaking' event with speaking=False
     - Frontend receives event → logs mic enabled state
   - Model waits for user input

4. **Cycle Repeats**
   - User can speak again
   - Microphone is ON and ready

## Key Features

### ✅ Automatic Pause/Resume
- No manual intervention needed
- Pausing happens on first output_transcription
- Resuming happens when response loop completes

### ✅ Prevents Echo Loops
- Microphone is OFF while ADA speaks
- ADA cannot hear its own output
- No echo to detect or filter
- Architectural solution (not filtering)

### ✅ State Consistency
- `_ada_output_started` prevents multiple pause calls
- Text accumulation allows tracking turn completion
- Reset at turn end prevents state leaks

### ✅ Frontend Awareness
- Frontend receives 'assistant_speaking' events
- Can optionally disable UI input controls during ADA speaking
- Can show visual indicator of mic state

## Testing Checklist

### Unit Level
- [ ] Verify `set_assistant_speaking(True)` pauses audio
- [ ] Verify `set_assistant_speaking(False)` resumes audio
- [ ] Verify state flags reset correctly between turns

### Integration Level
- [ ] Normal conversation flow (user → model → user)
- [ ] Multiple sentences from ADA (verify pause lasts full response)
- [ ] Rapid back-and-forth (verify mic pauses/resumes correctly)
- [ ] Tool calls during conversation (verify mic control not affected)

### Edge Cases
- [ ] User interrupts while ADA speaking (pause should hold)
- [ ] Very short ADA responses (pause/resume happens quickly)
- [ ] Multiple rapid outputs (verify _ada_output_started prevents multiple pauses)
- [ ] Network delays (verify turn end detection is robust)

### Audio Quality
- [ ] No audio glitches during pause transitions
- [ ] Mic resumes cleanly without pops/clicks
- [ ] No STT interference during pause

## Debugging

### Logs to Monitor

**Backend (ada.py):**
```
[ADA DEBUG] [HALF-DUPLEX] ADA START SPEAKING → Pausing microphone
[ADA DEBUG] [HALF-DUPLEX] ADA STOP SPEAKING → Resuming microphone
```

**Backend (server.py):**
```
[HALF-DUPLEX] Assistant speaking state: True
[HALF-DUPLEX] Assistant speaking state: False
```

**Frontend (App.jsx):**
```
[HALF-DUPLEX] ADA is SPEAKING
[HALF-DUPLEX] ADA is DONE SPEAKING
[HALF-DUPLEX] Microphone DISABLED
[HALF-DUPLEX] Microphone ENABLED
```

### Quick Test Commands

```bash
# Start backend
cd backend
python server.py

# Watch for half-duplex logs
grep "HALF-DUPLEX" <log-file>
```

## Files Modified

1. **backend/ada.py**
   - Lines 215: Added `on_assistant_speaking` parameter
   - Lines 245-250: State variables
   - Lines 331-350: `set_assistant_speaking()` method
   - Lines 733-738: Auto-pause trigger
   - Lines 1175-1179: Auto-resume trigger

2. **backend/server.py**
   - Lines 268-271: `on_assistant_speaking()` callback
   - Line 215: Updated AudioLoop constructor signature
   - Line 324: Pass callback to AudioLoop

3. **src/App.jsx**
   - Lines 495-508: New Socket event listener

## Status

✅ **COMPLETE** - Half-duplex architecture fully implemented

- Backend state management: ✅ Done
- Backend event emission: ✅ Done  
- Frontend state tracking: ✅ Done
- Auto-pause on output start: ✅ Done
- Auto-resume on turn completion: ✅ Done
- Documentation: ✅ Done

**Next Step:** Test complete flow with backend/frontend restart

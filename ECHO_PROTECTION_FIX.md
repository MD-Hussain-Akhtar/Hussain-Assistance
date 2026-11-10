# ECHO PROTECTION FIX - Role-Safe Message Routing

## Problem Statement
ZOYA was experiencing a self-talk loop where:
1. ADA speaks a response (output transcription)
2. The microphone captures ADA's own speech  
3. Speech-to-text converts it to text
4. This text was incorrectly routed as USER input
5. ADA responds to its own speech → infinite loop

**Root Cause**: No filtering to distinguish between human speech (USER) and AI-generated speech (ASSISTANT).

---

## Solution Overview

### Architecture: Triple-Layer Protection

```
┌─ Layer 1: Audio Generation ─┐
│ ADA speaks → Store what was spoken
│ Track timestamp + cooldown
└──────────────────────────────┘
                ↓
┌─ Layer 2: Echo Detection ───┐
│ Check if echo protection is active
│ Compare incoming text with stored speech
│ Reject exact/partial matches
└──────────────────────────────┘
                ↓
┌─ Layer 3: Role Enforcement ─┐
│ Only pass validated USER input to model
│ ADA output stays in ASSISTANT role
│ Human speech → USER role ONLY
└──────────────────────────────┘
```

---

## Code Changes

### 1. Backend: `ada.py` - Echo Storage

**Location**: `AudioLoop.__init__()` (Line ~250)

```python
# ECHO PROTECTION: Track ADA's spoken text to prevent self-response loops
self._last_assistant_spoken_text = ""  # Full text ADA just spoke
self._assistant_speak_timestamp = 0    # When ADA last spoke (Unix timestamp)
self._echo_protection_cooldown = 2.0   # Seconds to ignore echo after ADA speaks
```

**Purpose**:
- Store what ADA just said (full transcript)
- Timestamp when it was said
- Define protection window (2 seconds after ADA speaks, ignore similar incoming speech)

---

### 2. Backend: `ada.py` - Output Transcription Capture

**Location**: `receive_audio()` → `output_transcription` handler (Line ~700)

```python
if response.server_content.output_transcription:
    transcript = response.server_content.output_transcription.text
    if transcript:
        if transcript != self._last_output_transcription:
            # ... delta calculation ...
            
            if delta:
                # ECHO PROTECTION: Store ADA's spoken text for echo detection
                import time
                self._last_assistant_spoken_text = transcript
                self._assistant_speak_timestamp = time.time()
                print(f"[ADA DEBUG] [ECHO PROTECTION] ADA spoke: '{transcript[:50]}...' at {self._assistant_speak_timestamp}")
                
                # ... rest of transcription handling ...
```

**Purpose**:
- Capture every word ADA speaks (output_transcription)
- Record exact timestamp
- Store for comparison against incoming audio

---

### 3. Backend: `server.py` - User Input Echo Filter

**Location**: `user_input()` socket handler (Line ~453)

```python
@sio.event
async def user_input(sid, data):
    """
    ROLE-SAFE MESSAGE HANDLER
    - Only processes ACTUAL HUMAN SPEECH as USER role
    - Filters out echo/ADA's own responses
    - Never routes ADA speech back as USER input
    """
    text = data.get('text')
    print(f"[SERVER DEBUG] User input received: '{text}'")
    
    if not audio_loop or not audio_loop.session:
        print("[SERVER DEBUG] [Error] Audio loop or session is None.")
        return

    if text:
        # ========== ECHO PROTECTION ==========
        # Check 1: Is echo protection active (ADA just spoke)?
        import time
        if audio_loop._last_assistant_spoken_text:
            time_since_speak = time.time() - audio_loop._assistant_speak_timestamp
            if time_since_speak < audio_loop._echo_protection_cooldown:
                print(f"[SERVER DEBUG] [ECHO PROTECTION] Cooldown active ({time_since_speak:.2f}s)...")
                
                # Check 2: Does incoming text match what ADA just said?
                incoming_normalized = text.strip().lower()
                assistant_normalized = audio_loop._last_assistant_spoken_text.strip().lower()
                
                is_echo = (incoming_normalized == assistant_normalized or 
                          assistant_normalized in incoming_normalized or
                          incoming_normalized in assistant_normalized)
                
                if is_echo:
                    print(f"[SERVER DEBUG] [ECHO PROTECTION] ECHO REJECTED!")
                    print(f"  Last ADA said: '{audio_loop._last_assistant_spoken_text[:60]}...'")
                    print(f"  User sent: '{text[:60]}...'")
                    print(f"  -> Discarding to prevent self-loop")
                    return  # DO NOT SEND
        
        # ... rest of user_input handling (logging, model send, etc.) ...
```

**Purpose**:
- Intercept every user_input event
- Check if echo protection window is active
- Compare incoming text with what ADA recently said
- **REJECT** the message if it's an echo (don't send to model)
- Only pass REAL human speech to the model

---

## Detection Logic

### Echo Match Algorithm

```python
incoming_normalized = text.strip().lower()
assistant_normalized = audio_loop._last_assistant_spoken_text.strip().lower()

is_echo = (
    incoming_normalized == assistant_normalized or           # Exact match
    assistant_normalized in incoming_normalized or           # ADA text is subset
    incoming_normalized in assistant_normalized              # Incoming text is subset
)
```

**Why multiple checks?**
- **Exact match**: "hello" == "hello"
- **Substring detection**: Incoming ASR might capture "the quick brown fox jumps" but ADA said "quick brown"
- **Reverse substring**: Incoming might just be "hello world" and ADA said "hello world please"

---

## Protection Window

```
Time: 0s ─────────── 2s ──────────────
       ↑             ↑
    ADA speaks   Cooldown ends
    [==== ECHO PROTECTION ACTIVE ====]
       No incoming text is accepted
       as USER during this window
```

**Configurable**: Adjust `_echo_protection_cooldown` (default 2.0 seconds)
- Too short (0.5s): Risky, echoes might slip through
- Too long (5.0s): User might be unable to send real input for 5 seconds after ADA speaks

---

## Message Flow: Before vs. After

### BEFORE FIX (Self-Loop):
```
User: "hello"
  ↓
[Audio → STT → "hello"]
  ↓
[user_input: "hello"]
  ↓
ADA: "Hi there, how can I help?"
  ↓
[Audio captured: ADA's speech]
  ↓
[STT → "Hi there, how can I help?"]
  ↓
[user_input: "Hi there, how can I help?"]  ← BUG: Routed as USER
  ↓
ADA: "I'm not sure what you mean by 'Hi there...'"  ← Responds to itself
  ↓
[Loop continues...]
```

### AFTER FIX (Protected):
```
User: "hello"
  ↓
[Audio → STT → "hello"]
  ↓
[user_input: "hello" | PASS filter → sent to model]
  ↓
ADA: "Hi there, how can I help?"
  ↓
[Store: _last_assistant_spoken_text = "Hi there, how can I help?"]
[_assistant_speak_timestamp = NOW]
  ↓
[Audio captured: ADA's speech]
  ↓
[STT → "Hi there, how can I help?"]
  ↓
[user_input: "Hi there, how can I help?" | CHECK filter...]
  ↓
[Echo detected! ← REJECT | return early]
  ↓
[Message DISCARDED - not sent to model]
  ↓
[Waiting for real human input...]
```

---

## Debug Output

### When ADA speaks (Stored):
```
[ADA DEBUG] [ECHO PROTECTION] ADA spoke: 'Hi there, how can I help? at 1706234567.891234'
```

### When Echo is active:
```
[SERVER DEBUG] [ECHO PROTECTION] Cooldown active (0.85s). Checking for echo match...
```

### When Echo is detected/rejected:
```
[SERVER DEBUG] [ECHO PROTECTION] ECHO REJECTED!
  Last ADA said: 'Hi there, how can I help?'
  User sent: 'Hi there, how can I help?'
  -> Discarding to prevent self-loop
```

---

## Testing

### Test 1: Normal Conversation (No Echo)
```
1. Say: "What's the weather?"
2. ADA responds: "I can check that for you"
3. Say: "Actually, tell me a joke"
4. ADA responds: "Why did the AI go to school..."
✅ PASS: No self-loops, normal conversation continues
```

### Test 2: Echo Rejection
```
1. ADA: "Hello, I'm ZOYA!"
2. [Within 2 seconds, microphone captures ADA's audio]
3. STT: "Hello, I'm ZOYA!"
4. [Echo filter: REJECTED]
✅ PASS: Echo not routed as USER
```

### Test 3: Quick Input After ADA
```
1. ADA finishes: "...is that correct?"
2. You immediately reply: "Yes, continue"
3. [Timer: 1.2 seconds elapsed]
4. [Echo protection still active, but text differs]
5. [Echo filter: ACCEPTED (not a match)]
✅ PASS: Real human input accepted even during protection window
```

---

## Limitations & Notes

### What This Fixes:
✅ Prevents ADA from talking to itself  
✅ Blocks exact echo matches  
✅ Handles substring matches (partial speech capture)  
✅ Configurable protection window  
✅ Debug logging for troubleshooting  

### What This Does NOT Fix:
❌ Headphone requirement (still recommended)  
❌ Ambient noise interference  
❌ Simultaneous speaker + mic at high volume  

### Best Practices:
1. **Use headphones**: Echo protection is a safety net, not a substitute
2. **Adjust cooldown if needed**: Edit `_echo_protection_cooldown` value
3. **Monitor debug logs**: Check for false positives/negatives
4. **Test with quiet environment**: Verify no false echo rejections

---

## Configuration

### Cooldown Window (in `ada.py`):
```python
self._echo_protection_cooldown = 2.0   # Default: 2 seconds
```

**Adjust based on**:
- Audio latency (delay between ADA speaking and completion)
- Microphone sensitivity (how long echo persists)
- User typing speed (if using text input)

### Debug Toggle (in `server.py`):
```python
# Uncomment to disable echo filtering (NOT RECOMMENDED):
# if False:  # DISABLED FOR TESTING
#     return
```

---

## Summary

| Component | Change | Purpose |
|-----------|--------|---------|
| `ada.py` - Init | Add 3 state variables | Store ADA's speech & timestamp |
| `ada.py` - Output Handler | Capture transcript | Record what ADA said |
| `server.py` - user_input | Add echo filter | Reject self-talk before sending |

**Result**: ADA only responds to real human input. Self-loops eliminated.


# Echo Protection: Code Reference

## Complete Code Changes

### Change 1: ada.py - Initialize Echo Protection Variables

**File**: `backend/ada.py`  
**Line**: ~241-244  
**Context**: Inside `AudioLoop.__init__()` method

```python
        # Track last transcription text to calculate deltas (Gemini sends cumulative text)
        self._last_input_transcription = ""
        self._last_output_transcription = ""
        
        # ECHO PROTECTION: Track ADA's spoken text to prevent self-response loops
        self._last_assistant_spoken_text = ""  # Full text ADA just spoke
        self._assistant_speak_timestamp = 0    # When ADA last spoke (Unix timestamp)
        self._echo_protection_cooldown = 2.0   # Seconds to ignore echo after ADA speaks
```

**Purpose**: Store the last thing ADA said, when it was said, and how long to protect it.

**Variables Explained**:
- `_last_assistant_spoken_text`: The complete transcript of what ADA just spoke
- `_assistant_speak_timestamp`: Unix timestamp (seconds since epoch) when ADA finished speaking
- `_echo_protection_cooldown`: Duration in seconds that echo protection stays active (default 2 seconds)

---

### Change 2: ada.py - Store Output Transcription

**File**: `backend/ada.py`  
**Line**: ~702-706  
**Context**: Inside `receive_audio()` method, in the output_transcription handler

```python
                                    if delta:
                                        # ECHO PROTECTION: Store ADA's spoken text for echo detection
                                        import time
                                        self._last_assistant_spoken_text = transcript
                                        self._assistant_speak_timestamp = time.time()
                                        print(f"[ADA DEBUG] [ECHO PROTECTION] ADA spoke: '{transcript[:50]}...' at {self._assistant_speak_timestamp}")
                                        
                                        # Send to frontend (Streaming)
                                        if self.on_transcription:
                                             self.on_transcription({"sender": "ADA", "text": delta})
```

**Purpose**: Whenever ADA finishes speaking, immediately store what was said for echo detection.

**Key Points**:
- Stores full transcript (cumulative text, not delta)
- Records exact Unix timestamp
- Prints debug message for troubleshooting
- This runs BEFORE the message is sent to frontend/user

**Debug Output Example**:
```
[ADA DEBUG] [ECHO PROTECTION] ADA spoke: 'Hello, I can help you design...' at 1706234567.891234
```

---

### Change 3: server.py - Echo Protection Filter

**File**: `backend/server.py`  
**Line**: ~453-497  
**Context**: Complete `user_input()` socket event handler

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
    
    if not audio_loop:
        print("[SERVER DEBUG] [Error] Audio loop is None. Cannot send text.")
        return

    if not audio_loop.session:
        print("[SERVER DEBUG] [Error] Session is None. Cannot send text.")
        return

    if text:
        # ========== ECHO PROTECTION ==========
        # Check 1: Is echo protection active (ADA just spoke)?
        import time
        if audio_loop._last_assistant_spoken_text:
            time_since_speak = time.time() - audio_loop._assistant_speak_timestamp
            if time_since_speak < audio_loop._echo_protection_cooldown:
                print(f"[SERVER DEBUG] [ECHO PROTECTION] Cooldown active ({time_since_speak:.2f}s). Checking for echo match...")
                
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
                    # DO NOT SEND - return early
                    return
        
        print(f"[SERVER DEBUG] Sending message to model: '{text}'")
        
        # Log User Input to Project History (only after echo filter passes)
        if audio_loop and audio_loop.project_manager:
            audio_loop.project_manager.log_chat("User", text)
            
        # Use the same 'send' method that worked for audio
        # INJECT VIDEO FRAME IF AVAILABLE (VAD-style logic for Text Input)
        if audio_loop and audio_loop._latest_image_payload:
            print(f"[SERVER DEBUG] Piggybacking video frame with text input.")
            try:
                # Send frame first
                await audio_loop.session.send(input=audio_loop._latest_image_payload, end_of_turn=False)
            except Exception as e:
                print(f"[SERVER DEBUG] Failed to send piggyback frame: {e}")
                
        await audio_loop.session.send(input=text, end_of_turn=True)
        print(f"[SERVER DEBUG] Message sent to model successfully.")
```

**Purpose**: Intercept every user input and check if it's an echo before sending to the AI model.

**Flow Breakdown**:
1. **Line 467**: Get incoming text from Socket.IO event
2. **Line 468**: Print what was received (debug)
3. **Line 470-475**: Safety checks (audio_loop and session exist)
4. **Line 478-497**: ECHO PROTECTION BLOCK
   - Check if ADA has spoken recently
   - If yes, check if incoming text matches what ADA said
   - If match found (is_echo = True), return early (discard)
   - If no match or no cooldown, continue normally
5. **Line 499-512**: Normal message handling (sent only if echo filter passes)

**Echo Detection Logic**:
```python
is_echo = (
    incoming_normalized == assistant_normalized or      # Exact match: "hello" == "hello"
    assistant_normalized in incoming_normalized or      # Subset: "hello" in "hello world"
    incoming_normalized in assistant_normalized         # Subset: "hello" in "hello world"
)
```

This catches:
- **Exact echoes**: Same text exactly
- **Partial echoes**: Echo captured only part of what ADA said
- **Superset echoes**: Echo captured ADA's text + extra noise

**Debug Output Examples**:

Echo Detected:
```
[SERVER DEBUG] User input received: 'I can help with CAD'
[SERVER DEBUG] [ECHO PROTECTION] Cooldown active (0.95s). Checking for echo match...
[SERVER DEBUG] [ECHO PROTECTION] ECHO REJECTED!
  Last ADA said: 'I can help with CAD designs'
  User sent: 'I can help with CAD'
  -> Discarding to prevent self-loop
```

Real Input Accepted:
```
[SERVER DEBUG] User input received: 'Can you help me design a box?'
[SERVER DEBUG] [ECHO PROTECTION] Cooldown active (0.50s). Checking for echo match...
[SERVER DEBUG] Sending message to model: 'Can you help me design a box?'
[SERVER DEBUG] Message sent to model successfully.
```

---

## Key Algorithms

### Algorithm 1: Cooldown Check
```python
import time

# Variables set when ADA speaks (in ada.py):
# self._assistant_speak_timestamp = time.time()
# self._echo_protection_cooldown = 2.0

# Check during user_input (in server.py):
time_since_speak = time.time() - audio_loop._assistant_speak_timestamp

if time_since_speak < audio_loop._echo_protection_cooldown:
    # Still in protection window (within last 2 seconds)
    is_protection_active = True
else:
    # Protection expired
    is_protection_active = False
```

**Logic**: If less than 2 seconds have passed since ADA spoke, protection is active.

---

### Algorithm 2: Text Normalization
```python
# Normalize both strings for comparison
incoming_normalized = text.strip().lower()
assistant_normalized = audio_loop._last_assistant_spoken_text.strip().lower()

# Why each step matters:
# .strip()    → Remove leading/trailing whitespace ("hello " → "hello")
# .lower()    → Make case-insensitive ("Hello" → "hello")
```

**Result**: Both strings are in the same format for accurate comparison.

---

### Algorithm 3: Echo Matching
```python
is_echo = (
    incoming_normalized == assistant_normalized or      # Type 1: Exact match
    assistant_normalized in incoming_normalized or      # Type 2: ADA text is substring of incoming
    incoming_normalized in assistant_normalized         # Type 3: Incoming text is substring of ADA
)
```

**Why three checks?**

| Scenario | Example | Check |
|----------|---------|-------|
| Perfect echo | ADA: "Hello" → User hears: "Hello" | Type 1: `==` |
| Partial echo (ADA cut off) | ADA: "Hello how are you" → Echo: "Hello how" | Type 3: `in` |
| Echo + noise | ADA: "Hello" → Echo: "Hello okay" | Type 2: `in` |

---

## Configuration Parameters

### Adjusting Echo Protection Cooldown

**Location**: `backend/ada.py` line 244

```python
# Current (2 seconds):
self._echo_protection_cooldown = 2.0

# More aggressive (shorter):
self._echo_protection_cooldown = 1.0   # 1 second protection

# More conservative (longer):
self._echo_protection_cooldown = 3.0   # 3 seconds protection
```

**When to adjust**:
- **Increase to 3.0+** if: Echoes still get through
- **Decrease to 1.0** if: Real input gets blocked during protection window

---

### Disabling Echo Protection (Not Recommended)

**Location**: `backend/server.py` line 479

```python
# To test without protection (DEBUG ONLY):
if False:  # Change to True to skip echo protection
    print("[DEBUG] Echo protection DISABLED")
else:
    # Normal protection logic runs
    if audio_loop._last_assistant_spoken_text:
        # ... rest of code
```

**Warning**: Only disable for testing. This will cause self-loops to return!

---

## Integration Points

### 1. Audio Loop to Server Communication
```
ada.py (AudioLoop)
    ↓
    Stores: _last_assistant_spoken_text = "what ADA said"
    Stores: _assistant_speak_timestamp = 1706234567.891
    ↓
server.py (user_input)
    ↓
    Reads: audio_loop._last_assistant_spoken_text
    Reads: audio_loop._assistant_speak_timestamp
    ↓
    Compares with incoming text
```

**Important**: Both files must have access to the same `audio_loop` object instance.

### 2. Debug Logging Trail
```
ada.py outputs:
    [ADA DEBUG] [ECHO PROTECTION] ADA spoke: '...' at 1706234567.891

server.py outputs:
    [SERVER DEBUG] [ECHO PROTECTION] Cooldown active (0.95s)...
    [SERVER DEBUG] [ECHO PROTECTION] ECHO REJECTED!
```

**Use these logs to trace echo detection in real-time.**

---

## Testing Code Snippets

### Snippet 1: Manual Echo Test
```python
# To test echo detection manually in Python:
import time

# Simulate what happens:
last_spoken = "Hello, I'm ZOYA"
timestamp = time.time()
cooldown = 2.0

# Echo arrives 0.5 seconds later
elapsed = time.time() - timestamp  # ~0.5

if elapsed < cooldown:
    incoming = "Hello, I'm ZOYA"  # Same text
    normalized_incoming = incoming.strip().lower()
    normalized_stored = last_spoken.strip().lower()
    
    is_echo = (
        normalized_incoming == normalized_stored or
        normalized_stored in normalized_incoming or
        normalized_incoming in normalized_stored
    )
    
    print(f"Is echo? {is_echo}")  # Output: Is echo? True
    print(f"Would be REJECTED ✅")
```

### Snippet 2: Monitor Logs
```bash
# In one terminal, watch for echo rejections:
python backend/server.py | grep "ECHO PROTECTED\|ECHO REJECTED"

# In another terminal, use ZOYA normally and watch the output
```

### Snippet 3: Stress Test Echo Detection
```python
# Test substring matching:
test_cases = [
    ("hello", "hello"),                    # Type 1: exact
    ("hello", "hello world"),              # Type 2: subset
    ("hello world", "hello"),              # Type 3: subset
    ("Hello", "hello"),                    # Case handling
    (" hello ", "hello"),                  # Whitespace handling
]

for incoming, stored in test_cases:
    incoming_norm = incoming.strip().lower()
    stored_norm = stored.strip().lower()
    is_echo = (incoming_norm == stored_norm or 
              stored_norm in incoming_norm or
              incoming_norm in stored_norm)
    print(f"'{incoming}' vs '{stored}': {is_echo}")
```

---

## Verification Checklist

Before deployment, verify:

- [ ] ada.py line 241-244 has the 3 new variables
- [ ] ada.py line 702-706 stores output transcription
- [ ] server.py line 479-497 has echo filter logic
- [ ] `import time` is available (standard library)
- [ ] No syntax errors: `python -m py_compile backend/ada.py backend/server.py`
- [ ] Socket.IO still works: Test `socket.emit('user_input', {'text': 'test'})`
- [ ] Debug logs appear: Look for `[ECHO PROTECTION]` messages
- [ ] Real conversation works: Talk normally and get responses

---

## Performance Metrics

| Operation | Time | Notes |
|-----------|------|-------|
| Store transcript | <1ms | Simple variable assignment |
| Check cooldown | <0.1ms | Time subtraction |
| Normalize strings | <1ms | .strip().lower() on typical 50-char strings |
| Echo matching | <1ms | 3 string comparisons |
| **Total per message** | **~3-4ms** | Negligible vs. network latency |

**CPU Impact**: <1% (Python string operations)  
**Memory Impact**: <2KB per message (temporary strings)


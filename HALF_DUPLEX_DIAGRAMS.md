# Half-Duplex Architecture - Visual Diagrams

## 1. System State Diagram

```
┌──────────────────────┐
│   INITIAL STATE      │
│  Mic ON (paused=F)   │
│ assistant_speaking=F │
└──────────────────────┘
         │
         │ User starts speaking
         ↓
┌──────────────────────┐
│  USER SPEAKING       │
│  Mic ON, capturing   │
│ STT processing input │
└──────────────────────┘
         │
         │ STT completes, send to model
         │ Model receives input
         │ Model generates response
         ↓
┌──────────────────────┐
│ OUTPUT STARTS        │
│ First delta received │
│ Call set_assistant_  │
│ speaking(True)       │
│ Mic PAUSED           │
│ assistant_speaking=T │
└──────────────────────┘
         │
         │ Response continues
         │ (Mic stays paused)
         │ No echo possible
         ↓
┌──────────────────────┐
│  ADA SPEAKING        │
│  Mic OFF (paused=T)  │
│ TTS playing response │
│ No microphone input  │
│ No echo possible     │
└──────────────────────┘
         │
         │ Response loop ends
         │ Turn completes
         │ Call set_assistant_
         │ speaking(False)
         ↓
┌──────────────────────┐
│ OUTPUT ENDS          │
│ Mic RESUMED          │
│ Reset flags for      │
│ next turn            │
│ paused=F             │
│ assistant_speaking=F │
└──────────────────────┘
         │
         │ Ready for next turn
         │ Cycle repeats
         ↓
┌──────────────────────┐
│ READY FOR INPUT      │
│  Mic ON (paused=F)   │
│ assistant_speaking=F │
└──────────────────────┘
```

## 2. Code Execution Timeline

```
Timeline: User says "Hello"
═════════════════════════════════════════════════════════════════

T=0ms:   User starts speaking "Hello"
         ├─ Mic is ON (paused=False)
         ├─ PyAudio capturing audio
         └─ STT processing...

T=500ms: STT completes
         ├─ "Hello" detected
         ├─ Socket emits transcription: {"sender": "User", "text": "Hello"}
         ├─ Model receives input
         └─ Model generating response...

T=600ms: Model.output_transcription arrives
         ├─ First delta: "I'm"
         ├─ receive_audio() detects delta
         ├─ Checks: if not self._ada_output_started
         ├─ Calls: set_assistant_speaking(True)
         │   ├─ assistant_speaking = True
         │   ├─ set_paused(True)     ← MIC PAUSED
         │   └─ Emits callback
         └─ Server emits: {'assistant_speaking': True} to frontend

T=610ms: Model continues speaking
         ├─ More deltas arrive: "ZOYA, your"
         ├─ Accumulates in _ada_output_text
         ├─ Mic STAYS PAUSED
         └─ No echo possible!

T=1200ms: Response continues...
          ├─ "personal AI assistant"
          ├─ Mic STILL PAUSED
          └─ STT cannot capture anything

T=1500ms: Response ends
          ├─ async for response in turn: completes
          ├─ Runs code after loop
          ├─ Checks: if self.assistant_speaking
          ├─ Calls: set_assistant_speaking(False)
          │   ├─ assistant_speaking = False
          │   ├─ set_paused(False)    ← MIC RESUMED
          │   ├─ _ada_output_started = False
          │   ├─ _ada_output_text = ""
          │   └─ Emits callback
          └─ Server emits: {'assistant_speaking': False} to frontend

T=1510ms: Ready for next input
          ├─ assistant_speaking = False
          ├─ _ada_output_started = False
          ├─ Mic is ON
          └─ Listening for next user input...
```

## 3. Microphone State Timeline

```
Microphone State Throughout Conversation
═════════════════════════════════════════════════════════════════

│ Mic ON        ▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄ User Speaking ▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄
│              │                   │         │
│              ├─ Capturing audio  └─ STT → Model → Response
│              │                              │
│              │                              └─ First delta
│ Mic OFF                                      │
│  (paused)                                    ├─ set_assistant_speaking(True)
│                                              │  ▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼
│                                    ▲▲▲▲▲▲▲▲▲ Mic PAUSED ▼▼▼▼▼▼▼▼▼
│                                    │        │ (No input captured) │
│                                    │        │ (No echo possible)  │
│                                    │        │                     │
│                                    │        └─ Response loop ends
│                                    │           │
│ Mic ON        ▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲ ┘           │
│              │                              └─ set_assistant_speaking(False)
│              └─ Mic RESUMED, Ready for next input

Time ──────────────────────────────────────────────────────────────>
```

## 4. Method Call Sequence

```
Sequence Diagram: Full Conversation Cycle
═════════════════════════════════════════════════════════════════

User      STT    Model   Backend ada.py      Server.py   Frontend
 │         │      │            │                 │           │
 │─ Speak →│      │            │                 │           │
 │         │      │            │                 │           │
 │         │─ Input →│         │                 │           │
 │         │         │         │                 │           │
 │         │         │─ Respond│                 │           │
 │         │         │         │                 │           │
 │         │         │    Output Start          │           │
 │         │         │    │                      │           │
 │         │         │    ├─ set_assistant_speaking(True)
 │         │         │    │                      │           │
 │         │         │    ├─ set_paused(True)   │           │
 │         │         │    │                      │           │
 │         │         │    ├─ on_assistant_speaking()
 │         │         │    │    │                 │           │
 │         │         │    │    ├─ emit event    │           │
 │         │         │    │    │    │            │           │
 │         │         │    │    │    ├─ 'assistant_speaking' →│
 │         │         │    │    │    │            │           │
 │         │         │    │    │    │            │    Receive │
 │         │         │    │    │    │            │    │       │
 │         │         │    │    │    │            │    └─ Log & Update
 │         │         │    │ (Mic paused - no echo!)  │
 │ ❌ Cannot hear    │    │                          │
 │   ADA's voice      │    │                          │
 │         │         │    │ Response continues...     │
 │         │         │    │                          │
 │         │         │  Response Complete           │
 │         │         │    │                          │
 │         │         │    ├─ set_assistant_speaking(False)
 │         │         │    │                          │
 │         │         │    ├─ set_paused(False)  │    │
 │         │         │    │                      │    │
 │         │         │    ├─ on_assistant_speaking()
 │         │         │    │    │                 │    │
 │         │         │    │    ├─ emit event    │    │
 │         │         │    │    │    │            │    │
 │         │         │    │    │    ├─ 'assistant_speaking' →│
 │         │         │    │    │    │            │           │
 │         │         │    │    │    │            │    Receive │
 │         │         │    │    │    │            │    │       │
 │         │         │    │    │    │            │    └─ Log & Update
 │         │         │    │    │    │            │           │
 │ ✓ Can speak again │    │    │    │            │    Mic ON  │
 │─ Speak →│         │    │    │    │            │           │
 │         │─ Input →│    │    │    │            │           │
 │         │         │    │    │    │            │           │
 │         │         │─ Respond│ (Cycle repeats)│           │
 │         │         │    │    │    │            │           │
```

## 5. State Variable Transitions

```
State Variable Flow
═════════════════════════════════════════════════════════════════

┌─ assistant_speaking ─────┐     ┌─ _ada_output_started ─┐
│  (Boolean)               │     │  (Boolean)            │
│  Tracks if ADA speaking  │     │  Prevents double-pause│
│                          │     │                       │
│  Initial: False          │     │  Initial: False       │
│         │                │     │         │             │
│         ├─ User input    │     │         ├─ User input │
│         │   (no change)  │     │         │   (no change)
│         │                │     │         │             │
│         ├─ Output starts │     │         ├─ Output     │
│         │   → True       │     │         │   starts    │
│         │                │     │         │   → True    │
│         │                │     │         │             │
│         ├─ ADA speaking  │     │         ├─ Response   │
│         │   (stays True) │     │         │   continues │
│         │                │     │         │   (stays T) │
│         │                │     │         │             │
│         ├─ Response ends │     │         ├─ Loop ends  │
│         │   → False      │     │         │   → False   │
│         │                │     │         │             │
│         └─ Ready again   │     │         └─ Ready again│

┌─ _ada_output_text ───────────────┐
│  (String)                        │
│  Accumulates ADA's response      │
│                                  │
│  Initial: ""                     │
│         │                        │
│         ├─ User input            │
│         │   (no change)          │
│         │                        │
│         ├─ Output arrives        │
│         │   += "I'm "            │
│         │                        │
│         ├─ More output           │
│         │   += "ZOYA, your "     │
│         │                        │
│         ├─ Response continues    │
│         │   += "AI assistant..."  │
│         │                        │
│         ├─ Loop ends             │
│         │   = ""  (reset)        │
│         │                        │
│         └─ Ready again           │
```

## 6. Backend Flow: From Output to Resume

```
receive_audio() Method Flow
═════════════════════════════════════════════════════════════════

while True:                                    # Main loop
    turn = self.session.receive()              # Get response iter
    
    async for response in turn:                # Loop: <─── ENTER
        │
        ├─ if data := response.data:
        │   └─ Enqueue audio output
        │
        ├─ if response.server_content:
        │   │
        │   ├─ if response.server_content.input_transcription:
        │   │   └─ User speaking (send to frontend)
        │   │
        │   ├─ if response.server_content.output_transcription:
        │   │   ├─ if delta and not _ada_output_started:
        │   │   │   ├─ set_assistant_speaking(True)  ← PAUSE MIC
        │   │   │   └─ _ada_output_started = True
        │   │   │
        │   │   └─ _ada_output_text += delta
        │   │
        │   └─ # Flush buffer...
        │
        └─ if response.tool_call:
            └─ Handle tool calls...
                                               # Loop: <─── EXIT
    
    # After loop completes:
    self.flush_chat()
    
    # HALF-DUPLEX: Resume if we paused
    if self.assistant_speaking:
        set_assistant_speaking(False)          ← RESUME MIC
        _ada_output_started = False            ← RESET FLAG
        _ada_output_text = ""                  ← CLEAR TEXT
    
    # Clear input queue
    while not self.audio_in_queue.empty():
        self.audio_in_queue.get_nowait()
```

## 7. Set Paused Mechanism

```
How Microphone Actually Stops Listening
═════════════════════════════════════════════════════════════════

set_paused(True):
    │
    ├─ self.paused = True
    │
    └─ In read_input_audio() loop:
        ├─ while True:
        │   │
        │   ├─ if self.paused:
        │   │   ├─ await asyncio.sleep(0.1)
        │   │   └─ continue  ← SKIP AUDIO READING
        │   │
        │   └─ # Otherwise read from PyAudio

set_paused(False):
    │
    ├─ self.paused = False
    │
    └─ In read_input_audio() loop:
        ├─ while True:
        │   │
        │   ├─ if self.paused:
        │   │   └─ (skipped)
        │   │
        │   └─ # Read from PyAudio ← MICROPHONE ACTIVE AGAIN
```

## 8. Socket.IO Event Flow

```
How State Gets to Frontend
═════════════════════════════════════════════════════════════════

Backend (ada.py)
    │
    ├─ set_assistant_speaking(True)
    │   │
    │   └─ on_assistant_speaking({"speaking": True})
    │
Backend (server.py)
    │
    ├─ on_assistant_speaking callback
    │   │
    │   └─ sio.emit('assistant_speaking', {'speaking': True})
    │
WebSocket
    │
    └─ Message: {type: 'assistant_speaking', data: {speaking: True}}
    
Frontend (App.jsx)
    │
    ├─ socket.on('assistant_speaking', (data) => {...})
    │   │
    │   └─ console.log([HALF-DUPLEX] ADA is SPEAKING)
    │
UI
    │
    └─ Optional: Update mic indicator, disable controls, etc.
```

## 9. Error Prevention

```
Idempotency: Preventing Double-Pause
═════════════════════════════════════════════════════════════════

Problem: What if multiple deltas arrive?
         Each could call set_assistant_speaking(True)

Solution: _ada_output_started flag

Flow:

First delta arrives:
    if not self._ada_output_started:  ← True initially
        set_assistant_speaking(True)
        _ada_output_started = True    ← Set to True
        
Second delta arrives:
    if not self._ada_output_started:  ← Now False
        # (SKIPPED)
        
    self._ada_output_text += delta

Third delta arrives:
    if not self._ada_output_started:  ← Still False
        # (SKIPPED)
        
    self._ada_output_text += delta

Result: set_assistant_speaking(True) called only once! ✓
```

These diagrams provide visual reference for understanding the complete half-duplex flow.

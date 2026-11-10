# Half-Duplex Voice Testing Guide

## Quick Start Test

### 1. Start the Backend
```bash
cd backend
python server.py
```

Watch for logs:
- `[HALF-DUPLEX] Assistant speaking state: True` (when ADA starts)
- `[HALF-DUPLEX] Assistant speaking state: False` (when ADA stops)

### 2. Start the Frontend
In another terminal:
```bash
npm run dev
```

Open browser and watch console:
- `[HALF-DUPLEX] ADA is SPEAKING` (when ADA starts responding)
- `[HALF-DUPLEX] ADA is DONE SPEAKING` (when ADA finishes)
- `[HALF-DUPLEX] Microphone DISABLED` (mic paused)
- `[HALF-DUPLEX] Microphone ENABLED` (mic resumed)

### 3. Test Normal Conversation

**Test 1: Simple Query**
1. Say: "Hello, what's your name?"
2. ADA responds: "I'm ZOYA, an AI assistant..."
3. Observe: Mic should pause during response, resume when ADA finishes

**Expected Logs:**
```
Backend ada.py:
[ADA DEBUG] [HALF-DUPLEX] ADA START SPEAKING → Pausing microphone
[ADA DEBUG] [HALF-DUPLEX] ADA STOP SPEAKING → Resuming microphone

Backend server.py:
[HALF-DUPLEX] Assistant speaking state: True
[HALF-DUPLEX] Assistant speaking state: False

Frontend App.jsx:
[HALF-DUPLEX] ADA is SPEAKING
[HALF-DUPLEX] Microphone DISABLED
[HALF-DUPLEX] ADA is DONE SPEAKING
[HALF-DUPLEX] Microphone ENABLED
```

**Test 2: Multi-Sentence Response**
1. Say: "Can you help me with a project?"
2. ADA provides multi-sentence response
3. Observe: Mic stays paused throughout entire response, resumes only at end

**Test 3: Rapid Back-and-Forth**
1. Say: "What's the weather?"
2. ADA responds
3. Quickly say: "And tomorrow?"
4. ADA responds again
5. Observe: Each cycle has proper pause/resume

## Advanced Tests

### Test 4: Tool Calls
1. Say: "Create a CAD model of a box"
2. ADA may call tool, then respond
3. Observe: Mic control continues correctly through tool execution

### Test 5: Audio Quality
1. Listen for clean mic pause/resume transitions
2. Check for audio glitches or pops during state changes
3. Verify no double-speaking or overlapping audio

### Test 6: Long Responses
1. Ask ADA a question requiring a detailed, multi-paragraph answer
2. Observe: Mic stays paused until all text is finished
3. No interruption possible by external noise

## Troubleshooting

### Issue: Mic never pauses
**Check:**
- Backend ada.py lines 733-738: `set_assistant_speaking(True)` called?
- Backend server.py: `on_assistant_speaking()` callback defined?
- Look for error logs in backend console

### Issue: Mic pauses but doesn't resume
**Check:**
- Backend ada.py lines 1175-1179: Code after response loop?
- Is `self.assistant_speaking` True when loop ends?
- Look for error logs in backend console

### Issue: Frontend doesn't show state
**Check:**
- Backend emitting 'assistant_speaking' event? (check backend logs)
- Frontend listening for event? (src/App.jsx lines 495-508)
- Browser console showing logs? (check browser DevTools)

### Issue: State gets stuck
**Check:**
- Is `_ada_output_started` being reset? (should reset to False at end)
- Run simple test: "Hello" (short response) vs "Tell me about..." (long response)
- If stuck on short, reset flags may not be triggering

## Performance Checks

### Response Time
- Time between "ADA START SPEAKING" and actual pause
- Should be <100ms for imperceptible delay

### Pause Duration
- Verify mic stays paused entire duration of response
- Verify no premature resume

### Resume Timing
- Verify mic resumes immediately after turn completes
- Not too fast (would interrupt output)
- Not too slow (would prevent user from speaking)

## State Validation

### Check State Flags
In backend ada.py, these should flow:

**Initial State:**
```
assistant_speaking = False
_ada_output_started = False
_ada_output_text = ""
```

**During ADA Response:**
```
assistant_speaking = True
_ada_output_started = True
_ada_output_text = "ADA's response text..."
```

**After Response Completes:**
```
assistant_speaking = False
_ada_output_started = False
_ada_output_text = ""
```

## Monitoring Commands

### Watch Backend Logs
```bash
# Terminal 1: Start server with verbose output
python server.py 2>&1 | grep "HALF-DUPLEX"

# Shows: [HALF-DUPLEX] events as they happen
```

### Watch Frontend Logs
```javascript
// In browser console, filter for:
[HALF-DUPLEX]

// Shows: Frontend event listeners firing
```

### Check Mic State
Listen to actual audio capture:
1. Notice when audio input stops (during ADA response)
2. Notice when audio input resumes (after ADA finishes)
3. Try to interrupt ADA while speaking (should fail if mic properly paused)

## Validation Checklist

- [ ] Backend starts without errors
- [ ] Frontend starts without errors
- [ ] First query: ADA responds with mic paused
- [ ] First response completes: Mic resumes
- [ ] Second query: Mic accepts new input
- [ ] Log messages appear as expected
- [ ] Frontend console shows [HALF-DUPLEX] events
- [ ] No audio glitches during pause/resume
- [ ] Cannot interrupt ADA while speaking (mic properly paused)
- [ ] Can speak immediately after ADA finishes

## Success Criteria

✅ **Pass** if:
- Mic consistently pauses when ADA starts speaking
- Mic consistently resumes when ADA finishes
- No feedback loops or echo detected
- Conversation flows naturally
- All logs appear as documented
- No errors in backend/frontend consoles

❌ **Fail** if:
- Mic remains paused (never resumes)
- Mic never pauses (always on)
- State gets stuck in inconsistent state
- Audio glitches appear
- Errors appear in console
- Feedback loops still detected

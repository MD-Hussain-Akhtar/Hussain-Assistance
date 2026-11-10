# Half-Duplex Quick Reference Guide

## Files Modified

```
ada.py        - Backend state management + triggers
server.py     - Backend event emission
App.jsx       - Frontend event listener
```

## Key Code Locations

### Backend (ada.py)
- **Line 215**: `on_assistant_speaking` parameter
- **Lines 245-250**: State variables (assistant_speaking, _ada_output_started, _ada_output_text)
- **Lines 331-350**: `set_assistant_speaking()` method
- **Lines 733-738**: Auto-pause trigger (output_transcription)
- **Lines 1175-1179**: Auto-resume trigger (turn completion)

### Backend (server.py)
- **Lines 268-271**: `on_assistant_speaking()` callback
- **Line 324**: Pass callback to AudioLoop

### Frontend (App.jsx)
- **Lines 495-508**: Socket.IO event listener

## Quick Test Commands

### Start Backend
```bash
cd backend
python server.py
```

### Start Frontend
```bash
npm run dev
```

### Monitor Half-Duplex Logs (Backend)
```bash
# In new terminal, watch for HALF-DUPLEX logs
tail -f <log-file> | grep "HALF-DUPLEX"
```

### Monitor Socket Events (Frontend)
```javascript
// In browser console, type:
socket.on('assistant_speaking', (data) => console.log('[WATCH]', data));
```

## Test Scenarios

### Basic Test
1. Start backend: `python server.py`
2. Start frontend: `npm run dev`
3. Say: "Hello"
4. Check logs for [HALF-DUPLEX] messages
5. Verify mic pauses/resumes

### Expected Log Output

**Backend Start:**
```
AudioLoop initialized successfully.
Creating asyncio task for AudioLoop.run()
```

**During First Query:**
```
[ADA DEBUG] [HALF-DUPLEX] ADA START SPEAKING → Pausing microphone
[HALF-DUPLEX] Assistant speaking state: True
```

**After Response:**
```
[ADA DEBUG] [HALF-DUPLEX] ADA STOP SPEAKING → Resuming microphone
[HALF-DUPLEX] Assistant speaking state: False
```

**Frontend Console:**
```
[HALF-DUPLEX] ADA is SPEAKING
[HALF-DUPLEX] Microphone DISABLED
[HALF-DUPLEX] ADA is DONE SPEAKING
[HALF-DUPLEX] Microphone ENABLED
```

## State Flow Quick Diagram

```
Initial: Mic ON
    ↓
User Speaks (Mic ON, capturing)
    ↓
STT Complete → Send to Model
    ↓
Output Starts (First Delta)
    ↓
AUTO-PAUSE: set_assistant_speaking(True)
    ↓
Mic OFF (No input possible)
    ↓
ADA Speaks (Response)
    ↓
Response Loop Ends
    ↓
AUTO-RESUME: set_assistant_speaking(False)
    ↓
Mic ON (Ready for next input)
    ↓
(Cycle Repeats)
```

## Method Signatures

### Main Control Method
```python
def set_assistant_speaking(self, speaking: bool):
    """
    Pause mic when speaking=True
    Resume mic when speaking=False
    Emits state change to frontend
    """
```

### Callback Signature
```python
def on_assistant_speaking(data: dict):
    # data = {"speaking": True/False}
    # Emit to frontend via Socket.IO
```

### Socket Event
```javascript
socket.on('assistant_speaking', (data) => {
    // data = {speaking: true/false}
    // Update frontend state
});
```

## State Variables

| Variable | Type | Initial | Purpose |
|----------|------|---------|---------|
| `assistant_speaking` | bool | False | Current mic state |
| `_ada_output_started` | bool | False | Prevent double-pause |
| `_ada_output_text` | str | "" | Accumulate response |

## Debug Commands

### Check State in Running System
```python
# If you had REPL access to ada instance:
print(ada.assistant_speaking)       # Should toggle True/False
print(ada._ada_output_started)      # Should reset to False
print(len(ada._ada_output_text))    # Should accumulate then clear
```

### Check Paused State
```python
print(ada.paused)  # Should be True when speaking, False when listening
```

### Verify Callback
```python
print(ada.on_assistant_speaking)  # Should show callback function
```

## Common Issues & Quick Fixes

| Issue | Fix |
|-------|-----|
| Mic never pauses | Restart backend - check output_transcription handler |
| Mic never resumes | Check response loop end - line 1175 |
| Double pause | Verify `_ada_output_started` guard is in place |
| Events not reaching frontend | Check server.py line 324 callback wiring |
| Frontend not updating | Check App.jsx socket listener exists |

## Performance Check

### Expected Timing
- Pause latency: <100ms from first output
- Resume latency: <100ms from response complete
- No additional computation overhead

### Audio Quality
- No glitches during pause
- No pops/clicks on resume
- Clean transitions

## Monitoring Checklist

Before test:
- [ ] Backend syntax valid (checked ✓)
- [ ] Frontend syntax valid (checked ✓)
- [ ] All callbacks wired (checked ✓)

During test:
- [ ] Backend logs show state changes
- [ ] Frontend console shows events
- [ ] Mic demonstrably stops/starts

After test:
- [ ] No errors in console
- [ ] No feedback loops
- [ ] Conversation natural

## Toggle Logging

### Increase Logging (if needed)
In `set_assistant_speaking()`, it already logs:
```python
print("[ADA DEBUG] [HALF-DUPLEX] ...")
```

### Reduce Logging (if too verbose)
Comment out in set_assistant_speaking() if desired, but keep for now for testing.

## Reset System

If something gets stuck:
```bash
# Kill backend
Ctrl+C

# Kill frontend  
Ctrl+C

# Restart backend
python server.py

# Restart frontend
npm run dev
```

## Files to Keep Open During Testing

1. **Backend Console** - Watch for [HALF-DUPLEX] logs
2. **Frontend Console** - Watch for [HALF-DUPLEX] logs and errors
3. **Server Output** - Watch for state changes
4. **Code (optional)** - Reference implementation during test

## Success Indicators

You know it's working when:

```
Backend logs:
✓ [ADA DEBUG] [HALF-DUPLEX] ADA START SPEAKING → Pausing microphone
✓ [HALF-DUPLEX] Assistant speaking state: True
✓ [ADA DEBUG] [HALF-DUPLEX] ADA STOP SPEAKING → Resuming microphone
✓ [HALF-DUPLEX] Assistant speaking state: False

Frontend logs:
✓ [HALF-DUPLEX] ADA is SPEAKING
✓ [HALF-DUPLEX] Microphone DISABLED
✓ [HALF-DUPLEX] ADA is DONE SPEAKING
✓ [HALF-DUPLEX] Microphone ENABLED

Behavior:
✓ Cannot interrupt ADA (mic is paused)
✓ Can speak after ADA finishes
✓ No echo or feedback
✓ Natural conversation flow
```

## Implementation Summary

```
What: Half-duplex voice architecture
Why: Prevent audio/text feedback loops
How: Pause mic when ADA speaks, resume when done
Where: ada.py (pause/resume), server.py (emit), App.jsx (listen)
Status: ✅ COMPLETE & READY FOR TESTING
```

## Next Steps

1. ✅ Code implemented
2. ✅ Syntax validated
3. ✅ Documentation written
4. 🔄 **Test the system** ← You are here
5. 📊 Monitor logs
6. ✓ Validate behavior
7. 🎉 Deploy if successful

## Useful References

- [HALF_DUPLEX_VOICE_IMPLEMENTATION.md](HALF_DUPLEX_VOICE_IMPLEMENTATION.md) - Full details
- [HALF_DUPLEX_COMPLETE_SUMMARY.md](HALF_DUPLEX_COMPLETE_SUMMARY.md) - Complete flow
- [HALF_DUPLEX_DIAGRAMS.md](HALF_DUPLEX_DIAGRAMS.md) - Visual diagrams
- [HALF_DUPLEX_TESTING.md](HALF_DUPLEX_TESTING.md) - Test guide
- [COMPLETION_CHECKLIST.md](COMPLETION_CHECKLIST.md) - Checklist

---

**Ready?** Start with: `python server.py` then `npm run dev`, then say "Hello"! 🚀

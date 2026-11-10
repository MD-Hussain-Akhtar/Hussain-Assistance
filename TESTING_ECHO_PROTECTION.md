# Echo Protection Testing Guide

## Quick Verification

### 1. Check Code Changes Installed
Before starting ZOYA, verify the fixes are in place:

**Check ada.py** (Line ~241):
```bash
grep "_last_assistant_spoken_text" backend/ada.py
grep "_assistant_speak_timestamp" backend/ada.py
grep "_echo_protection_cooldown" backend/ada.py
```
✅ Should show 3 variables defined

**Check ada.py** (Line ~702):
```bash
grep -n "ECHO PROTECTION: Store ADA's spoken text" backend/ada.py
```
✅ Should appear at line 702

**Check server.py** (Line ~453):
```bash
grep -n "ECHO PROTECTION.*Check 1" backend/server.py
```
✅ Should appear around line 471

---

## Test Scenarios

### Scenario 1: Normal Conversation (Baseline)
**Purpose**: Verify legitimate input still works

**Steps**:
1. Start ZOYA
2. Say: "Hello ZOYA"
3. Wait for response
4. Say: "What can you do?"
5. Wait for response

**Expected Output** (in terminal):
```
[ADA DEBUG] [ECHO PROTECTION] ADA spoke: 'Hello! I can...' at 1706234567.891
[SERVER DEBUG] User input received: 'Hello ZOYA'
[SERVER DEBUG] Sending message to model: 'Hello ZOYA'
[ADA DEBUG] [ECHO PROTECTION] ADA spoke: 'I can help you...' at 1706234568.123
[SERVER DEBUG] User input received: 'What can you do?'
[SERVER DEBUG] Sending message to model: 'What can you do?'
```

**Pass Criteria**:
- ✅ No "ECHO REJECTED" messages
- ✅ All messages sent to model (normal conversation)
- ✅ Response feels natural, no delays

---

### Scenario 2: Echo Rejection Test
**Purpose**: Verify echo is correctly detected and rejected

**Prerequisites**: 
- Speaker volume at normal level
- Microphone sensitivity at normal level
- NO HEADPHONES (so speaker echo can be captured)

**Steps**:
1. Start ZOYA
2. Let ADA say something (wait for complete response)
3. Immediately (within 2 seconds) manually repeat back what ADA said
4. Observe terminal output

**Example**:
- ZOYA: "I'm ready to help with CAD designs"
- You repeat: "I'm ready to help with CAD designs"

**Expected Output** (in terminal):
```
[ADA DEBUG] [ECHO PROTECTION] ADA spoke: 'I'm ready to help with CAD designs' at 1706234567.891
[SERVER DEBUG] User input received: 'I'm ready to help with CAD designs'
[SERVER DEBUG] [ECHO PROTECTION] Cooldown active (0.85s). Checking for echo match...
[SERVER DEBUG] [ECHO PROTECTION] ECHO REJECTED!
  Last ADA said: 'I'm ready to help with CAD designs'
  User sent: 'I'm ready to help with CAD designs'
  -> Discarding to prevent self-loop
```

**Pass Criteria**:
- ✅ Echo detected and rejected within cooldown window
- ✅ Message NOT sent to model (prevented self-talk)
- ✅ No response from ADA (message was discarded)

---

### Scenario 3: Edge Case - Partial Echo
**Purpose**: Verify partial/substring echoes are caught

**Steps**:
1. ZOYA says: "The CAD model parameters are: width, height, depth"
2. You say: "width, height, depth" (just the subset)
3. Check terminal

**Expected**:
```
[SERVER DEBUG] [ECHO PROTECTION] ECHO REJECTED!
  Last ADA said: 'The CAD model parameters are: width, height, depth'
  User sent: 'width, height, depth'
  -> Discarding to prevent self-loop
```

**Pass Criteria**:
- ✅ Partial echo caught by substring matching
- ✅ Message rejected even though it's a subset

---

### Scenario 4: Case Insensitivity Test
**Purpose**: Verify echo detection ignores case

**Steps**:
1. ZOYA says: "I UNDERSTAND"
2. You immediately repeat: "i understand" (lowercase)
3. Check terminal

**Expected**:
```
[SERVER DEBUG] [ECHO PROTECTION] ECHO REJECTED!
  Last ADA said: 'I UNDERSTAND'
  User sent: 'i understand'
  -> Discarding to prevent self-loop
```

**Pass Criteria**:
- ✅ Echo detected despite case difference
- ✅ Normalization working (.lower() comparison)

---

### Scenario 5: Cooldown Window Test
**Purpose**: Verify cooldown expires after 2 seconds

**Steps**:
1. ZOYA says: "Ready to proceed"
2. Wait 3 seconds (longer than 2-second cooldown)
3. Say: "Ready to proceed" again
4. Check terminal

**Expected Output**:
```
[ADA DEBUG] [ECHO PROTECTION] ADA spoke: 'Ready to proceed' at 1706234567.891
[Wait 3 seconds...]
[SERVER DEBUG] User input received: 'Ready to proceed'
[SERVER DEBUG] Sending message to model: 'Ready to proceed'
```

**Pass Criteria**:
- ✅ After 2+ seconds, echo protection window expires
- ✅ Same text accepted if outside cooldown
- ✅ Message goes through to model (NOT rejected)

---

### Scenario 6: Real Input During Cooldown
**Purpose**: Verify legitimate input accepted even during cooldown

**Steps**:
1. ZOYA says: "How can I help?"
2. Immediately (within 2s) say: "Help me design a box" (different from what ADA said)
3. Check terminal

**Expected**:
```
[ADA DEBUG] [ECHO PROTECTION] ADA spoke: 'How can I help?' at 1706234567.891
[SERVER DEBUG] User input received: 'Help me design a box'
[SERVER DEBUG] [ECHO PROTECTION] Cooldown active (0.85s). Checking for echo match...
[SERVER DEBUG] Sending message to model: 'Help me design a box'
```

**Pass Criteria**:
- ✅ Message passes through (not echo)
- ✅ Sent to model successfully
- ✅ ZOYA responds normally
- ✅ No false rejection

---

## Debug Log Reference

| Log Message | Meaning | Action |
|------------|---------|--------|
| `[ADA DEBUG] [ECHO PROTECTION] ADA spoke: '...'` | ZOYA just finished speaking | Normal - tracking for echo |
| `[SERVER DEBUG] [ECHO PROTECTION] Cooldown active` | Echo window is active | Checking if message is echo |
| `[SERVER DEBUG] [ECHO PROTECTION] ECHO REJECTED!` | Echo detected & blocked | Good - self-loop prevented |
| `[SERVER DEBUG] Sending message to model: '...'` | Real input accepted | Normal conversation |

---

## Performance Baseline

| Metric | Expected |
|--------|----------|
| Time to reject echo | <10ms |
| Time to accept real input | <10ms |
| Cooldown duration | 2.0 seconds |
| CPU impact | <1% |
| Memory impact | <500KB |

---

## Troubleshooting

### Problem: Echo NOT being rejected (self-loop still occurs)

**Possible Causes**:
1. **STT mismatch**: Echo captured but transcribed differently
   - Solution: Adjust echo protection cooldown in `ada.py` line 244
   
2. **Timestamp issue**: Clock skew
   - Solution: Check system time is synchronized
   
3. **Changes not loaded**: Code still loading old version
   - Solution: 
     ```bash
     pkill -f "python backend/server.py"
     python backend/server.py
     ```

**Debug Steps**:
1. Check debug logs for `[ECHO PROTECTION]` messages
2. Verify `_last_assistant_spoken_text` is being set
3. Compare normalized strings in logs manually

---

### Problem: Legitimate input being rejected (false positive)

**Possible Causes**:
1. **Cooldown too long**: 2 seconds not enough for fast speakers
   - Solution: Reduce `_echo_protection_cooldown` to 1.0
   
2. **Substring matching too aggressive**: "help" matches "helpful"
   - Solution: Add length threshold check (only reject if >80% match)

**Debug Steps**:
1. Note the exact strings in rejection log
2. Check if they're legitimately different
3. Adjust cooldown or substring logic

---

### Problem: No debug output

**Possible Causes**:
1. Debug prints not enabled
2. Python output not capturing
3. Server not running latest code

**Solution**:
```bash
# Ensure Python prints to console (no buffering)
python -u backend/server.py
```

---

## Success Criteria

✅ **Complete Success** when:
1. Normal conversation works flawlessly
2. Echo is consistently rejected
3. No false positives (legitimate input blocked)
4. No false negatives (echo slips through)
5. Cooldown behavior matches expectations
6. Debug logs are clear and consistent

🎉 **System is production-ready** when all 6 criteria pass for 5 minutes of active use


# PERMANENT MEMORY SYSTEM - ARCHITECTURE & FLOW

## System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                     ZOYA AI FRONTEND                            │
│                 (React / Electron / Web)                        │
└──────────────────────────┬──────────────────────────────────────┘
                           │
                    Socket.IO Events
                           │
        ┌──────────────────┼──────────────────┐
        │                  │                  │
        ▼                  ▼                  ▼
  voice_input        user_introduce    learn_habit
  emotion_detected   (first time)       (pattern detected)
        │                  │                  │
        └──────────────────┼──────────────────┘
                           │
                    Server.py Router
                           │
        ┌──────────────────┼──────────────────┐
        │                  │                  │
        ▼                  ▼                  ▼
  Detect Memory    Check for First   Check for
  Trigger Command  Time Registration  Habit Pattern
        │                  │                  │
        │ "yaad rakh"      │                  │
        │ "pasand hai"     │                  │
        │                  │                  │
        └──────────────────┼──────────────────┘
                           │
          ┌────────────────┼────────────────┐
          │                │                │
          ▼                ▼                ▼
    MemoryIntegration  MemoryInitializer  HabitLearner
    (handle_*)         (register_new_user) (auto-detect)
          │                │                │
          └────────────────┼────────────────┘
                           │
                   MemoryManager
                           │
          ┌────────────────┼────────────────┐
          │                │                │
          ▼                ▼                ▼
    save_permanent    recall_memory     bind_identity
    get_permanent     find_context      voice/face
          │                │                │
          └────────────────┼────────────────┘
                           │
        ┌──────────────────┼──────────────────┐
        │                  │                  │
        ▼                  ▼                  ▼
    permanent_        identity_         user_profile
    memory.json       bindings.json     emotion_history
                      (face/voice)      conversation.json
```

---

## Data Flow: Voice Command to Memory Save

```
┌──────────────────────────────────────────────────────────────────┐
│  USER VOICE INPUT: "Zoya ye yaad rakh lo: Maine CNC order kiya"  │
└──────────────────┬───────────────────────────────────────────────┘
                   │
                   ▼
        ┌─────────────────────────┐
        │  Frontend: Speech-to-Text│
        │  (Google Web Speech)     │
        └────────────┬─────────────┘
                     │
                     ▼
        ┌──────────────────────────────────┐
        │ Socket.IO emit voice_input event │
        │ {text: "...", emotion: null}     │
        └────────────┬─────────────────────┘
                     │
                     ▼
        ┌─────────────────────────────┐
        │  server.py @sio.on()        │
        │  handle_voice_input()       │
        └────────────┬────────────────┘
                     │
         ┌───────────┴───────────┐
         │                       │
         ▼                       ▼
    Check keywords:          Check keywords:
    "yaad rakh"?             "pasand hai"?
    YES                      NO
    │                        │
    ▼                        ▼
memory_integration      Check emotion
.handle_memory_         _detected
save_request()          │
    │                   ▼
    │                  ... continue
    │                  normal flow
    │
    ▼
┌──────────────────────────────────┐
│ Extract memory text:             │
│ "Maine CNC order kiya"           │
└────────────┬─────────────────────┘
             │
             ▼
┌──────────────────────────────────┐
│ memory_manager                   │
│ .on_memory_save_request()        │
│ .save_permanent_memory()         │
└────────────┬─────────────────────┘
             │
             ▼
┌──────────────────────────────────┐
│ Write to disk:                   │
│ memory/permanent_memory.json      │
│ {                                │
│   "last_learning": "Maine CNC...",
│   "learning_timestamp": "...",   │
│   "last_conversations": [...]    │
│ }                                │
└────────────┬─────────────────────┘
             │
             ▼
┌──────────────────────────────────┐
│ Socket.IO emit response:         │
│ "Bilkul, maine yaad kar liya..." │
└──────────────────────────────────┘
             │
             ▼
┌──────────────────────────────────┐
│ Frontend shows confirmation      │
│ "Memory saved!"                  │
└──────────────────────────────────┘
```

---

## Data Flow: App Startup (with Memory)

```
┌────────────────────────────────────────┐
│   APP STARTS / SERVER.PY LAUNCHES      │
└─────────────┬──────────────────────────┘
              │
              ▼
┌────────────────────────────────────────┐
│ @app.on_event("startup")               │
│ Triggered                              │
└─────────────┬──────────────────────────┘
              │
              ▼
┌────────────────────────────────────────┐
│ MemoryInitializer()                    │
│ .initialize_on_startup()               │
└─────────────┬──────────────────────────┘
              │
              ▼
┌────────────────────────────────────────┐
│ Attempt to load:                       │
│ memory/permanent_memory.json            │
└─────────────┬──────────────────────────┘
              │
    ┌─────────┴─────────┐
    │                   │
    ▼                   ▼
  FILE          FILE
  EXISTS        MISSING
    │               │
    ▼               ▼
  Load JSON    Return default
  from disk    empty structure
    │               │
    │               ▼
    │        startup_info = {
    │          "user_identified": False,
    │          "greeting": "Namaste! Aapka naam kya hai?"
    │        }
    │               │
    │               ▼
    │        FIRST-TIME USER PATH
    │        (Request name from frontend)
    │
    └─────────┬────────────┘
              │
              ▼
        Check for
        user_id and name
        in memory
              │
        ┌─────┴──────┐
        │            │
    FOUND        NOT FOUND
        │            │
        ▼            ▼
   Load user    Continue as
   context      first-time user
        │
        ▼
 ╔═════════════════════════════════════╗
 ║ GreetingEngine                      ║
 ║ .generate_greeting(                 ║
 ║   time="morning",                   ║
 ║   emotion=None,                     ║
 ║   face_recognized=False             ║
 ║ )                                   ║
 ╚═════════════════════════════════════╝
        │
        ▼
┌────────────────────────────────────────┐
│ Build greeting from:                   │
│ 1. Time of day → base greeting        │
│ 2. Sleep time habit → context         │
│ 3. Emotion history → inference        │
│ 4. Preferences → recommendations      │
└─────────────┬──────────────────────────┘
              │
              ▼
┌────────────────────────────────────────┐
│ PERSONALIZED GREETING:                 │
│ "Good morning Ayush Sir!               │
│  Kal aap late soye the,                │
│  aaj thode tired lag rahe ho.          │
│  Aapka favorite music lofi hai.        │
│  Kya sunu?"                            │
└─────────────┬──────────────────────────┘
              │
              ▼
┌────────────────────────────────────────┐
│ startup_info = {                       │
│   "user_identified": true,             │
│   "user_name": "Ayush Sir",            │
│   "greeting": "Good morning Ayush...", │
│   "context_summary": {...},            │
│   "memories_loaded": true              │
│ }                                      │
└─────────────┬──────────────────────────┘
              │
              ▼
┌────────────────────────────────────────┐
│ Frontend receives greeting             │
│ Shows personalized welcome message     │
└────────────────────────────────────────┘
```

---

## Data Flow: Preference Learning

```
┌─────────────────────────────────────────────────────┐
│ USER VOICE: "Mujhe lofi music pasand hai"          │
└────────────┬────────────────────────────────────────┘
             │
             ▼
┌─────────────────────────────────────────────────────┐
│ server.py receives voice_input event                │
│ Text: "Mujhe lofi music pasand hai"                 │
│ Emotion: null                                        │
└────────────┬────────────────────────────────────────┘
             │
             ▼
┌─────────────────────────────────────────────────────┐
│ Check for preference keywords:                      │
│ "pasand hai" or "nahi pasand" ?                     │
│ YES - Match found                                    │
└────────────┬────────────────────────────────────────┘
             │
             ▼
┌─────────────────────────────────────────────────────┐
│ memory_integration                                   │
│ .handle_preference_expression()                     │
│                                                     │
│ Regex patterns:                                     │
│ r"mujhe (.+?) pasand hai"                          │
│ Matches: "lofi music"                               │
└────────────┬────────────────────────────────────────┘
             │
             ▼
┌─────────────────────────────────────────────────────┐
│ Auto-categorize preference:                         │
│ "lofi music" → contains "music"                     │
│ Category: "music"                                   │
└────────────┬────────────────────────────────────────┘
             │
             ▼
┌─────────────────────────────────────────────────────┐
│ memory_manager                                      │
│ .on_user_preference_detected(                       │
│   category="music",                                 │
│   key="favorite_genre",                             │
│   value="lofi",                                     │
│   confidence=1.0                                    │
│ )                                                   │
└────────────┬────────────────────────────────────────┘
             │
             ▼
┌─────────────────────────────────────────────────────┐
│ memory_manager                                      │
│ .save_preference(                                   │
│   "music", "favorite_genre", "lofi"                │
│ )                                                   │
└────────────┬────────────────────────────────────────┘
             │
             ▼
┌─────────────────────────────────────────────────────┐
│ Update permanent_memory.json:                       │
│ {                                                   │
│   "preferences": {                                  │
│     "music": {                                      │
│       "favorite_genre": {                           │
│         "value": "lofi",                            │
│         "timestamp": "2026-01-30T..."               │
│       }                                             │
│     }                                               │
│   },                                                │
│   "last_updated": "2026-01-30T..."                  │
│ }                                                   │
└────────────┬────────────────────────────────────────┘
             │
             ▼
┌─────────────────────────────────────────────────────┐
│ Response to user:                                   │
│ "Great! Maine note kar liya - aapko lofi pasand    │
│  hai."                                              │
└────────────┬────────────────────────────────────────┘
             │
             ▼
┌─────────────────────────────────────────────────────┐
│ Socket.IO emit to frontend                          │
│ Show confirmation message                           │
└────────────┬────────────────────────────────────────┘
             │
             ▼
┌─────────────────────────────────────────────────────┐
│ FUTURE USE:                                         │
│                                                     │
│ User: "Music suno"                                  │
│ Zoya: "Aapka favorite music lofi hai.              │
│        Kya lofi playlist chal du?"                  │
│                                                     │
│ (Uses saved preference from permanent_memory)      │
└─────────────────────────────────────────────────────┘
```

---

## Memory Life Cycle

```
CREATE                  UPDATE              RECALL              DELETE
┌──────────┐          ┌──────────┐        ┌──────────┐        ┌──────────┐
│ User says│          │ User says│        │ App asks │        │ Manual   │
│ new thing│          │ something│        │ for      │        │ cleanup  │
│          │          │ similar  │        │ memory   │        │ (future) │
└────┬─────┘          └────┬─────┘        └────┬─────┘        └────┬─────┘
     │                     │                   │                   │
     ▼                     ▼                   ▼                   ▼
 Save to              Update field        Recall by         Delete from
 permanent_           in existing         search query      permanent_
 memory.json          entry               (recall_memory)   memory.json
     │                     │                   │                   │
     │                     │                   │                   │
     ├─────────────────────┼───────────────────┤                   │
     │                     │                   │                   │
     └──────────┬──────────┴───────────────────┴───────────────────┘
                │
                ▼
    ┌─────────────────────────────┐
    │ Memory Survives Restart     │
    │ (Atomic file operations)    │
    │                             │
    │ On startup:                 │
    │ Load from permanent_memory  │
    │ Use in greetings + context  │
    └─────────────────────────────┘
```

---

## File Organization

```
memory/ (New Directory)
├── permanent_memory.json        ← Main user memory (NEW)
│   └─ Survives restarts
│   └─ Contains: name, prefs, habits, emotions, conversations
│
├── identity_bindings.json       ← Face/voice embeddings (NEW)
│   └─ User face recognition
│   └─ User voice recognition
│
├── user_profile.json            ← Legacy (for compatibility)
├── emotion_history.json         ← Legacy (for compatibility)
└── conversation_memory.json     ← Legacy (for compatibility)
```

---

## Class Dependencies

```
MemoryManager
├─ save_permanent_memory()
├─ recall_memory()
├─ bind_face_identity()
├─ bind_voice_identity()
└─ Auto-save triggers:
   ├─ on_user_preference_detected()
   ├─ on_memory_save_request()
   └─ on_emotional_conversation()
        │
        └─► GreetingEngine
            ├─ generate_greeting()
            └─ Uses:
               ├─ User name
               ├─ Sleep time habit
               ├─ Emotion history
               ├─ Preferences
               └─ Last conversations
        │
        └─► MemoryInitializer
            ├─ initialize_on_startup()
            ├─ register_new_user()
            ├─ identify_user_by_face()
            ├─ identify_user_by_voice()
            └─ get_personalization_prompt()
                 (For Gemini context)
        │
        └─► MemoryIntegration
            ├─ handle_memory_save_request()
            ├─ handle_preference_expression()
            ├─ handle_emotional_conversation()
            ├─ handle_habit_learning()
            ├─ get_memory_context_for_response()
            └─ build_gemini_system_prompt()
                 (For Gemini API)
```

---

## Integration Points

```
Frontend              Server.py              Ada.py             Gemini API
   │                    │                      │                   │
   │─ voice_input ─────►│                      │                   │
   │                    │─ check for ─────────►│                   │
   │                    │   memory trigger     │                   │
   │                    │                      │─ build context ──►│
   │                    │─ get_startup ───────►│                   │
   │                    │   greeting            │                   │
   │◄─────────response──│◄──────response───────│◄─────response─────│
   │                    │                      │                   │
   └────────────────────┴──────────────────────┴───────────────────┘
         (Uses permanent memory throughout)
```

---

## Example Complete User Journey

```
TIMELINE:

Day 1, 10:00 AM:
  APP START → No memory
  Zoya: "Namaste! Main Zoya hoon. Aapka naam kya hai?"

Day 1, 10:01 AM:
  USER: "Ayush Sir"
  Zoya: "Namaste Ayush Sir!"
  SAVED: name = "Ayush Sir"

Day 1, 10:05 AM:
  USER: "Mujhe lofi music pasand hai"
  Zoya: "Great! Maine note kar liya."
  SAVED: preferences.music.favorite = "lofi"

Day 1, 11:30 PM:
  USER: "Main ab so jaunga, 1:30 ko"
  Zoya: "Good night! Sleep well."
  SAVED: habit.sleep_time = "1:30 AM"

Day 1, 11:35 PM:
  USER: "Zoya, ye yaad rakh lo: Maine CNC order kiya"
  Zoya: "Bilkul!"
  SAVED: memory.last_learning = "Maine CNC order kiya"

Day 2, 10:00 AM:
  APP RESTART
  ▼
  memory/permanent_memory.json loaded
  ▼
  greeting_engine uses: name, sleep_time, emotion_history
  ▼
  Zoya: "Good morning Ayush Sir! Kal aap 1:30 ko soye, 
         aaj thode tired lag rahe ho. 
         Aapko lofi music pasand hai. 
         Kya sunu?"
  
  ✓ MEMORY PERSISTED ACROSS RESTART
  ✓ PERSONALIZED GREETING USING LEARNED DATA
```

---

## Status: Complete ✅

All flows documented and implemented!

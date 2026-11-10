# PERMANENT MEMORY - QUICK START REFERENCE

## 30-Second Overview
Zoya AI now **remembers user permanently**. Data survives app restarts using local JSON storage.

---

## Core Concepts

| Concept | Explanation |
|---------|-------------|
| **Permanent Memory** | User data saved in `memory/permanent_memory.json` that survives restarts |
| **Identity Binding** | Face/voice embeddings linked to user for automatic identification |
| **Memory Triggers** | Voice commands like "yaad rakh lo" and "pasand hai" auto-save to memory |
| **Context Injection** | Memory fed to Gemini API as system prompt for personalized responses |
| **Greeting Engine** | Generates natural greetings using user history on app startup |

---

## Main Classes

```
MemoryManager (memory_manager.py)
├─ save_permanent_memory(data)
├─ get_permanent_memory()
├─ save_preference(category, key, value)
├─ save_habit(category, data)
├─ save_emotion_permanent(emotion, context)
├─ recall_memory(query, type)
├─ bind_face_identity(user_id, embedding)
└─ bind_voice_identity(user_id, profile)

GreetingEngine (greeting_engine.py)
├─ generate_greeting(time, emotion, face_recognized)
├─ get_daily_summary()
└─ generate_contextual_response(message)

MemoryInitializer (memory_initializer.py)
├─ initialize_on_startup()
├─ register_new_user(name)
├─ identify_user_by_face(embedding)
├─ identify_user_by_voice(profile_id)
└─ get_personalization_prompt()

MemoryIntegration (memory_integration.py)
├─ handle_memory_save_request(text)
├─ handle_preference_expression(text)
├─ handle_emotional_conversation(text, emotion)
├─ handle_habit_learning(category, data)
├─ get_memory_context_for_response(query)
└─ build_gemini_system_prompt(query)
```

---

## Common Patterns

### 1. Initialize on Startup
```python
from memory_initializer import MemoryInitializer
init = MemoryInitializer()
startup_info = init.initialize_on_startup()
print(startup_info["greeting"])  # Personalized greeting
```

### 2. Save Preference from Voice
```python
from memory_integration import MemoryIntegration
integration = MemoryIntegration()
response = integration.handle_preference_expression("Mujhe lofi pasand hai")
```

### 3. Add Context to Gemini
```python
system_prompt = integration.build_gemini_system_prompt(user_query)
response = client.aio.generate_content([system_prompt, user_query])
```

### 4. Recall Memory
```python
from memory_manager import get_memory_manager
mm = get_memory_manager()
results = mm.recall_memory("lofi", search_type="preferences")
```

### 5. Bind Face Identity
```python
face_embedding = [0.1, 0.2, 0.3, ...]  # From MediaPipe
mm.bind_face_identity("user_001", face_embedding)
```

---

## Memory Types

| Type | Example | Trigger |
|------|---------|---------|
| **Preferences** | "lofi music" | "pasand hai" / "nahi pasand" |
| **Habits** | "sleep at 1:30 AM" | Detected from routine |
| **Emotions** | "tired", "happy" | Voice/face analysis |
| **Conversations** | "Last 20 messages" | Auto-saved with every message |
| **Identity** | Face/voice embedding | Face/voice recognition |

---

## File Locations

```
memory/
├─ permanent_memory.json      (Main user memory - survives restart)
├─ identity_bindings.json     (Face/voice embeddings)
├─ user_profile.json          (Legacy, for compatibility)
├─ emotion_history.json       (Legacy, for compatibility)
└─ conversation_memory.json   (Legacy, for compatibility)
```

---

## Voice Commands

| Command | What Happens |
|---------|--------------|
| "Zoya ye yaad rakh lo: X" | Saves X to permanent memory |
| "Mujhe X pasand hai" | Saves X as preference |
| "Mujhe X nahi pasand" | Saves X as dislike |
| (Emotional tone detected) | Saves emotion to history |

---

## Quick Integration

### In server.py startup:
```python
from memory_initializer import MemoryInitializer
init = MemoryInitializer()
startup_info = init.initialize_on_startup()
```

### In voice handler:
```python
from memory_integration import MemoryIntegration
integration = MemoryIntegration()
response = integration.handle_memory_save_request(user_voice_text)
```

### For Gemini context:
```python
system_prompt = integration.build_gemini_system_prompt(query)
```

---

## Status: PRODUCTION READY ✅

See documentation files for complete details:
- `PERMANENT_MEMORY_GUIDE.md` - Full guide
- `MEMORY_SERVER_INTEGRATION.md` - Integration steps
- `MEMORY_EXAMPLES.py` - Code examples

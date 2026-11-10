import json
from pathlib import Path
from datetime import datetime, timezone, timedelta
from typing import Optional, Dict, Any, List
import hashlib
import numpy as np

MEMORY_DIR = Path('memory')
USER_PROFILE = MEMORY_DIR / 'user_profile.json'
EMOTION_HISTORY = MEMORY_DIR / 'emotion_history.json'
CONVERSATION = MEMORY_DIR / 'conversation_memory.json'
PERMANENT_MEMORY = MEMORY_DIR / 'permanent_memory.json'  # NEW: Persistent memory across restarts
IDENTITY_BINDINGS = MEMORY_DIR / 'identity_bindings.json'  # NEW: Face/voice identity


def _now_iso():
    return datetime.now(timezone.utc).isoformat()


class MemoryManager:
    def __init__(self):
        MEMORY_DIR.mkdir(exist_ok=True)
        # load or init
        self.user_profile = self._load_json(USER_PROFILE, {})
        self.emotion_history = self._load_json(EMOTION_HISTORY, [])
        self.conversation = self._load_json(CONVERSATION, [])
        # NEW: Permanent memory system
        self.permanent_memory = self._load_json(PERMANENT_MEMORY, self._init_permanent_memory())
        self.identity_bindings = self._load_json(IDENTITY_BINDINGS, {})

    def _load_json(self, path: Path, default):
        try:
            if path.exists():
                with open(path, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except Exception:
            pass
        return default

    def _save_json(self, path: Path, data):
        tmp = path.with_suffix('.tmp')
        with open(tmp, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        tmp.replace(path)

    # ---------- User profile ----------
    def set_user_field(self, key: str, value: Any):
        self.user_profile[key] = value
        self._save_json(USER_PROFILE, self.user_profile)

    def get_user_profile(self) -> Dict[str, Any]:
        return dict(self.user_profile)

    def remove_user_field(self, key: str):
        if key in self.user_profile:
            del self.user_profile[key]
            self._save_json(USER_PROFILE, self.user_profile)
            return True
        return False

    # Facts generic (store in profile.facts)
    def add_fact(self, text: str):
        facts = self.user_profile.setdefault('facts', [])
        item = {'text': text, 'timestamp': _now_iso()}
        facts.append(item)
        self._save_json(USER_PROFILE, self.user_profile)
        return item

    def list_facts(self):
        return list(self.user_profile.get('facts', []))

    # ---------- Conversation memory ----------
    def add_conversation_entry(self, sender: str, text: str):
        item = {'sender': sender, 'text': text, 'timestamp': _now_iso()}
        self.conversation.append(item)
        self._save_json(CONVERSATION, self.conversation)
        return item

    def get_conversation(self, limit: Optional[int] = None) -> List[Dict[str, Any]]:
        if limit:
            return list(self.conversation[-limit:])
        return list(self.conversation)

    def get_last_user_message(self) -> Optional[Dict[str, Any]]:
        for item in reversed(self.conversation):
            if item.get('sender') == 'User':
                return item
        return None

    # ---------- Emotion history ----------
    def add_emotion(self, emotion: str, trigger: str = 'voice', confidence: Optional[float] = None):
        item = {'emotion': emotion, 'trigger': trigger, 'timestamp': _now_iso()}
        if confidence is not None:
            item['confidence'] = float(confidence)
        self.emotion_history.append(item)
        self._save_json(EMOTION_HISTORY, self.emotion_history)
        return item

    def list_emotions(self, limit: Optional[int] = None):
        if limit:
            return list(self.emotion_history[-limit:])
        return list(self.emotion_history)

    def clear_emotions(self):
        self.emotion_history = []
        self._save_json(EMOTION_HISTORY, self.emotion_history)

    # ---------- Forgetting ----------
    def forget_fact(self, text_substring: str) -> int:
        # remove all facts containing substring
        before = len(self.user_profile.get('facts', []))
        self.user_profile['facts'] = [f for f in self.user_profile.get('facts', []) if text_substring.lower() not in f.get('text', '').lower()]
        after = len(self.user_profile.get('facts', []))
        self._save_json(USER_PROFILE, self.user_profile)
        return before - after

    def forget_conversation(self, text_substring: str) -> int:
        before = len(self.conversation)
        self.conversation = [c for c in self.conversation if text_substring.lower() not in c.get('text','').lower()]
        self._save_json(CONVERSATION, self.conversation)
        return before - len(self.conversation)

    def reset_user_profile(self):
        self.user_profile = {}
        self._save_json(USER_PROFILE, self.user_profile)

    # ========== PERMANENT MEMORY SYSTEM (SURVIVES RESTART) ==========
    
    def _init_permanent_memory(self) -> Dict[str, Any]:
        """Initialize permanent memory structure"""
        return {
            "user_id": None,
            "name": None,
            "face_embedding_reference": None,
            "voice_profile_id": None,
            "preferences": {},
            "habits": {},
            "emotion_history": [],
            "last_conversations": [],
            "created_at": _now_iso(),
            "last_updated": _now_iso(),
            "memory_version": "1.0"
        }
    
    def save_permanent_memory(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Save data to permanent memory (survives restart)"""
        self.permanent_memory.update(data)
        self.permanent_memory["last_updated"] = _now_iso()
        self._save_json(PERMANENT_MEMORY, self.permanent_memory)
        return self.permanent_memory
    
    def get_permanent_memory(self) -> Dict[str, Any]:
        """Retrieve complete permanent memory"""
        return dict(self.permanent_memory)
    
    def update_memory_field(self, key: str, value: Any) -> None:
        """Update specific field in permanent memory"""
        self.permanent_memory[key] = value
        self.permanent_memory["last_updated"] = _now_iso()
        self._save_json(PERMANENT_MEMORY, self.permanent_memory)
    
    def save_preference(self, category: str, key: str, value: Any) -> Dict[str, Any]:
        """Save user preference with category (music, clothes, etc)"""
        if "preferences" not in self.permanent_memory:
            self.permanent_memory["preferences"] = {}
        if category not in self.permanent_memory["preferences"]:
            self.permanent_memory["preferences"][category] = {}
        
        self.permanent_memory["preferences"][category][key] = {
            "value": value,
            "timestamp": _now_iso()
        }
        self.permanent_memory["last_updated"] = _now_iso()
        self._save_json(PERMANENT_MEMORY, self.permanent_memory)
        return self.permanent_memory["preferences"][category]
    
    def get_preferences(self, category: Optional[str] = None) -> Dict[str, Any]:
        """Get user preferences"""
        prefs = self.permanent_memory.get("preferences", {})
        if category:
            return prefs.get(category, {})
        return prefs
    
    def save_habit(self, category: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Save daily habits (sleep time, work time, clothing preference, etc)"""
        if "habits" not in self.permanent_memory:
            self.permanent_memory["habits"] = {}
        
        self.permanent_memory["habits"][category] = {
            "data": data,
            "timestamp": _now_iso()
        }
        self.permanent_memory["last_updated"] = _now_iso()
        self._save_json(PERMANENT_MEMORY, self.permanent_memory)
        return self.permanent_memory["habits"][category]
    
    def get_habits(self, category: Optional[str] = None) -> Dict[str, Any]:
        """Get user habits"""
        habits = self.permanent_memory.get("habits", {})
        if category:
            return habits.get(category, {})
        return habits
    
    def save_emotion_permanent(self, emotion: str, context: str = "", confidence: float = 1.0) -> Dict[str, Any]:
        """Save emotion to permanent history"""
        if "emotion_history" not in self.permanent_memory:
            self.permanent_memory["emotion_history"] = []
        
        emotion_entry = {
            "emotion": emotion,
            "context": context,
            "confidence": confidence,
            "timestamp": _now_iso(),
            "date": datetime.now(timezone.utc).strftime("%Y-%m-%d")
        }
        self.permanent_memory["emotion_history"].append(emotion_entry)
        # Keep last 100 emotions
        self.permanent_memory["emotion_history"] = self.permanent_memory["emotion_history"][-100:]
        self.permanent_memory["last_updated"] = _now_iso()
        self._save_json(PERMANENT_MEMORY, self.permanent_memory)
        return emotion_entry
    
    def get_emotion_history(self, days: int = 7, limit: int = 50) -> List[Dict[str, Any]]:
        """Get emotion history from past N days"""
        emotions = self.permanent_memory.get("emotion_history", [])
        cutoff_date = (datetime.now(timezone.utc) - timedelta(days=days)).strftime("%Y-%m-%d")
        
        filtered = [e for e in emotions if e.get("date", "") >= cutoff_date]
        return filtered[-limit:]
    
    def save_conversation_permanent(self, sender: str, text: str, context: str = "") -> Dict[str, Any]:
        """Save conversation to permanent history (last N conversations survive restart)"""
        if "last_conversations" not in self.permanent_memory:
            self.permanent_memory["last_conversations"] = []
        
        conv_entry = {
            "sender": sender,
            "text": text,
            "context": context,
            "timestamp": _now_iso()
        }
        self.permanent_memory["last_conversations"].append(conv_entry)
        # Keep last 100 conversations
        self.permanent_memory["last_conversations"] = self.permanent_memory["last_conversations"][-100:]
        self.permanent_memory["last_updated"] = _now_iso()
        self._save_json(PERMANENT_MEMORY, self.permanent_memory)
        return conv_entry
    
    def get_conversations_permanent(self, limit: int = 20) -> List[Dict[str, Any]]:
        """Get recent conversations from permanent memory"""
        convs = self.permanent_memory.get("last_conversations", [])
        return convs[-limit:]
    
    def recall_memory(self, query: str, search_type: str = "all") -> List[Dict[str, Any]]:
        """
        Recall memory based on query string
        search_type: 'all', 'conversations', 'emotions', 'habits', 'preferences'
        """
        results = []
        query_lower = query.lower()
        
        if search_type in ['all', 'conversations']:
            for conv in self.permanent_memory.get("last_conversations", []):
                if query_lower in conv.get("text", "").lower():
                    results.append({"type": "conversation", "data": conv})
        
        if search_type in ['all', 'emotions']:
            for emotion in self.permanent_memory.get("emotion_history", []):
                if query_lower in emotion.get("context", "").lower() or query_lower in emotion.get("emotion", "").lower():
                    results.append({"type": "emotion", "data": emotion})
        
        if search_type in ['all', 'habits']:
            for category, habit_data in self.permanent_memory.get("habits", {}).items():
                if query_lower in category.lower() or query_lower in str(habit_data).lower():
                    results.append({"type": "habit", "category": category, "data": habit_data})
        
        if search_type in ['all', 'preferences']:
            for category, prefs in self.permanent_memory.get("preferences", {}).items():
                if query_lower in category.lower() or query_lower in str(prefs).lower():
                    results.append({"type": "preference", "category": category, "data": prefs})
        
        return results
    
    # ========== IDENTITY BINDING (FACE/VOICE) ==========
    
    def bind_face_identity(self, user_id: str, face_embedding: List[float]) -> Dict[str, Any]:
        """Store face embedding for identity recognition"""
        self.identity_bindings[user_id] = {
            "face_embedding": face_embedding,
            "bound_at": _now_iso(),
            "embedding_version": "mediapipe_v1"
        }
        self.permanent_memory["face_embedding_reference"] = user_id
        self._save_json(IDENTITY_BINDINGS, self.identity_bindings)
        self._save_json(PERMANENT_MEMORY, self.permanent_memory)
        return self.identity_bindings[user_id]
    
    def bind_voice_identity(self, user_id: str, voice_profile_data: Dict[str, Any]) -> Dict[str, Any]:
        """Store voice profile for identity recognition"""
        if user_id not in self.identity_bindings:
            self.identity_bindings[user_id] = {}
        
        self.identity_bindings[user_id]["voice_profile"] = {
            "profile_id": voice_profile_data.get("profile_id"),
            "features": voice_profile_data.get("features"),
            "bound_at": _now_iso()
        }
        self.permanent_memory["voice_profile_id"] = voice_profile_data.get("profile_id")
        self._save_json(IDENTITY_BINDINGS, self.identity_bindings)
        self._save_json(PERMANENT_MEMORY, self.permanent_memory)
        return self.identity_bindings[user_id]
    
    def get_identity_binding(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Get stored identity binding data"""
        return self.identity_bindings.get(user_id)
    
    def get_all_identity_bindings(self) -> Dict[str, Any]:
        """Get all stored identity bindings"""
        return dict(self.identity_bindings)
    
    # ========== AUTO-SAVE TRIGGERS ==========
    
    def on_user_preference_detected(self, category: str, key: str, value: Any, confidence: float = 1.0) -> None:
        """Triggered when user says 'pasand hai' or 'nahi pasand'"""
        self.save_preference(category, key, value)
        print(f"[MEMORY] Saved preference: {category}/{key} = {value}")
    
    def on_memory_save_request(self, text: str, context: str = "voice_request") -> None:
        """Triggered when user says 'Ada ye yaad rakh lo'"""
        fact = self.add_fact(text)  # Save to facts
        self.save_permanent_memory({"last_learning": text, "learning_timestamp": _now_iso()})
        print(f"[MEMORY] Saved memory request: {text}")
    
    def on_emotional_conversation(self, emotion: str, conversation_text: str, context: str = "") -> None:
        """Triggered during emotional conversations"""
        self.save_emotion_permanent(emotion, context=conversation_text, confidence=1.0)
        self.save_conversation_permanent("User", conversation_text, context=f"emotional_{emotion}")
        print(f"[MEMORY] Saved emotional memory: {emotion}")


# Singleton accessor
_memory_manager = None

def get_memory_manager():
    global _memory_manager
    if _memory_manager is None:
        _memory_manager = MemoryManager()
    return _memory_manager

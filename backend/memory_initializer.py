"""
Memory initialization and startup handler
Loads permanent memory on app startup and prepares greeting context
"""

from datetime import datetime
from typing import Dict, Any, Optional
from memory_manager import get_memory_manager
from greeting_engine import GreetingEngine
import json


class MemoryInitializer:
    def __init__(self):
        self.memory_manager = get_memory_manager()
        self.greeting_engine = GreetingEngine()
    
    def initialize_on_startup(self) -> Dict[str, Any]:
        """
        Called when server starts up
        Returns greeting and context information
        """
        
        memory = self.memory_manager.get_permanent_memory()
        
        startup_info = {
            "user_identified": False,
            "user_name": None,
            "greeting": None,
            "context_summary": None,
            "memories_loaded": False,
            "timestamp": datetime.now().isoformat()
        }
        
        # Check if user memory exists
        if memory.get("name"):
            startup_info["user_identified"] = True
            startup_info["user_name"] = memory.get("name")
            startup_info["memories_loaded"] = True
            
            # Generate contextual greeting
            greeting = self.greeting_engine.generate_greeting(
                time_of_day=self._get_time_of_day(),
                emotion_detected=None,
                face_recognized=False
            )
            startup_info["greeting"] = greeting
            
            # Get context summary
            startup_info["context_summary"] = self._build_startup_context(memory)
            
            print(f"[MEMORY] Initialized for user: {memory.get('name')}")
            print(f"[MEMORY] {greeting}")
        else:
            print("[MEMORY] First time user - no permanent memory found")
            startup_info["greeting"] = "Namaste! Main aapka AI assistant Ada hoon. Aapka naam kya hai?"
        
        return startup_info
    
    def _get_time_of_day(self) -> str:
        """Determine time of day"""
        hour = datetime.now().hour
        if 5 <= hour < 12:
            return "morning"
        elif 12 <= hour < 17:
            return "afternoon"
        elif 17 <= hour < 21:
            return "evening"
        else:
            return "night"
    
    def _build_startup_context(self, memory: Dict[str, Any]) -> Dict[str, Any]:
        """Build context information for app startup"""
        
        context = {
            "user_name": memory.get("name"),
            "preferences": memory.get("preferences", {}),
            "habits": memory.get("habits", {}),
            "recent_emotions": memory.get("emotion_history", [])[-5:],
            "last_conversations": memory.get("last_conversations", [])[-3:],
            "memory_entries": {
                "preferences": len(memory.get("preferences", {})),
                "habits": len(memory.get("habits", {})),
                "emotions": len(memory.get("emotion_history", [])),
                "conversations": len(memory.get("last_conversations", []))
            }
        }
        
        return context
    
    def register_new_user(self, user_name: str, user_id: str = None) -> Dict[str, Any]:
        """
        Register a new user in permanent memory
        Called when user introduces themselves
        """
        
        if user_id is None:
            # Generate user_id from name
            user_id = user_name.lower().replace(" ", "_") + "_" + str(int(datetime.now().timestamp()))
        
        self.memory_manager.save_permanent_memory({
            "user_id": user_id,
            "name": user_name,
            "created_at": datetime.now().isoformat()
        })
        
        print(f"[MEMORY] Registered new user: {user_name} (ID: {user_id})")
        
        return {
            "user_id": user_id,
            "user_name": user_name,
            "message": f"Namaste {user_name}! Aapko meet karke khushi hui. Ab main aapko yaad rakhungi."
        }
    
    def identify_user_by_face(self, face_embedding: list) -> Optional[Dict[str, Any]]:
        """
        Identify user by face embedding and load their memory
        Returns user info if match found, None otherwise
        """
        
        # Simple distance-based matching (implement proper face recognition in production)
        bindings = self.memory_manager.get_all_identity_bindings()
        
        best_match = None
        best_distance = float('inf')
        threshold = 0.6  # Tune this based on your face recognition accuracy
        
        for user_id, binding in bindings.items():
            ref_embedding = binding.get("face_embedding_reference")
            if ref_embedding:
                distance = self._euclidean_distance(face_embedding, ref_embedding)
                if distance < best_distance:
                    best_distance = distance
                    best_match = user_id
        
        if best_match and best_distance < threshold:
            user_memory = self.memory_manager.get_permanent_memory()
            return {
                "identified": True,
                "user_id": best_match,
                "name": user_memory.get("name"),
                "confidence": 1 - (best_distance / threshold),
                "greeting": self.greeting_engine.generate_greeting(
                    time_of_day=self._get_time_of_day(),
                    emotion_detected=None,
                    face_recognized=True
                )
            }
        
        return {
            "identified": False,
            "message": "New face detected. Aap kaun ho?"
        }
    
    def identify_user_by_voice(self, voice_profile_id: str) -> Optional[Dict[str, Any]]:
        """
        Identify user by voice profile and load their memory
        """
        
        bindings = self.memory_manager.get_all_identity_bindings()
        
        for user_id, binding in bindings.items():
            voice_profile = binding.get("voice_profile", {})
            if voice_profile.get("profile_id") == voice_profile_id:
                user_memory = self.memory_manager.get_permanent_memory()
                return {
                    "identified": True,
                    "user_id": user_id,
                    "name": user_memory.get("name"),
                    "greeting": self.greeting_engine.generate_greeting(
                        time_of_day=self._get_time_of_day()
                    )
                }
        
        return {
            "identified": False,
            "message": "Voice not recognized. Aap kaun ho?"
        }
    
    def _euclidean_distance(self, vec1: list, vec2: list) -> float:
        """Calculate Euclidean distance between two vectors"""
        if not vec1 or not vec2 or len(vec1) != len(vec2):
            return float('inf')
        
        sum_sq = sum((a - b) ** 2 for a, b in zip(vec1, vec2))
        return sum_sq ** 0.5
    
    def get_personalization_prompt(self) -> str:
        """
        Get a prompt that includes permanent memory context
        Use this when calling Gemini to give it user context
        """
        
        memory = self.memory_manager.get_permanent_memory()
        
        prompt_parts = []
        
        # User identity
        if memory.get("name"):
            prompt_parts.append(f"User's name: {memory.get('name')}")
        
        # Recent mood
        recent_emotions = memory.get("emotion_history", [])[-3:]
        if recent_emotions:
            emotions_str = ", ".join([e.get("emotion", "") for e in recent_emotions])
            prompt_parts.append(f"Recent emotions: {emotions_str}")
        
        # Preferences
        prefs = memory.get("preferences", {})
        if prefs:
            prefs_str = "; ".join([
                f"{cat}: {', '.join(v.get('value', '') for v in cat_prefs.values())}"
                for cat, cat_prefs in prefs.items() if isinstance(cat_prefs, dict)
            ])
            if prefs_str:
                prompt_parts.append(f"User preferences: {prefs_str}")
        
        # Habits
        habits = memory.get("habits", {})
        if habits:
            habits_str = "; ".join([
                f"{cat}: {str(h.get('data', ''))}"
                for cat, h in habits.items()
            ])
            if habits_str:
                prompt_parts.append(f"User habits: {habits_str}")
        
        # Recent conversations
        recent_convs = memory.get("last_conversations", [])[-2:]
        if recent_convs:
            conv_str = "; ".join([c.get("text", "") for c in recent_convs])
            if conv_str:
                prompt_parts.append(f"Recent conversation context: {conv_str}")
        
        context_prompt = "\n".join(prompt_parts)
        
        return f"""You are Ada, a helpful AI assistant. Here is context about the user:

{context_prompt}

Use this information to make responses more personal and contextual. Remember the user's name, preferences, and habits."""


# Example usage
if __name__ == "__main__":
    init = MemoryInitializer()
    
    # Test startup
    print("=== STARTUP INITIALIZATION ===")
    startup_info = init.initialize_on_startup()
    print(json.dumps(startup_info, indent=2, ensure_ascii=False))
    
    print("\n=== PERSONALIZATION PROMPT ===")
    print(init.get_personalization_prompt())

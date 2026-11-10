"""
Greeting Engine - Uses permanent memory to create personalized greetings
Generates natural, context-aware messages based on user history
"""

from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List
from memory_manager import get_memory_manager
import random


class GreetingEngine:
    def __init__(self):
        self.memory_manager = get_memory_manager()
    
    def generate_greeting(self, 
                         time_of_day: str = "morning",
                         emotion_detected: Optional[str] = None,
                         face_recognized: bool = False) -> str:
        """
        Generate personalized greeting using permanent memory
        
        Args:
            time_of_day: 'morning', 'afternoon', 'evening', 'night'
            emotion_detected: detected emotion from face/voice
            face_recognized: whether user was recognized via face recognition
        
        Returns:
            Personalized greeting string in Hinglish
        """
        
        memory = self.memory_manager.get_permanent_memory()
        name = memory.get("name", "User")
        
        # Build greeting components
        greeting_base = self._get_time_greeting(time_of_day, name)
        
        # Add memory-based context
        memory_context = self._build_memory_context(memory, emotion_detected)
        
        # Add habits-based observations
        habits_context = self._build_habits_context(memory)
        
        # Combine all
        full_greeting = greeting_base
        if memory_context:
            full_greeting += " " + memory_context
        if habits_context:
            full_greeting += " " + habits_context
        
        return full_greeting
    
    def _get_time_greeting(self, time_of_day: str, name: str) -> str:
        """Get base greeting for time of day"""
        greetings = {
            "morning": [
                f"Good morning {name}! Aaj kaisa tha raat?",
                f"Namaste {name}! Subah ho gai! Kaise ho?",
                f"Morning {name}! Kaise lag rahe ho aaj?"
            ],
            "afternoon": [
                f"Afternoon {name}! Lunch le liye?",
                f"Hi {name}! Dopahar ke baad kaisa chal raha hai?",
                f"Hello {name}! Thoda rest le lo agar thak gaye ho."
            ],
            "evening": [
                f"Good evening {name}! Din kaisa raha?",
                f"Shaam ho gai {name}! Kya kiya aajkal?",
                f"Hi {name}! Evening chai? Coffee?"
            ],
            "night": [
                f"Good night {name}! Sone ka time ho gaya?",
                f"Raat ho gai {name}! Kaise feel kar rahe ho?",
                f"Sleep well {name}! Aaj ka din achcha tha?"
            ]
        }
        
        selected = greetings.get(time_of_day, greetings["morning"])
        return random.choice(selected)
    
    def _build_memory_context(self, memory: Dict[str, Any], emotion_detected: Optional[str]) -> str:
        """Build context from recent memories and emotions"""
        
        contexts = []
        
        # Check recent emotional state
        recent_emotions = memory.get("emotion_history", [])[-5:]  # Last 5 emotions
        
        if emotion_detected:
            contexts.append(f"Tum {emotion_detected} ho kya?")
        elif recent_emotions:
            # Build context from emotional history
            last_emotion = recent_emotions[-1].get("emotion", "").lower()
            if last_emotion == "tired":
                contexts.append("Kal aap late soye the, aaj thode tired lag rahe ho.")
            elif last_emotion == "happy":
                contexts.append("Bilkul khush ho aaj! Achcha chal raha hai kya?")
            elif last_emotion == "stressed":
                contexts.append("Aap thode stress mein hain kya? Kya issue hai?")
        
        # Check if something was learned recently
        if "last_learning" in memory:
            last_learning = memory.get("last_learning", "")
            contexts.append(f"Haan, mujhe yaad hai aapne kaha tha: '{last_learning}'")
        
        # Check recent conversations
        recent_convs = memory.get("last_conversations", [])[-3:]
        if recent_convs:
            last_conv = recent_convs[-1].get("text", "")
            if len(last_conv) > 10:
                contexts.append(f"Aapka last message tha: '{last_conv[:50]}...'")
        
        return " ".join(contexts) if contexts else ""
    
    def _build_habits_context(self, memory: Dict[str, Any]) -> str:
        """Build context from user habits"""
        
        habits = memory.get("habits", {})
        contexts = []
        
        current_hour = datetime.now().hour
        
        # Sleep time habit
        if "sleep_time" in habits:
            sleep_data = habits["sleep_time"].get("data", {})
            typical_sleep = sleep_data.get("time", "")  # e.g., "1:30 AM"
            if typical_sleep and current_hour < 10:  # Morning greeting
                contexts.append(f"Aap usually {typical_sleep} ke baad sote ho na, aaj jaldi uth gaye?")
        
        # Work time habit
        if "work_time" in habits and current_hour >= 9 and current_hour < 18:
            work_data = habits["work_time"].get("data", {})
            work_schedule = work_data.get("schedule", "")
            if work_schedule:
                contexts.append(f"Work shuru ho gaya aaj? {work_schedule} check kar lete ho?")
        
        # Clothing preference
        if "clothing" in habits:
            clothing_data = habits["clothing"].get("data", {})
            preference = clothing_data.get("preference", "")
            if preference:
                contexts.append(f"Formal ya casual? Aaj {preference} pehen lo.")
        
        return " ".join(contexts) if contexts else ""
    
    def generate_contextual_response(self, user_message: str) -> Optional[str]:
        """
        Generate context-aware response referencing permanent memory
        E.g., if user says "I'm tired", reference that they slept late
        """
        memory = self.memory_manager.get_permanent_memory()
        message_lower = user_message.lower()
        
        # Check if message matches patterns and generate response with memory context
        
        if "tired" in message_lower or "sleepy" in message_lower:
            habits = memory.get("habits", {})
            if "sleep_time" in habits:
                sleep_data = habits["sleep_time"].get("data", {})
                typical_sleep = sleep_data.get("time", "")
                return f"Haan, kal raat {typical_sleep} ko soy the na? Thora rest kar lo."
            return "Haan, rest kar lo thoda. Aapke liye break zaruri hai."
        
        if "busy" in message_lower or "stressed" in message_lower:
            return "Thora relax karo. Aapka kya favorite music hai? Usi ko suno."
        
        if "remember" in message_lower or "yaad" in message_lower:
            # Recall memories
            results = self.memory_manager.recall_memory(user_message)
            if results:
                return f"Haan, mujhe yaad hai! Maine {len(results)} cheezein remember kari hain us baare mein."
        
        return None
    
    def get_daily_summary(self) -> Dict[str, Any]:
        """Generate daily summary of user state based on memory"""
        memory = self.memory_manager.get_permanent_memory()
        
        today = datetime.now().strftime("%Y-%m-%d")
        emotions_today = [
            e for e in memory.get("emotion_history", [])
            if e.get("date") == today
        ]
        
        conversations_today = [
            c for c in memory.get("last_conversations", [])
            if c.get("timestamp", "")[:10] == today
        ]
        
        return {
            "date": today,
            "emotions": emotions_today,
            "conversation_count": len(conversations_today),
            "habits_tracked": list(memory.get("habits", {}).keys()),
            "preferences_count": sum(len(prefs) for prefs in memory.get("preferences", {}).values())
        }


# Example usage
if __name__ == "__main__":
    engine = GreetingEngine()
    
    # Test greetings
    print("Morning greeting:")
    print(engine.generate_greeting(time_of_day="morning", emotion_detected="tired"))
    print("\nAfternoon greeting:")
    print(engine.generate_greeting(time_of_day="afternoon"))
    print("\nEvening greeting:")
    print(engine.generate_greeting(time_of_day="evening", emotion_detected="happy"))
    print("\nDaily summary:")
    print(engine.get_daily_summary())

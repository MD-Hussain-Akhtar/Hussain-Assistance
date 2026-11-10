"""
Memory Integration Examples - Shows how to use permanent memory with Ada
Demonstrates voice input handling, preference detection, and context usage
"""

from memory_manager import get_memory_manager
from memory_initializer import MemoryInitializer
from greeting_engine import GreetingEngine
import re


class MemoryIntegration:
    """Integration layer between voice/text input and memory system"""
    
    def __init__(self):
        self.memory_manager = get_memory_manager()
        self.memory_init = MemoryInitializer()
        self.greeting_engine = GreetingEngine()
    
    # ========== VOICE INPUT HANDLERS ==========
    
    def handle_memory_save_request(self, user_message: str) -> str:
        """
        Handle: "Ada ye yaad rakh lo", "Ada mujhe yaad rakho", "Remember this"
        """
        # Extract the text to remember
        patterns = [
            r"(?:yaad rakh|remember|yaad rakho).*?(?:[:,]\s*)(.+?)(?:\?|$|।)",
            r"(?:hai|hain).*?(.+?)$"
        ]
        
        text_to_remember = user_message
        for pattern in patterns:
            match = re.search(pattern, user_message, re.IGNORECASE)
            if match:
                text_to_remember = match.group(1).strip()
                break
        
        # Save to permanent memory
        self.memory_manager.on_memory_save_request(text_to_remember)
        
        return f"Bilkul, maine yaad kar liya: '{text_to_remember}'. Hamesha yaad rakhungi."
    
    def handle_preference_expression(self, user_message: str) -> str:
        """
        Handle: "Mujhe [music/clothes/food] pasand hai", "Mujhe nahi pasand"
        Extract preference and save to memory
        """
        
        # Patterns for preference detection
        like_patterns = [
            r"(?:mujhe|mujhko)\s+(.+?)\s+pasand\s+(?:hai|hain)",  # mujhe X pasand hai
            r"(?:i\s+)?(?:like|love|prefer|enjoy)\s+(.+?)(?:\?|$|।)",  # English
            r"(?:ka|ke|ki)\s+(.+?)\s+dost\s+hoon",  # X ka dost hoon
        ]
        
        dislike_patterns = [
            r"(?:mujhe|mujhko)\s+(.+?)\s+(?:nahi|na)\s+pasand",  # mujhe X nahi pasand
            r"(?:i\s+)?(?:don't|hate|dislike)\s+(.+?)(?:\?|$|।)",
        ]
        
        # Check for likes
        for pattern in like_patterns:
            match = re.search(pattern, user_message, re.IGNORECASE)
            if match:
                preference = match.group(1).strip()
                category = self._categorize_preference(preference)
                self.memory_manager.on_user_preference_detected(
                    category=category,
                    key="preference",
                    value=preference,
                    confidence=1.0
                )
                return f"Great! Maine note kar liya - aapko {preference} pasand hai."
        
        # Check for dislikes
        for pattern in dislike_patterns:
            match = re.search(pattern, user_message, re.IGNORECASE)
            if match:
                dislike = match.group(1).strip()
                category = self._categorize_preference(dislike)
                self.memory_manager.on_user_preference_detected(
                    category=category,
                    key="dislike",
                    value=dislike,
                    confidence=1.0
                )
                return f"Samajh gai! {dislike} aapko pasand nahi hai. Note kar diya."
        
        return None
    
    def handle_emotional_conversation(self, user_message: str, detected_emotion: str = None) -> str:
        """
        Handle emotional conversations and save to permanent memory
        Called when voice/face analysis detects emotion
        """
        
        if not detected_emotion:
            # Try to detect emotion from text
            detected_emotion = self._detect_emotion_from_text(user_message)
        
        if detected_emotion:
            self.memory_manager.on_emotional_conversation(
                emotion=detected_emotion,
                conversation_text=user_message,
                context=f"Detected emotion: {detected_emotion}"
            )
            
            # Generate empathetic response
            empathy_response = self._get_empathy_response(detected_emotion)
            return empathy_response
        
        return None
    
    def handle_habit_learning(self, habit_category: str, habit_data: dict) -> str:
        """
        Learn and save user habits
        Examples:
        - sleep_time: {"time": "1:30 AM", "quality": "good"}
        - work_time: {"start": "9 AM", "end": "6 PM"}
        - clothing: {"preference": "formal", "style": "professional"}
        """
        
        self.memory_manager.save_habit(habit_category, habit_data)
        
        habit_descriptions = {
            "sleep_time": f"Aap {habit_data.get('time')} ko sote ho. Noted!",
            "work_time": f"Aapka work time {habit_data.get('start')} se {habit_data.get('end')} hai.",
            "clothing": f"Aapko {habit_data.get('preference')} clothes pasand hain.",
            "meal_time": f"Aap {habit_data.get('time')} ko khana khate ho.",
            "exercise": f"Aap {habit_data.get('frequency')} ko exercise karte ho."
        }
        
        return habit_descriptions.get(habit_category, f"Aapka {habit_category} note kar diya.")
    
    # ========== MEMORY RECALL FOR CONTEXT ==========
    
    def get_memory_context_for_response(self, user_query: str) -> dict:
        """
        Get relevant memory context to include in Gemini prompt
        Makes responses more personalized
        """
        
        # Search memory for relevant context
        memory_results = self.memory_manager.recall_memory(user_query)
        
        memory = self.memory_manager.get_permanent_memory()
        
        context = {
            "user_name": memory.get("name"),
            "relevant_memories": memory_results[:5],  # Top 5 relevant memories
            "recent_preferences": list(memory.get("preferences", {}).keys())[:3],
            "last_conversation": memory.get("last_conversations", [])[-1:],
            "recent_emotion": memory.get("emotion_history", [])[-1:],
        }
        
        return context
    
    def build_gemini_system_prompt(self, user_query: str = None) -> str:
        """
        Build a system prompt for Gemini that includes permanent memory context
        Use this as the system instruction when calling Gemini API
        """
        
        base_prompt = self.memory_init.get_personalization_prompt()
        
        if user_query:
            context = self.get_memory_context_for_response(user_query)
            
            relevant = context.get("relevant_memories", [])
            if relevant:
                memory_context = "\nRelevant past interactions:\n"
                for mem in relevant[:3]:
                    mem_type = mem.get("type", "unknown")
                    if mem_type == "conversation":
                        memory_context += f"- User said: {mem.get('data', {}).get('text', '')}\n"
                    elif mem_type == "emotion":
                        memory_context += f"- User was {mem.get('data', {}).get('emotion', '')}\n"
                
                base_prompt += memory_context
        
        return base_prompt
    
    # ========== GREETING AND WELCOME ==========
    
    def get_startup_greeting(self) -> str:
        """
        Get personalized greeting on app startup
        """
        startup_info = self.memory_init.initialize_on_startup()
        return startup_info.get("greeting", "Namaste! Main Ada hoon.")
    
    def handle_first_time_user(self, user_name: str) -> str:
        """
        Called when new user introduces themselves
        """
        registration = self.memory_init.register_new_user(user_name)
        return registration.get("message")
    
    # ========== HELPER METHODS ==========
    
    def _categorize_preference(self, preference: str) -> str:
        """Auto-categorize preference into category"""
        
        preference_lower = preference.lower()
        
        music_keywords = ["music", "song", "gaan", "beat", "lofi", "classical", "rock"]
        clothing_keywords = ["cloth", "shirt", "dress", "formal", "casual", "saree", "suit"]
        food_keywords = ["food", "khana", "chai", "coffee", "pizza", "biryani", "recipe"]
        movie_keywords = ["movie", "series", "film", "show", "netflix", "cinema"]
        
        for keyword in music_keywords:
            if keyword in preference_lower:
                return "music"
        for keyword in clothing_keywords:
            if keyword in preference_lower:
                return "clothing"
        for keyword in food_keywords:
            if keyword in preference_lower:
                return "food"
        for keyword in movie_keywords:
            if keyword in preference_lower:
                return "entertainment"
        
        return "general"
    
    def _detect_emotion_from_text(self, text: str) -> str:
        """Detect emotion from text content"""
        
        text_lower = text.lower()
        
        emotions = {
            "happy": ["happy", "khush", "great", "awesome", "perfect"],
            "sad": ["sad", "dukhi", "bad", "terrible", "awful", "upset"],
            "tired": ["tired", "thak", "sleepy", "exhausted", "weak"],
            "stressed": ["stressed", "tension", "worried", "anxious", "busy"],
            "confused": ["confused", "samjh nahi", "unclear", "lost"],
            "excited": ["excited", "thrilled", "eager", "pumped"]
        }
        
        for emotion, keywords in emotions.items():
            for keyword in keywords:
                if keyword in text_lower:
                    return emotion
        
        return None
    
    def _get_empathy_response(self, emotion: str) -> str:
        """Generate empathetic response based on emotion"""
        
        responses = {
            "happy": "Wonderful! Aapka khusi padhkar main bhi khush ho gai!",
            "sad": "Mujhe aapka dukh samajh aata hai. Kya main help kar sakti hoon?",
            "tired": "Aap thak gaye lagte ho. Thoda rest kar lo. Main yahin hoon.",
            "stressed": "Relax karo. Ek ek kaam karte hain. Sabkuch manage ho jayega.",
            "confused": "Koi nahi, main samjhata hoon. Samjh nahi aaya toh pucho.",
            "excited": "Awesome! Mujhe bhi aapki excitement pasand aai!"
        }
        
        return responses.get(emotion, "Main samajhti hoon. Kya main help kar sakti hoon?")


# ========== EXAMPLE USAGE ==========

if __name__ == "__main__":
    integration = MemoryIntegration()
    
    print("=== EXAMPLE 1: STARTUP GREETING ===")
    greeting = integration.get_startup_greeting()
    print(greeting)
    
    print("\n=== EXAMPLE 2: MEMORY SAVE REQUEST ===")
    response = integration.handle_memory_save_request("Ada, mujhe ye yaad rakh lo: Maine kal CNC machine order kar diya")
    print(f"User: Ada, mujhe ye yaad rakh lo: Maine kal CNC machine order kar diya")
    print(f"Ada: {response}")
    
    print("\n=== EXAMPLE 3: PREFERENCE DETECTION ===")
    response = integration.handle_preference_expression("Mujhe lofi music bahut pasand hai")
    print(f"User: Mujhe lofi music bahut pasand hai")
    print(f"Ada: {response}")
    
    print("\n=== EXAMPLE 4: HABIT LEARNING ===")
    response = integration.handle_habit_learning("sleep_time", {"time": "1:30 AM", "quality": "good"})
    print(f"Ada: {response}")
    
    print("\n=== EXAMPLE 5: EMOTIONAL CONVERSATION ===")
    response = integration.handle_emotional_conversation("Main bahut tired hoon", detected_emotion="tired")
    print(f"User: Main bahut tired hoon")
    print(f"Ada: {response}")
    
    print("\n=== EXAMPLE 6: GEMINI SYSTEM PROMPT ===")
    prompt = integration.build_gemini_system_prompt("Tell me about my preferences")
    print(prompt[:500] + "...")

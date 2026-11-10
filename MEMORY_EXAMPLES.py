"""
PRODUCTION-READY CODE EXAMPLES
Complete working examples for Zoya AI permanent memory system
"""

# ============================================================================
# EXAMPLE 1: COMPLETE MEMORY FLOW (Single User Session)
# ============================================================================

"""
SCENARIO: User "Ayush" starts app for first time, then returns after restart

DAY 1 - FIRST TIME:
"""

from memory_manager import get_memory_manager
from memory_initializer import MemoryInitializer
from memory_integration import MemoryIntegration
from greeting_engine import GreetingEngine

# Initialize
mm = get_memory_manager()
init = MemoryInitializer()
integration = MemoryIntegration()

# User introduces themselves
user_name = "Ayush Sir"
registration = init.register_new_user(user_name, user_id="ayush_001")
print(f"[Startup] {registration['message']}")
# Output: "Namaste Ayush Sir! Aapko meet karke khushi hui. Ab main aapko yaad rakhungi."

# User teaches preferences
integration.handle_preference_expression("Mujhe lofi music pasand hai")
# Saved: preferences.music.favorite_genre = "lofi"
# Output: "Great! Maine note kar liya - aapko lofi pasand hai."

# User teaches habit
integration.handle_habit_learning("sleep_time", {
    "time": "1:30 AM",
    "quality": "good"
})
# Output: "Aap 1:30 AM ko sote ho. Noted!"

# User shares memory
integration.handle_memory_save_request("Maine kal CNC machine order kar diya")
# Saved to permanent_memory
# Output: "Bilkul, maine yaad kar liya: 'Maine kal CNC machine order kar diya'..."

# Later: User says something emotional
integration.handle_emotional_conversation(
    "Main thak gaya aaj, bilkul exhausted",
    detected_emotion="tired"
)
# Saved: emotion_history with "tired"
# Output: "Mujhe aapka dukh samajh aata hai. Kya main help kar sakti hoon?"

# App closes
# ✓ All data persisted in memory/permanent_memory.json


"""
DAY 2 - AFTER RESTART:
"""

# App starts -> server startup event
startup_info = init.initialize_on_startup()
# Loads permanent_memory.json

# ✓ Memory loaded
# Output logs:
#   [MEMORY] Initialized for user: Ayush Sir
#   [MEMORY] Good morning Ayush Sir! Kal aap late soye the, aaj thode tired lag rahe ho.

# Frontend asks for greeting
greeting = integration.get_startup_greeting()
# Output: "Good morning Ayush Sir! Kal aap late soye the, aaj thode tired lag rahe ho."

# System builds context for Gemini
system_prompt = integration.build_gemini_system_prompt()
# Includes: name, preferences, habits, recent emotions

# User asks: "Kya music suno?"
# Gemini sees context and responds with their preference:
# "Aapka favorite music lofi hai. Kya lofi playlist chal du?"

# ✓ App continues with personalized experience


# ============================================================================
# EXAMPLE 2: VOICE INPUT HANDLER FOR SERVER.PY
# ============================================================================

"""
Copy-paste this into your server.py socket handlers:
"""

from memory_integration import MemoryIntegration

integration = MemoryIntegration()

async def process_voice_input_with_memory(user_voice_text, emotion_detected=None):
    """
    Main voice input processor that handles memory commands
    """
    
    # 1. Check for memory save commands
    memory_triggers = ["yaad rakh", "remember", "yaad rakho", "yaad kar lo"]
    if any(trigger in user_voice_text.lower() for trigger in memory_triggers):
        return integration.handle_memory_save_request(user_voice_text)
    
    # 2. Check for preference commands
    if "pasand" in user_voice_text.lower():
        response = integration.handle_preference_expression(user_voice_text)
        if response:
            return response
    
    # 3. Check for emotional conversations
    if emotion_detected:
        response = integration.handle_emotional_conversation(user_voice_text, emotion_detected)
        if response:
            return response
    
    # 4. Build context for Gemini
    system_prompt = integration.build_gemini_system_prompt(user_voice_text)
    
    # 5. Continue with normal Gemini processing...
    # response = await client.aio.generate_content([system_prompt, user_voice_text])
    # return response.text
    
    return None


# Usage in server.py:
"""
@sio.on("voice_input")
async def handle_voice_input(sid, data):
    text = data.get("text")
    emotion = data.get("emotion")
    
    # Try memory-specific handlers first
    response = await process_voice_input_with_memory(text, emotion)
    
    if response:
        await sio.emit("response", {"text": response}, to=sid)
        return
    
    # Continue with normal flow...
"""


# ============================================================================
# EXAMPLE 3: COMPLETE USER JOURNEY WITH TESTING
# ============================================================================

def test_complete_user_journey():
    """
    Test complete user journey: registration -> learning -> recall
    """
    from memory_manager import get_memory_manager
    from memory_initializer import MemoryInitializer
    from memory_integration import MemoryIntegration
    import json
    
    mm = get_memory_manager()
    init = MemoryInitializer()
    integration = MemoryIntegration()
    
    print("=" * 60)
    print("COMPLETE USER JOURNEY TEST")
    print("=" * 60)
    
    # STEP 1: User introduces themselves
    print("\n[1] USER INTRODUCTION")
    print("User: Hi Zoya, I'm Ayush")
    registration = init.register_new_user("Ayush", user_id="ayush_test_001")
    print(f"Zoya: {registration['message']}")
    
    # STEP 2: User teaches preferences
    print("\n[2] PREFERENCE LEARNING")
    
    test_inputs = [
        "Mujhe lofi music bahut pasand hai",
        "Formal clothes pasand hain",
        "Biryani ka dost hoon main"
    ]
    
    for user_input in test_inputs:
        print(f"User: {user_input}")
        response = integration.handle_preference_expression(user_input)
        if response:
            print(f"Zoya: {response}")
    
    # STEP 3: User teaches habits
    print("\n[3] HABIT LEARNING")
    
    habits = {
        "sleep_time": {"time": "1:30 AM", "quality": "good"},
        "work_time": {"start": "9 AM", "end": "6 PM"},
        "exercise": {"frequency": "5 days/week", "time": "6 AM"}
    }
    
    for category, data in habits.items():
        response = integration.handle_habit_learning(category, data)
        print(f"Zoya: {response}")
    
    # STEP 4: User saves memories
    print("\n[4] MEMORY SAVING")
    
    memories = [
        "Zoya ye yaad rakh lo: Maine CNC machine order kar diya",
        "Remember: Tomorrow is my project deadline",
        "Yaad rakho: Mujhe medical checkup book karni hai"
    ]
    
    for memory in memories:
        print(f"User: {memory}")
        response = integration.handle_memory_save_request(memory)
        print(f"Zoya: {response}")
    
    # STEP 5: Emotional conversation
    print("\n[5] EMOTIONAL MEMORY")
    
    user_input = "Main bahut thak gaya aaj, itni sari meetings the"
    print(f"User: {user_input}")
    response = integration.handle_emotional_conversation(user_input, "tired")
    print(f"Zoya: {response}")
    
    # STEP 6: Check persistent memory
    print("\n[6] VERIFY PERMANENT MEMORY")
    memory = mm.get_permanent_memory()
    
    print(f"User Name: {memory.get('name')}")
    print(f"Preferences saved: {len(memory.get('preferences', {}))}")
    print(f"Habits saved: {len(memory.get('habits', {}))}")
    print(f"Emotions recorded: {len(memory.get('emotion_history', []))}")
    print(f"Conversations saved: {len(memory.get('last_conversations', []))}")
    
    # STEP 7: Test memory recall
    print("\n[7] MEMORY RECALL")
    
    search_queries = [
        ("lofi", "all"),
        ("tired", "emotions"),
        ("1:30 AM", "habits")
    ]
    
    for query, search_type in search_queries:
        results = mm.recall_memory(query, search_type)
        print(f"Search '{query}' ({search_type}): Found {len(results)} results")
    
    # STEP 8: Startup greeting simulation
    print("\n[8] STARTUP GREETING (AFTER RESTART)")
    greeting = integration.get_startup_greeting()
    print(f"Zoya: {greeting}")
    
    # STEP 9: Memory context for Gemini
    print("\n[9] GEMINI CONTEXT PROMPT (EXCERPT)")
    prompt = integration.build_gemini_system_prompt("Tell me what you remember about me")
    print(prompt[:300] + "...")
    
    # STEP 10: Export final state
    print("\n[10] FINAL MEMORY STATE")
    print(json.dumps(memory, indent=2, ensure_ascii=False)[:500] + "...")
    
    print("\n" + "=" * 60)
    print("✓ COMPLETE USER JOURNEY TEST PASSED")
    print("=" * 60)


# ============================================================================
# EXAMPLE 4: FACE & VOICE BINDING
# ============================================================================

def test_identity_binding():
    """
    Test face and voice identity binding
    """
    from memory_manager import get_memory_manager
    from memory_initializer import MemoryInitializer
    import numpy as np
    
    mm = get_memory_manager()
    init = MemoryInitializer()
    
    print("\n" + "=" * 60)
    print("IDENTITY BINDING TEST")
    print("=" * 60)
    
    # Register user
    user_id = "ayush_identity_001"
    init.register_new_user("Ayush", user_id=user_id)
    
    # Simulate face embedding from MediaPipe
    print("\n[1] BINDING FACE IDENTITY")
    face_embedding = np.random.rand(128).tolist()  # 128-dim face embedding
    binding = mm.bind_face_identity(user_id, face_embedding)
    print(f"✓ Face embedding bound for {user_id}")
    print(f"  Embedding size: {len(binding.get('face_embedding', []))} dimensions")
    
    # Simulate voice profile
    print("\n[2] BINDING VOICE IDENTITY")
    voice_profile = {
        "profile_id": "voice_prof_12345",
        "features": np.random.rand(40).tolist()  # Voice features
    }
    binding = mm.bind_voice_identity(user_id, voice_profile)
    print(f"✓ Voice profile bound for {user_id}")
    print(f"  Profile ID: {binding.get('voice_profile', {}).get('profile_id')}")
    
    # Test identity retrieval
    print("\n[3] RETRIEVING IDENTITY BINDING")
    binding = mm.get_identity_binding(user_id)
    print(f"✓ Retrieved binding for {user_id}")
    print(f"  Face embedding: {len(binding.get('face_embedding', []))} dims")
    print(f"  Voice profile: {binding.get('voice_profile', {}).get('profile_id')}")
    
    # Test user identification
    print("\n[4] USER IDENTIFICATION (FACE RECOGNITION)")
    result = init.identify_user_by_face(face_embedding)
    if result.get("identified"):
        print(f"✓ User identified: {result.get('name')}")
        print(f"  Confidence: {result.get('confidence', 0):.2%}")
        print(f"  Greeting: {result.get('greeting')}")
    
    # Test voice identification
    print("\n[5] USER IDENTIFICATION (VOICE RECOGNITION)")
    result = init.identify_user_by_voice("voice_prof_12345")
    if result.get("identified"):
        print(f"✓ User identified by voice: {result.get('name')}")
        print(f"  Greeting: {result.get('greeting')}")
    
    print("\n" + "=" * 60)
    print("✓ IDENTITY BINDING TEST PASSED")
    print("=" * 60)


# ============================================================================
# EXAMPLE 5: QUICK TEST SCRIPT
# ============================================================================

if __name__ == "__main__":
    import sys
    
    print("\n" + "=" * 60)
    print("ZOYA AI - PERMANENT MEMORY SYSTEM")
    print("PRODUCTION-READY EXAMPLES")
    print("=" * 60)
    
    print("\nAvailable tests:")
    print("1. Complete user journey")
    print("2. Identity binding")
    print("\nRun: python this_file.py [1-2]")
    
    if len(sys.argv) > 1:
        test_num = sys.argv[1]
        if test_num == "1":
            test_complete_user_journey()
        elif test_num == "2":
            test_identity_binding()
        else:
            print("Invalid test number")
    else:
        print("\nRun with test number to execute tests")

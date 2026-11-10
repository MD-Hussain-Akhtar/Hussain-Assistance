"""
SERVER.PY INTEGRATION CHECKLIST - Copy/paste ready code snippets

This file contains all the code needed to integrate permanent memory into server.py
"""

# ========================================
# 1. ADD IMPORTS AT TOP OF SERVER.PY
# ========================================

# Add these imports near the top of server.py (after existing imports):
"""
from memory_initializer import MemoryInitializer
from memory_integration import MemoryIntegration
"""


# ========================================
# 2. INITIALIZE MEMORY IN STARTUP EVENT
# ========================================

# Add this to your @app.on_event("startup") handler:
"""
@app.on_event("startup")
async def startup_event():
    # ... existing startup code ...
    
    # NEW: Initialize permanent memory
    try:
        memory_initializer = MemoryInitializer()
        startup_info = memory_initializer.initialize_on_startup()
        
        if startup_info.get("user_identified"):
            print(f"[MEMORY] Welcome back {startup_info['user_name']}!")
            print(f"[MEMORY] {startup_info['greeting']}")
            print(f"[MEMORY] Context: {startup_info['context_summary']}")
        else:
            print("[MEMORY] First time user detected")
            
    except Exception as e:
        print(f"[MEMORY] Error during initialization: {e}")
"""


# ========================================
# 3. ADD MEMORY INTEGRATION INSTANCE
# ========================================

# Add this as a global variable in server.py:
"""
memory_integration = MemoryIntegration()
"""


# ========================================
# 4. ADD SOCKET.IO HANDLER FOR VOICE INPUT
# ========================================

# Add this new socket event handler:
"""
@sio.on("process_voice_input")
async def handle_voice_input(sid, data):
    '''
    Handle voice input from frontend
    Checks for memory-related voice commands
    
    data: {
        "text": "user voice input text",
        "emotion": "detected emotion (optional)",
        "confidence": 0.95
    }
    '''
    user_input = data.get("text", "").strip()
    emotion = data.get("emotion")
    
    # Check for memory save request ("Zoya ye yaad rakh lo")
    if any(trigger in user_input.lower() for trigger in ["yaad rakh", "remember", "yaad rakho"]):
        response = memory_integration.handle_memory_save_request(user_input)
        await sio.emit("zoya_response", {"text": response, "type": "memory_save"}, to=sid)
        return
    
    # Check for preference expression ("Mujhe pasand hai / nahi pasand")
    if "pasand" in user_input.lower():
        response = memory_integration.handle_preference_expression(user_input)
        if response:
            await sio.emit("zoya_response", {"text": response, "type": "preference_saved"}, to=sid)
            return
    
    # Check for emotional conversation
    if emotion:
        response = memory_integration.handle_emotional_conversation(user_input, emotion)
        if response:
            await sio.emit("zoya_response", {"text": response, "type": "emotional_support"}, to=sid)
    
    # Save conversation to memory
    memory_manager.add_conversation_entry("User", user_input)
    
    # Return updated greeting if first greeting
    await sio.emit("status", {"msg": "Voice input processed"}, to=sid)
"""


# ========================================
# 5. ADD SOCKET.IO HANDLER FOR FIRST-TIME USER
# ========================================

# Add this new socket event handler:
"""
@sio.on("user_introduce")
async def handle_user_introduction(sid, data):
    '''
    Called when user introduces themselves for first time
    Registers user in permanent memory
    
    data: {
        "name": "User's name"
    }
    '''
    user_name = data.get("name", "").strip()
    
    if not user_name:
        await sio.emit("error", {"msg": "Please provide a name"}, to=sid)
        return
    
    try:
        registration = memory_integration.memory_init.register_new_user(user_name)
        
        # Save to memory manager for consistency
        memory_manager.set_user_field('name', user_name)
        
        await sio.emit("user_registered", {
            "user_name": user_name,
            "greeting": registration.get("message"),
            "user_id": registration.get("user_id")
        }, to=sid)
        
    except Exception as e:
        await sio.emit("error", {"msg": f"Registration failed: {e}"}, to=sid)
"""


# ========================================
# 6. UPDATE EMOTION HANDLER WITH MEMORY
# ========================================

# Update existing emotion detection handler to save to permanent memory:
"""
# In your existing emotion detection handler, add:

emotion = detected_emotion  # from face/voice analysis
confidence = emotion_confidence

# Save to both current and permanent memory
memory_manager.add_emotion(emotion, trigger=trigger, confidence=confidence)
memory_manager.save_emotion_permanent(emotion, context=context_description, confidence=confidence)
"""


# ========================================
# 7. ADD HABIT LEARNING HANDLER
# ========================================

# Add this new socket event handler:
"""
@sio.on("learn_habit")
async def handle_habit_learning(sid, data):
    '''
    Learn and save user habits
    
    data: {
        "category": "sleep_time",
        "habit_data": {"time": "1:30 AM", "quality": "good"}
    }
    '''
    category = data.get("category")
    habit_data = data.get("habit_data")
    
    if not category or not habit_data:
        await sio.emit("error", {"msg": "Invalid habit data"}, to=sid)
        return
    
    try:
        response = memory_integration.handle_habit_learning(category, habit_data)
        await sio.emit("zoya_response", {
            "text": response,
            "type": "habit_learned"
        }, to=sid)
    except Exception as e:
        await sio.emit("error", {"msg": f"Habit learning failed: {e}"}, to=sid)
"""


# ========================================
# 8. UPDATE GEMINI CONTEXT WITH MEMORY
# ========================================

# In your ada.py or wherever you call Gemini, add:
"""
from memory_integration import MemoryIntegration

memory_integration = MemoryIntegration()

# Before calling Gemini API:
system_prompt = memory_integration.build_gemini_system_prompt(user_query)

# Use in Gemini message:
response = await client.aio.generate_content(
    [system_prompt, user_query],
    model=MODEL,
    config=generationConfig,
    tools=tools_list
)
"""


# ========================================
# 9. ADD MEMORY RECALL ENDPOINT
# ========================================

# Add this new socket event handler:
"""
@sio.on("recall_memory")
async def handle_memory_recall(sid, data):
    '''
    Search permanent memory for user query
    
    data: {
        "query": "search term",
        "search_type": "all" | "conversations" | "emotions" | "habits" | "preferences"
    }
    '''
    query = data.get("query", "").strip()
    search_type = data.get("search_type", "all")
    
    if not query:
        await sio.emit("error", {"msg": "Please provide a search query"}, to=sid)
        return
    
    try:
        results = memory_manager.recall_memory(query, search_type)
        
        await sio.emit("memory_recall_results", {
            "query": query,
            "result_count": len(results),
            "results": results[:10]  # Top 10 results
        }, to=sid)
        
    except Exception as e:
        await sio.emit("error", {"msg": f"Memory recall failed: {e}"}, to=sid)
"""


# ========================================
# 10. ADD STARTUP GREETING ENDPOINT
# ========================================

# Add this new socket event handler:
"""
@sio.on("get_startup_greeting")
async def get_greeting(sid):
    '''
    Get personalized startup greeting
    Called by frontend when app loads
    '''
    try:
        greeting = memory_integration.get_startup_greeting()
        startup_info = memory_integration.memory_init.initialize_on_startup()
        
        await sio.emit("startup_greeting", {
            "greeting": greeting,
            "user_name": startup_info.get("user_name"),
            "context": startup_info.get("context_summary")
        }, to=sid)
        
    except Exception as e:
        await sio.emit("error", {"msg": f"Greeting generation failed: {e}"}, to=sid)
"""


# ========================================
# 11. COMPLETE INTEGRATION EXAMPLE
# ========================================

# Here's what the modified server.py startup would look like:

"""
import asyncio
from fastapi import FastAPI
from memory_initializer import MemoryInitializer
from memory_integration import MemoryIntegration

app = FastAPI()
memory_initializer = MemoryInitializer()
memory_integration = MemoryIntegration()

@app.on_event("startup")
async def startup_event():
    # Existing startup code...
    
    # NEW: Initialize permanent memory
    try:
        startup_info = memory_initializer.initialize_on_startup()
        
        if startup_info.get("user_identified"):
            print(f"[MEMORY] Welcome back {startup_info['user_name']}!")
            print(f"[MEMORY] Greeting: {startup_info['greeting']}")
        else:
            print("[MEMORY] First-time user setup required")
            
    except Exception as e:
        print(f"[MEMORY] Initialization error: {e}")

# Socket events...
@sio.on("process_voice_input")
async def handle_voice_input(sid, data):
    user_input = data.get("text", "").strip()
    emotion = data.get("emotion")
    
    # Check memory-specific commands
    if "yaad rakh" in user_input.lower():
        response = memory_integration.handle_memory_save_request(user_input)
        await sio.emit("zoya_response", {"text": response}, to=sid)
        return
    
    if "pasand" in user_input.lower():
        response = memory_integration.handle_preference_expression(user_input)
        if response:
            await sio.emit("zoya_response", {"text": response}, to=sid)
            return
    
    # Continue with normal processing...
    await sio.emit("process_to_gemini", {"text": user_input}, to=sid)

@sio.on("user_introduce")
async def handle_user_introduction(sid, data):
    user_name = data.get("name", "")
    registration = memory_integration.memory_init.register_new_user(user_name)
    await sio.emit("user_registered", registration, to=sid)

# More handlers...
"""


# ========================================
# QUICK START COMMANDS
# ========================================

"""
QUICK START:

1. Add imports at top:
   from memory_initializer import MemoryInitializer
   from memory_integration import MemoryIntegration

2. In startup event:
   memory_initializer = MemoryInitializer()
   memory_initializer.initialize_on_startup()

3. Add socket handlers (copy sections 4-10 above)

4. Update Gemini calls to use memory context:
   system_prompt = memory_integration.build_gemini_system_prompt(query)

5. Restart server

6. Test:
   - App startup should show personalized greeting
   - Say "Zoya ye yaad rakh lo: ..." to test memory save
   - Say "Mujhe X pasand hai" to test preference detection
"""


if __name__ == "__main__":
    print(__doc__)

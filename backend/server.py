import sys
import asyncio

# Fix for asyncio subprocess support on Windows
# MUST BE SET BEFORE OTHER IMPORTS
if sys.platform == 'win32':
    asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())

import socketio
import uvicorn
from fastapi import FastAPI
from contextlib import asynccontextmanager
import asyncio
import threading
import sys
import os
import json
import time  # FIXED: moved to top-level for echo protection
from datetime import datetime
from pathlib import Path



# Ensure we can import ada
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import ada
from authenticator import FaceAuthenticator
from kasa_agent import KasaAgent
from web_agent_view import router as web_agent_router
from command_view import router as command_router_view
from app_indexer import get_indexer
from command_router import get_command_router
from memory_initializer import MemoryInitializer
from memory_manager import get_memory_manager

# Create a Socket.IO server
sio = socketio.AsyncServer(async_mode='asgi', cors_allowed_origins='*')

import signal

# --- SHUTDOWN HANDLER ---
def signal_handler(sig, frame):
    print(f"\n[SERVER] Caught signal {sig}. Exiting gracefully...")
    # Clean up audio loop
    if audio_loop:
        try:
            print("[SERVER] Stopping Audio Loop...")
            audio_loop.stop() 
        except:
            pass
    # Force kill
    print("[SERVER] Force exiting...")
    os._exit(0)

signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)

# Global state
audio_loop = None
loop_task = None
authenticator = None
kasa_agent = KasaAgent()
memory_initializer = None
memory_manager = None
SETTINGS_FILE = "settings.json"

DEFAULT_SETTINGS = {
    "face_auth_enabled": False, # Default OFF as requested
    "tool_permissions": {
        "generate_cad": True,
        "run_web_agent": True,
        "write_file": True,
        "read_directory": True,
        "read_file": True,
        "create_project": True,
        "switch_project": True,
        "list_projects": True,
        "system_control": True,
        "screen_access": True,
        "file_access": True
    },
    "printers": [], # List of {host, port, name, type}
    "kasa_devices": [], # List of {ip, alias, model}
    "camera_flipped": False # Invert cursor horizontal direction
}

# Auto-confirm tool requests (when True, server will automatically accept tool confirmation requests)
DEFAULT_SETTINGS["auto_confirm_tools"] = False

SETTINGS = DEFAULT_SETTINGS.copy()

def load_settings():
    global SETTINGS
    if os.path.exists(SETTINGS_FILE):
        try:
            with open(SETTINGS_FILE, 'r') as f:
                loaded = json.load(f)
                # Merge with defaults to ensure new keys exist
                for k, v in loaded.items():
                    if k == "tool_permissions" and isinstance(v, dict):
                         SETTINGS["tool_permissions"].update(v)
                    else:
                        SETTINGS[k] = v
            print(f"Loaded settings: {SETTINGS}")
        except Exception as e:
            print(f"Error loading settings: {e}")

def save_settings():
    try:
        with open(SETTINGS_FILE, 'w') as f:
            json.dump(SETTINGS, f, indent=4)
        print("Settings saved.")
    except Exception as e:
        print(f"Error saving settings: {e}")

# Load on startup
load_settings()

authenticator = None
kasa_agent = KasaAgent(known_devices=SETTINGS.get("kasa_devices"))
# tool_permissions is now SETTINGS["tool_permissions"]

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    import sys
    global memory_initializer, memory_manager
    
    print(f"[SERVER DEBUG] Startup Event Triggered")
    print(f"[SERVER DEBUG] Python Version: {sys.version}")
    try:
        loop = asyncio.get_running_loop()
        print(f"[SERVER DEBUG] Running Loop: {type(loop)}")
        policy = asyncio.get_event_loop_policy()
        print(f"[SERVER DEBUG] Current Policy: {type(policy)}")
    except Exception as e:
        print(f"[SERVER DEBUG] Error checking loop: {e}")

    print("[SERVER] Startup: Initializing Kasa Agent...")
    await kasa_agent.initialize()

    # Initialize Memory System
    print("[SERVER] Startup: Initializing Permanent Memory System...")
    try:
        memory_initializer = MemoryInitializer()
        memory_manager = get_memory_manager()
        startup_info = memory_initializer.initialize_on_startup()
        print(f"[MEMORY] System initialized: {startup_info}")
    except Exception as e:
        print(f"[MEMORY] Error initializing memory system: {e}")

    # Build app index in background thread (may be IO-heavy)
    try:
        print("[SERVER] Startup: Building application index (app_index.json)...")
        await asyncio.to_thread(get_indexer().build_index)
        print("[SERVER] App index build complete.")
    except Exception as e:
        print(f"[SERVER] App index build failed: {e}")

    # Initialize command router singleton
    try:
        get_command_router()
    except Exception:
        pass
    
    yield
    
    # Shutdown (cleanup if needed)
    print("[SERVER] Shutting down...")
    print("[SERVER] Memory system saved and ready for next startup")

app = FastAPI(lifespan=lifespan)
app_socketio = socketio.ASGIApp(sio, app)

# Include WebAgent routes
app.include_router(web_agent_router)
app.include_router(command_router_view)

@app.get("/status")
async def status():
    return {"status": "running", "service": "ZOYA Backend"}

@sio.event
async def connect(sid, environ):
    print(f"Client connected: {sid}")
    await sio.emit('status', {'msg': 'Connected to ZOYA Backend'}, room=sid)

    global authenticator
    
    # Callback for Auth Status
    async def on_auth_status(is_auth):
        print(f"[SERVER] Auth status change: {is_auth}")
        await sio.emit('auth_status', {'authenticated': is_auth})

    # Callback for Auth Camera Frames
    async def on_auth_frame(frame_b64):
        await sio.emit('auth_frame', {'image': frame_b64})

    # Initialize Authenticator if not already done
    if authenticator is None:
        authenticator = FaceAuthenticator(
            reference_image_path="reference.jpg",
            on_status_change=on_auth_status,
            on_frame=on_auth_frame
        )
    
    # Check if already authenticated or needs to start
    if authenticator.authenticated:
        await sio.emit('auth_status', {'authenticated': True})
    else:
        # Check Settings for Auth
        if SETTINGS.get("face_auth_enabled", False):
            await sio.emit('auth_status', {'authenticated': False})
            # Start the auth loop in background
            asyncio.create_task(authenticator.start_authentication_loop())
        else:
            # Bypass Auth
            print("Face Auth Disabled. Auto-authenticating.")
            await sio.emit('auth_status', {'authenticated': True})

@sio.event
async def disconnect(sid):
    print(f"Client disconnected: {sid}")

@sio.event
async def start_audio(sid, data=None):
    global audio_loop, loop_task
    
    # Optional: Block if not authenticated
    # Only block if auth is ENABLED and not authenticated
    if SETTINGS.get("face_auth_enabled", False):
        if authenticator and not authenticator.authenticated:
            print("Blocked start_audio: Not authenticated.")
            await sio.emit('error', {'msg': 'Authentication Required'})
            return

    print("Starting Audio Loop...")
    
    device_index = None
    device_name = None
    if data:
        if 'device_index' in data:
            device_index = data['device_index']
        if 'device_name' in data:
            device_name = data['device_name']
            
    print(f"Using input device: Name='{device_name}', Index={device_index}")
    
    if audio_loop:
        if loop_task and (loop_task.done() or loop_task.cancelled()):
             print("Audio loop task appeared finished/cancelled. Clearing and restarting...")
             audio_loop = None
             loop_task = None
        else:
             print("Audio loop already running. Re-connecting client to session.")
             await sio.emit('status', {'msg': 'ZOYA Already Running'})
             return


    # Callback to send audio data to frontend
    def on_audio_data(data_bytes):
        asyncio.create_task(sio.emit('audio_data', {'data': list(data_bytes)}))

    # Callback to send CAL data to frontend
    def on_cad_data(data):
        info = f"{len(data.get('vertices', []))} vertices" if 'vertices' in data else f"{len(data.get('data', ''))} bytes (STL)"
        print(f"Sending CAD data to frontend: {info}")
        asyncio.create_task(sio.emit('cad_data', data))

    # Callback to send Browser data to frontend
    def on_web_data(data):
        print(f"Sending Browser data to frontend: {len(data.get('log', ''))} chars logs")
        asyncio.create_task(sio.emit('browser_frame', data))
        
    # Callback to send Transcription data to frontend
    def on_transcription(data):
        # ========== ROLE VALIDATION GATE ==========
        sender = data.get('sender')
        text = data.get('text')
        
        # RULE 1: Sender MUST be explicitly set
        if not sender or not isinstance(sender, str):
            print(f"[SERVER DEBUG] [ROLE GUARD] REJECTED: Invalid sender type. Got: {type(sender)}, Value: {sender}")
            return
        
        # RULE 2: Only 'User' and 'ADA' are valid roles
        if sender not in ['User', 'ADA']:
            print(f"[SERVER DEBUG] [ROLE GUARD] REJECTED: Invalid sender role. Got: '{sender}'")
            return
        
        # RULE 3: Text must exist and be string
        if not text or not isinstance(text, str):
            print(f"[SERVER DEBUG] [ROLE GUARD] REJECTED: Invalid text. Got: {type(text)}")
            return
        
        # ========== PASS: Valid role + text ==========
        print(f"[SERVER DEBUG] [ROLE VALIDATION] PASS: {sender} → '{text[:50]}...'")

        # ========== FIXED: ECHO PROTECTION TRACKING ==========
        # Update audio_loop's echo protection state when ADA speaks or User speaks
        if audio_loop:
            try:
                if sender == 'ADA':
                    prev = getattr(audio_loop, '_last_assistant_spoken_text', '') or ''
                    audio_loop._last_assistant_spoken_text = prev + text
                    audio_loop._assistant_speak_timestamp = time.time()
                elif sender == 'User':
                    audio_loop._last_assistant_spoken_text = ""
                    audio_loop._assistant_speak_timestamp = 0
            except Exception as _e:
                pass
        # =====================================================

        asyncio.create_task(sio.emit('transcription', {'sender': sender, 'text': text}))

    # HALF-DUPLEX: Callback to notify frontend of assistant speaking state
    def on_assistant_speaking(data):
        speaking = data.get('speaking', False)
        print(f"[HALF-DUPLEX] Assistant speaking state: {speaking}")
        asyncio.create_task(sio.emit('assistant_speaking', {'speaking': speaking}))

    # Callback to send Confirmation Request to frontend
    def on_tool_confirmation(data):
        print(f"Requesting confirmation for tool: {data.get('tool')}")
        if SETTINGS.get("auto_confirm_tools", False) and audio_loop:
            print(f"Auto-confirm enabled: auto-accepting tool request {data.get('id')} for {data.get('tool')}")
            try:
                audio_loop.resolve_tool_confirmation(data.get('id'), True)
            except Exception as e:
                print(f"Failed to auto-resolve tool confirmation: {e}")
        else:
            asyncio.create_task(sio.emit('tool_confirmation_request', data))

    # Callback to send CAD status to frontend
    def on_cad_status(status):
        if isinstance(status, dict):
            print(f"Sending CAD Status: {status.get('status')} (attempt {status.get('attempt')}/{status.get('max_attempts')})")
            asyncio.create_task(sio.emit('cad_status', status))
        else:
            print(f"Sending CAD Status: {status}")
            asyncio.create_task(sio.emit('cad_status', {'status': status}))

    # Callback to send CAD thoughts to frontend (streaming)
    def on_cad_thought(thought_text):
        asyncio.create_task(sio.emit('cad_thought', {'text': thought_text}))

    # Callback to send Project Update to frontend
    def on_project_update(project_name):
        print(f"Sending Project Update: {project_name}")
        asyncio.create_task(sio.emit('project_update', {'project': project_name}))

    # Callback to send Device Update to frontend
    def on_device_update(devices):
        print(f"Sending Kasa Device Update: {len(devices)} devices")
        asyncio.create_task(sio.emit('kasa_devices', devices))

    # Callback to send Error to frontend
    def on_error(msg):
        print(f"Sending Error to frontend: {msg}")
        asyncio.create_task(sio.emit('error', {'msg': msg}))

    # Callback to send System Data (screenshots, etc.) to frontend
    def on_system_data(data):
        print(f"[SERVER] System data received: {data.get('type', 'unknown')}")
        asyncio.create_task(sio.emit('system_data', data))

    # Initialize ADA
    try:
        print(f"Initializing AudioLoop with device_index={device_index}")
        audio_loop = ada.AudioLoop(
            video_mode="none", 
            on_audio_data=on_audio_data,
            on_cad_data=on_cad_data,
            on_web_data=on_web_data,
            on_transcription=on_transcription,
            on_tool_confirmation=on_tool_confirmation,
            on_cad_status=on_cad_status,
            on_cad_thought=on_cad_thought,
            on_project_update=on_project_update,
            on_device_update=on_device_update,
            on_assistant_speaking=on_assistant_speaking,
            on_error=on_error,
            on_system_data=on_system_data,
            input_device_index=device_index,
            input_device_name=device_name,
            kasa_agent=kasa_agent
        )
        print("AudioLoop initialized successfully.")

        # FIXED: Ensure echo protection attributes exist with safe defaults
        if not hasattr(audio_loop, '_last_assistant_spoken_text'):
            audio_loop._last_assistant_spoken_text = ""
        if not hasattr(audio_loop, '_assistant_speak_timestamp'):
            audio_loop._assistant_speak_timestamp = 0
        if not hasattr(audio_loop, '_echo_protection_cooldown'):
            audio_loop._echo_protection_cooldown = 2.0

        # Apply current permissions
        audio_loop.update_permissions(SETTINGS["tool_permissions"])
        
        # Check initial mute state
        if data and data.get('muted', False):
            print("Starting with Audio Paused")
            audio_loop.set_paused(True)

        print("Creating asyncio task for AudioLoop.run()")
        loop_task = asyncio.create_task(audio_loop.run())
        
        # Add a done callback to catch silent failures in the loop
        def handle_loop_exit(task):
            try:
                task.result()
            except asyncio.CancelledError:
                print("Audio Loop Cancelled")
            except Exception as e:
                print(f"Audio Loop Crashed: {e}")
        
        loop_task.add_done_callback(handle_loop_exit)
        
        print("Emitting 'Ada Started'")
        await sio.emit('status', {'msg': 'Ada Started'})

        # Load saved printers
        saved_printers = SETTINGS.get("printers", [])
        if saved_printers and audio_loop.printer_agent:
            print(f"[SERVER] Loading {len(saved_printers)} saved printers...")
            for p in saved_printers:
                audio_loop.printer_agent.add_printer_manually(
                    name=p.get("name", p["host"]),
                    host=p["host"],
                    port=p.get("port", 80),
                    printer_type=p.get("type", "moonraker"),
                    camera_url=p.get("camera_url")
                )
        
        # Start Printer Monitor
        asyncio.create_task(monitor_printers_loop())
        
    except Exception as e:
        print(f"CRITICAL ERROR STARTING ADA: {e}")
        import traceback
        traceback.print_exc()
        await sio.emit('error', {'msg': f"Failed to start: {str(e)}"})
        audio_loop = None


async def monitor_printers_loop():
    """Background task to query printer status periodically."""
    print("[SERVER] Starting Printer Monitor Loop")
    while audio_loop and audio_loop.printer_agent:
        try:
            agent = audio_loop.printer_agent
            if not agent.printers:
                await asyncio.sleep(5)
                continue
                
            tasks = []
            for host, printer in agent.printers.items():
                if printer.printer_type.value != "unknown":
                    tasks.append(agent.get_print_status(host))
            
            if tasks:
                results = await asyncio.gather(*tasks, return_exceptions=True)
                for res in results:
                    if isinstance(res, Exception):
                        pass
                    elif res:
                        await sio.emit('print_status_update', res.to_dict())
                        
        except asyncio.CancelledError:
            print("[SERVER] Printer Monitor Cancelled")
            break
        except Exception as e:
            print(f"[SERVER] Monitor Loop Error: {e}")
            
        await asyncio.sleep(2)

@sio.event
async def stop_audio(sid):
    global audio_loop
    if audio_loop:
        audio_loop.stop() 
        print("Stopping Audio Loop")
        audio_loop = None
        await sio.emit('status', {'msg': 'ZOYA Stopped'})

@sio.event
async def pause_audio(sid):
    global audio_loop
    if audio_loop:
        audio_loop.set_paused(True)
        print("Pausing Audio")
        await sio.emit('status', {'msg': 'Audio Paused'})

@sio.event
async def resume_audio(sid):
    global audio_loop
    if audio_loop:
        audio_loop.set_paused(False)
        print("Resuming Audio")
        await sio.emit('status', {'msg': 'Audio Resumed'})

@sio.event
async def confirm_tool(sid, data):
    request_id = data.get('id')
    confirmed = data.get('confirmed', False)
    
    print(f"[SERVER DEBUG] Received confirmation response for {request_id}: {confirmed}")
    
    if audio_loop:
        audio_loop.resolve_tool_confirmation(request_id, confirmed)
    else:
        print("Audio loop not active, cannot resolve confirmation.")

@sio.event
async def shutdown(sid, data=None):
    """Gracefully shutdown the server when the application closes."""
    global audio_loop, loop_task, authenticator
    
    print("[SERVER] ========================================")
    print("[SERVER] SHUTDOWN SIGNAL RECEIVED FROM FRONTEND")
    print("[SERVER] ========================================")
    
    if audio_loop:
        print("[SERVER] Stopping Audio Loop...")
        audio_loop.stop()
        audio_loop = None
    
    if loop_task and not loop_task.done():
        print("[SERVER] Cancelling loop task...")
        loop_task.cancel()
        loop_task = None
    
    if authenticator:
        print("[SERVER] Stopping Authenticator...")
        authenticator.stop()
    
    print("[SERVER] Graceful shutdown complete. Terminating process...")
    os._exit(0)

@sio.event
async def user_input(sid, data):
    """
    ROLE-SAFE MESSAGE HANDLER — with FIXED echo protection
    """
    text = data.get('text')
    print(f"[SERVER DEBUG] User input received: '{text}'")
    
    if not audio_loop:
        print("[SERVER DEBUG] [Error] Audio loop is None. Cannot send text.")
        return

    if not audio_loop.session:
        print("[SERVER DEBUG] [Error] Session is None. Cannot send text.")
        return

    if text:
        # ========== ROLE SAFEGUARD ==========
        print(f"[SERVER DEBUG] [ROLE GATE] user_input received (auto-role: USER)")
        
        # ========== FIXED: ECHO PROTECTION (safe getattr) ==========
        last_ada = getattr(audio_loop, '_last_assistant_spoken_text', '') or ''
        last_ts = getattr(audio_loop, '_assistant_speak_timestamp', 0)
        cooldown = getattr(audio_loop, '_echo_protection_cooldown', 2.0)

        if last_ada:
            time_since_speak = time.time() - last_ts
            if time_since_speak < cooldown:
                print(f"[SERVER DEBUG] [ECHO PROTECTION] Cooldown active ({time_since_speak:.2f}s). Checking for echo match...")
                
                incoming_normalized = text.strip().lower()
                assistant_normalized = last_ada.strip().lower()
                
                is_echo = (incoming_normalized == assistant_normalized or 
                          assistant_normalized in incoming_normalized or
                          incoming_normalized in assistant_normalized)
                
                if is_echo:
                    print(f"[SERVER DEBUG] [ECHO PROTECTION] ECHO REJECTED!")
                    print(f"  Last ADA said: '{last_ada[:60]}...'")
                    print(f"  User sent: '{text[:60]}...'")
                    print(f"  -> Discarding to prevent self-loop")
                    return
        # ============================================================
        
        print(f"[SERVER DEBUG] Sending message to model (role=USER): '{text}'")
        
        if audio_loop and audio_loop.project_manager:
            audio_loop.project_manager.log_chat("User", text)
            
        if audio_loop and audio_loop._latest_image_payload:
            print(f"[SERVER DEBUG] Piggybacking video frame with text input.")
            try:
                await audio_loop.session.send(input=audio_loop._latest_image_payload, end_of_turn=False)
            except Exception as e:
                print(f"[SERVER DEBUG] Failed to send piggyback frame: {e}")
                
        await audio_loop.session.send(input=text, end_of_turn=True)
        print(f"[SERVER DEBUG] Message sent to model successfully.")

# NOTE: This save_memory is overridden by the later definition — kept for reference
@sio.event
async def save_memory(sid, data):
    try:
        messages = data.get('messages', [])
        if not messages:
            print("No messages to save.")
            return

        memory_dir = Path("long_term_memory")
        memory_dir.mkdir(exist_ok=True)

        provided_name = data.get('filename')
        
        if provided_name:
            if not provided_name.endswith('.txt'):
                provided_name += '.txt'
            filename = memory_dir / Path(provided_name).name 
        else:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = memory_dir / f"memory_{timestamp}.txt"

        with open(filename, 'w', encoding='utf-8') as f:
            for msg in messages:
                sender = msg.get('sender', 'Unknown')
                text = msg.get('text', '')
                f.write(f"{sender}: {text}\n")
        print(f"Conversation saved to {filename}")
        await sio.emit('status', {'msg': 'Memory Saved Successfully'})

    except Exception as e:
        print(f"Error saving memory: {e}")
        await sio.emit('error', {'msg': f"Failed to save memory: {str(e)}"})

@sio.event
async def video_frame(sid, data):
    image_data = data.get('image')
    if image_data and audio_loop:
        asyncio.create_task(audio_loop.send_frame(image_data))

@sio.event
async def upload_memory(sid, data):
    print(f"Received memory upload request")
    try:
        memory_text = data.get('memory', '')
        if not memory_text:
            print("No memory data provided.")
            return

        if not audio_loop:
             print("[SERVER DEBUG] [Error] Audio loop is None. Cannot load memory.")
             await sio.emit('error', {'msg': "System not ready (Audio Loop inactive)"})
             return
        
        if not audio_loop.session:
             print("[SERVER DEBUG] [Error] Session is None. Cannot load memory.")
             await sio.emit('error', {'msg': "System not ready (No active session)"})
             return

        print("Sending memory context to model...")
        context_msg = f"System Notification: The user has uploaded a long-term memory file. Please load the following context into your understanding. The format is a text log of previous conversations:\n\n{memory_text}"
        
        await audio_loop.session.send(input=context_msg, end_of_turn=True)
        print("Memory context sent successfully.")
        await sio.emit('status', {'msg': 'Memory Loaded into Context'})

    except Exception as e:
        print(f"Error uploading memory: {e}")
        await sio.emit('error', {'msg': f"Failed to upload memory: {str(e)}"})

@sio.event
async def discover_kasa(sid):
    print(f"Received discover_kasa request")
    try:
        devices = await kasa_agent.discover_devices()
        await sio.emit('kasa_devices', devices)
        await sio.emit('status', {'msg': f"Found {len(devices)} Kasa devices"})
        
        saved_devices = []
        for d in devices:
            saved_devices.append({
                "ip": d["ip"],
                "alias": d["alias"],
                "model": d["model"]
            })
        
        SETTINGS["kasa_devices"] = saved_devices
        save_settings()
        print(f"[SERVER] Saved {len(saved_devices)} Kasa devices to settings.")
        
    except Exception as e:
        print(f"Error discovering kasa: {e}")
        await sio.emit('error', {'msg': f"Kasa Discovery Failed: {str(e)}"})

@sio.event
async def iterate_cad(sid, data):
    prompt = data.get('prompt')
    print(f"Received iterate_cad request: '{prompt}'")
    
    if not audio_loop or not audio_loop.cad_agent:
        await sio.emit('error', {'msg': "CAD Agent not available"})
        return

    try:
        await sio.emit('status', {'msg': 'Iterating design...'})
        await sio.emit('cad_status', {'status': 'generating'})
        
        cad_output_dir = str(audio_loop.project_manager.get_current_project_path() / "cad")
        result = await audio_loop.cad_agent.iterate_prototype(prompt, output_dir=cad_output_dir)
        
        if result:
            info = f"{len(result.get('data', ''))} bytes (STL)"
            print(f"Sending updated CAD data: {info}")
            await sio.emit('cad_data', result)
            if 'file_path' in result:
                saved_path = audio_loop.project_manager.save_cad_artifact(result['file_path'], prompt)
                if saved_path:
                    print(f"[SERVER] Saved iterated CAD to {saved_path}")

            await sio.emit('status', {'msg': 'Design updated'})
        else:
            await sio.emit('error', {'msg': 'Failed to update design'})
            
    except Exception as e:
        print(f"Error iterating CAD: {e}")
        await sio.emit('error', {'msg': f"Iteration Error: {str(e)}"})

@sio.event
async def generate_cad(sid, data):
    prompt = data.get('prompt')
    print(f"Received generate_cad request: '{prompt}'")
    
    if not audio_loop or not audio_loop.cad_agent:
        await sio.emit('error', {'msg': "CAD Agent not available"})
        return

    try:
        await sio.emit('status', {'msg': 'Generating new design...'})
        await sio.emit('cad_status', {'status': 'generating'})
        
        cad_output_dir = str(audio_loop.project_manager.get_current_project_path() / "cad")
        result = await audio_loop.cad_agent.generate_prototype(prompt, output_dir=cad_output_dir)
        
        if result:
            info = f"{len(result.get('data', ''))} bytes (STL)"
            print(f"Sending newly generated CAD data: {info}")
            await sio.emit('cad_data', result)

            if 'file_path' in result:
                saved_path = audio_loop.project_manager.save_cad_artifact(result['file_path'], prompt)
                if saved_path:
                    print(f"[SERVER] Saved generated CAD to {saved_path}")

            await sio.emit('status', {'msg': 'Design generated'})
        else:
            await sio.emit('error', {'msg': 'Failed to generate design'})
            
    except Exception as e:
        print(f"Error generating CAD: {e}")
        await sio.emit('error', {'msg': f"Generation Error: {str(e)}"})

@sio.event
async def prompt_web_agent(sid, data):
    prompt = data.get('prompt')
    print(f"Received web agent prompt: '{prompt}'")
    
    if not audio_loop or not audio_loop.web_agent:
        await sio.emit('error', {'msg': "Web Agent not available"})
        return

    try:
        await sio.emit('status', {'msg': 'Web Agent running...'})
        
        loop = asyncio.get_running_loop()
        try:
            result = await loop.run_in_executor(None, audio_loop.web_agent.run, prompt)
            if isinstance(result, dict):
                await sio.emit('status', {'msg': 'Web Agent finished', 'result': result})
            else:
                await sio.emit('status', {'msg': 'Web Agent finished'})
        except Exception as e:
            print(f"Error executing WebAgent in executor: {e}")
            await sio.emit('error', {'msg': f'Web Agent Error: {str(e)}'})
        
    except Exception as e:
        print(f"Error running Web Agent: {e}")
        await sio.emit('error', {'msg': f"Web Agent Error: {str(e)}"})

@sio.event
async def discover_printers(sid):
    print("Received discover_printers request")
    
    if not audio_loop or not audio_loop.printer_agent:
        saved_printers = SETTINGS.get("printers", [])
        if saved_printers:
            printer_list = []
            for p in saved_printers:
                printer_list.append({
                    "name": p.get("name", p["host"]),
                    "host": p["host"],
                    "port": p.get("port", 80),
                    "printer_type": p.get("type", "unknown"),
                    "camera_url": p.get("camera_url")
                })
            print(f"[SERVER] Returning {len(printer_list)} saved printers (audio_loop not ready)")
            await sio.emit('printer_list', printer_list)
            return
        else:
            await sio.emit('printer_list', [])
            await sio.emit('status', {'msg': "Connect to ZOYA to enable printer discovery"})
            return
        
    try:
        printers = await audio_loop.printer_agent.discover_printers()
        await sio.emit('printer_list', printers)
        await sio.emit('status', {'msg': f"Found {len(printers)} printers"})
    except Exception as e:
        print(f"Error discovering printers: {e}")
        await sio.emit('error', {'msg': f"Printer Discovery Failed: {str(e)}"})

@sio.event
async def add_printer(sid, data):
    raw_host = data.get('host')
    name = data.get('name') or raw_host
    ptype = data.get('type', "moonraker")
    
    if ":" in raw_host:
        host, port_str = raw_host.split(":")
        port = int(port_str)
    else:
        host = raw_host
        port = 80
    
    print(f"Received add_printer request: {host}:{port} ({ptype})")
    
    if not audio_loop or not audio_loop.printer_agent:
        await sio.emit('error', {'msg': "Printer Agent not available"})
        return
        
    try:
        camera_url = data.get('camera_url')
        printer = audio_loop.printer_agent.add_printer_manually(name, host, port=port, printer_type=ptype, camera_url=camera_url)
        
        new_printer_config = {
            "name": name,
            "host": host,
            "port": port,
            "type": ptype,
            "camera_url": camera_url
        }
        
        exists = False
        for p in SETTINGS.get("printers", []):
            if p["host"] == host and p["port"] == port:
                exists = True
                break
        
        if not exists:
            if "printers" not in SETTINGS:
                SETTINGS["printers"] = []
            SETTINGS["printers"].append(new_printer_config)
            save_settings()
            print(f"[SERVER] Saved printer {name} to settings.")
        
        print(f"Probing {host} to confirm type...")
        ports_to_try = [80, 7125, 4408]
        
        actual_type = "unknown"
        for port_probe in ports_to_try:
             found_type = await audio_loop.printer_agent._probe_printer_type(host, port_probe)
             if found_type.value != "unknown":
                 actual_type = found_type
                 if port_probe != 80:
                     printer.port = port_probe
                 break
        
        if actual_type != "unknown" and actual_type != printer.printer_type:
             printer.printer_type = actual_type
             print(f"Corrected type to {actual_type.value} on port {printer.port}")
             
        printers = [p.to_dict() for p in audio_loop.printer_agent.printers.values()]
        await sio.emit('printer_list', printers)
        await sio.emit('status', {'msg': f"Added printer: {name}"})
        
    except Exception as e:
        print(f"Error adding printer: {e}")
        await sio.emit('error', {'msg': f"Failed to add printer: {str(e)}"})

@sio.event
async def print_stl(sid, data):
    print(f"Received print_stl request: {data}")
    
    if not audio_loop or not audio_loop.printer_agent:
        await sio.emit('error', {'msg': "Printer Agent not available"})
        return
        
    try:
        stl_path = data.get('stl_path', 'current')
        printer_name = data.get('printer')
        profile = data.get('profile')
        
        if not printer_name:
             await sio.emit('error', {'msg': "No printer specified"})
             return
             
        await sio.emit('status', {'msg': f"Preparing print for {printer_name}..."})
        
        current_project_path = None
        if audio_loop and audio_loop.project_manager:
            current_project_path = str(audio_loop.project_manager.get_current_project_path())
            print(f"[SERVER DEBUG] Using project path: {current_project_path}")

        resolved_stl = audio_loop.printer_agent._resolve_file_path(stl_path, current_project_path)
        
        if resolved_stl and os.path.exists(resolved_stl):
            try:
                import base64
                with open(resolved_stl, 'rb') as f:
                    stl_data = f.read()
                stl_b64 = base64.b64encode(stl_data).decode('utf-8')
                stl_filename = os.path.basename(resolved_stl)
                
                print(f"[SERVER] Opening STL in CAD module: {stl_filename}")
                await sio.emit('cad_data', {
                    'format': 'stl',
                    'data': stl_b64,
                    'filename': stl_filename
                })
            except Exception as e:
                print(f"[SERVER] Warning: Could not preview STL: {e}")
        
        async def on_slicing_progress(percent, message):
            await sio.emit('slicing_progress', {
                'printer': printer_name,
                'percent': percent,
                'message': message
            })
            if percent < 100:
                 await sio.emit('status', {'msg': f"Slicing: {percent}%"})

        result = await audio_loop.printer_agent.print_stl(
            stl_path, 
            printer_name, 
            profile,
            progress_callback=on_slicing_progress,
            root_path=current_project_path
        )
        
        await sio.emit('print_result', result)
        await sio.emit('status', {'msg': f"Print Job: {result.get('status', 'unknown')}"})
        
    except Exception as e:
        print(f"Error printing STL: {e}")
        await sio.emit('error', {'msg': f"Print Failed: {str(e)}"})

@sio.event
async def get_slicer_profiles(sid):
    print("Received get_slicer_profiles request")
    if not audio_loop or not audio_loop.printer_agent:
        await sio.emit('error', {'msg': "Printer Agent not available"})
        return
    
    try:
        profiles = audio_loop.printer_agent.get_available_profiles()
        await sio.emit('slicer_profiles', profiles)
    except Exception as e:
        print(f"Error getting slicer profiles: {e}")
        await sio.emit('error', {'msg': f"Failed to get profiles: {str(e)}"})

@sio.event
async def control_kasa(sid, data):
    ip = data.get('ip')
    action = data.get('action')
    print(f"Kasa Control: {ip} -> {action}")
    
    try:
        success = False
        if action == "on":
            success = await kasa_agent.turn_on(ip)
        elif action == "off":
            success = await kasa_agent.turn_off(ip)
        elif action == "brightness":
            val = data.get('value')
            success = await kasa_agent.set_brightness(ip, val)
        elif action == "color":
            h = data.get('value', {}).get('h', 0)
            s = data.get('value', {}).get('s', 100)
            v = data.get('value', {}).get('v', 100)
            success = await kasa_agent.set_color(ip, (h, s, v))
        
        if success:
            await sio.emit('kasa_update', {
                'ip': ip,
                'is_on': True if action == "on" else (False if action == "off" else None),
                'brightness': data.get('value') if action == "brightness" else None,
            })
        else:
             await sio.emit('error', {'msg': f"Failed to control device {ip}"})

    except Exception as e:
         print(f"Error controlling kasa: {e}")
         await sio.emit('error', {'msg': f"Kasa Control Error: {str(e)}"})

# ========== MEMORY SYSTEM EVENT HANDLERS ==========

@sio.event
async def get_startup_info(sid):
    global memory_initializer
    if memory_initializer:
        try:
            startup_info = memory_initializer.initialize_on_startup()
            await sio.emit('startup_info', startup_info)
        except Exception as e:
            print(f"[MEMORY] Error getting startup info: {e}")
            await sio.emit('startup_info', {
                'user_identified': False,
                'greeting': "Namaste! Main aapka AI assistant Zoya hoon.",
                'error': str(e)
            })
    else:
        await sio.emit('startup_info', {
            'user_identified': False,
            'greeting': "Namaste! Main aapka AI assistant Zoya hoon.",
            'error': "Memory system not initialized"
        })

@sio.event
async def save_user_info(sid, data):
    global memory_initializer, memory_manager
    if not memory_manager:
        await sio.emit('error', {'msg': 'Memory system not initialized'})
        return
    
    try:
        user_name = data.get('user_name')
        user_id = data.get('user_id')
        
        if not user_name:
            await sio.emit('error', {'msg': 'User name is required'})
            return
        
        memory_manager.save_permanent_memory({
            "name": user_name,
            "user_id": user_id or user_name.lower().replace(" ", "_")
        })
        
        print(f"[MEMORY] Saved user: {user_name}")
        await sio.emit('memory_saved', {
            'type': 'user_info',
            'user_name': user_name,
            'success': True
        })
    except Exception as e:
        print(f"[MEMORY] Error saving user info: {e}")
        await sio.emit('error', {'msg': f'Failed to save user info: {str(e)}'})

@sio.event
async def get_memory(sid, data=None):
    global memory_manager
    if not memory_manager:
        await sio.emit('error', {'msg': 'Memory system not initialized'})
        return
    
    try:
        memory = memory_manager.get_permanent_memory()
        search_term = data.get('search') if data else None
        
        if search_term:
            results = memory_manager.recall_memory(search_term)
            await sio.emit('memory_data', {
                'search': search_term,
                'results': results
            })
        else:
            await sio.emit('memory_data', memory)
    except Exception as e:
        print(f"[MEMORY] Error retrieving memory: {e}")
        await sio.emit('error', {'msg': f'Failed to retrieve memory: {str(e)}'})

@sio.event
async def get_user_profile(sid):
    global memory_manager
    if not memory_manager:
        await sio.emit('error', {'msg': 'Memory system not initialized'})
        return
    
    try:
        profile = memory_manager.get_permanent_memory()
        await sio.emit('user_profile', profile)
    except Exception as e:
        print(f"[MEMORY] Error getting user profile: {e}")
        await sio.emit('error', {'msg': f'Failed to get user profile: {str(e)}'})

@sio.event
async def add_conversation_entry(sid, data):
    global memory_manager
    if not memory_manager:
        await sio.emit('error', {'msg': 'Memory system not initialized'})
        return
    
    try:
        sender = data.get('sender')
        text = data.get('text')
        
        if not sender or not text:
            await sio.emit('error', {'msg': 'Sender and text are required'})
            return
        
        memory_manager.add_conversation_entry(sender, text)
        print(f"[MEMORY] Conversation saved: {sender} → {text[:50]}...")
        await sio.emit('memory_saved', {
            'type': 'conversation',
            'sender': sender,
            'text': text,
            'success': True
        })
    except Exception as e:
        print(f"[MEMORY] Error saving conversation: {e}")
        await sio.emit('error', {'msg': f'Failed to save conversation: {str(e)}'})

@sio.event
async def clear_memory(sid, data=None):
    global memory_manager
    if not memory_manager:
        await sio.emit('error', {'msg': 'Memory system not initialized'})
        return
    
    try:
        from pathlib import Path
        memory_type = data.get('type', 'all') if data else 'all'
        
        if memory_type == 'all':
            print("[MEMORY] WARNING: Clearing ALL memories")
            memory_manager.permanent_memory = memory_manager._init_permanent_memory()
            perm_memory_path = Path('memory') / 'permanent_memory.json'
            memory_manager._save_json(perm_memory_path, memory_manager.permanent_memory)
        
        await sio.emit('memory_cleared', {
            'type': memory_type,
            'success': True
        })
    except Exception as e:
        print(f"[MEMORY] Error clearing memory: {e}")
        await sio.emit('error', {'msg': f'Failed to clear memory: {str(e)}'})

@sio.event
async def get_settings(sid):
    await sio.emit('settings', SETTINGS)

@sio.event
async def update_settings(sid, data):
    print(f"Updating settings: {data}")
    
    if "tool_permissions" in data:
        SETTINGS["tool_permissions"].update(data["tool_permissions"])
        if audio_loop:
            audio_loop.update_permissions(SETTINGS["tool_permissions"])
            
    if "face_auth_enabled" in data:
        SETTINGS["face_auth_enabled"] = data["face_auth_enabled"]
        if not data["face_auth_enabled"]:
             await sio.emit('auth_status', {'authenticated': True})
             if authenticator:
                 authenticator.stop() 

    if "camera_flipped" in data:
        SETTINGS["camera_flipped"] = data["camera_flipped"]
        print(f"[SERVER] Camera flip set to: {data['camera_flipped']}")

    if "auto_confirm_tools" in data:
        SETTINGS["auto_confirm_tools"] = data["auto_confirm_tools"]
        print(f"[SERVER] Auto-confirm tools set to: {data['auto_confirm_tools']}")

    save_settings()
    await sio.emit('settings', SETTINGS)

@sio.event
async def get_tool_permissions(sid):
    await sio.emit('tool_permissions', SETTINGS["tool_permissions"])

@sio.event
async def update_tool_permissions(sid, data):
    print(f"Updating permissions (legacy event): {data}")
    SETTINGS["tool_permissions"].update(data)
    save_settings()
    
    if audio_loop:
        audio_loop.update_permissions(SETTINGS["tool_permissions"])
    await sio.emit('tool_permissions', SETTINGS["tool_permissions"])

if __name__ == "__main__":
    uvicorn.run(
        "server:app_socketio", 
        host="127.0.0.1", 
        port=8000, 
        reload=False,
        loop="asyncio",
        reload_excludes=["temp_cad_gen.py", "output.stl", "*.stl"]
    )
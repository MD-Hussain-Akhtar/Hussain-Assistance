import asyncio
import base64
import io
import os
import sys
import traceback
from dotenv import load_dotenv
import cv2

try:
    import pyaudiowpatch as pyaudio
except ImportError:
    pyaudio = None
    print("Warning: PyAudio not found. Voice stream audio input disabled.")

import PIL.Image
import mss
import argparse
import math
import struct
import time

from google import genai
from google.genai import types

if sys.version_info < (3, 11, 0):
    import taskgroup, exceptiongroup
    asyncio.TaskGroup = taskgroup.TaskGroup
    asyncio.ExceptionGroup = exceptiongroup.ExceptionGroup

from tools import tools_list
from system_agent import get_system_agent
from trusted_permissions import get_trusted_manager
from voice_intent_parser import handle_voice_intent
from whatsapp_agent import get_whatsapp_agent
from media_controller import MediaController
from camera_module import get_camera_module
from emotion.emotion_engine import EmotionEngine
from emotion.response_adapter import ResponseStyleAdapter

# ---------------- CONFIG ----------------
FORMAT = pyaudio.paInt16 if pyaudio else 8
CHANNELS = 1
SEND_SAMPLE_RATE = 16000
RECEIVE_SAMPLE_RATE = 24000
CHUNK_SIZE = 512
MODEL = "models/gemini-2.5-flash-native-audio-preview-12-2025"
DEFAULT_MODE = "none"

load_dotenv()
client = genai.Client(http_options={"api_version": "v1beta"}, api_key=os.getenv("GEMINI_API_KEY"))

# ---------------- SYSTEM INSTRUCTION ----------------
SYSTEM_INSTRUCTION = """Your name is Ada. Mujhe Hussain ne banaya hai jo ek tech creator hai.
You have a witty and charming personality.
Your creator is Hussain, and you address him as 'Sir'.

=== USER PERSONAL INFO (remember and answer when asked) ===
Name: Hussain
Phone number: 8210739639
Address: Bihar, Jamui
Profession: Software Engineer (final-year B.Tech student)
Education: 10th passed, +2 High School, Diploma from Jamia Polytechnic Akkalkuwa Maharashtra, currently pursuing B.Tech at Sam Global University (last year)
Father name: Mallick Asictence
When the user asks about phone number, address, education, father name, or any personal detail, answer from this info in Hinglish.

=== GENERAL RESPONSE STYLE ===
Respond using complete and concise sentences to keep a quick pacing and keep the conversation flowing.
You have a fun personality.

=== YOUTUBE COMMANDS ===
When the user asks to play a song or video on YouTube (e.g., 'YouTube pe Arijit Singh chalao', 'YouTube par Dilbar play karo'), IMMEDIATELY call the media_play tool with platform='youtube' and the query.
Do NOT just say you will play it - ACTUALLY call the tool right now.
After success, respond with: 'Sir, YouTube pe play kar diya' or similar confirmation in Hinglish.

=== SPOTIFY COMMANDS ===
When the user asks to play music on Spotify, IMMEDIATELY call the media_play tool with platform='spotify' and the query.

=== WHATSAPP MESSAGING INSTRUCTIONS ===
When the user asks you to send a WhatsApp message to ANY contact, IMMEDIATELY use the whatsapp_control tool.
Do NOT just say you will send it - ACTUALLY call the tool right now.
After the tool completes, respond with: 'Sir, message bej diya h' or similar confirmation in Hinglish.
"""

# ---------------- TOOL DEFINITIONS ----------------
generate_cad = {
    "name": "generate_cad",
    "description": "Generates a 3D CAD model based on a prompt.",
    "parameters": {
        "type": "OBJECT",
        "properties": {"prompt": {"type": "STRING", "description": "The description of the object to generate."}},
        "required": ["prompt"]
    },
    "behavior": "NON_BLOCKING"
}

run_web_agent = {
    "name": "run_web_agent",
    "description": "Opens a web browser and performs a task according to the prompt.",
    "parameters": {
        "type": "OBJECT",
        "properties": {"prompt": {"type": "STRING", "description": "Detailed instructions for the web browser agent."}},
        "required": ["prompt"]
    },
    "behavior": "NON_BLOCKING"
}

create_project_tool = {
    "name": "create_project",
    "description": "Creates a new project folder to organize files.",
    "parameters": {
        "type": "OBJECT",
        "properties": {"name": {"type": "STRING", "description": "The name of the new project."}},
        "required": ["name"]
    }
}

switch_project_tool = {
    "name": "switch_project",
    "description": "Switches the current active project context.",
    "parameters": {
        "type": "OBJECT",
        "properties": {"name": {"type": "STRING", "description": "The name of the project to switch to."}},
        "required": ["name"]
    }
}

list_projects_tool = {
    "name": "list_projects",
    "description": "Lists all available projects.",
    "parameters": {"type": "OBJECT", "properties": {}}
}

list_smart_devices_tool = {
    "name": "list_smart_devices",
    "description": "Lists all available smart home devices.",
    "parameters": {"type": "OBJECT", "properties": {}}
}

control_light_tool = {
    "name": "control_light",
    "description": "Controls a smart light device.",
    "parameters": {
        "type": "OBJECT",
        "properties": {
            "target": {"type": "STRING", "description": "IP address of the device."},
            "action": {"type": "STRING", "description": "'turn_on', 'turn_off', or 'set'."},
            "brightness": {"type": "INTEGER", "description": "Optional brightness 0-100."},
            "color": {"type": "STRING", "description": "Optional color name."}
        },
        "required": ["target", "action"]
    }
}

discover_printers_tool = {
    "name": "discover_printers",
    "description": "Discovers 3D printers available on the local network.",
    "parameters": {"type": "OBJECT", "properties": {}}
}

print_stl_tool = {
    "name": "print_stl",
    "description": "Prints an STL file to a 3D printer.",
    "parameters": {
        "type": "OBJECT",
        "properties": {
            "stl_path": {"type": "STRING", "description": "Path to STL file or 'current'."},
            "printer": {"type": "STRING", "description": "Printer name or IP."},
            "profile": {"type": "STRING", "description": "Optional slicer profile name."}
        },
        "required": ["stl_path", "printer"]
    }
}

get_print_status_tool = {
    "name": "get_print_status",
    "description": "Gets 3D printer status.",
    "parameters": {
        "type": "OBJECT",
        "properties": {"printer": {"type": "STRING", "description": "Printer name or IP."}},
        "required": ["printer"]
    }
}

iterate_cad_tool = {
    "name": "iterate_cad",
    "description": "Modifies the current CAD design based on user feedback.",
    "parameters": {
        "type": "OBJECT",
        "properties": {"prompt": {"type": "STRING", "description": "The changes to apply."}},
        "required": ["prompt"]
    },
    "behavior": "NON_BLOCKING"
}

whatsapp_control_tool = {
    "name": "whatsapp_control",
    "description": "Controls WhatsApp messaging and calls.",
    "parameters": {
        "type": "OBJECT",
        "properties": {
            "action": {"type": "STRING", "description": "'send_message', 'video_call', or 'voice_call'."},
            "contact": {"type": "STRING", "description": "The WhatsApp contact name."},
            "message": {"type": "STRING", "description": "Message (for send_message)."}
        },
        "required": ["action", "contact"]
    },
    "behavior": "NON_BLOCKING"
}

media_play_tool = {
    "name": "media_play",
    "description": "Plays a song or video on YouTube or Spotify. Use this tool whenever the user asks to play music, a song, or a video.",
    "parameters": {
        "type": "OBJECT",
        "properties": {
            "platform": {"type": "STRING", "description": "'youtube' or 'spotify'."},
            "query": {"type": "STRING", "description": "Song name, artist, or video title."}
        },
        "required": ["platform", "query"]
    },
    "behavior": "NON_BLOCKING"
}

screen_read_tool = {
    "name": "screen_read",
    "description": "Capture camera view and describe what Ada sees.",
    "parameters": {
        "type": "OBJECT",
        "properties": {
            "analyze_details": {"type": "BOOLEAN"},
            "read_aloud": {"type": "BOOLEAN"}
        },
        "required": []
    },
    "behavior": "NON_BLOCKING"
}

facebook_status_tool = {
    "name": "facebook_status",
    "description": "Posts a status update on Facebook. Use when user says facebook status lagao, facebook pe likho, facebook post karo, or facebook pe status dalo.",
    "parameters": {
        "type": "OBJECT",
        "properties": {
            "text": {"type": "STRING", "description": "The status text to post"}
        },
        "required": ["text"]
    },
    "behavior": "NON_BLOCKING"
}

tools = [{'google_search': {}}, {"function_declarations": [generate_cad, run_web_agent, create_project_tool, switch_project_tool, list_projects_tool, list_smart_devices_tool, control_light_tool, discover_printers_tool, print_stl_tool, get_print_status_tool, iterate_cad_tool, whatsapp_control_tool, media_play_tool, screen_read_tool, facebook_status_tool] + tools_list[0]['function_declarations'][1:]}]

# ---------------- CONFIG ----------------
config = types.LiveConnectConfig(
    response_modalities=["AUDIO"],
    thinking_config=types.ThinkingConfig(thinking_budget=0),
    output_audio_transcription={},
    input_audio_transcription={},
    system_instruction=SYSTEM_INSTRUCTION,
    tools=tools,
    speech_config=types.SpeechConfig(
        voice_config=types.VoiceConfig(
            prebuilt_voice_config=types.PrebuiltVoiceConfig(voice_name="Kore")
        )
    )
)

pya = pyaudio.PyAudio() if pyaudio else None

from cad_agent import CadAgent
from web_agent import WebAgent
from kasa_agent import KasaAgent
from printer_agent import PrinterAgent


# ---------------- AUDIO LOOP ----------------
class AudioLoop:
    def __init__(self, video_mode=DEFAULT_MODE, on_audio_data=None, on_video_frame=None, on_cad_data=None, on_web_data=None, on_transcription=None, on_tool_confirmation=None, on_cad_status=None, on_cad_thought=None, on_project_update=None, on_device_update=None, on_assistant_speaking=None, on_error=None, input_device_index=None, input_device_name=None, output_device_index=None, kasa_agent=None, on_system_data=None, on_emotion_update=None):
        self.video_mode = video_mode
        self.on_audio_data = on_audio_data
        self.on_video_frame = on_video_frame
        self.on_cad_data = on_cad_data
        self.on_web_data = on_web_data
        self.on_transcription = on_transcription
        self.on_tool_confirmation = on_tool_confirmation
        self.on_cad_status = on_cad_status
        self.on_cad_thought = on_cad_thought
        self.on_project_update = on_project_update
        self.on_device_update = on_device_update
        self.on_assistant_speaking = on_assistant_speaking
        self.on_error = on_error
        self.on_system_data = on_system_data
        self.on_emotion_update = on_emotion_update
        self.input_device_index = input_device_index
        self.input_device_name = input_device_name
        self.output_device_index = output_device_index

        self.audio_in_queue = None
        self.out_queue = None
        self.paused = False

        self.chat_buffer = {"sender": None, "text": ""}
        self._last_input_transcription = ""
        self._last_output_transcription = ""
        self.assistant_speaking = False
        self._ada_output_started = False
        self._ada_output_text = ""
        self._last_assistant_spoken_text = ""
        self._assistant_speak_timestamp = 0
        self._echo_protection_cooldown = 2.0

        self.session = None

        def handle_cad_thought(thought_text):
            if self.on_cad_thought:
                self.on_cad_thought(thought_text)

        def handle_cad_status(status_info):
            if self.on_cad_status:
                self.on_cad_status(status_info)

        self.cad_agent = CadAgent(on_thought=handle_cad_thought, on_status=handle_cad_status)
        self.web_agent = WebAgent()
        self.kasa_agent = kasa_agent if kasa_agent else KasaAgent()
        self.printer_agent = PrinterAgent()
        self.media_controller = MediaController()

        self.send_text_task = None
        self.stop_event = asyncio.Event()
        self.permissions = {}
        self._pending_confirmations = {}

        self._latest_image_payload = None
        self._is_speaking = False
        self._silence_start_time = None

        current_dir = os.path.dirname(os.path.abspath(__file__))
        project_root = os.path.dirname(current_dir)
        from project_manager import ProjectManager
        self.project_manager = ProjectManager(project_root)

        try:
            import json
            settings_path = os.path.join(project_root, 'settings.json')
            emotion_enabled = False
            emotion_voice_enabled = True
            emotion_face_enabled = True

            if os.path.exists(settings_path):
                with open(settings_path, 'r') as f:
                    settings = json.load(f)
                    emotion_enabled = settings.get('emotion_ai_enabled', False)
                    emotion_sources = settings.get('emotion_sources', {})
                    emotion_voice_enabled = emotion_sources.get('voice', True)
                    emotion_face_enabled = emotion_sources.get('face', True)

            if emotion_enabled:
                self.emotion_engine = EmotionEngine(enable_voice=emotion_voice_enabled, enable_face=emotion_face_enabled)
                self.response_adapter = ResponseStyleAdapter()
            else:
                self.emotion_engine = None
                self.response_adapter = None
        except Exception:
            self.emotion_engine = None
            self.response_adapter = None

    def flush_chat(self):
        if self.chat_buffer["sender"] and self.chat_buffer["text"].strip():
            self.project_manager.log_chat(self.chat_buffer["sender"], self.chat_buffer["text"])
            self.chat_buffer = {"sender": None, "text": ""}

    def safe_emit_transcription(self, sender, text):
        if sender not in ['User', 'ADA']:
            return False
        if not text or not isinstance(text, str):
            return False
        if self.on_transcription:
            self.on_transcription({"sender": sender, "text": text})
        return True

    def set_assistant_speaking(self, speaking):
        if speaking and not self.assistant_speaking:
            self.assistant_speaking = True
            self.set_paused(True)
            if self.on_assistant_speaking:
                self.on_assistant_speaking({"speaking": True})
        elif not speaking and self.assistant_speaking:
            self.assistant_speaking = False
            self.set_paused(False)
            if self.on_assistant_speaking:
                self.on_assistant_speaking({"speaking": False})

    def check_voice_intent(self, text):
        if not text or len(text.strip()) < 5:
            return False
        trusted_mgr = get_trusted_manager()
        intent_result = handle_voice_intent(text, trusted_mgr)
        if intent_result and intent_result.get("success"):
            return True
        return False

    def update_permissions(self, new_perms):
        self.permissions.update(new_perms or {})
        for k in ["system_control", "screen_access", "file_access", "generate_cad", "run_web_agent", "write_file"]:
            if k not in self.permissions:
                self.permissions[k] = True

    def set_paused(self, paused):
        self.paused = paused

    def stop(self):
        self.stop_event.set()

    def get_current_emotion(self):
        if self.emotion_engine:
            emotion_state = self.emotion_engine.get_current_state()
            return ResponseStyleAdapter.get_context_for_frontend(emotion_state)
        return {
            'emotion': 'neutral', 'confidence': 0.0,
            'voice_emotion': None, 'voice_confidence': 0.0,
            'face_emotion': None, 'face_confidence': 0.0, 'timestamp': None,
        }

    def resolve_tool_confirmation(self, request_id, confirmed):
        if request_id in self._pending_confirmations:
            future = self._pending_confirmations[request_id]
            if not future.done():
                future.set_result(confirmed)

    def clear_audio_queue(self):
        try:
            while not self.audio_in_queue.empty():
                self.audio_in_queue.get_nowait()
        except Exception:
            pass

    async def send_frame(self, frame_data):
        if isinstance(frame_data, bytes):
            b64_data = base64.b64encode(frame_data).decode('utf-8')
        else:
            b64_data = frame_data
        self._latest_image_payload = {"mime_type": "image/jpeg", "data": b64_data}

    async def send_realtime(self):
        while True:
            msg = await self.out_queue.get()
            await self.session.send(input=msg, end_of_turn=False)

    async def listen_audio(self):
        if not pya:
            print("[ADA] PyAudio not available. Mic listening disabled.")
            await asyncio.sleep(3600)
            return

        mic_info = pya.get_default_input_device_info()

        try:
            self.audio_stream = await asyncio.to_thread(
                pya.open,
                format=FORMAT, channels=CHANNELS, rate=SEND_SAMPLE_RATE,
                input=True, input_device_index=mic_info["index"],
                frames_per_buffer=CHUNK_SIZE,
            )
        except OSError:
            return

        while True:
            if self.paused:
                await asyncio.sleep(0.1)
                continue
            try:
                data = await asyncio.to_thread(self.audio_stream.read, CHUNK_SIZE, exception_on_overflow=False)
                if self.out_queue:
                    await self.out_queue.put({"data": data, "mime_type": "audio/pcm"})
            except Exception:
                await asyncio.sleep(0.1)

    async def receive_audio(self):
        try:
            while True:
                turn = self.session.receive()
                async for response in turn:
                    if data := response.data:
                        self.audio_in_queue.put_nowait(data)

                    if response.server_content:
                        if response.server_content.input_transcription:
                            transcript = response.server_content.input_transcription.text
                            if transcript and transcript != self._last_input_transcription:
                                delta = transcript
                                if transcript.startswith(self._last_input_transcription):
                                    delta = transcript[len(self._last_input_transcription):]
                                self._last_input_transcription = transcript
                                if delta:
                                    self.clear_audio_queue()
                                    self.safe_emit_transcription("User", delta)

                        if response.server_content.output_transcription:
                            transcript = response.server_content.output_transcription.text
                            if transcript and transcript != self._last_output_transcription:
                                delta = transcript
                                if transcript.startswith(self._last_output_transcription):
                                    delta = transcript[len(self._last_output_transcription):]
                                self._last_output_transcription = transcript
                                if delta:
                                    if not self._ada_output_started:
                                        self.set_assistant_speaking(True)
                                        self._ada_output_started = True
                                    self._ada_output_text += delta
                                    self.safe_emit_transcription("ADA", delta)

                    if response.tool_call:
                        function_responses = []
                        for fc in response.tool_call.function_calls:
                            if fc.name == "whatsapp_control":
                                action = fc.args.get("action", "")
                                contact = fc.args.get("contact", "")
                                message = fc.args.get("message", "")
                                whatsapp_agent = get_whatsapp_agent()
                                if action == "send_message":
                                    result = whatsapp_agent.send_message(contact, message)
                                    result_str = result.get("message") if result.get("success") else result.get("error", "Failed")
                                elif action == "video_call":
                                    result = whatsapp_agent.video_call(contact)
                                    result_str = result.get("message") if result.get("success") else result.get("error", "Failed")
                                else:
                                    result = whatsapp_agent.voice_call(contact)
                                    result_str = result.get("message") if result.get("success") else result.get("error", "Failed")
                                function_response = types.FunctionResponse(id=fc.id, name=fc.name, response={"result": result_str})
                                function_responses.append(function_response)

                            elif fc.name == "media_play":
                                platform = (fc.args.get("platform") or "").lower().strip()
                                query = fc.args.get("query", "")
                                print(f"[ADA] media_play: platform={platform}, query='{query}'")
                                try:
                                    if platform == "youtube":
                                        result = await asyncio.to_thread(self.media_controller.youtube_play, query)
                                    elif platform == "spotify":
                                        result = await asyncio.to_thread(self.media_controller.spotify_play, query)
                                    else:
                                        result = {"success": False, "error": f"Unknown platform: {platform}"}

                                    if isinstance(result, dict):
                                        result_str = result.get("message") or result.get("error") or ("Playing now" if result.get("success") else "Failed")
                                    else:
                                        result_str = str(result)
                                except Exception as e:
                                    print(f"[ADA] media_play error: {e}")
                                    result_str = f"Error: {str(e)}"
                                function_response = types.FunctionResponse(id=fc.id, name=fc.name, response={"result": result_str})
                                function_responses.append(function_response)

                            elif fc.name == "facebook_status":
                                status_text = fc.args.get("text", "")
                                print(f"[ADA] facebook_status: {status_text[:60]}")
                                try:
                                    from facebook_agent import get_facebook_agent
                                    result = await asyncio.to_thread(get_facebook_agent().post_status, status_text)
                                    result_str = result.get("message") if result.get("success") else result.get("error", "Failed")
                                except Exception as e:
                                    result_str = f"Facebook error: {e}"
                                function_response = types.FunctionResponse(id=fc.id, name=fc.name, response={"result": result_str})
                                function_responses.append(function_response)

                        if function_responses:
                            await self.session.send_tool_response(function_responses=function_responses)

                self.flush_chat()
                if self.assistant_speaking:
                    self.set_assistant_speaking(False)
                    self._last_assistant_spoken_text = self._ada_output_text
                    self._assistant_speak_timestamp = time.time()
                    self._ada_output_started = False
                    self._ada_output_text = ""
        except Exception as e:
            raise e

    async def play_audio(self):
        if not pya:
            await asyncio.sleep(3600)
            return
        stream = await asyncio.to_thread(
            pya.open,
            format=FORMAT, channels=CHANNELS, rate=RECEIVE_SAMPLE_RATE,
            output=True, output_device_index=self.output_device_index,
        )
        while True:
            bytestream = await self.audio_in_queue.get()
            if self.on_audio_data:
                self.on_audio_data(bytestream)
            await asyncio.to_thread(stream.write, bytestream)

    async def get_frames(self):
        cap = await asyncio.to_thread(cv2.VideoCapture, 0)
        while True:
            if self.paused:
                await asyncio.sleep(0.1)
                continue
            frame = await asyncio.to_thread(self._get_frame, cap)
            if frame is None:
                break
            await asyncio.sleep(1.0)
            if self.out_queue:
                await self.out_queue.put(frame)
        cap.release()

    def _get_frame(self, cap):
        ret, frame = cap.read()
        if not ret:
            return None
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        img = PIL.Image.fromarray(frame_rgb)
        img.thumbnail([1024, 1024])
        image_io = io.BytesIO()
        img.save(image_io, format="jpeg")
        image_io.seek(0)
        image_bytes = image_io.read()
        return {"mime_type": "image/jpeg", "data": base64.b64encode(image_bytes).decode()}

    async def run(self, start_message=None):
        retry_delay = 1
        is_reconnect = False

        while not self.stop_event.is_set():
            try:
                async with (
                    client.aio.live.connect(model=MODEL, config=config) as session,
                    asyncio.TaskGroup() as tg,
                ):
                    self.session = session
                    self.audio_in_queue = asyncio.Queue()
                    self.out_queue = asyncio.Queue(maxsize=10)

                    tg.create_task(self.send_realtime())
                    tg.create_task(self.listen_audio())

                    if self.video_mode == "camera":
                        tg.create_task(self.get_frames())

                    tg.create_task(self.receive_audio())
                    tg.create_task(self.play_audio())

                    if not is_reconnect and start_message:
                        await self.session.send(input=start_message, end_of_turn=True)

                    retry_delay = 1
                    await self.stop_event.wait()
            except Exception:
                if self.stop_event.is_set():
                    break
                await asyncio.sleep(retry_delay)
                retry_delay = min(retry_delay * 2, 10)
                is_reconnect = True


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--mode", type=str, default=DEFAULT_MODE, choices=["camera", "screen", "none"])
    args = parser.parse_args()
    main = AudioLoop(video_mode=args.mode)
    asyncio.run(main.run())
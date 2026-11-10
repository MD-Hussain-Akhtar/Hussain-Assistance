import asyncio
import re
from typing import Dict
from app_registry import get_registry
from media_controller import get_media_controller
from screen_reader import get_screen_reader
from vision_analyzer import get_vision_analyzer
from ui_automator import get_ui_automator
from task_executor import get_task_executor
from trusted_mode_controller import get_trusted_mode_controller
import os

ROOT_SETTINGS = os.path.join(os.path.dirname(__file__), 'settings.json')


def _load_settings():
    try:
        import json
        if os.path.exists(ROOT_SETTINGS):
            with open(ROOT_SETTINGS, 'r', encoding='utf-8') as f:
                return json.load(f)
    except Exception:
        pass
    return {}


class CommandRouter:
    def __init__(self):
        """Initialize all controllers and settings."""
        self.registry = get_registry()
        self.media = get_media_controller()
        self.screen = get_screen_reader()
        self.vision = get_vision_analyzer()
        self.automator = get_ui_automator()
        self.executor = get_task_executor()
        self.trusted = get_trusted_mode_controller()
        self.settings = _load_settings()

    def detect_intent(self, text: str) -> str:
        """Detect command intent from text."""
        t = (text or '').lower()
        
        if any(k in t for k in ['open', 'launch', 'start', 'kholo']):
            return 'app_open'
        if any(k in t for k in ['play', 'spotify', 'youtube', 'song', 'music', 'gana', 'chalao', 'lagao']):
            return 'media_play'
        if any(k in t for k in ['screen', 'describe', 'see', 'understand', 'analyze', 'kya', 'dekh']):
            return 'screen_read'
        if any(k in t for k in ['close', 'band', 'hata', 'shutdown', 'restart', 'minimize', 'minimize', 'show desktop', 'desktop']):
            return 'system_control'
        if any(k in t for k in ['click', 'scroll', 'mouse', 'drag', 'move']):
            return 'ui_interaction'
        if any(k in t for k in ['type', 'write', 'input', 'text']):
            return 'ui_input'
        if any(k in t for k in ['stop', 'cancel', 'halt', 'abort', 'emergency']):
            return 'stop'
        if any(k in t for k in ['next', 'previous', 'prev', 'pause', 'volume', 'sound']):
            return 'media_control'
        if any(k in t for k in ['message', 'text', 'whatsapp', 'send', 'msg', 'mess', 'karo']):
            return 'send_message'
        return 'unknown'

    async def route(self, text: str) -> Dict:
        """Route command to appropriate handler using task executor."""
        try:
            # Use task executor for all command routing
            result = await self.executor.execute_command(text)
            return result
        except Exception as e:
            return {'success': False, 'error': f'Router error: {str(e)}'}

    def _extract_number(self, text: str, default: int = 50) -> int:
        """Extract number from text."""
        numbers = re.findall(r'\d+', text)
        return int(numbers[0]) if numbers else default


_router = None


def get_command_router() -> CommandRouter:
    """Get or create singleton CommandRouter instance."""
    global _router
    if _router is None:
        _router = CommandRouter()
    return _router

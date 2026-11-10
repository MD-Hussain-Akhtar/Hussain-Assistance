import asyncio
import json
from typing import Dict, Optional
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('TaskExecutor')


class TaskExecutor:
    def __init__(self):
        from trusted_mode_controller import get_trusted_mode_controller
        from vision_analyzer import get_vision_analyzer
        from ui_automator import get_ui_automator
        from media_automator import get_spotify_automator, get_youtube_automator, get_chrome_automator

        self.trusted = get_trusted_mode_controller()
        self.vision = get_vision_analyzer()
        self.automator = get_ui_automator()
        self.spotify = get_spotify_automator()
        self.youtube = get_youtube_automator()
        self.chrome = get_chrome_automator()

    async def execute_command(self, command: str) -> Dict:
        """Execute a high-level command"""
        try:
            cmd_lower = command.lower()

            # Spotify commands
            if 'spotify' in cmd_lower:
                return await self._handle_spotify_command(command)

            # YouTube commands
            if 'youtube' in cmd_lower or 'upload' in cmd_lower:
                return await self._handle_youtube_command(command)

            # Chrome commands
            if 'chrome' in cmd_lower or 'search' in cmd_lower or 'http' in cmd_lower:
                return await self._handle_chrome_command(command)

            # Screen reading
            if 'read' in cmd_lower or 'screen' in cmd_lower or 'see' in cmd_lower:
                return await self._handle_screen_read_command()

            # Mouse/keyboard
            if 'click' in cmd_lower or 'type' in cmd_lower or 'scroll' in cmd_lower:
                return await self._handle_ui_command(command)

            return {'success': False, 'error': f'Unknown command: {command}'}

        except Exception as e:
            logger.error(f"Command execution failed: {e}")
            return {'success': False, 'error': str(e)}

    async def _handle_spotify_command(self, command: str) -> Dict:
        """Handle Spotify automation tasks"""
        cmd_lower = command.lower()

        # Check trusted mode
        if not self.trusted.is_trusted_mode():
            return {'success': False, 'error': 'Trusted mode required for Spotify control'}

        loop = asyncio.get_running_loop()

        try:
            # Open Spotify
            if 'open' in cmd_lower:
                return await loop.run_in_executor(None, self.spotify.launch)

            # Play song
            if 'play' in cmd_lower:
                for keyword in ['play', 'song', 'track', 'gana']:
                    if keyword in cmd_lower:
                        query = command.split(keyword, 1)[1].strip()
                        if query:
                            return await loop.run_in_executor(None, self.spotify.search_and_play, query)

            # Next track
            if 'next' in cmd_lower or 'skip' in cmd_lower:
                return await loop.run_in_executor(None, self.spotify.next_track)

            # Previous track
            if 'previous' in cmd_lower or 'prev' in cmd_lower or 'back' in cmd_lower:
                return await loop.run_in_executor(None, self.spotify.previous_track)

            # Play/Pause
            if 'pause' in cmd_lower or 'stop' in cmd_lower:
                return await loop.run_in_executor(None, self.spotify.play_pause)

            if 'resume' in cmd_lower:
                return await loop.run_in_executor(None, self.spotify.play_pause)

            return {'success': False, 'error': 'Spotify command not recognized'}

        except Exception as e:
            logger.error(f"Spotify command failed: {e}")
            return {'success': False, 'error': str(e)}

    async def _handle_youtube_command(self, command: str) -> Dict:
        """Handle YouTube automation tasks"""
        cmd_lower = command.lower()

        if not self.trusted.is_trusted_mode():
            return {'success': False, 'error': 'Trusted mode required for YouTube control'}

        loop = asyncio.get_running_loop()

        try:
            # Upload video
            if 'upload' in cmd_lower:
                # Format: "upload file.mp4 title description"
                parts = command.split()
                if len(parts) >= 2:
                    file_path = parts[1]
                    title = ' '.join(parts[2:4]) if len(parts) > 2 else 'Uploaded Video'
                    description = ' '.join(parts[4:]) if len(parts) > 4 else ''
                    return await loop.run_in_executor(None, self.youtube.upload_video, file_path, title, description)

            # Search video
            if 'search' in cmd_lower:
                query = command.split('search', 1)[1].strip()
                return await loop.run_in_executor(None, self.youtube.search_video, query)

            # Open YouTube
            if 'open' in cmd_lower:
                return await loop.run_in_executor(None, self.youtube.open_youtube)

            # Open YouTube Studio
            if 'studio' in cmd_lower:
                return await loop.run_in_executor(None, self.youtube.open_studio)

            # Handle popups
            if 'agree' in cmd_lower or 'popup' in cmd_lower:
                return await loop.run_in_executor(None, self.youtube.handle_popups)

            return {'success': False, 'error': 'YouTube command not recognized'}

        except Exception as e:
            logger.error(f"YouTube command failed: {e}")
            return {'success': False, 'error': str(e)}

    async def _handle_chrome_command(self, command: str) -> Dict:
        """Handle Chrome automation tasks"""
        cmd_lower = command.lower()

        if not self.trusted.is_trusted_mode():
            return {'success': False, 'error': 'Trusted mode required for Chrome control'}

        loop = asyncio.get_running_loop()

        try:
            # Open URL
            if 'http' in cmd_lower or 'www.' in cmd_lower or 'search' in cmd_lower:
                if 'search' in cmd_lower:
                    query = command.split('search', 1)[1].strip()
                    url = f'https://www.google.com/search?q={query.replace(" ", "+")}'
                else:
                    # Extract URL
                    parts = command.split()
                    url = None
                    for part in parts:
                        if 'http' in part or 'www.' in part:
                            url = part if part.startswith('http') else f'https://{part}'
                            break
                    if not url:
                        url = 'https://' + command.split()[-1]

                return await loop.run_in_executor(None, self.chrome.open_url, url)

            # Open Chrome
            if 'open' in cmd_lower:
                return await loop.run_in_executor(None, self.chrome.launch)

            return {'success': False, 'error': 'Chrome command not recognized'}

        except Exception as e:
            logger.error(f"Chrome command failed: {e}")
            return {'success': False, 'error': str(e)}

    async def _handle_screen_read_command(self) -> Dict:
        """Read and analyze screen"""
        try:
            loop = asyncio.get_running_loop()
            description = await loop.run_in_executor(None, self.vision.describe_screen)
            return {'success': True, 'screen_analysis': description}
        except Exception as e:
            logger.error(f"Screen read failed: {e}")
            return {'success': False, 'error': str(e)}

    async def _handle_ui_command(self, command: str) -> Dict:
        """Handle mouse/keyboard UI commands"""
        cmd_lower = command.lower()
        loop = asyncio.get_running_loop()

        try:
            # Click command
            if 'click' in cmd_lower:
                # Try to find and click text
                for keyword in ['click', 'on', 'button']:
                    if keyword in cmd_lower:
                        target = command.split(keyword, 1)[1].strip()
                        if target:
                            box = await loop.run_in_executor(None, self.vision.find_text, target)
                            if box:
                                return await loop.run_in_executor(None, self.automator.click, box.cx, box.cy)

            # Type command
            if 'type' in cmd_lower or 'write' in cmd_lower:
                for keyword in ['type', 'write', 'text']:
                    if keyword in cmd_lower:
                        text = command.split(keyword, 1)[1].strip()
                        if text:
                            return await loop.run_in_executor(None, self.automator.type_text, text)

            # Scroll command
            if 'scroll' in cmd_lower:
                direction = 'down' if 'down' in cmd_lower else ('up' if 'up' in cmd_lower else 'down')
                x, y = await loop.run_in_executor(None, self.automator.get_mouse_position)
                amount = 5
                return await loop.run_in_executor(None, self.automator.scroll, x, y, direction, amount)

            return {'success': False, 'error': 'UI command not recognized'}

        except Exception as e:
            logger.error(f"UI command failed: {e}")
            return {'success': False, 'error': str(e)}

    async def execute_task(self, task_name: str, task_params: Dict) -> Dict:
        """Execute a predefined task"""
        try:
            if not self.trusted.is_trusted_mode():
                return {'success': False, 'error': 'Trusted mode required'}

            task_lower = task_name.lower()

            # Upload video task
            if task_lower == 'upload_video':
                file_path = task_params.get('file_path')
                title = task_params.get('title', 'Uploaded Video')
                description = task_params.get('description', '')
                tags = task_params.get('tags', '')

                loop = asyncio.get_running_loop()
                return await loop.run_in_executor(None, self.youtube.upload_video, file_path, title, description, tags)

            # Play music task
            if task_lower == 'play_music':
                artist = task_params.get('artist', '')
                song = task_params.get('song', '')
                query = f'{artist} {song}'.strip()

                loop = asyncio.get_running_loop()
                return await loop.run_in_executor(None, self.spotify.search_and_play, query)

            # Search and open task
            if task_lower == 'search_open':
                query = task_params.get('query', '')
                loop = asyncio.get_running_loop()
                return await loop.run_in_executor(None, self.chrome.open_url, f'https://www.google.com/search?q={query.replace(" ", "+")}')

            return {'success': False, 'error': f'Unknown task: {task_name}'}

        except Exception as e:
            logger.error(f"Task execution failed: {e}")
            return {'success': False, 'error': str(e)}


_executor = None


def get_task_executor() -> TaskExecutor:
    global _executor
    if _executor is None:
        _executor = TaskExecutor()
    return _executor

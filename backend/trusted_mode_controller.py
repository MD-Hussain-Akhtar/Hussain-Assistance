import json
import os
from typing import Dict
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('TrustedModeController')


class TrustedModeController:
    def __init__(self, settings_file: str = 'settings.json'):
        self.settings_file = settings_file
        self.settings = self._load_settings()

    def _load_settings(self) -> Dict:
        try:
            if os.path.exists(self.settings_file):
                with open(self.settings_file, 'r') as f:
                    return json.load(f)
        except Exception as e:
            logger.error(f"Load settings failed: {e}")
        return self._default_settings()

    def _default_settings(self) -> Dict:
        return {
            'trusted_mode': False,
            'trusted_user': None,
            'auto_approve_actions': [],
            'block_actions': [],
            'allow_system_control': False,
            'allow_app_launch': False,
            'allow_media_control': False,
            'allow_file_operations': False,
            'allow_screen_read': False,
            'silent_execution': False,
            'disable_confirmation': False,
        }

    def _save_settings(self):
        try:
            with open(self.settings_file, 'w') as f:
                json.dump(self.settings, f, indent=2)
        except Exception as e:
            logger.error(f"Save settings failed: {e}")

    def enable_trusted_mode(self, user_id: str) -> Dict:
        """Enable trusted mode for user"""
        try:
            self.settings['trusted_mode'] = True
            self.settings['trusted_user'] = user_id
            self.settings['silent_execution'] = True
            self.settings['disable_confirmation'] = True
            self._save_settings()
            logger.info(f"Trusted mode enabled for user {user_id}")
            return {'success': True, 'message': 'Trusted mode enabled'}
        except Exception as e:
            logger.error(f"Enable trusted mode failed: {e}")
            return {'success': False, 'error': str(e)}

    def disable_trusted_mode(self) -> Dict:
        """Disable trusted mode"""
        try:
            self.settings['trusted_mode'] = False
            self.settings['trusted_user'] = None
            self.settings['silent_execution'] = False
            self.settings['disable_confirmation'] = False
            self._save_settings()
            logger.info("Trusted mode disabled")
            return {'success': True, 'message': 'Trusted mode disabled'}
        except Exception as e:
            logger.error(f"Disable trusted mode failed: {e}")
            return {'success': False, 'error': str(e)}

    def is_trusted_mode(self) -> bool:
        """Check if trusted mode is active"""
        return self.settings.get('trusted_mode', False)

    def allow_action(self, action: str, allow: bool = True) -> Dict:
        """Allow or block specific action type"""
        try:
            if allow:
                if action not in self.settings['auto_approve_actions']:
                    self.settings['auto_approve_actions'].append(action)
                if action in self.settings['block_actions']:
                    self.settings['block_actions'].remove(action)
            else:
                if action not in self.settings['block_actions']:
                    self.settings['block_actions'].append(action)
                if action in self.settings['auto_approve_actions']:
                    self.settings['auto_approve_actions'].remove(action)

            self._save_settings()
            return {'success': True, 'action': action, 'allowed': allow}
        except Exception as e:
            logger.error(f"Allow action failed: {e}")
            return {'success': False, 'error': str(e)}

    def should_block_action(self, action: str) -> bool:
        """Check if action should be blocked"""
        if not self.is_trusted_mode():
            return False
        return action in self.settings.get('block_actions', [])

    def should_execute_silently(self, action: str) -> bool:
        """Check if action should execute silently"""
        if not self.is_trusted_mode():
            return False
        return self.settings.get('silent_execution', False)

    def get_status(self) -> Dict:
        """Get current trusted mode status"""
        return {
            'trusted_mode': self.is_trusted_mode(),
            'trusted_user': self.settings.get('trusted_user'),
            'allow_system_control': self.settings.get('allow_system_control', False),
            'allow_app_launch': self.settings.get('allow_app_launch', False),
            'allow_media_control': self.settings.get('allow_media_control', False),
            'allow_file_operations': self.settings.get('allow_file_operations', False),
            'allow_screen_read': self.settings.get('allow_screen_read', False),
            'silent_execution': self.settings.get('silent_execution', False),
            'auto_approve_actions': self.settings.get('auto_approve_actions', []),
            'block_actions': self.settings.get('block_actions', []),
        }

    def set_capability(self, capability: str, enabled: bool) -> Dict:
        """Enable/disable specific capability"""
        try:
            cap_key = f'allow_{capability}'
            if cap_key in self.settings:
                self.settings[cap_key] = enabled
                self._save_settings()
                logger.info(f"Capability {capability} set to {enabled}")
                return {'success': True, 'capability': capability, 'enabled': enabled}
            return {'success': False, 'error': f'Unknown capability: {capability}'}
        except Exception as e:
            logger.error(f"Set capability failed: {e}")
            return {'success': False, 'error': str(e)}


_trusted_controller = None


def get_trusted_mode_controller() -> TrustedModeController:
    global _trusted_controller
    if _trusted_controller is None:
        _trusted_controller = TrustedModeController()
    return _trusted_controller

"""
Trusted System Control Permissions Manager
Handles persistent trust decisions for system control actions.
Enables Jarvis-style automation with minimal popups while maintaining security.
"""

import json
import os
import logging
from pathlib import Path
from datetime import datetime

logger = logging.getLogger(__name__)

TRUSTED_PERMISSIONS_FILE = "trusted_permissions.json"

# Action Safety Classification
SAFE_ACTIONS = {
    "open_app",           # Opening trusted apps
    "type_text",          # Text input
    "control_volume",     # Volume control
    "control_brightness", # Brightness control
    "press_key",          # Keyboard navigation
    "click_mouse",        # Mouse clicks
}

DANGEROUS_ACTIONS = {
    "find_file",          # File search
    "open_file",          # File open (unknown files)
    "open_folder",        # Folder access
    "capture_screen",     # Screen capture (could expose private info)
}

# Actions that ALWAYS require confirmation
ALWAYS_CONFIRM_ACTIONS = {
    "execute_shell",
    "delete_file",
    "modify_registry",
}


class TrustedPermissionsManager:
    """Manages trusted system control permissions with persistent storage."""
    
    def __init__(self):
        """Initialize the trusted permissions manager."""
        self.config = self._load_config()
        logger.info(f"[TRUSTED] Initialized with config: enabled={self.config.get('enabled', False)}")
    
    def _load_config(self):
        """Load trusted permissions from file or create defaults."""
        if os.path.exists(TRUSTED_PERMISSIONS_FILE):
            try:
                with open(TRUSTED_PERMISSIONS_FILE, 'r') as f:
                    config = json.load(f)
                    logger.info(f"[TRUSTED] Loaded trusted permissions config")
                    return config
            except Exception as e:
                logger.error(f"[TRUSTED] Error loading config: {e}")
                return self._get_default_config()
        else:
            logger.info(f"[TRUSTED] No trusted config found, creating defaults")
            return self._get_default_config()
    
    def _get_default_config(self):
        """Get default trusted permissions structure."""
        return {
            "enabled": False,
            "remember_forever": False,
            "allowed_apps": [],  # ["chrome", "notepad", "vscode"]
            "allowed_actions": [],  # ["open_app", "type_text", "control_volume"]
            "trusted_since": None,
            "last_updated": None
        }
    
    def _save_config(self):
        """Save current config to file."""
        try:
            with open(TRUSTED_PERMISSIONS_FILE, 'w') as f:
                json.dump(self.config, f, indent=4)
            logger.info(f"[TRUSTED] Config saved to {TRUSTED_PERMISSIONS_FILE}")
        except Exception as e:
            logger.error(f"[TRUSTED] Error saving config: {e}")
    
    def is_action_safe(self, action):
        """Check if action is classified as safe."""
        return action in SAFE_ACTIONS
    
    def is_action_dangerous(self, action):
        """Check if action is classified as dangerous."""
        return action in DANGEROUS_ACTIONS or action in ALWAYS_CONFIRM_ACTIONS
    
    def always_requires_confirmation(self, action):
        """Check if action ALWAYS requires confirmation regardless of trust."""
        return action in ALWAYS_CONFIRM_ACTIONS
    
    def should_skip_confirmation(self, action, app_name=None):
        """
        Determine if confirmation popup should be skipped for this action.
        
        Args:
            action: The system control action
            app_name: The application name (for open_app actions)
        
        Returns:
            bool: True if confirmation can be skipped
        """
        # NEVER skip confirmation for actions that always require it
        if self.always_requires_confirmation(action):
            logger.info(f"[TRUSTED] Action '{action}' ALWAYS requires confirmation")
            return False
        
        # If trusted mode is not enabled, always show popup
        if not self.config.get("enabled", False):
            logger.debug(f"[TRUSTED] Trusted mode disabled")
            return False
        
        # Check if action is in allowed list
        allowed_actions = self.config.get("allowed_actions", [])
        if action not in allowed_actions:
            logger.debug(f"[TRUSTED] Action '{action}' not in allowed_actions")
            return False
        
        # For open_app, also check app is in allowed_apps
        if action == "open_app":
            allowed_apps = self.config.get("allowed_apps", [])
            if app_name and app_name.lower() not in [a.lower() for a in allowed_apps]:
                logger.debug(f"[TRUSTED] App '{app_name}' not in allowed_apps")
                return False
            logger.info(f"[TRUSTED] Trusting open_app: {app_name}")
        
        # Passed all checks - skip confirmation
        logger.info(f"[TRUSTED] Skipping confirmation for trusted action: {action}")
        return True
    
    def enable_trusted_mode(self):
        """Enable trusted system control mode."""
        self.config["enabled"] = True
        self.config["trusted_since"] = datetime.now().isoformat()
        self.config["last_updated"] = datetime.now().isoformat()
        self._save_config()
        logger.info(f"[TRUSTED] Trusted mode ENABLED")
    
    def disable_trusted_mode(self):
        """Disable trusted system control mode."""
        self.config["enabled"] = False
        self.config["last_updated"] = datetime.now().isoformat()
        self._save_config()
        logger.info(f"[TRUSTED] Trusted mode DISABLED")
    
    def set_remember_forever(self, remember):
        """Set remember_forever flag."""
        self.config["remember_forever"] = remember
        self.config["last_updated"] = datetime.now().isoformat()
        self._save_config()
        logger.info(f"[TRUSTED] Remember forever set to: {remember}")
    
    def add_allowed_app(self, app_name):
        """Add an app to the allowed list."""
        allowed_apps = self.config.get("allowed_apps", [])
        app_lower = app_name.lower()
        
        if app_lower not in [a.lower() for a in allowed_apps]:
            allowed_apps.append(app_name)
            self.config["allowed_apps"] = allowed_apps
            self.config["last_updated"] = datetime.now().isoformat()
            self._save_config()
            logger.info(f"[TRUSTED] Added app to allowed list: {app_name}")
            return True
        return False
    
    def remove_allowed_app(self, app_name):
        """Remove an app from the allowed list."""
        allowed_apps = self.config.get("allowed_apps", [])
        original_len = len(allowed_apps)
        
        # Case-insensitive removal
        allowed_apps = [a for a in allowed_apps if a.lower() != app_name.lower()]
        
        if len(allowed_apps) < original_len:
            self.config["allowed_apps"] = allowed_apps
            self.config["last_updated"] = datetime.now().isoformat()
            self._save_config()
            logger.info(f"[TRUSTED] Removed app from allowed list: {app_name}")
            return True
        return False
    
    def set_allowed_apps(self, apps):
        """Set the complete allowed apps list."""
        self.config["allowed_apps"] = [a.lower() for a in apps]
        self.config["last_updated"] = datetime.now().isoformat()
        self._save_config()
        logger.info(f"[TRUSTED] Set allowed apps: {apps}")
    
    def add_allowed_action(self, action):
        """Add an action to the allowed list."""
        allowed_actions = self.config.get("allowed_actions", [])
        
        if action not in allowed_actions:
            allowed_actions.append(action)
            self.config["allowed_actions"] = allowed_actions
            self.config["last_updated"] = datetime.now().isoformat()
            self._save_config()
            logger.info(f"[TRUSTED] Added action to allowed list: {action}")
            return True
        return False
    
    def set_allowed_actions(self, actions):
        """Set the complete allowed actions list."""
        self.config["allowed_actions"] = actions
        self.config["last_updated"] = datetime.now().isoformat()
        self._save_config()
        logger.info(f"[TRUSTED] Set allowed actions: {actions}")
    
    def get_config(self):
        """Get the current trusted permissions config."""
        return self.config.copy()
    
    def reset_to_defaults(self):
        """Reset all trusted permissions to defaults."""
        self.config = self._get_default_config()
        self._save_config()
        logger.info(f"[TRUSTED] Reset to default configuration")


# Global instance
_trusted_manager = None

def get_trusted_manager():
    """Get or create the global trusted permissions manager."""
    global _trusted_manager
    if _trusted_manager is None:
        _trusted_manager = TrustedPermissionsManager()
    return _trusted_manager

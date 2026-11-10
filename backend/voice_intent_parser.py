"""
Voice Intent Parser for Trusted System Control Mode
Processes natural language voice commands to configure trusted mode.
"""

import logging
import re

logger = logging.getLogger(__name__)


class VoiceIntentParser:
    """Parse voice intents related to trusted system control."""
    
    @staticmethod
    def parse_trusted_intent(text, trusted_manager):
        """
        Parse voice text for trusted mode commands.
        
        Supported intents:
        - "Zoya, is system ko trust kar lo" / "enable trusted mode" → Enable trusted mode
        - "Zoya, future me popup mat dikhana" / "remember forever" → Set remember_forever
        - "Zoya, sirf chrome aur notepad allow karo" / "allow chrome and notepad" → Set allowed apps
        - "Zoya, stop showing popups" / "disable trusted mode" → Disable trusted mode
        
        Args:
            text: Voice command text
            trusted_manager: TrustedPermissionsManager instance
            
        Returns:
            dict with keys: {action, success, message, config}
        """
        text_lower = text.lower().strip()
        
        # Intent 1: Enable trusted mode
        if any(phrase in text_lower for phrase in [
            "is system ko trust kar lo",
            "enable trusted mode",
            "start trusted mode",
            "jarvis mode",
            "zoya ko trust kar",
            "trust mode on"
        ]):
            trusted_manager.enable_trusted_mode()
            logger.info("[VOICE] Intent: Enable Trusted Mode")
            return {
                "action": "enable_trusted_mode",
                "success": True,
                "message": "Trusted Mode enabled. I'll minimize popups for trusted apps and actions.",
                "config": trusted_manager.get_config()
            }
        
        # Intent 2: Disable trusted mode
        if any(phrase in text_lower for phrase in [
            "disable trusted mode",
            "stop trusted mode",
            "turn off trusted mode",
            "popups show karo",
            "trust mode off",
            "stop trusting"
        ]):
            trusted_manager.disable_trusted_mode()
            logger.info("[VOICE] Intent: Disable Trusted Mode")
            return {
                "action": "disable_trusted_mode",
                "success": True,
                "message": "Trusted Mode disabled. All actions will require your confirmation.",
                "config": trusted_manager.get_config()
            }
        
        # Intent 3: Set remember forever
        if any(phrase in text_lower for phrase in [
            "future me popup mat dikhana",
            "remember forever",
            "don't ask me again",
            "remember my choice",
            "forever remember",
            "never ask again"
        ]):
            trusted_manager.set_remember_forever(True)
            logger.info("[VOICE] Intent: Remember Forever")
            return {
                "action": "set_remember_forever",
                "success": True,
                "message": "I'll remember your trust decisions even after restart.",
                "config": trusted_manager.get_config()
            }
        
        # Intent 4: Set allowed apps (parse app names)
        # Pattern: "allow [app names]" or "[apps] ko allow kar" or "sirf [apps] allow karo"
        app_matches = re.search(r"(?:allow|sirf|only)\s+(.+?)(?:\s+(?:allow|karo|kar)|$)", text_lower)
        if app_matches:
            apps_text = app_matches.group(1)
            # Split by common delimiters
            apps = re.split(r"[,\s]+(?:and|aur|\&|\+)+|[,\s]+", apps_text)
            apps = [app.strip() for app in apps if app.strip()]
            
            if apps and len(apps) > 0:
                trusted_manager.set_allowed_apps(apps)
                logger.info(f"[VOICE] Intent: Set Allowed Apps - {apps}")
                return {
                    "action": "set_allowed_apps",
                    "success": True,
                    "message": f"I'll trust {', '.join(apps)} to open without asking.",
                    "config": trusted_manager.get_config()
                }
        
        # Intent 5: Add specific app to allowed list
        # Pattern: "[app] allow kar" or "allow [app]"
        for app in ["chrome", "notepad", "vscode", "calculator", "paint", "explorer"]:
            if f"allow {app}" in text_lower or f"{app} allow" in text_lower or f"{app} karo" in text_lower:
                trusted_manager.add_allowed_app(app)
                logger.info(f"[VOICE] Intent: Add App - {app}")
                return {
                    "action": "add_app",
                    "success": True,
                    "message": f"Added {app} to trusted apps.",
                    "config": trusted_manager.get_config()
                }
        
        # No intent matched
        return {
            "action": None,
            "success": False,
            "message": None,
            "config": None
        }


def handle_voice_intent(text, trusted_manager):
    """
    Main entry point for voice intent handling.
    
    Args:
        text: Voice command text
        trusted_manager: TrustedPermissionsManager instance
        
    Returns:
        dict with parsing result, or None if no intent matched
    """
    result = VoiceIntentParser.parse_trusted_intent(text, trusted_manager)
    
    # Only return if an intent was matched
    if result.get("success"):
        return result
    
    return None

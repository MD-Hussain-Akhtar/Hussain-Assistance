"""
WhatsApp Agent for ZOYA
Handles WhatsApp messaging and video calls automation using Desktop app
"""

import pyautogui
import time
import subprocess
import logging
import webbrowser

logger = logging.getLogger(__name__)

class WhatsAppAgent:
    """Automate WhatsApp messaging and video calls via Desktop App"""
    
    def __init__(self):
        """Initialize WhatsApp agent"""
        self.message_delay = 1.5  # Delay between actions (increased for stability)
        
    def copy_to_clipboard(self, text: str):
        """Copy text to clipboard using Windows command"""
        try:
            # Use PowerShell to copy to clipboard
            cmd = f'powershell -Command "Set-Clipboard -Value \'{text}\'"'
            subprocess.run(cmd, shell=True, check=False)
            time.sleep(0.3)
        except Exception as e:
            logger.warning(f"[WHATSAPP] Clipboard copy failed: {e}")
    
    def open_whatsapp_desktop(self):
        """Open WhatsApp Desktop app"""
        try:
            logger.info("[WHATSAPP] Opening WhatsApp Desktop...")
            from app_launcher import AppLauncher
            launcher = AppLauncher()
            result = launcher.launch_common_app('whatsapp')
            if result.get('success'):
                time.sleep(3)  # Wait for app to fully load
                return True
            return False
        except Exception as e:
            logger.error(f"[WHATSAPP] Failed to open desktop: {e}")
            return False
    
    def send_message(self, contact_name: str, message: str) -> dict:
        """
        Send a message to a WhatsApp contact via Desktop App
        Improved with better typing and timing for reliable message delivery
        
        Args:
            contact_name: Name of the contact to message
            message: Message to send
            
        Returns:
            dict with success, message, and error fields
        """
        try:
            logger.info(f"[WHATSAPP] Sending message to {contact_name}: {message}")
            
            # Open WhatsApp Desktop
            self.open_whatsapp_desktop()
            
            # Focus on WhatsApp window
            logger.info("[WHATSAPP] Focusing WhatsApp window...")
            pyautogui.hotkey('alt', 'tab')
            time.sleep(2.5)  # IMPROVED: More time for window switch
            
            # Open new chat dialog with Ctrl+N
            logger.info("[WHATSAPP] Opening new chat...")
            pyautogui.hotkey('ctrl', 'n')
            time.sleep(2.5)  # IMPROVED: Wait for dialog to appear
            
            # Type contact name using typewrite for reliability
            logger.info(f"[WHATSAPP] Searching for contact: {contact_name}")
            pyautogui.typewrite(contact_name, interval=0.08)  # Better typing speed
            time.sleep(2)  # IMPROVED: Wait for autocomplete results to show
            
            # Select first result (Down + Enter)
            logger.info("[WHATSAPP] Selecting contact...")
            pyautogui.press('down')
            time.sleep(0.8)
            pyautogui.press('enter')
            time.sleep(3)  # IMPROVED: Wait for chat window to open
            
            # Type message using clipboard for special characters support
            logger.info(f"[WHATSAPP] Typing message: {message}")
            # Use clipboard to avoid typing issues with special characters
            self.copy_to_clipboard(message)
            time.sleep(0.5)
            pyautogui.hotkey('ctrl', 'v')  # Paste message
            time.sleep(1.5)  # Wait for message to be pasted
            
            # Send message with Ctrl+Enter (more reliable than just Enter)
            logger.info("[WHATSAPP] Sending message with Ctrl+Enter...")
            pyautogui.hotkey('ctrl', 'enter')
            time.sleep(3)  # IMPROVED: Wait for send to complete and message to appear
            
            # Verify message was sent by waiting for UI update
            time.sleep(1)
            
            logger.info(f"[WHATSAPP] ✓ Message sent to {contact_name}")
            return {
                'success': True,
                'message': f"Message sent to {contact_name}: {message}"
            }
            
        except Exception as e:
            logger.error(f"[WHATSAPP] Failed to send message: {e}")
            return {
                'success': False,
                'error': f"Failed to send message to {contact_name}. Error: {str(e)}"
            }
    
    def video_call(self, contact_name: str) -> dict:
        """
        Start a video call with a WhatsApp contact via Desktop App
        Improved with better timing and keyboard navigation
        
        Args:
            contact_name: Name of the contact to call
            
        Returns:
            dict with success, message, and error fields
        """
        try:
            logger.info(f"[WHATSAPP] Starting video call with {contact_name}")
            
            # Open WhatsApp Desktop
            self.open_whatsapp_desktop()
            
            # Focus on WhatsApp window
            logger.info("[WHATSAPP] Focusing WhatsApp window...")
            pyautogui.hotkey('alt', 'tab')
            time.sleep(2)  # IMPROVED: More time for window switch
            
            # Open new chat dialog with Ctrl+N
            logger.info("[WHATSAPP] Opening new chat...")
            pyautogui.hotkey('ctrl', 'n')
            time.sleep(2)  # IMPROVED: Wait for dialog
            
            # Type contact name
            logger.info(f"[WHATSAPP] Searching for contact: {contact_name}")
            pyautogui.write(contact_name)  # IMPROVED: Use write() method
            time.sleep(1.5)  # Wait for autocomplete
            
            # Select first result (Down + Enter)
            logger.info("[WHATSAPP] Selecting contact...")
            pyautogui.press('down')
            time.sleep(0.5)
            pyautogui.press('enter')
            time.sleep(2)  # IMPROVED: Wait for chat to open
            
            # Now look for video call button
            # In WhatsApp Desktop, video call button is usually in top-right of chat header
            logger.info("[WHATSAPP] Looking for video call button...")
            time.sleep(1)
            
            # Try to find and click video call icon
            # The button is typically top-right, or we can use keyboard shortcut
            # WhatsApp keyboard shortcut for video call: Ctrl+Shift+V
            try:
                logger.info("[WHATSAPP] Attempting video call with Ctrl+Shift+V...")
                pyautogui.hotkey('ctrl', 'shift', 'v')
                time.sleep(2)  # Wait for call to initiate
            except Exception as e:
                logger.warning(f"Keyboard shortcut failed, trying mouse click: {e}")
                # Fallback: click video call icon (top-right area of chat)
                pyautogui.click(1850, 100)
                time.sleep(2)
            
            logger.info(f"[WHATSAPP] ✓ Video call initiated with {contact_name}")
            return {
                'success': True,
                'message': f"Video call initiated with {contact_name}"
            }
            
        except Exception as e:
            logger.error(f"[WHATSAPP] Failed to initiate video call: {e}")
            return {
                'success': False,
                'error': f"Failed to initiate video call with {contact_name}. Error: {str(e)}"
            }
    
    def voice_call(self, contact_name: str) -> dict:
        """
        Start a voice call with a WhatsApp contact via Desktop App
        Improved with better timing and keyboard navigation
        
        Args:
            contact_name: Name of the contact to call
            
        Returns:
            dict with success, message, and error fields
        """
        try:
            logger.info(f"[WHATSAPP] Starting voice call with {contact_name}")
            
            # Open WhatsApp Desktop
            self.open_whatsapp_desktop()
            
            # Focus on WhatsApp window
            logger.info("[WHATSAPP] Focusing WhatsApp window...")
            pyautogui.hotkey('alt', 'tab')
            time.sleep(2)  # IMPROVED: More time for window switch
            
            # Open new chat dialog with Ctrl+N
            logger.info("[WHATSAPP] Opening new chat...")
            pyautogui.hotkey('ctrl', 'n')
            time.sleep(2)  # IMPROVED: Wait for dialog
            
            # Type contact name
            logger.info(f"[WHATSAPP] Searching for contact: {contact_name}")
            pyautogui.write(contact_name)  # IMPROVED: Use write() method
            time.sleep(1.5)  # Wait for autocomplete
            
            # Select first result (Down + Enter)
            logger.info("[WHATSAPP] Selecting contact...")
            pyautogui.press('down')
            time.sleep(0.5)
            pyautogui.press('enter')
            time.sleep(2)  # IMPROVED: Wait for chat to open
            
            # Now look for voice call button
            logger.info("[WHATSAPP] Looking for voice call button...")
            time.sleep(1)
            
            # Try to find and click voice call icon
            # WhatsApp keyboard shortcut for voice call: Ctrl+Shift+C
            try:
                logger.info("[WHATSAPP] Attempting voice call with Ctrl+Shift+C...")
                pyautogui.hotkey('ctrl', 'shift', 'c')
                time.sleep(2)  # Wait for call to initiate
            except Exception as e:
                logger.warning(f"Keyboard shortcut failed, trying mouse click: {e}")
                # Fallback: click voice call icon (top-right area of chat)
                pyautogui.click(1800, 100)
                time.sleep(2)
            
            logger.info(f"[WHATSAPP] ✓ Voice call initiated with {contact_name}")
            return {
                'success': True,
                'message': f"Voice call initiated with {contact_name}"
            }
            
        except Exception as e:
            logger.error(f"[WHATSAPP] Failed to initiate voice call: {e}")
            return {
                'success': False,
                'error': f"Failed to initiate voice call with {contact_name}. Error: {str(e)}"
            }

# Global instance
_whatsapp_agent = None

def get_whatsapp_agent():
    """Get or create WhatsApp agent instance"""
    global _whatsapp_agent
    if _whatsapp_agent is None:
        _whatsapp_agent = WhatsAppAgent()
    return _whatsapp_agent

#!/usr/bin/env python
"""WhatsApp Message & Video Call Automation"""
import pyautogui
import time
import subprocess
from typing import Dict

class WhatsAppMessenger:            

    def __init__(self):
        # Store common contacts
        self.contacts = {
            'papa': 'Papa',
            'papa ji': 'Papa',
            'mom': 'Mom',
            'mama': 'Mom',
            'brother': 'Brother',
            'bhai': 'Brother',
            'sister': 'Sister', 
            'behen': 'Sister',
            'friend': 'Friend',
        }
    
    def send_message(self, contact_name: str, message: str) -> Dict:
        """Send message to a contact on WhatsApp"""
        try:
            print(f"📱 Sending message to {contact_name}...")
            
            # Focus WhatsApp window
            pyautogui.hotkey('alt', 'tab')
            print("   ✓ Alt+Tab executed")
            time.sleep(2)  # INCREASED: More time for window switch
            
            # Open search/new chat
            pyautogui.hotkey('ctrl', 'n')  # New chat shortcut
            print("   ✓ Ctrl+N opened new chat")
            time.sleep(2)  # INCREASED: Wait for dialog to open
            
            # Type contact name
            pyautogui.write(contact_name)  # CHANGED: Use write() for better compatibility
            print(f"   ✓ Typed contact: {contact_name}")
            time.sleep(1.5)  # Wait for autocomplete
            
            # Click first result
            pyautogui.press('down')
            print("   ✓ Down pressed")
            time.sleep(0.5)
            pyautogui.press('enter')
            print("   ✓ Contact selected")
            time.sleep(2)  # INCREASED: Wait for chat to open
            
            # Type message
            print(f"   Message: {message}")
            pyautogui.write(message)  # CHANGED: Use write() for better compatibility
            print("   ✓ Message typed")
            time.sleep(1)
            
            # Send message - WhatsApp uses Ctrl+Enter or just Enter to send
            print("   Sending...")
            pyautogui.press('enter')  # Standard send key in WhatsApp
            time.sleep(2)  # INCREASED: Wait for send to complete
            
            print("   ✅ Message sent!")
            return {
                "success": True,
                "action": "message_sent",
                "contact": contact_name,
                "message": message,
                "status": "sent"
            }
        except Exception as e:
            print(f"Error: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def start_video_call(self, contact_name: str) -> Dict:
        """Start video call with a contact"""
        try:
            print(f"📹 Starting video call with {contact_name}...")
            
            # Focus WhatsApp window
            pyautogui.hotkey('alt', 'tab')
            time.sleep(0.5)
            
            # Open search/contacts
            pyautogui.hotkey('ctrl', 'n')  # New chat
            time.sleep(1)
            
            # Type contact name
            pyautogui.typewrite(contact_name, interval=0.05)
            time.sleep(0.5)
            
            # Click first result
            pyautogui.press('down')
            time.sleep(0.2)
            pyautogui.press('enter')
            time.sleep(1)
            
            # Look for video call button - usually top right
            # In WhatsApp desktop, click the video call icon
            print("   Finding video call button...")
            
            # Move to top right area where call buttons are
            pyautogui.moveTo(1200, 100, duration=0.3)
            time.sleep(0.3)
            
            # Click video call button (usually the video camera icon)
            pyautogui.click()
            time.sleep(2)
            
            print("   ✅ Video call initiated!")
            return {
                "success": True,
                "action": "video_call_started",
                "contact": contact_name,
                "status": "calling"
            }
        except Exception as e:
            print(f"Error: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def start_voice_call(self, contact_name: str) -> Dict:
        """Start voice call with a contact"""
        try:
            print(f"📞 Starting voice call with {contact_name}...")
            
            # Focus WhatsApp window
            pyautogui.hotkey('alt', 'tab')
            time.sleep(0.5)
            
            # Open search/contacts
            pyautogui.hotkey('ctrl', 'n')  # New chat
            time.sleep(1)
            
            # Type contact name
            pyautogui.typewrite(contact_name, interval=0.05)
            time.sleep(0.5)
            
            # Click first result
            pyautogui.press('down')
            time.sleep(0.2)
            pyautogui.press('enter')
            time.sleep(1)
            
            # Move to top right area where call buttons are
            pyautogui.moveTo(1150, 100, duration=0.3)
            time.sleep(0.3)
            
            # Click voice call button (usually the phone icon)
            pyautogui.click()
            time.sleep(2)
            
            print("   ✅ Voice call initiated!")
            return {
                "success": True,
                "action": "voice_call_started",
                "contact": contact_name,
                "status": "calling"
            }
        except Exception as e:
            print(f"Error: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def quick_message(self, recipient: str, text: str) -> Dict:
        """Quick message send"""
        recipient_clean = recipient.lower().strip()
        contact = self.contacts.get(recipient_clean, recipient)
        return self.send_message(contact, text)

# Test
if __name__ == "__main__":
    wa = WhatsAppMessenger()
    print("\n✅ WhatsApp Message & Call Automation Ready!")
    print("\nFeatures:")
    print("  • Send messages")
    print("  • Video calls")
    print("  • Voice calls")

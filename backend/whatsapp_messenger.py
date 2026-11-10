#!/usr/bin/env python
"""WhatsApp Message Automation"""
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
            time.sleep(0.5)
            
            # Open search/new chat
            pyautogui.hotkey('ctrl', 'n')  # New chat shortcut
            time.sleep(1)
            
            # Type contact name
            pyautogui.typewrite(contact_name, interval=0.05)
            time.sleep(0.5)
            
            # Click first result
            pyautogui.press('down')
            time.sleep(0.2)
            pyautogui.press('enter')
            time.sleep(1)
            
            # Type message
            print(f"   Message: {message}")
            pyautogui.typewrite(message, interval=0.02)
            time.sleep(0.5)
            
            # Send message - WhatsApp uses Ctrl+Enter or just Enter to send
            print("   Sending...")
            pyautogui.press('enter')  # Standard send key in WhatsApp
            time.sleep(1)
            
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
    
    def quick_message(self, recipient: str, text: str) -> Dict:
        """Quick message send"""
        # Clean recipient name
        recipient_clean = recipient.lower().strip()
        
        # Map to actual contact
        contact = self.contacts.get(recipient_clean, recipient)
        
        return self.send_message(contact, text)

# Test
if __name__ == "__main__":
    wa = WhatsAppMessenger()
    print("\n✅ WhatsApp Message Automation Ready!")
    print("\nUsage:")
    print('  message_to("papa", "hello papa how are you")')
    print('  message_to("mom", "hi mom")')
    print('  message_to("friend", "hey whats up")')

#!/usr/bin/env python3
"""
Test script to verify WhatsApp message sending functionality
This tests the actual send_message method with proper timing and feedback
"""

import sys
import time
from whatsapp_agent import get_whatsapp_agent

def test_whatsapp_message():
    """Test sending a WhatsApp message"""
    print("\n" + "="*60)
    print("WHATSAPP MESSAGE SENDING TEST")
    print("="*60)
    
    agent = get_whatsapp_agent()
    
    # Test message
    contact = "Ayush"  # Change this to a real contact name
    message = "Test message from automation"
    
    print(f"\n[TEST] Sending message to: {contact}")
    print(f"[TEST] Message: {message}")
    print(f"\n[INFO] Starting WhatsApp message send in 3 seconds...")
    print("[INFO] Make sure WhatsApp is installed and you're logged in")
    
    time.sleep(3)
    
    print("\n[EXECUTING] Calling send_message()...")
    result = agent.send_message(contact, message)
    
    print("\n[RESULT]:")
    print(f"  Success: {result.get('success')}")
    if result.get('success'):
        print(f"  Message: {result.get('message')}")
        print("\n✅ TEST PASSED - Message should have been sent!")
    else:
        print(f"  Error: {result.get('error')}")
        print("\n❌ TEST FAILED - Check the error above")
    
    print("\n" + "="*60)
    print("TEST COMPLETE")
    print("="*60 + "\n")

if __name__ == "__main__":
    test_whatsapp_message()

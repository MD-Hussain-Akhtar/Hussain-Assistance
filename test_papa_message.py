#!/usr/bin/env python
"""Test WhatsApp messaging to papa"""
import sys
import time
sys.path.insert(0, 'g:\\ada_v2-main\\backend')

from whatsapp_agent import get_whatsapp_agent

print("=" * 60)
print("TESTING WHATSAPP MESSAGE TO PAPA")
print("=" * 60)

agent = get_whatsapp_agent()

# Test send message to papa
print("\n[TEST] Sending message to papa...")
print("Contact: papa")
print("Message: Kya kar rahe ho papa?")
print("\nStarting WhatsApp Web...")

result = agent.send_message("papa", "Kya kar rahe ho papa?")

print(f"\nResult: {result}")

if result.get('success'):
    print("\n✅ SUCCESS: Message sent!")
else:
    print("\n❌ FAILED:")
    print(f"Error: {result.get('error')}")

print("\n" + "=" * 60)
print("Make sure:")
print("1. WhatsApp Web is open in a browser")
print("2. You're already logged in to WhatsApp Web")
print("3. Papa is in your contacts")
print("=" * 60)

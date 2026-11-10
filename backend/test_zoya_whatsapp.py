#!/usr/bin/env python
"""
Test WhatsApp messaging feature end-to-end
This simulates what happens when you tell Zoya to send a message
"""

from whatsapp_agent import get_whatsapp_agent

print("=== WhatsApp Feature Test (via Zoya) ===\n")

# This is what happens when you say "send message to papa: hello"
whatsapp_agent = get_whatsapp_agent()

print("[1] Testing WhatsApp message send...")
print("    Contact: papa")
print("    Message: hello\n")

result = whatsapp_agent.send_message('papa', 'hello')

print(f"\nResult:")
print(f"  Success: {result.get('success')}")
print(f"  Message: {result.get('message') or result.get('error')}")

if result.get('success'):
    print("\n✅ FEATURE WORKING!")
    print("   You can now say to Zoya:")
    print("   - 'Send message to papa: hello'")
    print("   - 'Message mama: how are you'")
    print("   - 'Tell [contact name]: [your message]'")
else:
    print("\n⚠️  Message send encountered an issue.")
    print("   Check the WhatsApp window on your desktop.")

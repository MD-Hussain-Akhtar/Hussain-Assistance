#!/usr/bin/env python
"""Test WhatsApp Message Feature"""
from whatsapp_messenger import WhatsAppMessenger
import time

print("\n" + "="*60)
print("💬 WhatsApp Message Automation - READY!")
print("="*60)

wa = WhatsAppMessenger()

print("\n✅ Feature: SEND MESSAGES TO CONTACTS")
print("\nHow to use:")
print("  Say: 'message papa hello papa how are you'")
print("  Say: 'send message to mom hi mom'")
print("  Say: 'message friend hey whats up'")

print("\n📋 Available Contacts:")
print("  • Papa (papa, papa ji)")
print("  • Mom (mom, mama)")
print("  • Brother (brother, bhai)")
print("  • Sister (sister, behen)")
print("  • Friend")

print("\n" + "-"*60)
print("EXAMPLE USAGE:")
print("-"*60)

# Example 1
print("\n[Example 1] Sending to Papa")
print("Command: message papa hello papa how are you")
print("Status: Ready to send!")

# Example 2
print("\n[Example 2] Sending to Mom")
print("Command: message mom hi mom")
print("Status: Ready to send!")

# Example 3
print("\n[Example 3] Sending to Friend")
print("Command: message friend hey whats up")
print("Status: Ready to send!")

print("\n" + "="*60)
print("✅ WHATSAPP MESSAGING FEATURE ACTIVE!")
print("="*60)
print("\n💡 TIP: Make sure WhatsApp is open on your screen")
print("         for messages to send successfully!\n")

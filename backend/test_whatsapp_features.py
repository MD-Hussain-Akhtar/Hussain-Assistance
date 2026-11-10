#!/usr/bin/env python
"""Test WhatsApp Message and Video Call Features"""
from whatsapp_v2 import WhatsAppMessenger

print("\n" + "="*60)
print("💬 WhatsApp Features - ENHANCED")
print("="*60)

wa = WhatsAppMessenger()

print("\n✅ FEATURE 1: SEND MESSAGES")
print("   Commands:")
print("   • 'message papa hello'")
print("   • 'message mom hi'")
print("   • 'message friend hey'")

print("\n✅ FEATURE 2: VIDEO CALLS")
print("   Commands:")
print("   • 'video call papa'")
print("   • 'video call mom'")
print("   • 'call papa' (voice)")

print("\n✅ FEATURE 3: VOICE CALLS")
print("   Commands:")
print("   • 'call papa'")
print("   • 'call mom'")
print("   • 'voice call friend'")

print("\n" + "="*60)
print("📱 AVAILABLE CONTACTS:")
print("="*60)
for key in wa.contacts:
    print(f"   • {key}")

print("\n" + "="*60)
print("HOW TO USE:")
print("="*60)
print("""
MESSAGE:        Say "message papa hello papa"
VIDEO CALL:     Say "video call papa"  
VOICE CALL:     Say "call papa"

Make sure WhatsApp is visible on screen!
""")
print("="*60)

#!/usr/bin/env python
"""
Test WhatsApp video call feature with papa
"""
from whatsapp_agent import get_whatsapp_agent

print("=== WhatsApp Video Call Test ===\n")
print("Initiating video call with Papa...\n")

agent = get_whatsapp_agent()
result = agent.video_call('papa')

print(f"\nResult:")
print(f"  Success: {result.get('success')}")
print(f"  Message: {result.get('message') or result.get('error')}")

if result.get('success'):
    print("\n✅ VIDEO CALL WORKING!")
    print("   You can now say to Zoya:")
    print("   - 'Video call papa'")
    print("   - 'Call mama on video'")
    print("   - 'Start video call with brother'")
else:
    print("\n⚠️  Video call encountered an issue")
    print("   Check your WhatsApp window")

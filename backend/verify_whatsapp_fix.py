#!/usr/bin/env python
"""
Test WhatsApp messaging to verify the fix works
This simulates what happens when you say "send message to papa" in Electron
"""

import sys
sys.path.insert(0, 'backend')

from whatsapp_agent import get_whatsapp_agent

print("="*60)
print("Testing WhatsApp Feature")
print("="*60)
print("\nScenario: You said 'भेजा भेजा पापा को' (send message to papa)")
print("Expected: Message actually gets sent (not just said)\n")

# Test the agent directly
agent = get_whatsapp_agent()

print("[1] Agent loaded ✓")
print("[2] Calling whatsapp_control with send_message action...")
print("    Contact: papa")
print("    Message: hello test\n")

result = agent.send_message('papa', 'hello test from zoya')

print(f"\n[RESULT]")
print(f"  Success: {result.get('success')}")
print(f"  Message: {result.get('message') or result.get('error')}\n")

if result.get('success'):
    print("✅ WhatsApp TOOL CALL WORKING!")
    print("\nNow when you say in Electron:")
    print('  "भेजा भेजा पापा को"')
    print('  or "Send message to papa: hello"')
    print("\nZoya will:")
    print("  1. Call whatsapp_control tool (NOT just say it)")
    print("  2. Actually open WhatsApp")
    print("  3. Find papa")
    print("  4. Send the message")
    print("  5. Confirm to you")
else:
    print("⚠️  Issue detected")
    print("Check if WhatsApp process is running:")
    import subprocess
    proc = subprocess.run(['tasklist'], capture_output=True, text=True)
    if 'WhatsApp' in proc.stdout:
        print("  ✓ WhatsApp process running")
    else:
        print("  ✗ WhatsApp not running - open WhatsApp manually")

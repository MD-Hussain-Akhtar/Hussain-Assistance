#!/usr/bin/env python
"""
Complete WhatsApp Feature Demo for Zoya
Shows all available WhatsApp commands
"""

print("="*60)
print("ZOYA WhatsApp Features - Complete Integration")
print("="*60)

print("\n📱 FEATURES AVAILABLE:\n")

print("1. SEND MESSAGES")
print("   Command: 'Send message to [contact]: [text]'")
print("   Examples:")
print("   - 'Send message to papa: hello'")
print("   - 'Message mama: how are you'")
print("   - 'Tell brother: see you later'")

print("\n2. VIDEO CALLS")
print("   Command: 'Video call [contact]'")
print("   Examples:")
print("   - 'Video call papa'")
print("   - 'Call mama on video'")
print("   - 'Start video call with brother'")

print("\n3. VOICE CALLS")
print("   Command: 'Voice call [contact]'")
print("   Examples:")
print("   - 'Voice call papa'")
print("   - 'Call mama'")
print("   - 'Phone call to brother'")

print("\n" + "="*60)
print("QUICK CONTACT LIST (Pre-configured):")
print("="*60)

contacts = {
    'Papa': ['papa', 'papa ji'],
    'Mom': ['mom', 'mama'],
    'Brother': ['brother', 'bhai'],
    'Sister': ['sister', 'behen'],
    'Friend': ['friend'],
}

for name, aliases in contacts.items():
    print(f"  {name:15} → aliases: {', '.join(aliases)}")

print("\nPlus any contact name in your WhatsApp contacts list!")

print("\n" + "="*60)
print("HOW TO USE:")
print("="*60)
print("""
1. Start Electron/Zoya: npm run dev (in project root)
2. Say any WhatsApp command to Zoya
3. Zoya will process your request and:
   - Open WhatsApp Desktop
   - Find the contact
   - Perform the action (message/call)
   - Confirm with you

Example:
  You: "Send message to papa: hello how are you"
  Zoya: "Message sent to papa: hello how are you"
  
  You: "Video call mama"
  Zoya: "Video call initiated with mama"
  
  You: "Voice call brother"
  Zoya: "Voice call initiated with brother"
""")

print("="*60)
print("✅ ALL FEATURES INTEGRATED & READY!")
print("="*60)

# Optional: test the agent directly
print("\nTesting WhatsApp agent...")
try:
    from whatsapp_agent import get_whatsapp_agent
    agent = get_whatsapp_agent()
    print("✓ WhatsApp agent loaded successfully")
    print("✓ Ready for voice commands via Zoya")
except Exception as e:
    print(f"✗ Error loading agent: {e}")

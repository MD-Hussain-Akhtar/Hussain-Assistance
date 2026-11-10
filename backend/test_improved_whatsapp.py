#!/usr/bin/env python
"""Test the improved whatsapp_v2 module"""
from whatsapp_v2 import WhatsAppMessenger

wa = WhatsAppMessenger()
print("Testing improved WhatsApp messaging...\n")
result = wa.quick_message('papa', 'hello')
print(f"\nFinal result: {result}")

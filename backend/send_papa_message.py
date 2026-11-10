#!/usr/bin/env python
from whatsapp_v2 import WhatsAppMessenger
import time

print('=== WhatsApp Message Test ===\n')
print('Sending "hello" to Papa...')
time.sleep(2)  # Give WhatsApp time to be in focus

wa = WhatsAppMessenger()
result = wa.quick_message('papa', 'hello')

print(f'\n✓ Result: {result}')
if result.get('success'):
    print('✓ Message sent successfully!')
else:
    print(f'✗ Error: {result.get("error")}')

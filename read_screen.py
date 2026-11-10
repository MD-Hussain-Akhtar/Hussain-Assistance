#!/usr/bin/env python
import sys
sys.path.insert(0, r'G:\ada_v2-main\backend')

from screen_reader import get_screen_reader

reader = get_screen_reader()
result = reader.read_screen()

if result['success']:
    print('=== Screen Text (OCR) ===\n')
    print(result['text'])
else:
    print('Error:', result.get('error', 'Unknown error'))

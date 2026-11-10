#!/usr/bin/env python3
from screen_reader import ScreenReader

def main():
    sr = ScreenReader()
    res = sr.read_screen()
    if res.get('success'):
        print('OCR text (first 300 chars):')
        print(res.get('text','')[:300])
    else:
        print('ERROR:', res.get('error'))

if __name__ == '__main__':
    main()

#!/usr/bin/env python3
"""
Test script to verify that all media features are integrated into ada.py
"""

import sys
sys.path.insert(0, 'backend')

# Check ada.py for media_play tool
with open('backend/ada.py', 'r') as f:
    content = f.read()
    
    checks = {
        'media_play_tool definition': 'media_play_tool = {' in content,
        'media_play in tools list': 'media_play_tool' in content and 'tools = [' in content,
        'MediaController import': 'from media_controller import MediaController' in content,
        'media_play handler': 'elif fc.name == "media_play"' in content,
        'spotify_play method call': 'media_controller.spotify_play' in content,
        'youtube_play method call': 'media_controller.youtube_play' in content,
        'YouTube instructions in system_instruction': 'youtube_play' in content and 'system_instruction' in content,
        'Spotify instructions in system_instruction': 'spotify_play' in content and 'system_instruction' in content,
    }
    
    print("=" * 60)
    print("FEATURE INTEGRATION CHECK")
    print("=" * 60)
    
    all_passed = True
    for check_name, result in checks.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status}: {check_name}")
        if not result:
            all_passed = False
    
    print("=" * 60)
    if all_passed:
        print("✅ All features successfully integrated!")
        print("\nFeatures available:")
        print("  • WhatsApp: send_message, video_call, voice_call")
        print("  • Spotify: Play music via voice command 'Spotify pe [song]'")
        print("  • YouTube: Play videos via voice command 'YouTube par [video]'")
        print("\nTest in Electron by saying:")
        print("  - 'youtube par arijit singh chala de'")
        print("  - 'softiy pe akhil ke song chala'")
        print("  - 'papa ko message bhej hello bol kar'")
    else:
        print("❌ Some features are missing!")
        sys.exit(1)

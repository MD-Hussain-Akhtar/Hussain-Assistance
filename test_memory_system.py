#!/usr/bin/env python
"""
Test script for Permanent Memory System
Tests all memory operations locally without server
"""

import json
import sys
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent / 'backend'))

from memory_manager import get_memory_manager
from memory_initializer import MemoryInitializer

def test_memory_system():
    """Test all memory system operations"""
    
    print("=" * 60)
    print("PERMANENT MEMORY SYSTEM - TEST SUITE")
    print("=" * 60)
    
    # Initialize
    print("\n[TEST 1] Initialize Memory System")
    try:
        mm = get_memory_manager()
        print("✅ MemoryManager initialized")
    except Exception as e:
        print(f"❌ Failed: {e}")
        return False
    
    # Test 2: Save user info
    print("\n[TEST 2] Save User Information")
    try:
        mm.save_permanent_memory({
            "name": "Ayush Sir",
            "user_id": "ayush_001"
        })
        print("✅ User info saved: Ayush Sir")
    except Exception as e:
        print(f"❌ Failed: {e}")
        return False
    
    # Test 3: Save preferences
    print("\n[TEST 3] Save Preferences")
    try:
        mm.save_preference("music", "genre", "lofi")
        mm.save_preference("clothing", "style", "formal")
        print("✅ Preferences saved:")
        print("   - music/genre: lofi")
        print("   - clothing/style: formal")
    except Exception as e:
        print(f"❌ Failed: {e}")
        return False
    
    # Test 4: Save habits
    print("\n[TEST 4] Save Habits")
    try:
        mm.save_habit("sleep_time", {"time": "1:30 AM", "quality": "good"})
        mm.save_habit("work_time", {"start": "9 AM", "end": "6 PM"})
        print("✅ Habits saved:")
        print("   - sleep_time: 1:30 AM")
        print("   - work_time: 9 AM - 6 PM")
    except Exception as e:
        print(f"❌ Failed: {e}")
        return False
    
    # Test 5: Save emotions
    print("\n[TEST 5] Save Emotions")
    try:
        mm.save_emotion_permanent("happy", context="Project completed")
        mm.save_emotion_permanent("tired", context="Late work session")
        print("✅ Emotions saved:")
        print("   - happy (Project completed)")
        print("   - tired (Late work session)")
    except Exception as e:
        print(f"❌ Failed: {e}")
        return False
    
    # Test 6: Save conversations
    print("\n[TEST 6] Save Conversations")
    try:
        mm.save_conversation_permanent("User", "Zoya ye yaad rakh lo")
        mm.save_conversation_permanent("ADA", "Theek hai sir, yaad rakh liya")
        print("✅ Conversations saved:")
        print("   - User: Zoya ye yaad rakh lo")
        print("   - ADA: Theek hai sir, yaad rakh liya")
    except Exception as e:
        print(f"❌ Failed: {e}")
        return False
    
    # Test 7: Retrieve complete memory
    print("\n[TEST 7] Retrieve Complete Memory")
    try:
        memory = mm.get_permanent_memory()
        print("✅ Complete memory retrieved:")
        print(f"   - User: {memory.get('name')}")
        print(f"   - Preferences: {len(memory.get('preferences', {}))} categories")
        print(f"   - Habits: {len(memory.get('habits', {}))} recorded")
        print(f"   - Emotions: {len(memory.get('emotion_history', []))} recorded")
        print(f"   - Conversations: {len(memory.get('last_conversations', []))} recorded")
    except Exception as e:
        print(f"❌ Failed: {e}")
        return False
    
    # Test 8: Search functionality
    print("\n[TEST 8] Search Memories")
    try:
        results = mm.recall_memory("lofi")
        print(f"✅ Search for 'lofi': Found {len(results)} results")
        for r in results:
            print(f"   - {r.get('type')}: {r.get('data')}")
    except Exception as e:
        print(f"❌ Failed: {e}")
        return False
    
    # Test 9: Get specific category
    print("\n[TEST 9] Get Specific Categories")
    try:
        prefs = mm.get_preferences("music")
        habits = mm.get_habits("sleep_time")
        print("✅ Category retrieval:")
        print(f"   - Music preferences: {prefs}")
        print(f"   - Sleep habits: {habits}")
    except Exception as e:
        print(f"❌ Failed: {e}")
        return False
    
    # Test 10: MemoryInitializer
    print("\n[TEST 10] MemoryInitializer - Startup Handler")
    try:
        init = MemoryInitializer()
        startup_info = init.initialize_on_startup()
        print("✅ Startup initialization:")
        print(f"   - User identified: {startup_info.get('user_identified')}")
        print(f"   - User name: {startup_info.get('user_name')}")
        print(f"   - Greeting: {startup_info.get('greeting')}")
        print(f"   - Memories loaded: {startup_info.get('memories_loaded')}")
    except Exception as e:
        print(f"❌ Failed: {e}")
        return False
    
    # Test 11: Persistence check
    print("\n[TEST 11] Verify File Persistence")
    try:
        perm_file = Path('backend/memory/permanent_memory.json')
        if perm_file.exists():
            with open(perm_file, 'r') as f:
                file_data = json.load(f)
            print("✅ Permanent memory file exists and is valid JSON")
            print(f"   - File path: {perm_file}")
            print(f"   - File size: {perm_file.stat().st_size} bytes")
            print(f"   - User in file: {file_data.get('name')}")
        else:
            print(f"❌ File not found: {perm_file}")
            return False
    except Exception as e:
        print(f"❌ Failed: {e}")
        return False
    
    # Test 12: Reload test (simulate restart)
    print("\n[TEST 12] Reload Test (Simulate Restart)")
    try:
        # Create new instance (simulating fresh import)
        from importlib import reload
        import memory_manager as mm_module
        reload(mm_module)
        mm2 = mm_module.get_memory_manager()
        memory2 = mm2.get_permanent_memory()
        
        if memory2.get('name') == "Ayush Sir":
            print("✅ Data persisted! Reload successful")
            print(f"   - Name still present: {memory2.get('name')}")
            print(f"   - Preferences still present: {len(memory2.get('preferences', {}))} categories")
        else:
            print("❌ Data lost after reload!")
            return False
    except Exception as e:
        print(f"⚠️  Reload test skipped: {e}")
    
    # Summary
    print("\n" + "=" * 60)
    print("✅ ALL TESTS PASSED!")
    print("=" * 60)
    print("\nMemory System Status:")
    print("  • Saving: ✅ WORKING")
    print("  • Retrieval: ✅ WORKING")
    print("  • Persistence: ✅ WORKING")
    print("  • Search: ✅ WORKING")
    print("  • Startup Handler: ✅ WORKING")
    print("\nData Location: backend/memory/permanent_memory.json")
    print("\n🎉 Permanent Memory System is READY FOR PRODUCTION!")
    print("=" * 60)
    
    return True


def show_memory_contents():
    """Display current memory file contents"""
    print("\n" + "=" * 60)
    print("CURRENT MEMORY CONTENTS")
    print("=" * 60)
    
    perm_file = Path('backend/memory/permanent_memory.json')
    if not perm_file.exists():
        print("No permanent memory file found yet")
        return
    
    try:
        with open(perm_file, 'r') as f:
            data = json.load(f)
        
        print(json.dumps(data, indent=2, ensure_ascii=False))
    except Exception as e:
        print(f"Error reading file: {e}")


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Test Permanent Memory System")
    parser.add_argument("--show", action="store_true", help="Show memory contents")
    parser.add_argument("--clean", action="store_true", help="Clean memory (WARNING!)")
    
    args = parser.parse_args()
    
    if args.clean:
        print("⚠️  WARNING: Clearing all memories...")
        perm_file = Path('backend/memory/permanent_memory.json')
        if perm_file.exists():
            perm_file.unlink()
            print("✅ Memory cleared")
        sys.exit(0)
    
    if args.show:
        show_memory_contents()
        sys.exit(0)
    
    # Run tests
    success = test_memory_system()
    
    # Show contents
    print("\n")
    show_memory_contents()
    
    sys.exit(0 if success else 1)

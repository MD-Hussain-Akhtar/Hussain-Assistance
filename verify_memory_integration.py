#!/usr/bin/env python
"""
Quick verification that the permanent memory system is integrated into the backend
Checks that all components are properly connected
"""

import os
import sys
from pathlib import Path

def check_file_exists(path, description):
    """Check if a file exists and print status"""
    exists = Path(path).exists()
    status = "✅" if exists else "❌"
    print(f"{status} {description}: {path}")
    return exists

def check_import(module_name, description):
    """Check if a module can be imported"""
    try:
        __import__(module_name)
        print(f"✅ {description}: {module_name}")
        return True
    except ImportError as e:
        print(f"❌ {description}: {module_name} - {e}")
        return False

def check_server_integration():
    """Check if server.py has memory integration"""
    server_file = Path("backend/server.py")
    if not server_file.exists():
        print("❌ Cannot find backend/server.py")
        return False
    
    with open(server_file, 'r') as f:
        content = f.read()
    
    checks = {
        "Memory imports": "from memory_initializer import MemoryInitializer" in content,
        "MemoryInitializer initialization": "memory_initializer = MemoryInitializer()" in content,
        "Startup handler": "initialize_on_startup" in content,
        "Socket.IO events": "@sio.event" in content and "save_memory" in content,
    }
    
    all_good = True
    for check_name, passed in checks.items():
        status = "✅" if passed else "❌"
        print(f"{status} {check_name}")
        if not passed:
            all_good = False
    
    return all_good

def main():
    print("=" * 70)
    print("PERMANENT MEMORY SYSTEM - INTEGRATION VERIFICATION")
    print("=" * 70)
    
    print("\n📁 FILE STRUCTURE CHECK")
    print("-" * 70)
    
    all_files_ok = True
    
    # Backend files
    all_files_ok &= check_file_exists("backend/memory_manager.py", "Memory Manager")
    all_files_ok &= check_file_exists("backend/memory_initializer.py", "Memory Initializer")
    all_files_ok &= check_file_exists("backend/greeting_engine.py", "Greeting Engine")
    all_files_ok &= check_file_exists("backend/memory_integration.py", "Memory Integration")
    all_files_ok &= check_file_exists("backend/server.py", "Server (main)")
    
    print("\n📦 PYTHON IMPORTS CHECK")
    print("-" * 70)
    
    os.chdir('backend')
    sys.path.insert(0, '.')
    
    all_imports_ok = True
    all_imports_ok &= check_import("memory_manager", "Memory Manager module")
    all_imports_ok &= check_import("memory_initializer", "Memory Initializer module")
    all_imports_ok &= check_import("greeting_engine", "Greeting Engine module")
    
    print("\n🔗 SERVER INTEGRATION CHECK")
    print("-" * 70)
    
    os.chdir('..')
    server_integration_ok = check_server_integration()
    
    print("\n📄 DOCUMENTATION CHECK")
    print("-" * 70)
    
    all_docs_ok = True
    all_docs_ok &= check_file_exists("MEMORY_SYSTEM_GUIDE.md", "Complete System Guide")
    all_docs_ok &= check_file_exists("PERMANENT_MEMORY_QUICK_SETUP.md", "Quick Setup Guide")
    all_docs_ok &= check_file_exists("MEMORY_SYSTEM_COMPLETE.md", "Completion Report")
    all_docs_ok &= check_file_exists("test_memory_system.py", "Test Suite")
    
    print("\n" + "=" * 70)
    if all_files_ok and all_imports_ok and server_integration_ok and all_docs_ok:
        print("✅ ALL CHECKS PASSED - SYSTEM IS READY!")
        print("=" * 70)
        print("\n🚀 NEXT STEPS:")
        print("1. Start the backend server: python backend/server.py")
        print("2. Memory system will auto-initialize on startup")
        print("3. Connect frontend to Socket.IO events (see documentation)")
        print("4. Test with: socket.emit('get_startup_info')")
        print("\n📚 DOCUMENTATION:")
        print("- Complete guide: MEMORY_SYSTEM_GUIDE.md")
        print("- Quick start: PERMANENT_MEMORY_QUICK_SETUP.md")
        print("- Full report: MEMORY_SYSTEM_COMPLETE.md")
        return 0
    else:
        print("⚠️  SOME CHECKS FAILED - PLEASE REVIEW ABOVE")
        print("=" * 70)
        return 1

if __name__ == "__main__":
    sys.exit(main())

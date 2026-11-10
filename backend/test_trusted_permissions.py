"""
Test suite for Trusted System Control Mode
Tests all functionality of the trusted permissions system.
"""

import json
import os
import sys
sys.path.insert(0, os.path.dirname(__file__))

from trusted_permissions import TrustedPermissionsManager, get_trusted_manager
from voice_intent_parser import VoiceIntentParser

def test_trusted_permissions_manager():
    """Test TrustedPermissionsManager basic operations."""
    print("\n=== Testing TrustedPermissionsManager ===\n")
    
    mgr = TrustedPermissionsManager()
    
    # Test 1: Default state
    print("Test 1: Default state (disabled)")
    assert mgr.config["enabled"] == False, "Should be disabled by default"
    assert mgr.config["allowed_apps"] == [], "Should have no allowed apps by default"
    assert mgr.config["allowed_actions"] == [], "Should have no allowed actions by default"
    print("✅ PASS: Default state is disabled\n")
    
    # Test 2: Enable trusted mode
    print("Test 2: Enable trusted mode")
    mgr.enable_trusted_mode()
    assert mgr.config["enabled"] == True, "Should be enabled"
    assert mgr.config["trusted_since"] is not None, "Should have trusted_since timestamp"
    print("✅ PASS: Trusted mode enabled\n")
    
    # Test 3: Add allowed apps
    print("Test 3: Add allowed apps")
    mgr.add_allowed_app("chrome")
    mgr.add_allowed_app("notepad")
    assert "chrome" in mgr.config["allowed_apps"], "Chrome should be in allowed apps"
    assert "notepad" in mgr.config["allowed_apps"], "Notepad should be in allowed apps"
    print("✅ PASS: Apps added to allowed list\n")
    
    # Test 4: Set allowed actions
    print("Test 4: Set allowed actions")
    mgr.set_allowed_actions(["open_app", "type_text", "control_volume"])
    assert "open_app" in mgr.config["allowed_actions"], "open_app should be allowed"
    print("✅ PASS: Allowed actions set\n")
    
    # Test 5: Should skip confirmation for trusted action
    print("Test 5: Should skip confirmation for trusted app open")
    should_skip = mgr.should_skip_confirmation("open_app", "chrome")
    assert should_skip == True, "Should skip confirmation for trusted open_app with chrome"
    print("✅ PASS: Confirmation skipped for trusted action\n")
    
    # Test 6: Should NOT skip for untrusted app
    print("Test 6: Should NOT skip confirmation for untrusted app")
    should_skip = mgr.should_skip_confirmation("open_app", "unknown.exe")
    assert should_skip == False, "Should NOT skip for untrusted app"
    print("✅ PASS: Confirmation not skipped for untrusted app\n")
    
    # Test 7: Dangerous actions always require confirmation
    print("Test 7: Dangerous actions always require confirmation")
    should_skip = mgr.should_skip_confirmation("find_file")
    assert should_skip == False, "find_file is dangerous and should always require confirmation"
    print("✅ PASS: Dangerous action requires confirmation\n")
    
    # Test 8: Disable trusted mode
    print("Test 8: Disable trusted mode")
    mgr.disable_trusted_mode()
    assert mgr.config["enabled"] == False, "Should be disabled"
    should_skip = mgr.should_skip_confirmation("open_app", "chrome")
    assert should_skip == False, "Should NOT skip when disabled"
    print("✅ PASS: Confirmation required when disabled\n")
    
    # Clean up
    os.remove("trusted_permissions.json")
    print("✅ Cleaned up test file\n")


def test_voice_intents():
    """Test voice intent parsing."""
    print("\n=== Testing Voice Intent Parser ===\n")
    
    mgr = TrustedPermissionsManager()
    
    # Test 1: Enable trusted mode intent
    print("Test 1: Enable trusted mode voice intent")
    result = VoiceIntentParser.parse_trusted_intent("enable trusted mode", mgr)
    assert result["success"] == True, "Should parse enable intent"
    assert result["action"] == "enable_trusted_mode", "Should be enable_trusted_mode action"
    assert mgr.config["enabled"] == True, "Trusted mode should be enabled"
    print("✅ PASS: Enable intent parsed and executed\n")
    
    # Test 2: Set allowed apps intent
    print("Test 2: Set allowed apps voice intent")
    result = VoiceIntentParser.parse_trusted_intent("allow chrome and notepad", mgr)
    assert result["success"] == True, "Should parse allowed apps intent"
    assert "chrome" in mgr.config["allowed_apps"], "Chrome should be allowed"
    assert "notepad" in mgr.config["allowed_apps"], "Notepad should be allowed"
    print("✅ PASS: Allowed apps intent parsed and executed\n")
    
    # Test 3: Remember forever intent
    print("Test 3: Remember forever voice intent")
    result = VoiceIntentParser.parse_trusted_intent("remember forever", mgr)
    assert result["success"] == True, "Should parse remember forever intent"
    assert mgr.config["remember_forever"] == True, "Remember forever should be enabled"
    print("✅ PASS: Remember forever intent parsed and executed\n")
    
    # Test 4: Disable trusted mode intent
    print("Test 4: Disable trusted mode voice intent")
    result = VoiceIntentParser.parse_trusted_intent("disable trusted mode", mgr)
    assert result["success"] == True, "Should parse disable intent"
    assert mgr.config["enabled"] == False, "Trusted mode should be disabled"
    print("✅ PASS: Disable intent parsed and executed\n")
    
    # Test 5: Hindi phrase intent
    print("Test 5: Hindi phrase voice intent")
    mgr.enable_trusted_mode()
    result = VoiceIntentParser.parse_trusted_intent("Zoya, sirf chrome aur notepad allow karo", mgr)
    assert result["success"] == True, "Should parse Hindi intent"
    print("✅ PASS: Hindi phrase parsed and executed\n")
    
    # Clean up
    os.remove("trusted_permissions.json")
    print("✅ Cleaned up test file\n")


def test_action_safety_classification():
    """Test action safety classification."""
    print("\n=== Testing Action Safety Classification ===\n")
    
    mgr = TrustedPermissionsManager()
    
    # Test 1: Safe actions
    print("Test 1: Safe actions")
    assert mgr.is_action_safe("open_app") == True, "open_app is safe"
    assert mgr.is_action_safe("type_text") == True, "type_text is safe"
    assert mgr.is_action_safe("control_volume") == True, "control_volume is safe"
    print("✅ PASS: Safe actions identified correctly\n")
    
    # Test 2: Dangerous actions
    print("Test 2: Dangerous actions")
    assert mgr.is_action_dangerous("find_file") == True, "find_file is dangerous"
    assert mgr.is_action_dangerous("capture_screen") == True, "capture_screen is dangerous"
    print("✅ PASS: Dangerous actions identified correctly\n")
    
    # Test 3: Always require confirmation
    print("Test 3: Always require confirmation actions")
    assert mgr.always_requires_confirmation("delete_file") == True, "delete_file always requires confirmation"
    assert mgr.always_requires_confirmation("execute_shell") == True, "execute_shell always requires confirmation"
    print("✅ PASS: Always-confirm actions identified correctly\n")


def test_persistent_storage():
    """Test persistent storage functionality."""
    print("\n=== Testing Persistent Storage ===\n")
    
    # Test 1: Create and save config
    print("Test 1: Create and save config")
    mgr1 = TrustedPermissionsManager()
    mgr1.enable_trusted_mode()
    mgr1.set_allowed_apps(["chrome", "vscode"])
    mgr1.set_allowed_actions(["open_app", "type_text"])
    
    assert os.path.exists("trusted_permissions.json"), "Config file should exist"
    print("✅ PASS: Config file created\n")
    
    # Test 2: Load config from file
    print("Test 2: Load config from file")
    mgr2 = TrustedPermissionsManager()
    assert mgr2.config["enabled"] == True, "Enabled state should persist"
    assert "chrome" in mgr2.config["allowed_apps"], "Apps should persist"
    assert "open_app" in mgr2.config["allowed_actions"], "Actions should persist"
    print("✅ PASS: Config loaded from file correctly\n")
    
    # Clean up
    os.remove("trusted_permissions.json")
    print("✅ Cleaned up test file\n")


def test_global_singleton():
    """Test global singleton pattern."""
    print("\n=== Testing Global Singleton ===\n")
    
    mgr1 = get_trusted_manager()
    mgr2 = get_trusted_manager()
    
    assert mgr1 is mgr2, "Should return same instance"
    print("✅ PASS: Global singleton works correctly\n")
    
    # Clean up
    if os.path.exists("trusted_permissions.json"):
        os.remove("trusted_permissions.json")


def main():
    """Run all tests."""
    print("\n" + "="*60)
    print("TRUSTED SYSTEM CONTROL MODE - TEST SUITE")
    print("="*60)
    
    try:
        test_trusted_permissions_manager()
        test_voice_intents()
        test_action_safety_classification()
        test_persistent_storage()
        test_global_singleton()
        
        print("\n" + "="*60)
        print("✅ ALL TESTS PASSED!")
        print("="*60 + "\n")
        return 0
        
    except AssertionError as e:
        print(f"\n❌ TEST FAILED: {e}\n")
        return 1
    except Exception as e:
        print(f"\n❌ UNEXPECTED ERROR: {e}\n")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    exit(main())

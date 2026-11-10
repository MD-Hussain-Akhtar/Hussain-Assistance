#!/usr/bin/env python3
"""
Comprehensive test script for screen_read feature integration.
Verifies all components are properly set up and working.
"""

import sys
import os

def test_imports():
    """Test that all required modules can be imported."""
    print("\n" + "="*70)
    print("TEST 1: Module Imports")
    print("="*70)
    
    tests = [
        ("mss", "Screen capture library"),
        ("pytesseract", "OCR library"),
        ("PIL", "Image processing"),
    ]
    
    all_ok = True
    for module_name, description in tests:
        try:
            __import__(module_name)
            print(f"✅ {module_name:20} - {description}")
        except ImportError as e:
            print(f"❌ {module_name:20} - {description}")
            print(f"   Error: {e}")
            all_ok = False
    
    return all_ok


def test_ada_integration():
    """Test that ada.py has screen_read tool properly registered."""
    print("\n" + "="*70)
    print("TEST 2: Ada.py Tool Registration")
    print("="*70)
    
    try:
        with open("backend/ada.py", "r") as f:
            content = f.read()
        
        checks = {
            "screen_read_tool definition": 'screen_read_tool = {' in content,
            "screen_read in tools list": '"screen_read_tool"' in content or 'screen_read_tool' in content,
            "ScreenReader import": 'from screen_reader_simple import ScreenReader' in content,
            "screen_read handler": 'elif fc.name == "screen_read"' in content,
            "system_instruction mentions screen_read": 'screen_read' in content and 'system_instruction' in content,
        }
        
        all_ok = True
        for check, result in checks.items():
            status = "✅" if result else "❌"
            print(f"{status} {check}")
            if not result:
                all_ok = False
        
        return all_ok
    except Exception as e:
        print(f"❌ Error reading ada.py: {e}")
        return False


def test_screen_reader_module():
    """Test that screen_reader_simple module works."""
    print("\n" + "="*70)
    print("TEST 3: Screen Reader Module")
    print("="*70)
    
    try:
        from backend.screen_reader_simple import ScreenReader
        print("✅ ScreenReader class imported successfully")
        
        reader = ScreenReader()
        print("✅ ScreenReader instance created successfully")
        
        # Test read_screen method exists
        if hasattr(reader, 'read_screen'):
            print("✅ read_screen() method exists")
        else:
            print("❌ read_screen() method not found")
            return False
        
        return True
    except Exception as e:
        print(f"❌ Error with screen reader module: {e}")
        return False


def test_tesseract():
    """Test if Tesseract OCR is installed and working."""
    print("\n" + "="*70)
    print("TEST 4: Tesseract OCR Installation")
    print("="*70)
    
    try:
        import pytesseract
        
        # Try to get tesseract version
        try:
            version = pytesseract.pytesseract.get_tesseract_version()
            print(f"✅ Tesseract installed: {version}")
            return True
        except pytesseract.TesseractNotFoundError:
            print("❌ Tesseract not found in PATH")
            print("\n📌 INSTALLATION REQUIRED:")
            print("   1. Download from: https://github.com/UB-Mannheim/tesseract/wiki")
            print("   2. Install to: C:\\Program Files\\Tesseract-OCR")
            print("   3. Add to PATH or set: pytesseract.pytesseract.tesseract_cmd = r'C:\\Program Files\\Tesseract-OCR\\tesseract.exe'")
            return False
    except Exception as e:
        print(f"❌ Error checking Tesseract: {e}")
        return False


def test_screen_capture():
    """Test if we can capture the screen."""
    print("\n" + "="*70)
    print("TEST 5: Screen Capture Capability")
    print("="*70)
    
    try:
        import mss
        with mss.mss() as sct:
            monitors = sct.monitors
            print(f"✅ Found {len(monitors)} monitor(s)")
            for i, monitor in enumerate(monitors):
                if i == 0:
                    print(f"   Monitor {i}: {monitor}")
                else:
                    print(f"   Monitor {i}: {monitor['width']}x{monitor['height']}")
        return True
    except Exception as e:
        print(f"❌ Error with screen capture: {e}")
        return False


def test_ocr_live():
    """Test live OCR on current screen (if Tesseract available)."""
    print("\n" + "="*70)
    print("TEST 6: Live OCR Test")
    print("="*70)
    
    try:
        from backend.screen_reader_simple import ScreenReader
        
        reader = ScreenReader()
        result = reader.read_screen()
        
        if result.get('success'):
            text = result.get('text', '')
            if text:
                preview = text[:100] + ("..." if len(text) > 100 else "")
                print(f"✅ OCR successful!")
                print(f"   Text detected: '{preview}'")
                print(f"   Total characters: {len(text)}")
            else:
                print(f"⚠️  OCR succeeded but no text found on screen")
            return True
        else:
            error = result.get('error', 'Unknown error')
            print(f"❌ OCR failed: {error}")
            if "tesseract is not installed" in error.lower():
                print("\n📌 Need to install Tesseract OCR first")
                return False
            return False
    except Exception as e:
        print(f"❌ Error during OCR test: {e}")
        return False


def main():
    """Run all tests and report results."""
    print("\n")
    print("╔" + "="*68 + "╗")
    print("║" + " SCREEN READ FEATURE - INTEGRATION TEST ".center(68) + "║")
    print("╚" + "="*68 + "╝")
    
    results = {
        "Module Imports": test_imports(),
        "Ada.py Integration": test_ada_integration(),
        "Screen Reader Module": test_screen_reader_module(),
        "Tesseract OCR": test_tesseract(),
        "Screen Capture": test_screen_capture(),
        "Live OCR": test_ocr_live(),
    }
    
    # Summary
    print("\n" + "="*70)
    print("TEST SUMMARY")
    print("="*70)
    
    for test_name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status}: {test_name}")
    
    all_passed = all(results.values())
    
    print("\n" + "="*70)
    if all_passed:
        print("🎉 ALL TESTS PASSED! Screen read feature is fully operational!")
        print("\nYou can now use voice commands in Electron:")
        print("  • 'Read the screen'")
        print("  • 'Screen ko read kar'")
        print("  • 'Ye likha kya h?'")
    else:
        failed = [k for k, v in results.items() if not v]
        print(f"⚠️  {len(failed)} test(s) failed:")
        for test_name in failed:
            print(f"   • {test_name}")
        
        if "Tesseract OCR" in failed:
            print("\n📌 NEXT STEP: Install Tesseract OCR")
            print("   Download: https://github.com/UB-Mannheim/tesseract/wiki")
            print("   Then run this test again!")
    
    print("="*70 + "\n")
    
    return 0 if all_passed else 1


if __name__ == "__main__":
    sys.exit(main())

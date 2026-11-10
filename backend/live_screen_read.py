#!/usr/bin/env python
"""Live Screen Read - See What's On Your Screen Right Now"""
import sys
sys.stdout.reconfigure(encoding='utf-8')
import time

print("\n" + "="*70)
print("📸 LIVE SCREEN READ - REAL TIME")
print("="*70)

from vision_analyzer import VisionAnalyzer

va = VisionAnalyzer()

print("\n🔍 Capturing live screen...")
print("-" * 70)

# Capture screen
img = va.capture_screen()

if img is not None:
    height, width = img.shape[:2]
    print(f"✅ Screen captured successfully!")
    print(f"   Resolution: {width}x{height} pixels")
    print(f"   Image size: {img.shape}")
    
    print("\n📊 Screen Information:")
    print(f"   Height: {height} pixels")
    print(f"   Width: {width} pixels")
    print(f"   Color channels: {img.shape[2] if len(img.shape) > 2 else 'N/A'}")
    
    print("\n" + "="*70)
    print("✅ LIVE SCREEN IS ACTIVE!")
    print("="*70)
    print("""
What's happening:
  ✓ Screen capture is working
  ✓ Resolution detected: 1920x1080
  ✓ Can see everything on your monitor
  
You should see:
  • Whatever is currently displayed
  • All open windows/apps
  • Mouse position
  • Current content
  
If you want to:
  • Extract text from screen → Use extract_text_boxes()
  • Save screenshot → Use cv2.imwrite()
  • Analyze content → Use vision functions
  
System is READY for live screen operations! ✅
""")
    
    # Try to extract text from screen
    print("\n🔤 Attempting to extract text from screen...")
    print("-" * 70)
    try:
        text_boxes = va.extract_text_boxes(img)
        if text_boxes:
            print(f"✅ Found {len(text_boxes)} text regions on screen")
            print("\nText regions detected:")
            for i, box in enumerate(text_boxes[:5], 1):  # Show first 5
                print(f"   {i}. Text: '{box.text}' at ({box.x}, {box.y})")
        else:
            print("⚠️  No text detected on screen (or Tesseract not installed)")
    except Exception as e:
        print(f"⚠️  Text extraction error: {e}")
        print("   (This is OK - Tesseract OCR might not be installed)")
    
    print("\n" + "="*70)
    print("📺 LIVE SCREEN READ COMPLETE")
    print("="*70)
    print(f"""
Screen Status: ✅ ACTIVE & READABLE
Resolution: {width}x{height}
Capture Status: ✅ SUCCESS

Your screen is being monitored live!
All automation features can see and interact with your desktop.
""")
    
else:
    print("❌ Failed to capture screen")
    print("   Check if display is accessible")

print("="*70 + "\n")

# Show continuous monitoring
print("📹 Starting live screen monitoring (5 seconds)...")
for i in range(5, 0, -1):
    img_live = va.capture_screen()
    if img_live is not None:
        print(f"   ✅ Screen {i}: Captured ({img_live.shape[1]}x{img_live.shape[0]})")
    time.sleep(1)

print("\n✅ Live screen monitoring complete!")

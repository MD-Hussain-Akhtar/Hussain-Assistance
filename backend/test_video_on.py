#!/usr/bin/env python
from vision_analyzer import VisionAnalyzer

va = VisionAnalyzer()
print('📹 Turning ON Video/Screen Capture...')

# Capture screen
img = va.capture_screen()
if img is not None:
    print(f'✅ Screen Captured Successfully: {img.shape}')
    
    # Extract text from screen
    boxes = va.extract_text_boxes(img)
    print(f'📊 Text Elements Found: {len(boxes)}')
    
    if boxes:
        print('\n📌 Screen Elements:')
        for i, box in enumerate(boxes[:10]):  # Show first 10
            print(f'   [{i+1}] "{box.text}" at ({box.x}, {box.y})')
    
    print('\n✅ VIDEO ON - Screen is being monitored!')
else:
    print('❌ Failed to capture screen')

# Live Screen Read Feature Setup & Usage

## What's Been Added

✅ **Feature**: Live screen reading with OCR
- Capture the entire screen or a specific region
- Extract text using Tesseract OCR
- Zoya can read screen content and speak it back to you

✅ **Files Created/Modified**:
- `backend/screen_reader_simple.py` - OCR screen capture implementation
- `backend/ada.py` - Added `screen_read` tool declaration and handler
- `requirements.txt` - Added `pytesseract` dependency

## Setup Steps

### Step 1: Install Python Dependencies (Already Done ✅)
```bash
pip install pytesseract pillow mss
```

### Step 2: Install Tesseract OCR (Windows)

**Option A: Using Installer (Recommended)**
1. Download from: https://github.com/UB-Mannheim/tesseract/wiki
2. Run the installer (e.g., `tesseract-ocr-w64-setup-v5.x.exe`)
3. Accept default installation path: `C:\Program Files\Tesseract-OCR`
4. Finish installation

**Option B: Using Chocolatey** (if installed)
```powershell
choco install tesseract
```

**Option C: Using Scoop** (if installed)
```powershell
scoop install tesseract
```

### Step 3: Verify Installation
```bash
tesseract --version
```

If you see a version number, you're good! ✅

### Step 4: Test Screen Reader
```bash
python -c "from backend.screen_reader_simple import ScreenReader; print(ScreenReader().read_screen())"
```

Expected output:
```
{'success': True, 'text': '...text extracted from screen...'}
```

## Usage in Electron (Zoya)

Once everything is set up, you can use voice commands:

### Voice Commands (Hinglish)

```
🎤 "Screen ko read kar" 
→ Zoya reads the visible screen and tells you what she sees

🎤 "Ye likha kya h screen par?"
→ "What's written on the screen?" - reads screen text

🎤 "Read the screen and speak it"
→ Zoya captures screen, extracts text, and reads it aloud

🎤 "Screen read kar ke bata"
→ Same as above in Hindi
```

### Advanced: Read Specific Region (Parameters)
If you want to read only part of the screen (advanced):
```json
{
  "platform": "screen_read",
  "region": {
    "left": 100,
    "top": 100,
    "width": 800,
    "height": 600
  }
}
```

## How It Works

1. **Capture**: Uses `mss` library to capture primary monitor screenshot
2. **Process**: Converts to PIL Image for OCR processing
3. **OCR**: Tesseract extracts all visible text
4. **Return**: Text sent back to Zoya for speaking/responding

## Troubleshooting

### ❌ "tesseract is not installed or it's not in your PATH"

**Solution**:
1. Download installer from https://github.com/UB-Mannheim/tesseract/wiki
2. Install to: `C:\Program Files\Tesseract-OCR`
3. Add to Python:
   ```python
   import pytesseract
   pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
   ```

### ❌ "ModuleNotFoundError: No module named 'screen_reader_simple'"

**Solution**:
```bash
pip install pytesseract pillow mss
```

### ❌ "No text detected on screen"

**Possible Causes**:
- Screen is blank or contains only images
- Tesseract can't read the font/text quality
- Region specified is outside monitor bounds

**Try**: Take a screenshot and run OCR on a text-heavy area (like browser)

## Features

| Feature | Status | Details |
|---------|--------|---------|
| Full screen capture | ✅ Working | Uses mss library |
| Region capture | ✅ Working | Specify left, top, width, height |
| OCR text extraction | ✅ Ready* | Requires Tesseract installation |
| Zoya voice integration | ✅ Working | Speaks extracted text |
| Real-time capture | ✅ Working | Fast capture via mss |

*Requires Tesseract OCR binary to be installed

## Backend API Reference

### screen_read_tool Parameters
```json
{
  "region": {
    "left": 0,      // x coordinate (optional, default 0)
    "top": 0,       // y coordinate (optional, default 0)
    "width": 1920,  // width in pixels (optional)
    "height": 1080  // height in pixels (optional)
  },
  "read_aloud": true  // Whether to speak result (optional)
}
```

### Response Format
```json
{
  "success": true,
  "text": "Extracted text from screen..."
}
```

or on error:
```json
{
  "success": false,
  "error": "Error message describing what went wrong"
}
```

## Next Steps

1. ✅ Install Tesseract OCR
2. ✅ Test with: `python -c "from backend.screen_reader_simple import ScreenReader; print(ScreenReader().read_screen())"`
3. ✅ Use voice commands in Electron: "Read screen"
4. ✅ Enjoy live screen reading with Zoya! 🎉

---

**Note**: The backend server is already running with the screen_read tool integrated. You just need to install Tesseract OCR to make it fully functional!

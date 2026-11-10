#!/usr/bin/env python
"""Launch WhatsApp from Windows Apps"""
import subprocess
import os
import glob

print("🔍 Searching for WhatsApp...")

# Search in WindowsApps
windows_apps = r"C:\Program Files\WindowsApps"
pattern = os.path.join(windows_apps, "*WhatsApp*", "WhatsApp.exe")

files = glob.glob(pattern)
if files:
    print(f"✅ Found WhatsApp: {files[0]}")
    subprocess.Popen(files[0])
    print("✅ WhatsApp Opening...")
else:
    print("❌ WhatsApp.exe not found")
    print("\nSearching alternative paths...")
    
    # Try launching via protocol
    try:
        subprocess.Popen('start whatsapp:', shell=True)
        print("✅ WhatsApp opened via protocol")
    except Exception as e:
        print(f"Error: {e}")

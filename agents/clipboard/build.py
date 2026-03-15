"""
Build script — Creates .exe for Windows
"""

import PyInstaller.__main__
import os

# Clean previous builds
for folder in ['build', 'dist']:
    if os.path.exists(folder):
        import shutil
        shutil.rmtree(folder)

PyInstaller.__main__.run([
    'main.py',                          # Entry point
    '--name=AI-Clipboard-Manager',      # App name
    '--onefile',                        # Single .exe file
    '--windowed',                       # No console window
    '--icon=icon.ico',                  # App icon
    '--add-data=config.py;.',           # Include config
    '--add-data=database.py;.',         # Include database
    '--add-data=ai_agent.py;.',         # Include AI agent
    '--add-data=content_detector.py;.', # Include detector
    '--add-data=clipboard_monitor.py;.',# Include monitor
    '--add-data=gui.py;.',             # Include GUI
    '--hidden-import=ollama',
    '--hidden-import=pyperclip',
    '--hidden-import=PIL',
    '--hidden-import=PIL.Image',
    '--hidden-import=PIL.ImageGrab',
    '--hidden-import=PIL.ImageTk',
    '--hidden-import=win32clipboard',
    '--clean',
])

print("\n✅ Build complete!")
print("Find your app at: dist/AI-Clipboard-Manager.exe")
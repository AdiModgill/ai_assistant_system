"""
Creates a release ZIP package
"""

import os
import shutil
from datetime import datetime

VERSION = "1.0.0"
RELEASE_NAME = f"AI-Clipboard-Manager-v{VERSION}"
RELEASE_DIR = f"release/{RELEASE_NAME}"

# Clean previous release
if os.path.exists("release"):
    shutil.rmtree("release")

os.makedirs(RELEASE_DIR, exist_ok=True)

# Copy .exe
shutil.copy2(
    "dist/AI-Clipboard-Manager.exe",
    f"{RELEASE_DIR}/AI-Clipboard-Manager.exe"
)

# Create README for release
readme_content = f"""
===================================================
  AI Smart Clipboard Manager v{VERSION}
===================================================

SETUP:
  1. Install Ollama    - https://ollama.com/download
  2. Open terminal     - Run: ollama pull llama3:8b
  3. Start Ollama      - Run: ollama serve
  4. Run the app       - Double-click AI-Clipboard-Manager.exe

FEATURES:
  - Auto-captures copied text
  - Detects and stores links
  - Saves copied screenshots
  - AI classifies and tags content
  - Smart AI-powered search
  - Favorite items

REQUIREMENTS:
  - Windows 10/11
  - Ollama installed and running
  - llama3:8b model pulled
  - NVIDIA GPU recommended (works on CPU too)

BUILD DATE: {datetime.now().strftime('%Y-%m-%d')}
"""

# ✅ Added encoding='utf-8'
with open(f"{RELEASE_DIR}/README.txt", 'w', encoding='utf-8') as f:
    f.write(readme_content)

# Create ZIP
shutil.make_archive(
    f"release/{RELEASE_NAME}",
    'zip',
    "release",
    RELEASE_NAME
)

print(f"Release package created:")
print(f"   release/{RELEASE_NAME}.zip")
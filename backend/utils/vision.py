# utils/vision.py
import base64
import requests
from config.settings import OLLAMA_URL

def describe_image(image_bytes: bytes) -> str:
    try:
        b64 = base64.b64encode(image_bytes).decode("utf-8")

        payload = {
            "model": "llava:latest",
            "messages": [{
                "role": "user",
                "content": "Describe this image briefly in 1 sentence.",
                "images": [b64]
            }],
            "stream": False
        }

        response = requests.post(
            f"{OLLAMA_URL}/api/chat",
            json=payload,
            timeout=30
        )
        response.raise_for_status()
        return response.json()["message"]["content"].strip()

    except Exception as e:
        print(f"❌ Image description error: {e}")
        return "[sent an image]"
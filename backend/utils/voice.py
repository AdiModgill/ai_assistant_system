# utils/voice.py
import os
import tempfile
from groq import Groq
from config.settings import GROQ_API_KEY

client = Groq(api_key=GROQ_API_KEY)

def transcribe_voice(audio_bytes: bytes, mime_type: str = "audio/ogg") -> str:
    try:
        suffix = ".ogg"
        if "mp4" in mime_type:
            suffix = ".mp4"
        elif "mpeg" in mime_type:
            suffix = ".mp3"

        with tempfile.NamedTemporaryFile(suffix=suffix, delete=False) as tmp:
            tmp.write(audio_bytes)
            tmp_path = tmp.name

        with open(tmp_path, "rb") as f:
            transcription = client.audio.transcriptions.create(
                file=(os.path.basename(tmp_path), f),
                model="whisper-large-v3-turbo",
                language="hi",
                temperature=0.0
            )

        os.unlink(tmp_path)
        return transcription.text.strip()

    except Exception as e:
        print(f"❌ Voice transcription error: {e}")
        return "[voice note - transcription failed]"
# core/memory.py
from database.database import db
from datetime import datetime
import pytz

IST = pytz.timezone("Asia/Kolkata")

class MemoryManager:
    def __init__(self):
        self.messages = db.get_collection("messages")

    def save_message(self, phone, role, content, channel="whatsapp"):
        message = {
            "phone": phone,
            "channel": channel,
            "role": role,
            "content": content,
            "timestamp": datetime.now(IST)
        }
        self.messages.insert_one(message)

    def get_last_messages(self, phone, channel="whatsapp", limit=10):
        cursor = self.messages.find(
            {"phone": phone, "channel": channel}
        ).sort("timestamp", -1).limit(limit)

        messages = list(cursor)
        messages.reverse()
        return messages
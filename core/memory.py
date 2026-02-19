
from database.database import database
from datetime import datetime


class MemoryManager:
    def __init__(self):
        self.messages = database.get_collection("messages")

    def save_message(self, phone, role, content, channel="whatsapp"):
        message = {
            "phone": phone,
            "channel": channel,
            "role": role,
            "content": content,
            "timestamp": datetime.utcnow()
        }
        self.messages.insert_one(message)

    def get_last_messages(self, phone, channel="whatsapp", limit=10):
        cursor = self.messages.find(
            {"phone": phone, "channel": channel}
        ).sort("timestamp", -1).limit(limit)

        messages = list(cursor)
        messages.reverse()  # Oldest first

        return messages

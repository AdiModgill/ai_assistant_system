from pymongo import MongoClient, DESCENDING
from config.settings import MONGO_URI, DB_NAME, COLLECTIONS
from datetime import datetime

# Connect to MongoDB
client = MongoClient(MONGO_URI)
db = client[DB_NAME]

# Collection handles
contacts_col  = db[COLLECTIONS["contacts"]]
whatsapp_col  = db[COLLECTIONS["whatsapp_messages"]]
email_col     = db[COLLECTIONS["email_messages"]]
scheduled_col = db[COLLECTIONS["scheduled_tasks"]]
goals_col = db["goals"]
conversation_col = db["conversations"]  # Nova's main conversation history
profile_col = db["user_profile"]


class Database:
    def __init__(self):
        self.client   = client
        self.db       = db
        self.contacts = contacts_col
        self.whatsapp = whatsapp_col
        self.email    = email_col
        self.scheduled = scheduled_col
        self.conversations = conversation_col
        self.profile = profile_col
        self.goals = goals_col


    # ── Nova conversation memory ────────────────────────────

    def save_message(self, role: str, content: str) -> None:
        """Save a single message to conversation history."""
        self.conversations.insert_one({
            "role":      role,
            "content":   content,
            "timestamp": datetime.utcnow()
        })

    def get_messages(self, limit: int = 50):
        """Fetch last N messages from conversation history."""
        cursor = self.conversations.find(
            {},
            {"_id": 0, "role": 1, "content": 1}
        ).sort("timestamp", DESCENDING).limit(limit)

        # return in chronological order
        messages = list(cursor)
        messages.reverse()
        return messages

    def search_messages(self, keyword: str):
        """Search conversation history by keyword."""
        cursor = self.conversations.find(
            {"content": {"$regex": keyword, "$options": "i"}},
            {"_id": 0, "role": 1, "content": 1}
        ).sort("timestamp", DESCENDING).limit(20)
        return list(cursor)

    def clear_all(self) -> None:
        """Wipe all conversation history."""
        self.conversations.delete_many({})

    def get_profile(self) -> dict:
        """Get Nova's owner profile."""
        doc = self.profile.find_one({"_id": "owner"}, {"_id": 0})
        return doc or {}

    def update_profile(self, data: dict) -> None:
        """Update owner profile."""
        self.profile.update_one(
            {"_id": "owner"},
            {"$set": data},
            upsert=True
        )    
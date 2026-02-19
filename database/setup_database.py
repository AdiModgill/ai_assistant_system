from database.database import contacts_col , whatsapp_col , email_col , scheduled_col
from pymongo import ASCENDING , DESCENDING

def setup_indexes():
    # Contacts - unique phone
    contacts_col.create_index([("phone", ASCENDING)], unique=True)
    print(" contacts index created")

    # WhatsApp messages - phone + timestamp
    whatsapp_col.create_index([("phone", ASCENDING), ("timestamp", DESCENDING)])
    print(" whatsapp_messages index created")

    # Email messages - email + timestamp
    email_col.create_index([("email", ASCENDING), ("timestamp", DESCENDING)])
    print(" email_messages index created")

    # Scheduled tasks - run_at + status
    scheduled_col.create_index([("run_at", ASCENDING), ("status", ASCENDING)])
    print(" scheduled_tasks index created")

def insert_sample_contact():
    sample = {
         "name": "Test User",
        "phone": "+910000000000",
        "email": "",
        "birthday": None,
        "preferences": {
            "tone": "casual",
            "emoji_usage": "high",
            "language": "en",
            "timezone": "Asia/delhi",
            "channel": "whatsapp"
            }
     }
    try:
        contacts_col.insert_one(sample)
        print("Sample contact inserted")
    except Exception as e:
        print(f"Sample contact skipped (probably already exists): {e}")



if __name__ == "__main__":
    setup_indexes()
    insert_sample_contact()
    print("\n Database setup complete!")    
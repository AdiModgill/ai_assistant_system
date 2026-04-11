from pymongo import MongoClient
from config.settings import MONGO_URI, DB_NAME, COLLECTIONS

# Connect to MongoDB
client = MongoClient(MONGO_URI)
db = client[DB_NAME]

# Collection handles 
contacts_col = db[COLLECTIONS["contacts"]]
whatsapp_col = db[COLLECTIONS["whatsapp_messages"]]
email_col = db[COLLECTIONS["email_messages"]]
scheduled_col = db[COLLECTIONS["scheduled_tasks"]]


# Wrapper class (FIX FOR YOUR ERROR)
class Database:
    def __init__(self):
        self.client = client
        self.db = db
        self.contacts = contacts_col
        self.whatsapp = whatsapp_col
        self.email = email_col
        self.scheduled = scheduled_col
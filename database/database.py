
from pymongo import MongoClient
from config.settings import MONGO_URI, DB_NAME, COLLECTIONS

client = MongoClient(MONGO_URI)
db = client[DB_NAME]

# Collection handles 

contacts_col = db[COLLECTIONS["contacts"]]
whatsapp_col = db[COLLECTIONS["whatsapp_messages"]]
email_col = db[COLLECTIONS["email_messages"]]
scheduled_col = db[COLLECTIONS["scheduled_tasks"]]
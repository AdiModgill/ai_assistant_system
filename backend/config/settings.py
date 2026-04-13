import os 
from dotenv import load_dotenv

load_dotenv()

MONGO_URI = os.getenv("MONGO_URI" , "mongodb://localhost:27017")
DB_NAME = "ai_assistant"

COLLECTIONS = {
    "contacts": "contacts",
    "whatsapp_messages": "whatsapp_messages",
    "email_messages": "email_messages",
    "scheduled_tasks": "scheduled_tasks",
}


#Ollama / LLM
OLLAMA_URL = os.getenv("OLLAMA_URL","http://localhost:11434")
LLM_MODEL = "llama3:latest"


#WhatsApp Agent

WHATSAPP_CONTEXT_LIMIT = 15


#traslation
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")

class Settings:
    def __init__(self):
        self.MONGO_URI = MONGO_URI
        self.DB_NAME = DB_NAME
        self.COLLECTIONS = COLLECTIONS
        self.OLLAMA_URL = OLLAMA_URL
        self.LLM_MODEL = LLM_MODEL
        self.WHATSAPP_CONTEXT_LIMIT = WHATSAPP_CONTEXT_LIMIT
        self.GROQ_API_KEY = GROQ_API_KEY


# ✅ this is what your project is looking for
settings = Settings()
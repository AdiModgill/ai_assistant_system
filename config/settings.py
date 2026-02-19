import os 
from dotenv import load_dotenv

load_dotenv()

MONGO_URI = os.getenv("MONGO_URI" , "maongodb://localhost:27017")
DB_NAME = "ai_assistant"

COLLECTIONS = {
    "contacts": "contacts",
    "whatsapp_messages": "whatsapp_messages",
    "email_messages": "email_messages",
    "scheduled_tasks": "scheduled_tasks",
}


#Ollama / LLM
OLLAMA_URL = os.getenv("OLLAMA_URL", "http://localhost:11434")
LLM_MODEL = "qwen2.5:3b"


#WhatsApp Agent

WHATSAPP_CONTEXT_LIMIT = 15

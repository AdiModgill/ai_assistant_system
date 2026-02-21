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
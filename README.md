# Aditya — AI Assistant System

A full-stack AI assistant system with modular backend agents and a modern frontend UI.  
The system can handle automation tasks, WhatsApp messaging, scheduling, and AI-based responses using a local LLM.

---

# 📁 Project Structure

ai_assistant_system/
│
├── backend/        → Python AI backend (agents + core system)
├── frontend/       → UI application (React / Vite)
├── README.txt      → Project documentation

---

# ⚙️ Backend Features

- Multi-agent system (modular architecture)
  - WhatsApp Agent
  - Email Agent
  - Alarm Agent
  - Weather Agent
  - Music Agent
  - Clipboard Agent
  - Goal Agent
- AI Brain (LLM integration via Ollama / Groq)
- Message memory system
- Task scheduling system
- REST API (FastAPI / Uvicorn)
- Database integration (MongoDB)

---

# 🎨 Frontend Features

- Modern UI (React + Vite)
- Chat-based interface (AI assistant style)
- API integration with backend
- Fast and responsive design
- Clean component structure

---

# 🚀 How to Run Backend

1. Go to backend folder:
   cd backend

2. Install dependencies:
   pip install -r requirements.txt

3. Start server:
   python run_backend.py
   OR
   uvicorn api.server:app --reload --port 8000

Backend runs at:
http://127.0.0.1:8000

---

# 💻 How to Run Frontend

1. Go to frontend folder:
   cd frontend

2. Install dependencies:
   npm install

3. Start frontend:
   npm run dev

Frontend runs at:
http://localhost:5173

---

# 🔐 Environment Variables

Create a .env file inside backend:

MONGO_URI=your_mongo_url
OLLAMA_URL=http://localhost:11434
GROQ_API_KEY=your_api_key

DO NOT push .env to GitHub.

---

# ⚠️ Important Notes

- Keep backend and frontend running separately
- Ensure MongoDB is running locally or remotely
- Install Ollama for local LLM support
- Use Python 3.10+

---

# 🧠 Tech Stack

Backend:
- Python
- FastAPI / Uvicorn
- MongoDB
- Ollama / Groq
- Neonize (WhatsApp automation)

Frontend:
- React
- Vite
- TypeScript
- CSS

---

# 🔒 Privacy

All processing is done locally unless external APIs are used.  
No sensitive data should be pushed to GitHub.

---

# 📌 Author

Aditya — AI Assistant Project  
Built for learning AI automation and full-stack system design.

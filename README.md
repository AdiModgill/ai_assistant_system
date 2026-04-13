# 🤖 Aditya — AI Assistant System

A full-stack AI assistant system with modular backend agents and a modern frontend UI.  
It can automate tasks, handle WhatsApp messaging, scheduling, and AI-based responses using a **local LLM (Ollama + LLaMA 3)**.

---

# 📁 Project Structure

ai_assistant_system/
│
├── backend/        → Python AI backend (agents + core system)
├── frontend/       → UI application (React / Vite)
├── README.md       → Project documentation

---

# 🧠 AI MODEL (LOCAL LLM)

This project uses a fully local AI model setup:

- **Ollama** → Local LLM runtime engine
- **Model Used** → LLaMA 3 (llama3:latest / 8B variant)
- **API Endpoint** → http://localhost:11434

### ⚙️ Why Ollama + LLaMA 3?
- 100% local processing (no cloud dependency)
- No API cost
- Faster responses
- Privacy-safe (data stays on your system)
- Ideal for AI agents & automation systems

---

# 🚀 Setup Ollama (Required)

### 1. Install Ollama
https://ollama.com

### 2. Pull model
```bash
ollama pull llama3:latest

3. Start Ollama server
ollama serve
⚙️ Backend Features
Multi-agent system (modular architecture)
WhatsApp Agent (Neonize integration)
Email Agent
Alarm Agent
Weather Agent
Music Agent
Clipboard Agent
Goal Agent
AI Brain (Ollama + optional Groq support)
Memory system (conversation history)
Task scheduling system
REST API (FastAPI / Uvicorn)
Database integration (MongoDB)
🎨 Frontend Features
Modern UI built with React + Vite
Chat-style AI assistant interface
Real-time API communication with backend
Fast and responsive design
Clean component-based architecture
🚀 How to Run Backend
cd backend
Install dependencies
pip install -r requirements.txt
Run backend
python run_backend.py

OR

uvicorn api.server:app --reload --port 8000

Backend runs at:
http://127.0.0.1:8000

💻 How to Run Frontend
cd frontend
Install dependencies
npm install
Start frontend
npm run dev

Frontend runs at:
http://localhost:5173

🔐 Environment Variables

Create a .env file inside backend/:

MONGO_URI=your_mongodb_url
OLLAMA_URL=http://localhost:11434
GROQ_API_KEY=your_api_key_here

⚠️ Never push .env to GitHub (it contains secrets).

🧠 System Architecture

User
↓
Frontend (React UI)
↓
Backend API (FastAPI)
↓
AI Router (Agents System)
↓
LLM (Ollama + LLaMA 3)
↓
Response returned

⚙️ Tech Stack
Backend
Python
FastAPI / Uvicorn
MongoDB
Ollama (LLaMA 3)
Neonize (WhatsApp automation)
Frontend
React
Vite
TypeScript
CSS
🔒 Privacy
Fully local AI processing via Ollama
No sensitive data leaves system unless external APIs are used
Secure local execution
⚠️ Important Notes
Start Ollama before running backend
Ensure MongoDB is running
Run backend and frontend separately
Requires Python 3.10+

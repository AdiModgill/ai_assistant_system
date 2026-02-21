# Aditya — AI WhatsApp Agent

An AI agent that replies to WhatsApp messages on your behalf, using a local LLM to chat like a normal Indian college student in Hinglish.

---

## Tech Stack

- **WhatsApp** — Neonize 0.3.14
- **LLM** — Llama 3 8B via Ollama (runs locally)
- **Database** — MongoDB
- **Language** — Python 3.13
- **Audio** — FFmpeg

---

## Requirements

- Python 3.10+
- 12GB+ RAM
- [Ollama](https://ollama.com)
- [MongoDB](https://www.mongodb.com/try/download/community)
- [FFmpeg](https://www.gyan.dev/ffmpeg/builds/) — copy `ffmpeg.exe`, `ffprobe.exe`, `ffplay.exe` into project folder

---

## Installation

**1. Install dependencies**
```bash
pip install neonize pymongo pytz requests python-dotenv groq
```

**2. Pull the LLM model**
```bash
ollama pull llama3:latest
```

**3. Create `.env` file**
```env
MONGO_URI=mongodb://localhost:27017
OLLAMA_URL=http://localhost:11434
GROQ_API_KEY=your_key_here
```
Get free Groq key from [console.groq.com](https://console.groq.com)

**4. Run**
```bash
python main.py
```

On first run, scan the QR code in terminal from WhatsApp → Settings → Linked Devices → Link a Device.

---

## Features

- Auto-replies in Hinglish like a real college student
- Waits 1.5s to batch multiple messages into one reply
- Remembers last 6 messages per contact (MongoDB)
- Different tone per contact — mom, gf, friend, classmate
- Group support — only replies when tagged (`adi`, `aditya`)
- Birthday wishes sent automatically
- Scheduled messages support
- Handles text, images, video, stickers, voice notes

---

## Setting Contact Relationships

Open MongoDB Compass and run:

```js
db.contacts.updateOne(
  { "phone": "91XXXXXXXXXX" },
  { "$set": { "name": "Mom", "relationship": "mom" } }
)
```

Valid values: `mom`, `dad`, `gf`, `friend`, `classmate`, `unknown`

---

## Scheduling a Message

```js
db.scheduled_tasks.insertOne({
  "type": "scheduled",
  "phone": "91XXXXXXXXXX",
  "message": "Bhai kal test hai yaad hai na?",
  "status": "pending",
  "run_at": new Date("2026-02-22T09:00:00")
})
```

---

## Troubleshooting

| Error | Fix |
|-------|-----|
| `401 logged out` | Delete `whatsapp.session` and re-scan QR |
| `LLM 404 error` | Run `ollama serve`, check model name in `settings.py` |
| `Ollama timeout` | Increase timeout in `utils/llm.py` to `180` |
| Double replies | Clear history: `db.messages.deleteMany({})` |
| MongoDB error | Start MongoDB service |

---

## Privacy

All data stays 100% local. LLM runs on your PC via Ollama. No data is sent to any cloud service. Use a separate number to keep your personal WhatsApp safe.

---

*Built as a college AI project*
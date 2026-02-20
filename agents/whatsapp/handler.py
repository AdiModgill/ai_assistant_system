# agents/whatsapp/handler.py
from neonize.client import NewClient
from neonize.events import MessageEv
from utils.llm import chat
from core.memory import MemoryManager
from database.database import db
from datetime import datetime
import pytz
import threading
import re

IST = pytz.timezone("Asia/Kolkata")
AGENT_START_TIME = datetime.now(IST)
memory = MemoryManager()
contacts_col = db["contacts"]
_pending = {}
_lock = threading.Lock()

SYSTEM_PROMPT = """You are Adi.

Reply like a normal human chatting on WhatsApp.

Keep replies short (1 line).
Max 15 words.
Be casual and natural.
Use simple English.
You may add 1 emoji if it fits naturally.
Do not overthink.
Do not explain.
Do not act like AI.
No long replies.
"""


def save_contact(phone: str, name: str):
    existing = contacts_col.find_one({"phone": phone})
    if not existing:
        contacts_col.insert_one({
            "phone": phone,
            "name": name,
            "email": "",
            "birthday": None,
            "preferences": {
                "tone": "casual",
                "emoji_usage": "medium",
                "language": "hinglish",
                "timezone": "Asia/Kolkata",
                "channel": "whatsapp"
            },
            "notes": "",
            "created_at": datetime.now(IST)
        })
        print(f"✅ New contact saved: {name} ({phone})")
    else:
        if name and name != "Unknown" and existing.get("name") == "Unknown":
            contacts_col.update_one(
                {"phone": phone},
                {"$set": {"name": name}}
            )
            print(f"✅ Contact name updated: {name} ({phone})")


def extract_info(phone: str, text: str):
    email_match = re.search(r'[\w.-]+@[\w.-]+\.\w+', text)
    if email_match:
        email = email_match.group()
        contacts_col.update_one({"phone": phone}, {"$set": {"email": email}})
        print(f"📧 Email saved: {email}")

    birthday_match = re.search(
        r'(\d{1,2}[/-]\d{1,2}[/-]\d{2,4}|'
        r'(?:jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)\w*\s+\d{1,2})',
        text.lower()
    )
    if birthday_match:
        birthday = birthday_match.group()
        contacts_col.update_one({"phone": phone}, {"$set": {"birthday": birthday}})
        print(f"🎂 Birthday saved: {birthday}")


def build_prompt(phone: str) -> str:
    contact = contacts_col.find_one({"phone": phone}) or {}
    name = contact.get("name", "Unknown")
    prefs = contact.get("preferences", {})
    tone = prefs.get("tone", "casual")
    extra = f"\nYou are talking to: {name}. Tone: {tone}."
    return SYSTEM_PROMPT + extra


class MessageHandler:
    def __init__(self, client: NewClient):
        self.client = client

    def process(self, message: MessageEv):
        try:
            # filter old messages
            try:
                msg_time = datetime.fromtimestamp(
                    message.Info.Timestamp, tz=IST
                )
                if msg_time < AGENT_START_TIME:
                    return
            except:
                pass

            # ignore own messages
            if message.Info.MessageSource.IsFromMe:
                return

            # ignore group messages
            if message.Info.MessageSource.IsGroup:
                return

            # extract phone
            phone = message.Info.MessageSource.Sender.User
            if not phone:
                return

            # save Chat JID directly from message
            chat_jid = message.Info.MessageSource.Chat

            # extract name
            name = getattr(message.Info, 'PushName', None) or "Unknown"

            # extract text
            text = ""
            try:
                text = message.Message.conversation or ""
                if not text:
                    text = message.Message.extendedTextMessage.text or ""
            except:
                pass

            text = text.strip()
            if not text:
                return

            print(f"\n📩 {name} ({phone}): {text}")

            save_contact(phone, name)
            extract_info(phone, text)

            # debounce — collect messages for 2.5s then reply once
            with _lock:
                if phone in _pending:
                    _pending[phone]["timer"].cancel()
                    _pending[phone]["messages"].append(text)
                else:
                    _pending[phone] = {
                        "messages": [text],
                        "name": name,
                        "chat_jid": chat_jid,
                    }

                timer = threading.Timer(2.5, self._reply, args=[phone])
                _pending[phone]["timer"] = timer
                timer.start()

        except Exception as e:
            import traceback
            print(f"❌ Process error: {e}")
            traceback.print_exc()

    def _reply(self, phone: str):
        try:
            with _lock:
                if phone not in _pending:
                    return
                data = _pending.pop(phone)

            messages = data["messages"]
            name = data["name"]
            chat_jid = data["chat_jid"]

            combined = " | ".join(messages)
            print(f"💬 Replying to {name}: {combined}")

            memory.save_message(phone, "user", combined)

            history = memory.get_last_messages(phone, limit=10)
            context = [
                {"role": m["role"], "content": m["content"]}
                for m in history
            ]

            system = build_prompt(phone)
            reply = chat(context, system)

            print(f"🤖 Aditya: {reply}")

            memory.save_message(phone, "assistant", reply)

            # send using Chat JID directly
            self.client.send_message(chat_jid, reply)
            print(f"✅ Message sent to {name}!")

        except Exception as e:
            import traceback
            print(f"❌ Reply error: {e}")
            traceback.print_exc()
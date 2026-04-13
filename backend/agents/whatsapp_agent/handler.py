# agents/whatsapp_agent/handler.py
from neonize.client import NewClient
from neonize.events import MessageEv
from utils.llm import LLMClient
from database.db import db
from datetime import datetime
import pytz
import threading
import re

IST = pytz.timezone("Asia/Kolkata")
AGENT_START_TIME = datetime.now(IST)

llm = LLMClient()
contacts_col = db["contacts"]
whatsapp_col = db["whatsapp_messages"]
profile_col  = db["user_profile"]

# Keywords that trigger profile lookup
PERSONAL_KEYWORDS = [
    "kahan", "where are you", "kya kar", "what are you doing",
    "college", "hostel", "ghar", "home", "family", "mummy", "papa",
    "bhai", "sister", "dost", "friend", "hobby", "khana", "food",
    "study", "exam", "class", "free", "busy", "aaj", "kal"
]

def get_profile_context(text: str) -> str:
    """Only load profile if message contains personal keywords."""
    text_lower = text.lower()
    if not any(k in text_lower for k in PERSONAL_KEYWORDS):
        return ""
    try:
        p = profile_col.find_one({"type": "owner_profile"})
        if not p:
            return ""
        return (
            f"\n[About you: Name={p['name']}, Location={p['location']}, "
            f"College={p['college']}, Friends={','.join(p['friends'])}, "
            f"Family={p['family']}, Hobbies={p['hobbies']}]"
        )
    except Exception:
        return ""

_pending = {}
_lock = threading.Lock()

BOT_TRIGGERS = ["aditya", "@aditya", "adi"]

SYSTEM_PROMPT = """You are Aditya, a 20 year old Indian college student chatting on WhatsApp.

PERSONALITY:
- normal guy
- Speaks in english (mix of hindi + english)
- Short replies only - 1 sentence usually, max 2
- Replies to what was ACTUALLY said - nothing extra
- Does not give advice unless asked
- Does not ask too many questions
- Sounds like a real person texting fast

STRICT OUTPUT RULES:
- MAX 1 emoji per message. If no emoji needed, use none.
- Never use more than 2 lines
- Never repeat yourself
- Never sound like a bot or assistant
- If someone asks if you are AI say exactly: "Adi hu bhai 😂"

EXAMPLES:
"heyy" or "haan bol" -> when someone says hi
"thik hu tu bata" -> when asked how are you
"kuch nahi yaar" -> when asked what are you doing
"ha chal" -> when someone says lets meet
"k" -> when someone says ok
"""


def save_contact(phone: str, name: str):
    existing = contacts_col.find_one({"phone": phone})
    if not existing:
        contacts_col.insert_one({
            "phone": phone,
            "name": name,
            "email": "",
            "birthday": None,
            "relationship": "unknown",
            "preferences": {
                "tone": "casual",
                "language": "hinglish",
                "timezone": "Asia/Kolkata",
                "channel": "whatsapp"
            },
            "notes": "",
            "created_at": datetime.now(IST)
        })
        print(f"New contact saved: {name} ({phone})")
    else:
        if name and name != "Unknown" and existing.get("name") in ["Unknown", None, ""]:
            contacts_col.update_one({"phone": phone}, {"$set": {"name": name}})
            print(f"Contact name updated: {name} ({phone})")


def get_display_name(phone: str, fallback: str) -> str:
    contact = contacts_col.find_one({"phone": phone}) or {}
    name = contact.get("name", "")
    if name and name != "Unknown":
        return name
    return fallback or "Unknown"


def build_prompt(phone: str, message: str = "") -> str:
    contact = contacts_col.find_one({"phone": phone}) or {}
    name = contact.get("name", "Unknown")
    relationship = contact.get("relationship", "unknown")
    tone = contact.get("preferences", {}).get("tone", "casual")

    extra = f"\nTalking to: {name}. Relationship: {relationship}. Tone: {tone}."

    if relationship == "mom":
        extra += "\nThis is your mom. Be respectful but casual."
    elif relationship == "gf":
        extra += "\nThis is your girlfriend. Be sweet and loving."
    elif relationship == "friend":
        extra += "\nThis is your close friend. Be fully casual and funny."
    elif relationship == "classmate":
        extra += "\nThis is a classmate. Normal friendly tone."

    # Only add profile info if the message needs it
    extra += get_profile_context(message)

    return SYSTEM_PROMPT + extra


def get_chat_history(phone: str, limit: int = 6):
    """Get last N messages for this phone number from DB."""
    cursor = whatsapp_col.find(
        {"phone": phone},
        {"_id": 0, "role": 1, "content": 1}
    ).sort("timestamp", -1).limit(limit)
    messages = list(cursor)
    messages.reverse()
    return messages


def save_whatsapp_message(phone: str, role: str, content: str):
    """Save a WhatsApp message to DB."""
    whatsapp_col.insert_one({
        "phone": phone,
        "role": role,
        "content": content,
        "timestamp": datetime.now(IST)
    })


def extract_text(message: MessageEv) -> tuple:
    msg = message.Message
    try:
        if msg.extendedTextMessage.text:
            text = msg.extendedTextMessage.text.strip()
            try:
                q = msg.extendedTextMessage.contextInfo.quotedMessage
                quoted = ""
                if q.conversation:
                    quoted = q.conversation
                elif q.extendedTextMessage.text:
                    quoted = q.extendedTextMessage.text
                elif q.imageMessage.mimetype:
                    quoted = "[image]"
                elif q.audioMessage.seconds > 0:
                    quoted = "[voice note]"
                elif q.videoMessage.mimetype:
                    quoted = "[video]"
                elif q.stickerMessage.mimetype:
                    quoted = "[sticker]"
                if quoted:
                    text = f"[replying to: '{quoted}'] {text}"
            except:
                pass
            return text, "text"

        if msg.conversation:
            return msg.conversation.strip(), "text"
        if msg.audioMessage.seconds > 0:
            return "VOICE_NOTE", "audio"
        if msg.imageMessage.mimetype:
            caption = msg.imageMessage.caption or ""
            return (f"[sent an image: {caption}]" if caption else "[sent an image]"), "image"
        if msg.videoMessage.mimetype:
            caption = msg.videoMessage.caption or ""
            return (f"[sent a video: {caption}]" if caption else "[sent a video]"), "video"
        if msg.stickerMessage.mimetype:
            return "STICKER", "sticker"
        if msg.documentMessage.mimetype:
            filename = msg.documentMessage.fileName or "a file"
            return f"[sent a document: {filename}]", "document"
    except:
        pass
    return "", "unknown"


def send_message(client: NewClient, chat_jid, text: str):
    try:
        client.send_message(chat_jid, text)
        print(f"Message sent!")
    except Exception as e:
        print(f"Send failed: {e}")


VOICE_REPLIES = [
    "bhai voice note sun nahi sakta, text kar 😅",
    "arre type kar yaar, voice note nahi sunta",
    "bhai likh de na, voice note mat bhej",
    "sun nahi sakta, text kar",
]
_voice_index = 0


def get_voice_reply() -> str:
    global _voice_index
    reply = VOICE_REPLIES[_voice_index % len(VOICE_REPLIES)]
    _voice_index += 1
    return reply


STICKER_REPLIES = ["😂", "haha", "lol", "💀", "hahaha"]
_sticker_index = 0


def get_sticker_reply() -> str:
    global _sticker_index
    reply = STICKER_REPLIES[_sticker_index % len(STICKER_REPLIES)]
    _sticker_index += 1
    return reply


class MessageHandler:
    def __init__(self, client: NewClient):
        self.client = client

    def process(self, message: MessageEv):
        try:
            try:
                msg_time = datetime.fromtimestamp(message.Info.Timestamp, tz=IST)
                if msg_time < AGENT_START_TIME:
                    return
            except:
                pass

            if message.Info.MessageSource.IsFromMe:
                return

            is_group = message.Info.MessageSource.IsGroup
            phone = message.Info.MessageSource.Sender.User
            if not phone:
                return

            chat_jid = message.Info.MessageSource.Chat
            push_name = getattr(message.Info, "PushName", None) or "Unknown"
            display_name = get_display_name(phone, push_name)

            text, msg_type = extract_text(message)
            if not text:
                return

            if is_group:
                if not any(t in text.lower() for t in BOT_TRIGGERS):
                    return
                print(f"\nGROUP {display_name} ({phone}): {text}")
            else:
                print(f"\n{display_name} ({phone}) [{msg_type}]: {text}")

            save_contact(phone, push_name)

            if msg_type == "audio":
                reply = get_voice_reply()
                send_message(self.client, chat_jid, reply)
                return

            if msg_type == "sticker":
                reply = get_sticker_reply()
                send_message(self.client, chat_jid, reply)
                return

            pending_key = str(chat_jid) if is_group else phone

            with _lock:
                if pending_key in _pending:
                    _pending[pending_key]["timer"].cancel()
                    _pending[pending_key]["messages"].append(text)
                else:
                    _pending[pending_key] = {
                        "messages": [text],
                        "display_name": display_name,
                        "chat_jid": chat_jid,
                        "phone": phone,
                    }

                timer = threading.Timer(1.5, self._reply, args=[pending_key])
                timer.daemon = True
                _pending[pending_key]["timer"] = timer
                timer.start()

        except Exception as e:
            import traceback
            print(f"Process error: {e}")
            traceback.print_exc()

    def _reply(self, pending_key: str):
        try:
            with _lock:
                if pending_key not in _pending:
                    return
                data = _pending.pop(pending_key)

            messages = data["messages"]
            display_name = data["display_name"]
            chat_jid = data["chat_jid"]
            phone = data["phone"]

            combined = "\n".join(messages)
            print(f"Replying to {display_name}: {combined}")

            save_whatsapp_message(phone, "user", combined)

            history = get_chat_history(phone, limit=6)
            context = [{"role": m["role"], "content": m["content"]} for m in history]

            system = build_prompt(phone, combined)
            reply = llm.chat(context, system_prompt=system)

            reply = reply.strip()
            lines = [l.strip() for l in reply.split("\n") if l.strip()]
            reply = " ".join(lines[:2])

            print(f"Aditya: {reply}")

            save_whatsapp_message(phone, "assistant", reply)
            send_message(self.client, chat_jid, reply)

        except Exception as e:
            import traceback
            print(f"Reply error: {e}")
            traceback.print_exc()

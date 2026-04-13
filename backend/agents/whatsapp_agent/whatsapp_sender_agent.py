# agents/whatsapp_agent/whatsapp_sender_agent.py
"""
WhatsApp Sender Agent
======================
Sends WhatsApp messages via neonize (same connection as the bot).
Nova calls: agent.handle(user_input, memory)

Usage:
  "send happy birthday to Abhiava on WhatsApp"
  "WhatsApp Rahul that I will be late"
  "send message to Mom saying dinner is ready"
"""

import json
import datetime
import pytz
import threading

from utils.llm import LLMClient
from pymongo import MongoClient
from config.settings import MONGO_URI, DB_NAME, COLLECTIONS

_mongo = MongoClient(MONGO_URI)
_db = _mongo[DB_NAME]
contacts_col = _db[COLLECTIONS["contacts"]]
whatsapp_col = _db[COLLECTIONS["whatsapp_messages"]]

IST = pytz.timezone("Asia/Kolkata")
llm = LLMClient()

# Shared neonize client — set when WhatsApp bot connects
_neonize_client = None
_client_lock = threading.Lock()


def set_neonize_client(client):
    """Called by whatsapp_agent.py when bot connects."""
    global _neonize_client
    with _client_lock:
        _neonize_client = client
    print("WhatsAppSenderAgent: neonize client registered!")


class WhatsAppSenderAgent:
    name = "WhatsAppSenderAgent"

    def handle(self, user_input: str, memory=None) -> str:
        """Called by Nova router."""

        intent = self._extract_intent(user_input)
        if "error" in intent:
            return f"Could not understand: {intent['error']}"

        contact_name = intent.get("contact_name", "")
        message_type = intent.get("message_type", "custom")
        custom_text  = intent.get("custom_text", "")

        phone = self._lookup_phone(contact_name)
        if not phone:
            return (
                f"Could not find '{contact_name}' in your contacts.\n"
                f"Make sure they have messaged you on WhatsApp first so they are saved."
            )

        message = self._compose_message(message_type, contact_name, custom_text)
        success, error = self._send(phone, message)

        if not success:
            return f"Failed to send: {error}"

        self._save_to_db(phone, contact_name, message)
        return f"Message sent to {contact_name}!\n\"{message}\""

    def _extract_intent(self, user_input: str) -> dict:
        system_prompt = """You are an intent extractor for a WhatsApp sender.
Extract info from the user instruction and respond ONLY with JSON.

Format:
{"contact_name": "Abhiava", "message_type": "birthday", "custom_text": ""}

message_type: "birthday" or "custom"
custom_text: actual message if specified, else empty string.

Examples:
"send happy birthday to Abhiava" -> {"contact_name": "Abhiava", "message_type": "birthday", "custom_text": ""}
"WhatsApp Rahul that I will be late" -> {"contact_name": "Rahul", "message_type": "custom", "custom_text": "I will be late"}
"message Mom saying dinner ready" -> {"contact_name": "Mom", "message_type": "custom", "custom_text": "dinner ready"}

If no contact found: {"error": "no contact name found"}"""

        try:
            text = llm.chat(
                [{"role": "user", "content": user_input}],
                system_prompt=system_prompt
            )
            start = text.find("{")
            end   = text.rfind("}") + 1
            if start != -1 and end > start:
                return json.loads(text[start:end])
            return {"error": "Could not parse LLM response"}
        except Exception as e:
            return {"error": str(e)}

    def _lookup_phone(self, contact_name: str):
        if not contact_name:
            return None
        contact = contacts_col.find_one(
            {"name": {"$regex": f"^{contact_name}$", "$options": "i"}}
        )
        if not contact:
            contact = contacts_col.find_one(
                {"name": {"$regex": contact_name, "$options": "i"}}
            )
        if contact:
            phone = contact.get("phone", "")
            if phone and not phone.startswith("+"):
                phone = "+" + phone
            return phone or None
        return None

    def _compose_message(self, message_type: str, contact_name: str, custom_text: str) -> str:
        if message_type == "custom" and custom_text:
            return custom_text

        if message_type == "birthday":
            prompt = f"Write a short casual birthday wish for {contact_name} in hinglish. Max 1-2 sentences with 1 emoji."
        else:
            prompt = f"Write a short casual WhatsApp message saying: {custom_text}. Keep it natural and brief."

        try:
            return llm.chat([{"role": "user", "content": prompt}])
        except Exception:
            if message_type == "birthday":
                return f"Happy Birthday {contact_name}! Have a great day!"
            return custom_text or "Hey!"

    def _send(self, phone: str, message: str):
        with _client_lock:
            client = _neonize_client

        if client is None:
            return False, "WhatsApp bot is not connected."

        try:
            from neonize.proto.Neonize_pb2 import JID
            number = phone.lstrip("+")
            jid = JID(
                User=number,
                Server="s.whatsapp.net",
                RawAgent=0,
                Device=0,
                Integrator=0,
                IsEmpty=False
            )
            client.send_message(jid, message)
            return True, ""
        except Exception as e:
            try:
                import time
                time.sleep(2)
                from neonize.proto.Neonize_pb2 import JID
                number = phone.lstrip("+")
                jid = JID(
                    User=number,
                    Server="s.whatsapp.net",
                    RawAgent=0,
                    Device=0,
                    Integrator=0,
                    IsEmpty=False
                )
                client.send_message(jid, message)
                return True, ""
            except Exception as e2:
                return False, str(e2)

    def _save_to_db(self, phone: str, contact_name: str, message: str):
        try:
            whatsapp_col.insert_one({
                "phone":     phone,
                "name":      contact_name,
                "role":      "assistant",
                "content":   message,
                "timestamp": datetime.datetime.now(IST),
                "sent_by":   "nova",
            })
        except Exception as e:
            print(f"Could not save to DB: {e}")

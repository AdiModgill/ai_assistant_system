# agents/whatsapp_agent/scheduler.py
from database.db import db
from utils.llm import LLMClient
from datetime import datetime
import pytz
import threading
import time

IST = pytz.timezone("Asia/Kolkata")
contacts_col = db["contacts"]
scheduled_col = db["scheduled_tasks"]

llm = LLMClient()
_client = None


def set_client(client):
    global _client
    _client = client


def send_birthday_wishes():
    if not _client:
        return

    today = datetime.now(IST)
    today_str = f"{today.day}/{today.month}"
    contacts = list(contacts_col.find({"birthday": {"$ne": None}}))

    for contact in contacts:
        birthday = contact.get("birthday", "")
        if not birthday or today_str not in str(birthday):
            continue

        phone = contact["phone"]
        name = contact.get("name", "friend")

        already_sent = scheduled_col.find_one({
            "type": "birthday",
            "phone": phone,
            "date": today.strftime("%Y-%m-%d")
        })
        if already_sent:
            continue

        wish = llm.chat(
            [{"role": "user", "content": f"Generate a short casual birthday wish for {name} in hinglish. Max 1-2 sentences with emoji."}]
        )

        try:
            _client.send_message(f"{phone}@s.whatsapp.net", wish)
            print(f"Birthday wish sent to {name} ({phone})")
            scheduled_col.insert_one({
                "type": "birthday",
                "phone": phone,
                "date": today.strftime("%Y-%m-%d"),
                "sent_at": datetime.now(IST)
            })
        except Exception as e:
            print(f"Failed to send birthday wish: {e}")


def send_scheduled_messages():
    if not _client:
        return

    now = datetime.now(IST)
    pending = scheduled_col.find({
        "type": "scheduled",
        "status": "pending",
        "run_at": {"$lte": now}
    })

    for task in pending:
        try:
            phone = task["phone"]
            message = task["message"]
            _client.send_message(f"{phone}@s.whatsapp.net", message)
            print(f"Scheduled message sent to {phone}")
            scheduled_col.update_one(
                {"_id": task["_id"]},
                {"$set": {"status": "done", "sent_at": now}}
            )
        except Exception as e:
            print(f"Scheduled message failed: {e}")

def start_scheduler():
    def loop():
        while True:
            now = datetime.now(IST)
            # Run if it's between 9 AM and 11 PM
            # AND hasn't been sent today yet (DB checks this)
            if now.hour >= 9:
                send_birthday_wishes()   # DB prevents duplicates automatically
                send_scheduled_messages()
            time.sleep(3600)  # check once every hour

    t = threading.Thread(target=loop, daemon=True)
    t.start()
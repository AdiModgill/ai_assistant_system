# command.py
from neonize.client import NewClient
from neonize.events import ConnectedEv
from neonize.proto.Neonize_pb2 import JID
from neonize.proto.waE2E.WAWebProtobufsE2E_pb2 import Message as WaMessage
from utils.llm import chat
from database.database import db
import pytz

IST = pytz.timezone("Asia/Kolkata")
contacts_col = db["contacts"]
_client = None


def make_jid(phone: str) -> JID:
    jid = JID()
    jid.User = phone
    jid.Server = "s.whatsapp.net"
    jid.RawAgent = 0
    jid.Device = 0
    jid.Integrator = 0
    return jid


def find_contact(name: str):
    return contacts_col.find_one({
        "name": {"$regex": name, "$options": "i"}
    })


def generate_message(topic: str, contact: dict) -> str:
    name = contact.get("name", "friend")
    relationship = contact.get("relationship", "friend")

    prompt = [{
        "role": "user",
        "content": f"Generate a short WhatsApp message from Aditya to his {relationship} named {name} about: {topic}. 2-3 lines max. Casual Hinglish tone. 1 emoji only."
    }]

    return chat(prompt)


def send_command(command: str):
    command_lower = command.strip().lower()

    if "send message to" in command_lower:
        parts = command_lower.replace("send message to", "").strip()
        words = parts.split()

        if not words:
            print("❌ Please provide a name. Example: send message to mummy happy birthday")
            return

        name = words[0]
        topic = " ".join(words[1:]) if len(words) > 1 else "hi"

        contact = find_contact(name)
        if not contact:
            print(f"❌ Contact '{name}' not found in database!")
            return

        phone = contact["phone"]
        print(f"📤 Sending to {contact['name']} ({phone})...")

        message = generate_message(topic, contact)
        print(f"🤖 Generated: {message}")

        try:
            jid = make_jid(phone)
            msg = WaMessage()
            msg.conversation = message
            _client.send_message(jid, msg)
            print(f"✅ Sent to {contact['name']}!")
        except Exception as e:
            print(f"❌ Failed to send: {e}")

    else:
        print("❌ Command not understood.")
        print("Try: send message to mummy happy birthday")
        print("Try: send message to abhinav how are you")


def on_connected(client, connected):
    global _client
    _client = client
    print("✅ Connected to WhatsApp!")
    print("\nCommands you can use:")
    print("  send message to [name] [topic]")
    print("  exit\n")

    while True:
        try:
            command = input("> ").strip()
            if not command:
                continue
            if command.lower() == "exit":
                print("Bye!")
                break
            send_command(command)
        except KeyboardInterrupt:
            print("\nBye!")
            break


if __name__ == "__main__":
    client = NewClient("whatsapp.session")
    client.event(ConnectedEv)(on_connected)
    print("🚀 Connecting to WhatsApp...")
    client.connect()
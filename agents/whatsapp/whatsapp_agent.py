# agents/whatsapp/whatsapp_agent.py
from neonize.client import NewClient
from neonize.events import MessageEv, ConnectedEv
from agents.whatsapp.handler import MessageHandler
from agents.whatsapp.scheduler import set_client, start_scheduler
import pytz

IST = pytz.timezone("Asia/Kolkata")

_handler = None


def on_connected(client: NewClient, connected: ConnectedEv):
    global _handler
    _handler = MessageHandler(client)
    set_client(client)
    print("✅ WhatsApp connected!")
    print("💬 Aditya agent is live...")


def on_message(client: NewClient, message: MessageEv):
    if _handler:
        _handler.process(message)


def start_whatsapp_agent():
    start_scheduler()
    client = NewClient("whatsapp.session")
    client.event(ConnectedEv)(on_connected)
    client.event(MessageEv)(on_message)
    print("🚀 Starting WhatsApp Agent...")
    client.connect()
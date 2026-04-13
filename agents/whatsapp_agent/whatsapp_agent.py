# agents/whatsapp_agent/whatsapp_agent.py
from neonize.client import NewClient
from neonize.events import MessageEv, ConnectedEv
from agents.whatsapp_agent.handler import MessageHandler
from agents.whatsapp_agent.scheduler import set_client, start_scheduler
from agents.whatsapp_agent.whatsapp_sender_agent import set_neonize_client
import pytz

IST = pytz.timezone("Asia/Kolkata")

_handler = None


def on_connected(client: NewClient, connected: ConnectedEv):
    global _handler
    _handler = MessageHandler(client)
    set_client(client)
    set_neonize_client(client)  # share with sender agent
    print("WhatsApp connected!")
    print("Aditya agent is live...")


def on_message(client: NewClient, message: MessageEv):
    if _handler:
        _handler.process(message)


def start_whatsapp_agent():
    start_scheduler()
    client = NewClient("whatsapp.session")
    client.event(ConnectedEv)(on_connected)
    client.event(MessageEv)(on_message)
    print("Starting WhatsApp Agent...")
    client.connect()


if __name__ == "__main__":
    start_whatsapp_agent()

"""
Nova - The Central Brain / Controller
"""

from core.router import Router
from core.memory import MemoryManager
from utils.llm import LLMClient
from config.settings import settings

HISTORY_ON_STARTUP = 10
CONTEXT_WINDOW = 10

NOVA_SYSTEM_PROMPT = """You are Nova, a smart, friendly and helpful personal AI assistant.
You have a warm, casual personality like a helpful friend who is also very capable.
Your capabilities: send emails, get weather, set alarms, send WhatsApp messages, manage clipboard.
When someone greets you or chats casually, respond warmly and naturally.
Keep responses concise - 1-3 sentences for casual chat.
Never say you cannot do general conversation - you can and should chat naturally.
"""

class Nova:
    def __init__(self):
        print("\n[Nova] Initializing...")
        self.memory = MemoryManager()
        self.router = Router()
        self.llm = LLMClient()
        self.name = "Nova"
        self._load_past_memory()

    def _load_past_memory(self):
        past = self.memory.get_history(limit=HISTORY_ON_STARTUP)
        if past:
            self.memory.load_into_session(past)
            print(f"[Nova] Loaded {len(past)} past messages from memory.")
        else:
            print("[Nova] No past memory found. Starting fresh.")

    def run(self):
        self._print_banner()
        while True:
            try:
                user_input = input("You: ").strip()
                if not user_input:
                    continue
                if user_input.lower() in ("quit", "exit", "bye", "goodbye"):
                    print(f"\n{self.name}: Goodbye! See you next time. \n")
                    break
                if user_input.lower() in ("clear memory", "forget everything"):
                    self._handle_clear_memory()
                    continue
                if user_input.lower() in ("history", "show history"):
                    self._show_history()
                    continue
                if user_input.lower() in ("help", "what can you do"):
                    self._show_help()
                    continue

                response = self.process(user_input)
                print(f"\n{self.name}: {response}\n")

            except KeyboardInterrupt:
                print(f"\n\n{self.name}: Interrupted. Goodbye!\n")
                break
            except Exception as e:
                print(f"\n[Nova ERROR] Something went wrong: {e}")
                print("Please try again.\n")

    def process(self, user_input: str) -> str:
        self.memory.add("user", user_input)

        agent = self.router.route(user_input)

        if agent:
            response = agent.handle(user_input)
        else:
            response = self._casual_chat(user_input)

        self.memory.add("assistant", response)
        return response

    def _casual_chat(self, user_input: str) -> str:
        try:
            recent = self.memory.get_recent(limit=CONTEXT_WINDOW)
            messages = [{"role": m["role"], "content": m["content"]} for m in recent[:-1]]
            messages.append({"role": "user", "content": user_input})
            return self.llm.chat(messages, system_prompt=NOVA_SYSTEM_PROMPT)
        except Exception as e:
            return f"Sorry, I had trouble thinking about that. ({e})"

    def _handle_clear_memory(self):
        confirm = input(f"  {self.name}: Are you sure? (yes / no): ").strip().lower()
        if confirm == "yes":
            self.memory.clear_all()
            print(f"{self.name}: Memory cleared.\n")
        else:
            print(f"{self.name}: No changes made.\n")

    def _show_history(self):
        messages = self.memory.get_recent(limit=10)
        if not messages:
            print(f"\n{self.name}: No history yet.\n")
            return

        print("\n── Recent History ──────────────────────────")
        for msg in messages:
            label = "You" if msg["role"] == "user" else self.name
            print(f"  [{label}] {msg['content']}")
        print("────────────────────────────────────────────\n")

    def _show_help(self):
        print(f"""
What {self.name} can do:
  Email    - "Send an email to john@example.com"
  Weather  - "Whats the weather in Delhi?"
  Alarm    - "Remind me at 7:30 AM"
  WhatsApp - "Send WhatsApp to Abhiava saying Happy Birthday"
  Clipboard- "Read my clipboard"
  Music    - "Suggest songs" / "Play sad songs"
  Commands - history, clear memory, help, exit
""")

    def _print_banner(self):
        print("""
Nova AI Assistant
Type your request. Type 'help' to see what I can do. Type 'exit' to quit.
""")
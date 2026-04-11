"""
Nova - The Central Brain / Controller
========================================
- Single entry point for all user interaction
- Routes to agents or falls back to clarification
- Loads past conversation history from DB on startup
- Text-based input (keyboard)
"""

from core.router import Router
from core.memory import MemoryManager
from utils.llm import LLMClient
from config.settings import settings


# ── How many past messages to load on startup ──
HISTORY_ON_STARTUP = 10

# ── How many messages to send as context to LLM ──
CONTEXT_WINDOW = 10


class Nova:
    def __init__(self):
        print("\n[Nova] Initializing...")

        self.memory = MemoryManager()
        self.router = Router()
        self.llm    = LLMClient()
        self.name   = "Nova"

        self._load_past_memory()

    # ──────────────────────────────────────────────────────────────
    # Startup
    # ──────────────────────────────────────────────────────────────

    def _load_past_memory(self):
        """Load the last N messages from DB into the session buffer on startup."""
        past = self.memory.get_history(limit=HISTORY_ON_STARTUP)

        if past:
            self.memory.load_into_session(past)
            print(f"[Nova] Loaded {len(past)} past messages from memory.")
        else:
            print("[Nova] No past memory found. Starting fresh.")

    # ──────────────────────────────────────────────────────────────
    # Main Loop
    # ──────────────────────────────────────────────────────────────

    def run(self):
        """Start the main conversation loop."""
        self._print_banner()

        while True:
            try:
                user_input = input("You: ").strip()

                if not user_input:
                    continue

                # ── Built-in commands ──
                if user_input.lower() in ("quit", "exit", "bye", "goodbye"):
                    print(f"\n{self.name}: Goodbye! See you next time. 👋\n")
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

                # ── Normal processing ──
                response = self.process(user_input)
                print(f"\n{self.name}: {response}\n")

            except KeyboardInterrupt:
                print(f"\n\n{self.name}: Interrupted. Goodbye!\n")
                break
            except Exception as e:
                print(f"\n[Nova ERROR] Something went wrong: {e}")
                if settings.DEBUG:
                    import traceback
                    traceback.print_exc()
                print("Please try again.\n")

    # ──────────────────────────────────────────────────────────────
    # Core Pipeline
    # ──────────────────────────────────────────────────────────────

    def process(self, user_input: str) -> str:
        """
        Main processing pipeline:
          1. Save user message to memory
          2. Try to route to a specific agent
          3. If no agent matched → ask user to clarify
          4. Save response to memory
          5. Return response
        """
        # Step 1 — Save user message
        self.memory.add("user", user_input)

        # Step 2 — Try routing
        agent = self.router.route(user_input)

        if agent:
            if settings.DEBUG:
                print(f"[Nova] → Routing to {agent.name}")
            response = agent.handle(user_input, self.memory)

        else:
            # Step 3 — No agent matched: ask for clarification
            response = self._ask_for_clarification()

        # Step 4 — Save response
        self.memory.add("assistant", response)

        # Step 5 — Return
        return response

    # ──────────────────────────────────────────────────────────────
    # Clarification  (no agent matched)
    # ──────────────────────────────────────────────────────────────

    def _ask_for_clarification(self) -> str:
        """
        Politely ask the user to clarify.
        Lists what Nova can currently do so the user knows their options.
        """
        capabilities = self.router.list_capabilities()

        lines = [
            "I'm not sure what you're asking for. Could you clarify?",
            "",
            "Here's what I can help with right now:",
        ]
        for cap in capabilities:
            lines.append(f"  • {cap}")

        lines.append("")
        lines.append("Try rephrasing using one of those topics, or type 'help' for examples.")

        return "\n".join(lines)

    # ──────────────────────────────────────────────────────────────
    # Built-in Command Handlers
    # ──────────────────────────────────────────────────────────────

    def _handle_clear_memory(self):
        """Wipe all DB memory after confirmation."""
        confirm = input(
            f"  {self.name}: Are you sure you want to clear ALL memory? (yes / no): "
        ).strip().lower()

        if confirm == "yes":
            self.memory.clear_all()
            print(f"{self.name}: Memory cleared. Starting fresh.\n")
        else:
            print(f"{self.name}: No changes made. Memory kept.\n")

    def _show_history(self):
        """Print the last 10 messages from the current session."""
        messages = self.memory.get_recent(limit=10)

        if not messages:
            print(f"\n{self.name}: No history yet in this session.\n")
            return

        print("\n── Recent History ──────────────────────────")
        for msg in messages:
            label = "You " if msg["role"] == "user" else self.name
            print(f"  [{label}] {msg['content']}")
        print("────────────────────────────────────────────\n")

    def _show_help(self):
        """Print usage examples for each agent."""
        print(f"""
── What {self.name} can do ─────────────────────────────
  📧 Email
      "Send an email to john@example.com about the meeting"
      "Check my inbox"

  🌤  Weather
      "What's the weather in Delhi?"
      "Temperature in Mumbai today"

  ⏰  Alarm / Timer
      "Set a timer for 20 minutes"
      "Remind me at 7:30 AM"

  💬  WhatsApp
      "Send WhatsApp to +91XXXXXXXXXX saying Hello!"

  📋  Clipboard
      "Read my clipboard"
      "Copy this text to clipboard: Hello World"

  🛠  Built-in Commands
      history          → show recent chat
      clear memory     → wipe all history
      help             → show this menu
      exit / quit      → stop Nova
────────────────────────────────────────────────────\n""")

    # ──────────────────────────────────────────────────────────────
    # Banner
    # ──────────────────────────────────────────────────────────────

    def _print_banner(self):
        print("""
╔══════════════════════════════════════════╗
║           N O V A  AI  ASSISTANT         ║
║          Your personal AI helper         ║
╚══════════════════════════════════════════╝

  Type your request below.
  Type 'help' to see what I can do.
  Type 'exit' to quit.
""")
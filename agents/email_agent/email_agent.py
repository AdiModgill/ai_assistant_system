from agents.email_agent.agent import AIAgent   # ✅ FIXED IMPORT


class EmailAgent:
    def __init__(self):
        self.agent = AIAgent()
        print("📧 EmailAgent initialized")

    def handle(self, user_input):
        return self.agent.process_user_input(user_input)
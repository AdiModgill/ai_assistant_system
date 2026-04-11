from ollama import Client
import json
from agents.email_agent.email_tool import EmailTool   # ✅ FIXED IMPORT


class AIAgent:
    def __init__(self):
        self.client = Client(host="http://localhost:11434")
        self.email_tool = EmailTool()
        self.conversation_history = []

    def process_user_input(self, user_message):

        print("\n" + "="*70)
        print(f"USER INPUT: {user_message}")
        print("="*70)

        self.conversation_history.append({
            "role": "user",
            "content": user_message
        })

        system_prompt = """You are an AI email assistant. You can send emails.

When a user asks you to send an email, respond with JSON like:
{
  "action": "send_email",
  "recipient": "john@example.com",
  "subject": "Hello",
  "body": "Hi John"
}
Then explain briefly.
"""

        conversation_text = "\n".join([
            f"{msg['role']}: {msg['content']}"
            for msg in self.conversation_history
        ])

        full_prompt = f"{system_prompt}\n\nConversation:\n{conversation_text}"

        try:
            response = self.client.generate(
                model="qwen2.5:3b",
                prompt=full_prompt,
                stream=False
            )

            llm_response = response.response.strip()
            print(f"\n🤖 Response:\n{llm_response}")

        except Exception as e:
            return f"Error: {str(e)}"

        final_response = llm_response

        try:
            json_start = llm_response.find("{")
            json_end = llm_response.rfind("}") + 1

            if json_start != -1 and json_end > json_start:
                json_str = llm_response[json_start:json_end]
                action_data = json.loads(json_str)

                if action_data.get("action") == "send_email":
                    recipient = action_data.get("recipient")
                    subject = action_data.get("subject")
                    body = action_data.get("body")

                    result = self.email_tool.send_email(recipient, subject, body)

                    if result["success"]:
                        final_response = result["message"]
                    else:
                        final_response = result["error"]

        except:
            pass

        self.conversation_history.append({
            "role": "assistant",
            "content": final_response
        })

        return final_response
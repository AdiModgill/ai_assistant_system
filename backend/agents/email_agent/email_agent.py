"""
Email Agent
===========
Handles sending emails via Gmail SMTP.
Uses Ollama to extract recipient, subject, body from natural language.
"""

import json
from ollama import Client
from agents.email_agent.email_tool import EmailTool


class EmailAgent:
    def __init__(self):
        self.client = Client(host="http://localhost:11434")
        self.email_tool = EmailTool()
        print("EmailAgent initialized")

    def handle(self, user_input):
        print(f"\n[EmailAgent] Input: {user_input}")

        # Simple prompt — don't confuse llama with too much
        prompt = f"""Extract email details from this message and reply ONLY with JSON.

Message: "{user_input}"

Reply with this exact format:
{{
  "recipient": "email address here",
  "subject": "subject here",
  "body": "email body here"
}}

For the body, write it naturally and warmly like a human would.
Keep it short and friendly. No extra text, just the JSON."""

        try:
            response = self.client.generate(
                model="llama3:latest",
                prompt=prompt,
                stream=False
            )
            llm_response = response.response.strip()
            print(f"[EmailAgent] LLM response: {llm_response}")

        except Exception as e:
            return f"Sorry, I couldn't process that. Error: {str(e)}"

        # Parse JSON from response
        try:
            json_start = llm_response.find("{")
            json_end = llm_response.rfind("}") + 1

            if json_start == -1:
                return "I couldn't understand the email details. Try: 'send email to john@gmail.com saying happy birthday'"

            json_str = llm_response[json_start:json_end]
            data = json.loads(json_str)

            recipient = data.get("recipient", "").strip()
            subject = data.get("subject", "").strip()
            body = data.get("body", "").strip()

            if not recipient or "@" not in recipient:
                return "I couldn't find a valid email address. Please include one like john@gmail.com"

            if not subject:
                subject = "Hello"
            if not body:
                body = "Hi there!"

            # Send it
            result = self.email_tool.send_email(recipient, subject, body)

            if result["success"]:
                return f"✅ Email sent to {recipient}!\nSubject: {subject}"
            else:
                return f"❌ Couldn't send email: {result['error']}"

        except json.JSONDecodeError:
            return "I had trouble reading the email details. Try again like: 'send email to john@gmail.com saying happy birthday'"

        except Exception as e:
            return f"Something went wrong: {str(e)}"
from ollama import Client
import json
from email_tool import EmailTool


class AIAgent:
    """
    The AI AGENT - the brain that thinks and makes decisions.
    """
    
    def __init__(self):
        """Constructor - sets up the agent."""
        self.client = Client(host="http://localhost:11434")
        self.email_tool = EmailTool()
        self.conversation_history = []
    
    def process_user_input(self, user_message):
        """
        Main agent method - processes what the user typed.
        """
        
        print("\n" + "="*70)
        print(f"USER INPUT: {user_message}")
        print("="*70)
        
        # Add to memory
        self.conversation_history.append({
            "role": "user",
            "content": user_message
        })
        
        # System prompt
        system_prompt = """You are an AI email assistant. You can send emails.

When a user asks you to send an email, respond with a JSON block like this:
{
  "action": "send_email",
  "recipient": "john@example.com",
  "subject": "Hello",
  "body": "Hi John, how are you?"
}

Then add a message explaining what you did.

If not about email, just respond normally without JSON."""
        
        # Build prompt
        conversation_text = "\n".join([
            f"{msg['role']}: {msg['content']}" 
            for msg in self.conversation_history
        ])
        
        full_prompt = f"{system_prompt}\n\nConversation:\n{conversation_text}"
        
        # Send to Qwen2.5
        print("\n📡 Sending to Qwen2.5...")
        
        try:
            response = self.client.generate(
                model="qwen2.5:3b",
                prompt=full_prompt,
                stream=False
            )
            
            llm_response = response.response.strip()
            print(f"\n🤖 Qwen2.5 Response:\n{llm_response}")
        
        except Exception as e:
            print(f"\n Error: {str(e)}")
            return f"Error: Could not reach Qwen2.5. Make sure 'ollama serve' is running."
        
        # Extract and process JSON
        final_response = llm_response
        
        try:
            # Find JSON in response
            json_start = llm_response.find("{")
            json_end = llm_response.rfind("}") + 1
            
            if json_start != -1 and json_end > json_start:
                json_str = llm_response[json_start:json_end]
                action_data = json.loads(json_str)
                
                # Check if should send email
                if action_data.get("action") == "send_email":
                    print("\n  Agent decided to send an email!")
                    
                    # Extract details
                    recipient = action_data.get("recipient")
                    subject = action_data.get("subject")
                    body = action_data.get("body")
                    
                    print(f"   To: {recipient}")
                    print(f"   Subject: {subject}")
                    print(f"   Body: {body}")
                    
                    # Send email
                    result = self.email_tool.send_email(recipient, subject, body)
                    
                    if result["success"]:
                        print(f"\n {result['message']}")
                        final_response = f" {result['message']}"
                    else:
                        print(f"\n❌ {result['error']}")
                        final_response = f" {result['error']}"
        
        except (json.JSONDecodeError, ValueError):
            pass
        
        # Add to memory
        self.conversation_history.append({
            "role": "assistant",
            "content": final_response
        })
        
        return final_response
    
    def clear_history(self):
        """Clear conversation history"""
        self.conversation_history = []
# utils/llm.py
import requests
from config.settings import OLLAMA_URL, LLM_MODEL

def chat(messages: list, system_prompt: str = "") -> str:
    
    final_messages = []

    # inject system prompt as first message
    if system_prompt:
        final_messages.append({
            "role": "system",
            "content": system_prompt
        })

    # add conversation history
    final_messages.extend(messages)

    payload = {
        "model": LLM_MODEL,
        "messages": final_messages,
        "stream": False
    }

    try:
        response = requests.post(
            f"{OLLAMA_URL}/api/chat",
            json=payload,
            timeout=60
        )
        response.raise_for_status()
        return response.json()["message"]["content"].strip()

    except requests.exceptions.ConnectionError:
        return "Cannot connect to Ollama. Is it running?"
    except requests.exceptions.Timeout:
        return "Ollama took too long to respond."
    except Exception as e:
        return f"LLM error: {str(e)}"
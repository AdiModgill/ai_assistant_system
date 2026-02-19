
import requests
from config.settings import OLLAMA_URL, LLM_MODEL

def chat(messages: list, system_prompt: str = "") -> str:
    """
    Send messages to Ollama and get a reply.
    
    messages format:
    [
        {"role": "user", "content": "hey!"},
        {"role": "assistant", "content": "hey back!"},
        {"role": "user", "content": "how are you?"}
    ]
    """
    payload = {
        "model": LLM_MODEL,
        "messages": messages,
        "stream": False
    }

    if system_prompt:
        payload["system"] = system_prompt

    try:
        response = requests.post(
            f"{OLLAMA_URL}/api/chat",
            json=payload,
            timeout=60
        )
        response.raise_for_status()
        return response.json()["message"]["content"].strip()

    except requests.exceptions.ConnectionError:
        return " Cannot connect to Ollama. Is it running?"
    except requests.exceptions.Timeout:
        return " Ollama took too long to respond."
    except Exception as e:
        return f" LLM error: {str(e)}"
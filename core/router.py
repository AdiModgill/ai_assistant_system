"""
Router - Decides which agent handles a user request.
Uses regex keyword matching. Easy to add new agents.
"""

import re
from typing import Optional, List


class Router:
    def __init__(self):
        # Import agents here (avoids circular imports at module level)
        #from agents.email_agent     import EmailAgent
        from agents.weather_agent.weather_agent import WeatherAgent 
        from agents.alarm_agent     import AlarmAgent
        from agents.whatsapp_agent  import WhatsAppAgent
        from agents.clipboard_agent import ClipboardAgent
        from agents.email_agent.email_agent import EmailAgent

        # Each entry: (agent_instance, [regex patterns], human-readable description)
        self.routes = [
            (
                EmailAgent(),
                [r"\bemail\b", r"send mail", r"\binbox\b", r"compose"],
                "Email — send or check emails",
            ),
            (
                WeatherAgent(),
                [r"\bweather\b", r"\btemperature\b", r"\bforecast\b", r"\brain\b", r"\bsunny\b"],
                "Weather — get current weather for any city",
            ),
            (
                AlarmAgent(),
                [r"\balarm\b", r"\breminder\b", r"remind me", r"set timer", r"\btimer\b", r"wake me"],
                "Alarm / Timer — set timers and reminders",
            ),
            (
                WhatsAppAgent(),
                [r"\bwhatsapp\b", r"whats ?app", r"send (a )?message to", r"text to"],
                "WhatsApp — send WhatsApp messages",
            ),
            (
                ClipboardAgent(),
                [r"\bclipboard\b", r"\bpaste\b", r"\bcopy\b", r"\bclip\b"],
                "Clipboard — read or write clipboard content",
            ),
        ]

    def route(self, user_input: str) -> Optional[object]:
        """
        Match user input against keyword patterns.
        Returns the first matching agent, or None.
        """
        text = user_input.lower()

        for agent, patterns, _ in self.routes:
            for pattern in patterns:
                if re.search(pattern, text):
                    return agent

        return None  # No match → Nova handles clarification

    def list_capabilities(self) -> List[str]:
        """Return human-readable list of what Nova can do. Used in help/clarification."""
        return [description for _, _, description in self.routes]
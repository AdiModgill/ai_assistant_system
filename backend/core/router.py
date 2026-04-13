import re

class Router:
    def __init__(self):
        from agents.weather_agent.weather_agent import WeatherAgent
        from agents.alarm_agent.alarm_agent import AlarmAgent
        from agents.clipboard_agent.clipboard_agent import ClipboardAgent
        from agents.email_agent.email_agent import EmailAgent
        from agents.whatsapp_agent.whatsapp_sender_agent import WhatsAppSenderAgent
        from agents.music_agent.music_agent import MusicAgent
        from agents.goal_agent.goal_agent import GoalAgent

        # ✅ CREATE INSTANCES ONCE
        self.music_agent = MusicAgent()
        self.goal_agent = GoalAgent()
        self.email_agent = EmailAgent()
        self.weather_agent = WeatherAgent()
        self.alarm_agent = AlarmAgent()
        self.whatsapp_agent = WhatsAppSenderAgent()
        self.clipboard_agent = ClipboardAgent()

        self.routes = [
            (self.music_agent, [r'\bmusic\b', r'\bsong\b', r'\bsongs\b', r'play', r'suggest.*song'], 'Music - suggest songs'),
            (self.goal_agent, [r'\bgoal\b', r'\bdone\b', r'\bprogress\b'], 'Goal Tracker'),
            (self.email_agent, [r'\bemail\b', r'send mail', r'\binbox\b'], 'Email - send or check emails'),
            (self.weather_agent, [r'\bweather\b', r'\btemperature\b', r'\bforecast\b'], 'Weather - get current weather'),
            (self.alarm_agent, [r'\balarm\b', r'\breminder\b', r'remind me', r'wake me'], 'Alarm - set timers'),
            (self.whatsapp_agent, [r'\bwhatsapp\b', r'send.*message to', r'text to'], 'WhatsApp - send messages'),
            (self.clipboard_agent, [r'\bclipboard\b', r'\bpaste\b', r'\bcopy\b'], 'Clipboard - read or write'),
        ]

    def route(self, user_input):
        text = user_input.lower()
        for agent, patterns, _ in self.routes:
            for pattern in patterns:
                if re.search(pattern, text):
                    return agent
        return None

    def list_capabilities(self):
        return [desc for _, _, desc in self.routes]
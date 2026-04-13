import random
import re

class MusicAgent:
    def __init__(self):
        self.music_db = {
            "happy": [
                "Pharrell Williams - Happy",
                "Justin Timberlake - Can't Stop the Feeling",
                "Katy Perry - Firework"
            ],
            "sad": [
                "Billie Eilish - Happier Than Ever",
                "Adele - Someone Like You",
                "Arijit Singh - Channa Mereya"
            ],
            "study": [
                "Lofi Hip Hop Radio",
                "Deep Focus Playlist",
                "Instrumental Study Music"
            ],
            "gym": [
                "Eminem - Lose Yourself",
                "Kanye West - Stronger",
                "Travis Scott - Sicko Mode"
            ],
            "chill": [
                "Joji - Slow Dancing in the Dark",
                "The Weeknd - Call Out My Name",
                "Coldplay - Yellow"
            ]
        }

        # keywords to detect intent
        self.music_keywords = [
            "music", "song", "songs", "play", "suggest", "listen"
        ]

    # 🎯 MAIN ENTRY
    def handle(self, message: str):
        try:
            message = message.lower()

            # check if this agent should handle it
            if not self.is_music_request(message):
                return None  # important → don't break other agents

            count = self.extract_number(message)
            mood = self.detect_mood(message)

            songs = self.get_songs(mood, count)

            return self.format_response(mood, songs)

        except Exception as e:
            return "⚠️ Couldn't fetch songs right now."

    # 🧠 detect music intent (even messy text)
    def is_music_request(self, message):
        return any(word in message for word in self.music_keywords)

    # 🔍 detect mood
    def detect_mood(self, message):
        for key in self.music_db.keys():
            if key in message:
                return key
        return "random"

    # 🔢 extract number safely
    def extract_number(self, message):
        numbers = re.findall(r'\d+', message)
        if numbers:
            try:
                return int(numbers[0])
            except:
                return 3
        return 3  # default

    # 🎵 get songs safely
    def get_songs(self, mood, count):
        if mood in self.music_db:
            songs = self.music_db[mood]
        else:
            songs = []
            for v in self.music_db.values():
                songs.extend(v)

        count = min(max(count, 1), 10)  # limit 1–10
        return random.sample(songs, min(count, len(songs)))

    # 🔗 youtube search link
    def get_youtube_link(self, song):
        query = song.replace(" ", "+")
        return f"https://www.youtube.com/results?search_query={query}"

    # 📤 FINAL RESPONSE (single-line format ✅)
    def format_response(self, mood, songs):
        if mood == "random":
            response = "🎵 Here are some songs:\n\n"
        else:
            response = f"🎵 {mood.capitalize()} Songs:\n\n"

        for i, song in enumerate(songs, 1):
            link = self.get_youtube_link(song)
            response += f"{i}) {song} - 🔗 {link}\n"

        return response
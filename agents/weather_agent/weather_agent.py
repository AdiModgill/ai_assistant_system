import ollama
import requests


class WeatherAgent:
    def __init__(self):
        print("🌦️ WeatherAgent initialized")

    def get_weather(self, city_name):
        # Step 1: Get coordinates
        geo_url = f"https://geocoding-api.open-meteo.com/v1/search?name={city_name}&count=1&language=en&format=json"
        geo_res = requests.get(geo_url).json()

        if not geo_res.get('results'):
            return "Could not find that city."

        lat = geo_res['results'][0]['latitude']
        lon = geo_res['results'][0]['longitude']

        # Step 2: Get weather
        weather_url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current_weather=true"
        weather_res = requests.get(weather_url).json()

        current = weather_res['current_weather']

        return f"The current temperature in {city_name} is {current['temperature']}°C with windspeed {current['windspeed']} km/h."

    def handle(self, user_input):
        print(f"🌦️ Processing weather request: {user_input}")

        try:
            # Extract city using LLM
            response = ollama.chat(
                model='llama3:8b',
                messages=[
                    {
                        'role': 'system',
                        'content': 'Extract only the city name from the user input.'
                    },
                    {
                        'role': 'user',
                        'content': user_input,
                    },
                ],
            )

            city = response['message']['content'].strip()

            weather_info = self.get_weather(city)

            # Final response
            final_response = ollama.chat(
                model='llama3:8b',
                messages=[
                    {
                        'role': 'system',
                        'content': 'You are a friendly weather assistant.'
                    },
                    {
                        'role': 'user',
                        'content': f"User asked: {user_input}. Weather data: {weather_info}",
                    },
                ],
            )

            return final_response['message']['content']

        except Exception as e:
            return f"Weather error: {str(e)}"
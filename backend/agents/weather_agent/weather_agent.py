"""
Weather Agent
=============
Gets real weather data from Open-Meteo (free, no API key needed).
"""

import re
import requests
import ollama


WEATHER_CODES = {
    0: "Clear sky", 1: "Mainly clear", 2: "Partly cloudy", 3: "Overcast",
    45: "Foggy", 48: "Icy fog", 51: "Light drizzle", 53: "Drizzle",
    55: "Heavy drizzle", 61: "Light rain", 63: "Rain", 65: "Heavy rain",
    71: "Light snow", 73: "Snow", 75: "Heavy snow", 80: "Rain showers",
    81: "Heavy showers", 82: "Violent showers", 95: "Thunderstorm",
}


class WeatherAgent:
    def __init__(self):
        print("WeatherAgent initialized")

    def _extract_city(self, user_input):
        """Extract city name using LLM — just the name, nothing else."""
        try:
            response = ollama.chat(
                model='llama3:latest',
                messages=[
                    {
                        'role': 'system',
                        'content': 'Extract ONLY the city name from the message. Reply with just the city name, nothing else. No punctuation, no explanation.'
                    },
                    {
                        'role': 'user',
                        'content': user_input
                    }
                ]
            )
            city = response['message']['content'].strip()
            # Clean up any extra words just in case
            city = city.split('\n')[0].strip()
            city = re.sub(r'[^a-zA-Z\s]', '', city).strip()
            return city
        except Exception as e:
            print(f"[WeatherAgent] City extraction error: {e}")
            return None

    def _get_weather(self, city):
        """Fetch real weather data from Open-Meteo."""
        # Step 1: Get coordinates
        geo_url = f"https://geocoding-api.open-meteo.com/v1/search?name={city}&count=1&language=en&format=json"
        geo_res = requests.get(geo_url, timeout=10).json()

        if not geo_res.get('results'):
            return None, f"I couldn't find a city called '{city}'. Please check the spelling."

        result = geo_res['results'][0]
        lat = result['latitude']
        lon = result['longitude']
        city_name = result['name']
        country = result.get('country', '')

        # Step 2: Get weather
        weather_url = (
            f"https://api.open-meteo.com/v1/forecast"
            f"?latitude={lat}&longitude={lon}"
            f"&current_weather=true"
            f"&hourly=relative_humidity_2m,apparent_temperature"
            f"&timezone=auto"
            f"&forecast_days=1"
        )
        weather_res = requests.get(weather_url, timeout=10).json()
        current = weather_res['current_weather']

        temp = current['temperature']
        windspeed = current['windspeed']
        code = current.get('weathercode', 0)
        condition = WEATHER_CODES.get(code, "Clear")

        # Get humidity from hourly (first value = current hour)
        humidity = weather_res.get('hourly', {}).get('relative_humidity_2m', [None])[0]
        feels_like = weather_res.get('hourly', {}).get('apparent_temperature', [None])[0]

        weather_text = (
            f"📍 {city_name}, {country}\n"
            f"🌡️ Temperature: {temp}°C"
            + (f" (feels like {feels_like}°C)" if feels_like else "") + "\n"
            f"🌤️ Condition: {condition}\n"
            f"💨 Wind: {windspeed} km/h"
            + (f"\n💧 Humidity: {humidity}%" if humidity else "")
        )

        return weather_text, None

    def handle(self, user_input):
        print(f"[WeatherAgent] Input: {user_input}")

        # Extract city
        city = self._extract_city(user_input)
        if not city:
            return "I couldn't figure out which city you meant. Try: 'weather in Delhi'"

        print(f"[WeatherAgent] City extracted: {city}")

        # Get real weather
        weather_text, error = self._get_weather(city)
        if error:
            return error

        return f"Here's the current weather:\n\n{weather_text}"
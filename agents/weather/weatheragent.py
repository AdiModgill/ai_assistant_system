import ollama
import requests
import json

def get_weather(city_name):
    # Step 1: Get coordinates for the city
    geo_url = f"https://geocoding-api.open-meteo.com/v1/search?name={city_name}&count=1&language=en&format=json"
    geo_res = requests.get(geo_url).json()

    if not geo_res.get('results'):
        return "Could not find coordinates for that city."

    lat = geo_res['results'][0]['latitude']
    lon = geo_res['results'][0]['longitude']

    # Step 2: Get weather data
    weather_url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current_weather=true"
    weather_res = requests.get(weather_url).json()

    current = weather_res['current_weather']
    return f"The current temperature in {city_name} is {current['temperature']}°C with a windspeed of {current['windspeed']} km/h."

def run_weather_agent(user_prompt):
    print(f"Agent is thinking about: {user_prompt}...")

    # Ask Llama 3 to extract the city name from the prompt
    response = ollama.chat(model='llama3:8b', messages=[          # <-- changed here
        {
            'role': 'system',
            'content': 'You are a helpful assistant. Extract only the city name from the user prompt. Return only the city name, nothing else.'
        },
        {
            'role': 'user',
            'content': user_prompt,
        },
    ])

    city = response['message']['content'].strip()
    weather_info = get_weather(city)

    # Final response generation
    final_response = ollama.chat(model='llama3:8b', messages=[    # <-- changed here
        {
            'role': 'system',
            'content': 'You are a friendly weather reporter. Use the provided data to answer the user.'
        },
        {
            'role': 'user',
            'content': f"User asked: {user_prompt}. Weather data: {weather_info}",
        },
    ])

    print("\nAI Agent:", final_response['message']['content'])

if __name__ == "__main__":
    user_input = input("Ask me about the weather in any city: ")
    run_weather_agent(user_input)

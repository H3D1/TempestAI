import requests
from flask import Flask, request, jsonify
import geocoder

app = Flask(__name__)

# Define the API keys for weather and holidays
WEATHER_API_KEY = "a134b189fda91998f757308c019ea4f3"
HOLIDAY_API_KEY = "f+x1TcSMIBurP7YC8pgjKw==8cCHKvn8VpJBWuG9"
GEMINI_API_KEY = "AIzaSyCpnZCSeIQKGnsBTiDW6ZMflvaOcX7RG4s"

@app.route('/recommend', methods=['POST'])
def recommend():
    # Extract data from the POST request
    user_input = request.json.get('input')
    latitude = request.json.get('latitude')
    longitude = request.json.get('longitude')

    # Get the weather data (you can use OpenWeatherMap or your preferred service)
    print(latitude, longitude)

    weather = get_weather(latitude, longitude)

    # Get the public holidays data for Tunisia
    holidays = get_public_holidays()

    # Based on the weather and holidays, return a recommendation
    recommendation = generate_recommendation(user_input, weather, holidays)
    
    # Return the recommendation as a JSON response
    return jsonify({'recommendation': recommendation})

def get_weather(latitude, longitude):
    # Fetch weather data from OpenWeatherMap (you'll use your actual weather API here)
    weather_url = f"http://api.openweathermap.org/data/2.5/weather?lat={latitude}&lon={longitude}&appid={WEATHER_API_KEY}"
    response = requests.get(weather_url)
    weather_data = response.json()
    
    # Extract the relevant weather information
    temperature = weather_data['main']['temp']
    weather_description = weather_data['weather'][0]['description']
    
    return {
        'temperature': temperature,
        'description': weather_description
    }

def get_public_holidays():
    # Fetch public holiday data for Tunisia in 2024
    holidays_url = "https://api.api-ninjas.com/v1/holidays?country=Tunisia&year=2024&type=public_holiday"
    headers = {
        "X-Api-Key": HOLIDAY_API_KEY
    }
    response = requests.get(holidays_url, headers=headers)
    holidays_data = response.json()
    
    # Extract holiday names and dates
    holidays = []
    for holiday in holidays_data:
        holidays.append({
            'name': holiday['name'],
            'date': holiday['date']
        })
    
    return holidays

def generate_recommendation(user_input, weather, holidays):
    # Example: Simple recommendation logic based on weather and holidays
    if "outdoor" in user_input and weather['description'] != "rain":
        return f"The weather is great for outdoor activities like hiking! The temperature is {weather['temperature']}°C."
    elif "holiday" in user_input and holidays:
        next_holiday = holidays[0]  # For simplicity, just pick the first holiday
        return f"Next holiday is {next_holiday['name']} on {next_holiday['date']}. It's a great day to relax!"
    else:
        return "The weather is nice. How about a walk in the park?"

if __name__ == '__main__':
    app.run(debug=True)

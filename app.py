import requests
from flask import Flask, request, jsonify
from datetime import datetime

app = Flask(__name__)

# API keys for weather and holiday services
WEATHER_API_KEY = "a134b189fda91998f757308c019ea4f3"
HOLIDAY_API_KEY = "f+x1TcSMIBurP7YC8pgjKw==8cCHKvn8VpJBWuG9"
EVENTBRITE_API_TOKEN = "5TFI2V3IH7DB6WVCOZ"
GEOCODIO_API_KEY = "46a4a7f33b66636a647a9fa7babafb6cac6c6aa"  # Replace with your actual Geocodio API key

@app.route('/recommend', methods=['POST'])
def recommend():
    try:
        data = request.json or request.get_json(force=True)
        address = data.get('address')  # Expecting address instead of latitude and longitude

        if not address:
            return jsonify({'error': 'Missing required fields in request'}), 400

        # Get latitude and longitude from Geocodio
        latitude, longitude = geocode_address(address)

        if latitude is None or longitude is None:
            return jsonify({'error': 'Geocoding failed'}), 500

        weather = get_weather(latitude, longitude)
        holidays = get_public_holidays()
        recommendation = generate_conversational_recommendation(weather, holidays, latitude, longitude)

        return jsonify({'recommendation': recommendation})

    except Exception as e:
        print(f"Error: {e}")
        return jsonify({'error': 'Internal server error'}), 500

def geocode_address(address):
    url = f"https://api.geocod.io/v1.7/geocode"
    params = {
        'q': address,
        'api_key': GEOCODIO_API_KEY
    }

    response = requests.get(url, params=params)
    
    if response.status_code == 200:
        data = response.json()
        if data['results']:
            # Get the first result
            location = data['results'][0]['location']
            return location['lat'], location['lng']
    
    print("Error fetching data from Geocodio:", response.status_code)
    return None, None

def get_weather(latitude, longitude):
    weather_url = f"http://api.openweathermap.org/data/2.5/weather?lat={latitude}&lon={longitude}&units=metric&appid={WEATHER_API_KEY}"
    response = requests.get(weather_url)
    
    if response.status_code == 200:
        weather_data = response.json()
        
        temperature = weather_data['main']['temp']
        weather_description = weather_data['weather'][0]['description']

        return {
            'temperature': temperature,
            'description': weather_description
        }
    
    print("Error fetching weather data:", response.status_code)
    return {}

def get_public_holidays():
    holidays_url = "https://api.api-ninjas.com/v1/holidays?country=Tunisia&year=2024&type=public_holiday"
    headers = {"X-Api-Key": HOLIDAY_API_KEY}
    
    response = requests.get(holidays_url, headers=headers)
    
    if response.status_code == 200:
        holidays_data = response.json()
        
        return [{'name': holiday['name'], 'date': holiday['date']} for holiday in holidays_data]
    
    print("Error fetching holidays:", response.status_code)
    return []

def seasonal_activity_recommendation(weather):
    season = determine_season()  
    if season == "winter":
        return "How about going skiing or visiting a local museum?"
    elif season == "spring":
        return "It's a great time for a picnic or a hike!"
    elif season == "summer":
        return "Consider going to the beach or enjoying some outdoor concerts."
    elif season == "fall":
        return "You might enjoy apple picking or visiting a fall festival."
    return ""

def determine_season():
    now = datetime.now()
    month = now.month
    day = now.day

    if (month == 12 and day >= 21) or (month <= 2) or (month == 3 and day < 20):
        return "winter"
    elif (month == 3 and day >= 20) or (month <= 5) or (month == 6 and day < 21):
        return "spring"
    elif (month == 6 and day >= 21) or (month <= 8) or (month == 9 and day < 22):
        return "summer"
    elif (month == 9 and day >= 22) or (month <= 11) or (month == 12 and day < 21):
        return "fall"
    
    return ""

def get_local_events(latitude, longitude):
    events_url = f"https://api.eventbrite.com/v3/events/search/?location.latitude={latitude}&location.longitude={longitude}&token={EVENTBRITE_API_TOKEN}"
    response = requests.get(events_url)
    
    if response.status_code == 200:
        events = response.json().get('events', [])
        return [{"name": event["name"]["text"], "date": event["start"]["local"]} for event in events]
    
    print("Error fetching local events:", response.status_code)
    return []

def get_nearby_attractions(latitude, longitude):
    # You can implement nearby attractions functionality here if needed.
    # For example, you could use another API to fetch nearby points of interest.
    
    # Placeholder for now; you can remove this function if not needed.
    return []

def generate_conversational_recommendation(weather, holidays, latitude, longitude):
    context = f"The weather is currently {weather['description']} with a temperature of {weather['temperature']}°C."
    
    # Seasonal activity recommendation
    seasonal_activity = seasonal_activity_recommendation(weather)

    recommendations = []
    
    if seasonal_activity:
        recommendations.append(seasonal_activity)

    local_events = get_local_events(latitude, longitude)

    if local_events:
        events_list = ", ".join([event['name'] for event in local_events])
        recommendations.append(f"Upcoming local events: {events_list}.")

    # Combine all recommendations into one message
    return " ".join(recommendations) if recommendations else context

if __name__ == '__main__':
    app.run(debug=True)
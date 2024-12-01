import requests
import spacy
import random
import numpy as np
from flask import Flask, request, jsonify
from datetime import datetime
from flask_cors import CORS
from sklearn.preprocessing import StandardScaler
from sklearn.neighbors import NearestNeighbors

# Load spaCy English language model
nlp = spacy.load("en_core_web_sm")

app = Flask(__name__)
CORS(app)

# API keys (Replace with your actual keys)
WEATHER_API_KEY = "a134b189fda91998f757308c019ea4f3"
GEOAPIFY_API_KEY = "4adf872c5b2a462b86453a37b2f39342"
FSQ_API_TOKEN = "fsq3vBaSTMcX5WQuXycdZRozX3PqRe+aadjnpLM3z+QzZto="

class RecommendationAI:
    def __init__(self):
        # Sample training data (synthetic for demonstration)
        # Features: [temperature, time_of_day, weather_type, user_mood]
        self.training_data = np.array([
            [10, 12, 0, 0],   # Cold morning, rainy, neutral mood
            [25, 15, 1, 1],   # Warm afternoon, sunny, happy mood
            [5, 20, 2, -1],   # Very cold evening, cloudy, sad mood
        ])
        
        # Corresponding recommendations
        self.recommendations = [
            ['Indoor museum', 'Warm cafe', 'Book reading'],
            ['Outdoor park', 'Photography', 'Picnic'],
            ['Indoor movie', 'Comfort food', 'Cozy restaurant']
        ]
        
        # Prepare the model
        self.scaler = StandardScaler()
        self.scaled_data = self.scaler.fit_transform(self.training_data)
        
        # K-Nearest Neighbors for recommendation
        self.model = NearestNeighbors(n_neighbors=2, algorithm='ball_tree')
        self.model.fit(self.scaled_data)
    
    def get_recommendation(self, current_features):
        """
        Get AI-powered recommendations based on current context
        
        Args:
            current_features (list): [temperature, time_of_day, weather_type, user_mood]
        
        Returns:
            list: Recommended activities
        """
        # Scale input features
        scaled_features = self.scaler.transform([current_features])
        
        # Find nearest neighbors
        distances, indices = self.model.kneighbors(scaled_features)
        
        # Collect recommendations from nearest neighbors
        ai_recommendations = []
        for idx in indices[0]:
            ai_recommendations.extend(self.recommendations[idx])
        
        return list(set(ai_recommendations))  # Remove duplicates

def extract_contextual_data(weather_description):
    """
    Extract contextual data (e.g., activities) from weather descriptions using spaCy.
    """
    doc = nlp(weather_description)
    activities = [token.text.lower() for token in doc if token.pos_ in ['NOUN', 'VERB']]
    return activities

def get_weather(latitude, longitude):
    weather_url = f"http://api.openweathermap.org/data/2.5/weather?lat={latitude}&lon={longitude}&units=metric&appid={WEATHER_API_KEY}"
    try:
        response = requests.get(weather_url)
        if response.status_code == 200:
            data = response.json()
            return {
                "temperature": round(data["main"]["temp"], 1),
                "description": data["weather"][0]["description"],
                "weather_main": data["weather"][0]["main"]
            }
    except Exception as e:
        print(f"Weather API error: {e}")
    return {}

def reverse_geocode(latitude, longitude):
    url = f"https://api.geoapify.com/v1/geocode/reverse"
    params = {
        'lat': latitude,
        'lon': longitude,
        'apiKey': GEOAPIFY_API_KEY
    }

    try:
        response = requests.get(url, params=params)
        
        if response.status_code == 200:
            data = response.json()
            if data.get('features'):
                details = data['features'][0]['properties']
                return {
                    'city': details.get('city', "Unknown City"),
                    'country': details.get("country", "Unknown Country"),
                    "formatted_address": details.get("formatted", "Unknown Location")
                }
    except Exception as e:
        print(f"Geocoding error: {e}")
    
    return {
        "city": "Unknown City",
        "country": "Unknown Country",
        "formatted_address": "Unknown Location"
    }

def get_nearby_attractions(latitude, longitude):
    """
    Fetch nearby attractions using Foursquare API and return them as a list.
    """
    foursquare_url = "https://api.foursquare.com/v3/places/search"
    headers = {
        "Accept": "application/json",
        "Authorization": FSQ_API_TOKEN
    }
    params = {
        "ll": f"{latitude},{longitude}",
        "radius": 5000,
        "limit": 5,
    }

    try:
        response = requests.get(foursquare_url, headers=headers, params=params)
        if response.status_code == 200:
            results = response.json().get('results', [])
            return [{"name": result["name"], "location": result["geocodes"]["main"]} for result in results]
    except Exception as e:
        print(f"Foursquare API error: {e}")
    return []

def generate_recommendations(weather, latitude, longitude):
    """
    Generate recommendations based on weather, location, and nearby attractions.
    """
    temperature = weather.get('temperature', 20)
    weather_main = weather.get('weather_main', 'Clear')

    # Extract activities based on weather description
    activities = extract_contextual_data(weather.get('description', ''))

    recommendations = []

    # Match activities based on the weather conditions
    if 'rain' in weather_main or 'storm' in weather_main:
        recommendations.extend(['Visit an indoor museum', 'Watch a movie'])
    elif 'sunny' in weather_main or 'clear' in weather_main:
        recommendations.extend(['Go for a walk in the park', 'Try outdoor photography'])

    # Add activities from the context (weather-based or user interests)
    for activity in activities:
        if 'park' in activity:
            recommendations.append("Visit a nearby park")
        elif 'museum' in activity:
            recommendations.append("Explore a local museum")
        elif 'restaurant' in activity:
            recommendations.append("Try a new restaurant")
        elif 'movie' in activity:
            recommendations.append("Watch a movie")

    # Fetch nearby attractions and add them to recommendations
    nearby_attractions = get_nearby_attractions(latitude, longitude)

    # Add nearby attractions as strings to recommendations
    if nearby_attractions:
        for attraction in nearby_attractions:
            name = attraction['name']
            recommendations.append(f"{name}")

    # Initialize AI Recommendation System
    recommendation_ai = RecommendationAI()
    
    # Prepare features for AI
    current_features = [
        temperature,  # temperature
        datetime.now().hour,  # time of day
        0 if 'rain' in weather_main.lower() else 1,  # weather type
        0  # neutral mood (could be expanded with more complex mood detection)
    ]
    
    # Get AI recommendations
    ai_recommendations = recommendation_ai.get_recommendation(current_features)
    
    # Combine existing and AI recommendations
    recommendations.extend(ai_recommendations)

    # Get the reverse geocoded location (address)
    location_info = reverse_geocode(latitude, longitude)

    return {
        'recommendations': list(set(recommendations)),  # Remove duplicates
        'nearby_attractions': nearby_attractions,
        'weather': weather,
        'location': location_info,
        'ai_insights': 'Recommendations enhanced with machine learning'
    }

@app.route('/recommend-dynamic', methods=['POST'])
def recommend_dynamic():
    """
    Endpoint that receives latitude and longitude and returns dynamic recommendations.
    """
    try:
        data = request.json
        latitude = data.get('latitude')
        longitude = data.get('longitude')

        if latitude is None or longitude is None:
            return jsonify({'error': 'Missing location data'}), 400

        # Get weather data
        weather = get_weather(latitude, longitude)

        if not weather:
            return jsonify({'error': 'Weather data could not be fetched'}), 500

        # Generate recommendations
        recommendations = generate_recommendations(weather, latitude, longitude)

        # Return recommendations
        return jsonify(recommendations)

    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
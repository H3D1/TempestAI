import requests
import spacy
import random
from flask import Flask, request, jsonify
from datetime import datetime
from flask_cors import CORS
from flask_mail import Mail, Message

# Load spaCy English language model
nlp = spacy.load("en_core_web_sm")

app = Flask(__name__)
CORS(app)

# Configure Flask-Mail
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'TempestAI700@gmail.com'  # Replace with your email
app.config['MAIL_PASSWORD'] = 'T3mpestA1'  # Replace with your password or use environment variables
mail = Mail(app)

# API keys for weather and holiday services
WEATHER_API_KEY = "a134b189fda91998f757308c019ea4f3"
HOLIDAY_API_KEY = "f+x1TcSMIBurP7YC8pgjKw==8cCHKvn8VpJBWuG9"
GEOAPIFY_API_KEY = "4adf872c5b2a462b86453a37b2f39342"

# Comprehensive activity database with detailed categorization
ACTIVITY_DATABASE = {
    'indoor': {
        'rainy': [
            'explore a local museum or art gallery', 
            'have a movie marathon with gourmet popcorn', 
            'try a new board game or puzzle', 
            'start an indoor gardening project'
        ],
        'cold': [
            'take a cooking class online', 
            'read a best-selling novel', 
            'learn a new skill on an educational platform', 
            'have a cozy tea and book afternoon'
        ]
    },
    'outdoor': {
        'warm': [
            'go for a scenic bike ride', 
            'explore a nearby hiking trail', 
            'have a picnic in a local park', 
            'try outdoor photography'
        ],
        'hot': [
            'visit a local water park', 
            'go early morning jogging', 
            'explore a botanical garden', 
            'do some sunrise yoga outdoors'
        ]
    },
    'social': [
        'attend a local community event', 
        'join a workshop or class', 
        'visit a farmers market', 
        'explore a local cafe or restaurant'
    ],
    'seasonal': {
        'winter': [
            'visit a holiday market', 
            'go ice skating', 
            'enjoy winter photography', 
            'attend a local winter festival'
        ],
        'summer': [
            'attend an outdoor concert', 
            'go beach or lake swimming', 
            'participate in community barbecue', 
            'explore local summer festivals'
        ]
    }
}

@app.route('/recommend', methods=['POST'])
def recommend():
    try:
        data = request.json
        if not data:
            data = request.get_json(force=True)

        print("Received data:", data)

        latitude = data.get('latitude')
        longitude = data.get('longitude')

        if latitude is None or longitude is None:
            return jsonify({'error': 'Missing required fields: latitude and longitude'}), 400

        address_details = reverse_geocode(latitude, longitude)
        
        weather = get_weather(latitude, longitude)
        
        recommendation = generate_nlp_recommendation(
            weather, 
            address_details['city'], 
            address_details['country']
        )

        return jsonify({
            'recommendation': recommendation,
            'location': address_details,
            'weather': weather
        })

    except Exception as e:
        print(f"Error in recommendation route: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/send-feedback', methods=['POST'])
def send_feedback():
    data = request.json
    feedback_type = data.get('feedback')

    msg_body = f"User Feedback: {feedback_type}"
    
    msg = Message("User Feedback", sender='TempestAI700@gmail.com', recipients=['bejaouimedhedi2@gmail.com'])
    
    # Send simple positive/negative feedback message
    if feedback_type == "positive feedback":
        msg.body = "Positive feedback received from user."
    else:
        msg.body = "Negative feedback received from user."

    try:
        mail.send(msg)
        return jsonify({'status': 'success'}), 200
    except Exception as e:
        print(f"Error sending email: {e}")
        return jsonify({'status': 'error', 'message': str(e)}), 500

def generate_nlp_recommendation(weather, city, country):
    temperature = weather.get('temperature', 20)
    description = weather.get('description', 'mild')
    
    temp_category = ('cold' if temperature < 10 else 
                     ('warm' if temperature < 25 else 
                      'hot'))
    
    selected_activities = []
    
    if temperature < 10 or description in ['rainy', 'stormy']:
        selected_activities.extend(ACTIVITY_DATABASE['indoor'].get(temp_category, []))
    
    if temperature >= 15 and description not in ['rainy', 'stormy']:
         selected_activities.extend(ACTIVITY_DATABASE['outdoor'].get(temp_category, []))
    
    season = determine_season()
    selected_activities.extend(ACTIVITY_DATABASE['seasonal'].get(season, []))
    selected_activities.extend(ACTIVITY_DATABASE['social'])
    
    unique_recommendations = random.sample(selected_activities, min(3, len(selected_activities)))
    
    recommendation_texts = ', '.join(unique_recommendations)
    recommendation_texts += f". Enjoy your time in {city}!"
     
    recommendation = (
        f"Location: {city}, {country}. "
        f"Temperature: {temperature}°C. "
        f"Weather: {description}. "
        f"Recommended Activities: {recommendation_texts}"
    )
    
    return recommendation

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

def get_weather(latitude, longitude):
     weather_url = f"http://api.openweathermap.org/data/2.5/weather?lat={latitude}&lon={longitude}&units=metric&appid={WEATHER_API_KEY}"
     
     try:
         response = requests.get(weather_url)
         
         if response.status_code == 200:
             weather_data = response.json()
             return {
                 "temperature": round(weather_data["main"]["temp"], 1),
                 "description": weather_data["weather"][0]["description"]
             }
     except Exception as e:
          print(f"Weather API error: {e}")
     
     return {}

def determine_season():
      now = datetime.now()
      month = now.month

      if month in [12, 1, 2]:
          return "winter"
      elif month in [3, 4, 5]:
          return "spring"
      elif month in [6, 7, 8]:
          return "summer"
      else:
          return "fall"

if __name__ == '__main__':
      app.run(host='0.0.0.0', port=5000, debug=True)
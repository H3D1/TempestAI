# Tempest[AI]

Tempest[AI] is a location-based recommendation app that combines weather data, geolocation, nearby attractions, and a simple machine-learning recommendation engine to suggest activities for the user.

## Overview

The project consists of:
- A Flask backend in app.py that fetches weather and location data and generates recommendations.
- A frontend in index.html that requests the user’s location and displays weather, attractions, and activity suggestions.
- A lightweight machine-learning component that uses a K-Nearest Neighbors model to enhance recommendations.

## Features

- Detects the user's current location
- Fetches real-time weather information
- Reverse-geocodes coordinates into a readable address
- Retrieves nearby attractions using the Foursquare Places API
- Produces AI-style recommendations based on weather and time context
- Displays results in a simple web interface

## Tech Stack

- Python
- Flask
- scikit-learn
- spaCy
- Requests
- HTML/CSS/JavaScript
- Tailwind CSS
- Leaflet.js

## Project Structure

- app.py — Flask server and recommendation logic
- index.html — frontend UI and map rendering
- requirements.txt — Python dependencies
- package.json — frontend package metadata
- ratings.txt — existing data file

## Setup Instructions

### 1. Clone or open the project

```bash
cd TempestAI
```

### 2. Create and activate a Python virtual environment

On Windows:

```bash
python -m venv .venv
.venv\Scripts\activate
```

### 3. Install Python dependencies

```bash
pip install -r requirements.txt
```

### 4. Download the spaCy language model

```bash
python -m spacy download en_core_web_sm
```

## Running the Application

### Start the backend

```bash
python app.py
```

The Flask server will start on:

```text
http://localhost:5000
```

### Open the frontend

Open the index.html file in your browser, or serve the project with a simple local server.

Example:

```bash
python -m http.server 8000
```

Then visit:

```text
http://localhost:8000/index.html
```

## API Endpoint

The backend exposes this endpoint:

- POST /recommend-dynamic

Request body:

```json
{
  "latitude": 40.7128,
  "longitude": -74.0060
}
```

Response includes:
- recommendations
- nearby_attractions
- weather
- location
- ai_insights

## Notes

- The app currently uses hardcoded API keys in app.py for demo purposes. For production use, move these values to environment variables.
- The recommendation engine is intentionally simple and intended for demonstration rather than production-grade personalization.

## License

This project is provided as-is for educational and demonstration purposes.

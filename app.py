import matplotlib
matplotlib.use('Agg')
from flask import Flask, render_template, request
import requests
import matplotlib.pyplot as plt
from datetime import datetime
import os

app = Flask(__name__)

API_KEY = 'b3e39923ffdefcd9343d76d2f3bec139'
BASE_URL_CURRENT = 'http://api.openweathermap.org/data/2.5/weather'
BASE_URL_FORECAST = 'http://api.openweathermap.org/data/2.5/forecast'

# Mapping of weather conditions to corresponding icon files
condition_icons = {
    "Clear": "clear.png",
    "Clouds": "clouds.png",
    "Rain": "rain.png",
    "Drizzle": "drizzle.png",
    "Thunderstorm": "thunderstorm.png",
    "Snow": "snow.png",
    "Mist": "mist.png",
    "Smoke": "smoke.png",
    "Haze": "haze.png",
    "Fog": "fog.png",
    "Sand": "sand.png",
    "Dust": "dust.png",
    "Ash": "ash.png",
    "Squalls": "squalls.png",
    "Tornado": "tornado.png"
}

def get_icon_for_condition(condition):
    for key in condition_icons:
        if key.lower() in condition.lower():
            return f"/static/icons/{condition_icons[key]}"
    return "/static/icons/default.png"  

def get_weather_data(city_name):
    # Fetch current weather data
    current_weather_params = {
        'q': city_name,
        'appid': API_KEY,
        'units': 'metric'
    }
    response_current = requests.get(BASE_URL_CURRENT, params=current_weather_params)
    current_data = response_current.json()
    
    # Fetch 5-day forecast data
    forecast_params = {
        'q': city_name,
        'appid': API_KEY,
        'units': 'metric'
    }
    response_forecast = requests.get(BASE_URL_FORECAST, params=forecast_params)
    forecast_data = response_forecast.json()
    
    return current_data, forecast_data

def plot_forecast(forecast_data):
    dates = []
    temperatures = []
    
    # Process forecast data
    for item in forecast_data['list']:
        date = datetime.fromtimestamp(item['dt'])
        temp = item['main']['temp']
        dates.append(date)
        temperatures.append(temp)
    
    
    plt.figure(figsize=(10, 5))
    plt.plot(dates, temperatures, marker='o', linestyle='-', color='b')
    plt.title("5-Day Temperature Forecast")
    plt.xlabel("Date and Time")
    plt.ylabel("Temperature (°C)")
    plt.xticks(rotation=45)
    plt.tight_layout()
    
    # Save plot to static folder
    plot_path = os.path.join('static', 'plot.png')
    plt.savefig(plot_path)
    plt.close()
    return plot_path

@app.route("/", methods=["GET", "POST"])
def index():
    weather_data = []
    
    if request.method == "POST":
        cities = request.form.get("city").split(",")
        
        for city in cities:
            current_data, forecast_data = get_weather_data(city.strip())
            
            if current_data.get("cod") != 200:
                weather_info = {"error": current_data.get("message", "City not found")}
            else:
                condition = current_data['weather'][0]['description'].title()
                icon_path = get_icon_for_condition(condition)
                
                # Extract and format weather data
                weather_info = {
                    "city": city.strip().title(),
                    "temperature": current_data['main']['temp'],
                    "condition": condition,
                    "humidity": current_data['main']['humidity'],
                    "wind_speed": current_data['wind']['speed'],
                    "icon_path": icon_path
                }
                plot_path = plot_forecast(forecast_data)
                
                weather_data.append((weather_info, plot_path))  # Tuple with info and plot path
    
    return render_template("index.html", weather_data=weather_data)

if __name__ == "__main__":
    app.run(debug=True)

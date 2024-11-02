import matplotlib
matplotlib.use('Agg')
from flask import Flask, render_template, request, redirect, url_for
import requests
import matplotlib.pyplot as plt
from datetime import datetime
import io
import os
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas

app = Flask(__name__)

API_KEY = 'b3e39923ffdefcd9343d76d2f3bec139'
BASE_URL_CURRENT = 'http://api.openweathermap.org/data/2.5/weather'
BASE_URL_FORECAST = 'http://api.openweathermap.org/data/2.5/forecast'

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
    
    # Plotting
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
    weather_info = None
    plot_path = None
    
    if request.method == "POST":
        city = request.form.get("city")
        current_data, forecast_data = get_weather_data(city)
        
        if current_data.get("cod") != 200:
            weather_info = {"error": current_data.get("message", "City not found")}
        else:
            # Extract current weather data
            weather_info = {
                "city": city.title(),
                "temperature": current_data['main']['temp'],
                "condition": current_data['weather'][0]['description'].title(),
                "humidity": current_data['main']['humidity'],
                "wind_speed": current_data['wind']['speed']
            }
            # Generate forecast plot
            plot_path = plot_forecast(forecast_data)
    
    return render_template("index.html", weather_info=weather_info, plot_path=plot_path)

if __name__ == "__main__":
    app.run(debug=True)

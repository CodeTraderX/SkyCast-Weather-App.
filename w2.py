import os
import requests
import tkinter as tk
from tkinter import messagebox
from tkinter import ttk
from PIL import Image, ImageTk
from io import BytesIO
import datetime

API_KEY = os.getenv('WEATHER_API_KEY', 'your api key')
BASE_URL = 'http://api.openweathermap.org/data/2.5/forecast'
CURRENT_WEATHER_URL = 'http://api.openweathermap.org/data/2.5/weather'

def get_forecast(city):
    params = {'q': city, 'appid': API_KEY, 'units': 'metric'}
    try:
        response = requests.get(BASE_URL, params=params)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        messagebox.showerror("Error", f"Failed to retrieve data: {e}")
        return None

def get_current_weather(city):
    params = {'q': city, 'appid': API_KEY, 'units': 'metric'}
    try:
        response = requests.get(CURRENT_WEATHER_URL, params=params)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        messagebox.showerror("Error", f"Failed to retrieve current weather: {e}")
        return None

def parse_forecast_data(data):
    forecast_list = []
    try:
        for entry in data['list'][:5]:  # Limit to first 5 entries
            date_time = entry['dt_txt']
            temp = entry['main']['temp']
            humidity = entry['main']['humidity']
            description = entry['weather'][0]['description']
            icon = entry['weather'][0]['icon']
            forecast_list.append((date_time, temp, humidity, description, icon))
    except KeyError:
        messagebox.showerror("Error", "Unexpected data format received.")
    return forecast_list

def get_icon(icon_code):
    try:
        icon_url = f"http://openweathermap.org/img/wn/{icon_code}@2x.png"
        response = requests.get(icon_url)
        response.raise_for_status()
        img_data = response.content
        img = Image.open(BytesIO(img_data)).resize((50, 50))
        return ImageTk.PhotoImage(img)
    except requests.RequestException:
        return ImageTk.PhotoImage(Image.new("RGB", (50, 50), color="gray"))

def display_forecast():
    city = city_entry.get()
    current_weather = get_current_weather(city)
    forecast_data = get_forecast(city)
    
    if current_weather:
        temp = current_weather['main']['temp']
        description = current_weather['weather'][0]['description']
        icon = get_icon(current_weather['weather'][0]['icon'])
        current_weather_label.config(text=f"Current Temp: {temp}°C\n{description}", image=icon, compound='left')
        current_weather_label.image = icon
    
    if forecast_data:
        forecast_list = parse_forecast_data(forecast_data)
        for widget in forecast_frame.winfo_children():
            widget.destroy()
        for forecast in forecast_list:
            date_time, temp, humidity, description, icon_code = forecast
            icon = get_icon(icon_code)
            frame = ttk.Frame(forecast_frame)
            frame.pack(pady=5, fill='x')
            icon_label = ttk.Label(frame, image=icon)
            icon_label.image = icon
            icon_label.pack(side='left', padx=10)
            text_label = ttk.Label(frame, text=f"{date_time}\nTemp: {temp}°C\nHumidity: {humidity}%\n{description}", anchor='w')
            text_label.pack(side='left', padx=10)

root = tk.Tk()
root.title("SkyCast-Weather-App")
root.geometry("400x550")
root.configure(bg='#87CEEB')  # Light blue background
style = ttk.Style()
style.theme_use("clam")

header_frame = ttk.Frame(root, padding=10, style='TFrame')
header_frame.pack(fill='x')

time_label = ttk.Label(header_frame, text=datetime.datetime.now().strftime("%m-%d-%y %H:%M:%S"), font=("Arial", 10))
time_label.pack(side='right', padx=10)

def update_time():
    time_label.config(text=datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    root.after(1000, update_time)
update_time()

input_frame = ttk.Frame(root, padding=10)
input_frame.pack(fill='x')
ttk.Label(input_frame, text="Enter City:").grid(row=0, column=0, padx=5, pady=5)
city_entry = ttk.Entry(input_frame)
city_entry.grid(row=0, column=1, padx=5, pady=5)
ttk.Button(input_frame, text="Get Forecast", command=display_forecast).grid(row=0, column=2, padx=5, pady=5)

current_weather_label = ttk.Label(root, text="", font=("Arial", 12), background='#87CEEB')
current_weather_label.pack(pady=10)

forecast_frame = ttk.Frame(root, padding=10)
forecast_frame.pack(fill='both', expand=True)

root.mainloop()

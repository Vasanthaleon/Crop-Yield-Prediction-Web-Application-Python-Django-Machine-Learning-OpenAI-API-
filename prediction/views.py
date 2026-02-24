from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User

from .models import Prediction

import os
import joblib
import pandas as pd
import requests

from openai import OpenAI

# --------------------------------------------------
# BASE DIRECTORY
# --------------------------------------------------
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# --------------------------------------------------
# LOAD ML MODEL & ENCODERS
# --------------------------------------------------
model = joblib.load(os.path.join(BASE_DIR, 'ml_model/crop_yield_model.pkl'))
le_state = joblib.load(os.path.join(BASE_DIR, 'ml_model/state_encoder.pkl'))
le_crop = joblib.load(os.path.join(BASE_DIR, 'ml_model/crop_encoder.pkl'))
le_season = joblib.load(os.path.join(BASE_DIR, 'ml_model/season_encoder.pkl'))

# --------------------------------------------------
# API KEYS (PASTE YOUR KEYS)
# --------------------------------------------------
WEATHER_API_KEY = 
AI_API_KEY =

client = OpenAI(api_key=AI_API_KEY)

# --------------------------------------------------
# WEATHER FUNCTION
# --------------------------------------------------
def get_weather(city):
    url = f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid={WEATHER_API_KEY}&units=metric"
    data = requests.get(url).json()

    temperature = data['main']['temp']
    rainfall = data.get('rain', {}).get('1h', 0)

    return temperature, rainfall

# --------------------------------------------------
# AI SUMMARY FUNCTION (REAL AI)
# --------------------------------------------------
def generate_ai_summary(context):
    prompt = f"""
    You are an agriculture expert.

    Using the data below, generate a short, clear,
    farmer-friendly explanation of the crop yield prediction.

    Data:
    {context}

    Instructions:
    - 2 to 4 sentences
    - Natural language
    - Mention yield quality, soil and weather
    """

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "user", "content": prompt}
        ],
        temperature=0.7
    )

    return response.choices[0].message.content.strip()

# --------------------------------------------------
# AUTH VIEWS
# --------------------------------------------------
def login_view(request):
    if request.method == "POST":
        user = authenticate(
            username=request.POST['username'],
            password=request.POST['password']
        )
        if user:
            login(request, user)
            return redirect('home')
    return render(request, 'login.html')


def register_view(request):
    if request.method == "POST":
        User.objects.create_user(
            username=request.POST['username'],
            password=request.POST['password']
        )
        return redirect('login')
    return render(request, 'register.html')


def logout_view(request):
    logout(request)
    return redirect('login')

# --------------------------------------------------
# MAIN PREDICTION VIEW
# --------------------------------------------------
@login_required
def index(request):
    result = None
    ai_summary = None
    temp = rain = None
    error = None

    if request.method == "POST":
        try:
            city = request.POST['city']
            state = request.POST['state']
            crop = request.POST['crop']
            season = request.POST['season']

            area = float(request.POST['area'])
            soil_ph = float(request.POST['soil_ph'])
            nitrogen = float(request.POST['nitrogen'])
            phosphorus = float(request.POST['phosphorus'])
            potassium = float(request.POST['potassium'])

            temp, rain = get_weather(city)

            input_data = pd.DataFrame([{
                "State": le_state.transform([state])[0],
                "Crop": le_crop.transform([crop])[0],
                "Season": le_season.transform([season])[0],
                "Area": area,
                "Rainfall": rain,
                "Temperature": temp,
                "Soil_pH": soil_ph,
                "Nitrogen": nitrogen,
                "Phosphorus": phosphorus,
                "Potassium": potassium
            }])

            result = round(model.predict(input_data)[0], 2)

            # Save to DB
            Prediction.objects.create(
                user=request.user,
                city=city,
                state=state,
                crop=crop,
                season=season,
                area=area,
                temperature=temp,
                rainfall=rain,
                soil_ph=soil_ph,
                nitrogen=nitrogen,
                phosphorus=phosphorus,
                potassium=potassium,
                predicted_yield=result
            )

            # AI CONTEXT
            context = f"""
            State: {state}
            Crop: {crop}
            Season: {season}
            Predicted Yield: {result} tons per hectare
            Soil pH: {soil_ph}
            Nitrogen: {nitrogen}
            Rainfall: {rain}
            Temperature: {temp}
            """

            ai_summary = generate_ai_summary(context)

        except Exception as e:
            error = str(e)

    return render(request, 'index.html', {
        'result': result,
        'ai_summary': ai_summary,
        'error': error
    })

# --------------------------------------------------
# HISTORY
# --------------------------------------------------
@login_required
def history(request):
    data = Prediction.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'history.html', {'data': data})

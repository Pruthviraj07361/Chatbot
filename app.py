import os
from flask import Flask, render_template, request, jsonify
import json
import requests
import google.generativeai as genai

# 🔐 Load API keys
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
WEATHER_API_KEY = os.getenv("WEATHER_API_KEY")

# 🤖 Configure Gemini
genai.configure(api_key=GEMINI_API_KEY)

app = Flask(__name__)

# 📂 Load intents (optional if used)
with open("intents.json") as file:
    intents = json.load(file)


# 🤖 Gemini response
def get_ai_response(user_input):
    try:
        model = genai.GenerativeModel("gemini-1.5-flash")
        response = model.generate_content(user_input)
        return response.text
    except Exception as e:
        print("Gemini Error:", e)
        return "⚠️ AI not available right now."


# 🌦 WEATHER FUNCTION
def get_weather(city):
    try:
        url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={WEATHER_API_KEY}&units=metric"
        res = requests.get(url).json()

        return f"{city}: {res['main']['temp']}°C, {res['weather'][0]['description']}"
    except:
        return "⚠️ Unable to fetch weather."


# 💱 CURRENCY FUNCTION
def get_currency(amount, from_curr, to_curr):
    try:
        url = f"https://api.exchangerate-api.com/v4/latest/{from_curr}"
        data = requests.get(url).json()

        rate = data["rates"].get(to_curr)

        if not rate:
            return "Invalid currency"

        result = amount * rate
        return f"{amount} {from_curr} = {round(result, 2)} {to_curr}"
    except:
        return "⚠️ Currency service error."


# 🧠 MAIN CHATBOT LOGIC
def get_response(user_input):
    text = user_input.lower().strip()

    # 🌦 Weather
    if "weather" in text:
        words = text.split()
        if "in" in words:
            city = words[words.index("in") + 1]
            return get_weather(city)
        return "Use: weather in Ahmedabad"

    # 💱 Currency
    if "convert" in text:
        try:
            words = text.split()
            amount = float(words[1])
            from_curr = words[2].upper()
            to_curr = words[4].upper()
            return get_currency(amount, from_curr, to_curr)
        except:
            return "Use: convert 100 USD to INR"

    # Basic replies
    if any(word in text for word in ["hi", "hello"]):
        return "Hello! I am your AI assistant 🤖"

    if "bye" in text:
        return "Goodbye! 👋"

    # 🤖 Gemini fallback
    return get_ai_response(user_input)


# 🌐 Home
@app.route("/")
def home():
    return render_template("index.html")


# 💬 Chat
@app.route("/chat", methods=["POST"])
def chat():
    user_input = request.json["message"]
    response = get_response(user_input)
    return jsonify({"response": response})


# 🌦 Weather API
@app.route("/weather")
def weather():
    city = request.args.get("city")

    try:
        url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={WEATHER_API_KEY}&units=metric"
        data = requests.get(url).json()

        return jsonify({
            "temp": data["main"]["temp"],
            "description": data["weather"][0]["description"]
        })
    except:
        return jsonify({"error": "Weather error"})


# 💱 Currency API
@app.route("/currency")
def currency():
    try:
        amount = float(request.args.get("amount"))
        from_curr = request.args.get("from").upper()
        to_curr = request.args.get("to").upper()

        url = f"https://api.exchangerate-api.com/v4/latest/{from_curr}"
        data = requests.get(url).json()

        rate = data["rates"].get(to_curr)

        if not rate:
            return jsonify({"error": "Invalid currency"})

        result = amount * rate

        return jsonify({"result": round(result, 2)})

    except Exception as e:
        print("Currency Error:", e)
        return jsonify({"error": "Something went wrong"})


# ▶️ RUN
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
"""
chat_handler.py - Chatbot Logic Layer
=======================================
This module contains the actual chatbot intelligence.
Currently uses rule-based responses, but can be swapped for:
- OpenAI GPT API
- Anthropic Claude API
- Local HuggingFace model

This is the "Model Layer" of our MLOps system.
"""

import os
import re
import json
import random
from datetime import datetime

# ─────────────────────────────────────────────
# Rule-Based Response Engine
# ─────────────────────────────────────────────

# Define response rules as (pattern, response_list) pairs
RESPONSE_RULES = [
    # Greetings
    (r"\b(hi|hello|hey|howdy|greetings)\b",
     ["Hello! How can I help you today? 😊",
      "Hi there! What's on your mind?",
      "Hey! Great to see you. What can I do for you?"]),

    # Farewells
    (r"\b(bye|goodbye|see you|later|ciao|farewell)\b",
     ["Goodbye! Have a wonderful day! 👋",
      "See you later! Feel free to come back anytime.",
      "Bye! Take care! 😊"]),

    # How are you
    (r"\b(how are you|how do you do|how's it going|what's up)\b",
     ["I'm just a bot, but I'm running great! 🤖 How can I help you?",
      "All systems operational! How about you?",
      "Doing well, thanks for asking! What can I do for you?"]),

    # Name questions
    (r"\b(your name|who are you|what are you)\b",
     ["I'm ChatBot v1.0 — your AI assistant! 🤖",
      "I'm an AI chatbot built with FastAPI and React.",
      "Call me ChatBot! I'm here to help you."]),

    # Help requests
    (r"\b(help|assist|support|can you)\b",
     ["Sure! I can answer questions, have conversations, and more. What do you need?",
      "Of course! Tell me what you need help with.",
      "I'm here to help! What's your question?"]),

    # Weather (demonstrate API integration potential)
    (r"\b(weather|temperature|forecast|rain|sunny)\b",
     ["I don't have live weather data, but you can check weather.com! 🌤️",
      "For real-time weather, try a weather app. I'm a general chatbot!",
      "Weather updates require a live API. Try Google Weather! ⛅"]),

    # Math
    (r"\b(calculate|math|add|subtract|multiply|divide|\d+\s*[\+\-\*\/]\s*\d+)\b",
     ["I can do basic math! Try typing something like '5 + 3'.",
      "Math time! 🧮 What calculation do you need?",
      "Numbers are fun! What do you want to calculate?"]),

    # Jokes
    (r"\b(joke|funny|laugh|humor|tell me something)\b",
     ["Why did the programmer quit? Because they didn't get arrays! 😄",
      "What do you call a fish without eyes? A fsh! 🐟",
      "Why is Python the best language? Because it's the only one that 'herds' bugs! 🐍"]),

    # AI/Tech questions
    (r"\b(ai|artificial intelligence|machine learning|ml|deep learning)\b",
     ["AI is fascinating! This chatbot itself is built with ML principles. 🧠",
      "Machine Learning powers modern AI systems. Want to learn more?",
      "Great question! AI/ML is a huge field. Ask me something specific!"]),

    # Thanks
    (r"\b(thank you|thanks|thx|appreciate)\b",
     ["You're welcome! 😊",
      "Happy to help! Is there anything else?",
      "Anytime! That's what I'm here for! 🤖"]),
]

# ─────────────────────────────────────────────
# Simple Math Evaluator (safe)
# ─────────────────────────────────────────────

def try_math_eval(message: str) -> str | None:
    """
    Safely evaluate simple math expressions.
    Example: "what is 5 + 3?" → "8"
    """
    # Extract a math expression
    expr = re.search(r"\d+\s*[\+\-\*\/]\s*\d+", message)
    if expr:
        try:
            result = eval(expr.group())  # Safe: only matches numbers + operators
            return f"The answer is: **{result}** 🧮"
        except:
            pass
    return None


# ─────────────────────────────────────────────
# Main Response Function
# ─────────────────────────────────────────────

def get_bot_response(user_message: str) -> str:
    """
    Main function: takes user message → returns bot response.

    Priority order:
    1. Math evaluation (if it's a math expression)
    2. Rule-based pattern matching
    3. LLM API (if OPENAI_API_KEY is set)
    4. Default fallback
    """
    message_lower = user_message.lower().strip()

    # Priority 1: Check if it's a math expression
    math_result = try_math_eval(message_lower)
    if math_result:
        return math_result

    # Priority 2: Rule-based matching
    for pattern, responses in RESPONSE_RULES:
        if re.search(pattern, message_lower):
            return random.choice(responses)

    # Priority 3: Try OpenAI if API key is configured
    openai_key = os.getenv("OPENAI_API_KEY", "")
    if openai_key and openai_key != "your_openai_key_here":
        try:
            return call_openai_api(user_message, openai_key)
        except Exception as e:
            print(f"OpenAI API error: {e}")

    # Priority 4: Default fallback
    fallback_responses = [
        f"Interesting! You said: '{user_message}'. I'm still learning! 🤔",
        "That's a great question! I'm a simple bot and still improving.",
        "I'm not sure how to respond to that yet. Try asking something else!",
        "Hmm, I'll need to think about that one. Ask me something else! 🤖",
    ]
    return random.choice(fallback_responses)


def call_openai_api(message: str, api_key: str) -> str:
    """
    Call OpenAI ChatGPT API.
    This is only used if OPENAI_API_KEY is set in .env

    Replace this with any LLM API (Anthropic, Cohere, etc.)
    """
    import urllib.request

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }

    payload = json.dumps({
        "model": "gpt-3.5-turbo",
        "messages": [
            {"role": "system", "content": "You are a helpful chatbot assistant."},
            {"role": "user", "content": message}
        ],
        "max_tokens": 200
    }).encode("utf-8")

    req = urllib.request.Request(
        "https://api.openai.com/v1/chat/completions",
        data=payload,
        headers=headers,
        method="POST"
    )

    with urllib.request.urlopen(req, timeout=10) as response:
        data = json.loads(response.read())
        return data["choices"][0]["message"]["content"]

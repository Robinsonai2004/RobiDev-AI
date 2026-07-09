"""
RobiDev AI - Intent Data
v0.3 Step 2: keyword-based intents for natural conversation variety.
Add new intents here without touching matching logic in intent_matcher.py.
NOTE: "your name" and "how are you" are handled directly in chatbot.py
already - they are intentionally NOT duplicated here.
"""

import random

INTENTS = {
    "greeting_hello": {
        "keywords": ["hello", "hi", "hey", "hi there", "hello there"],
        "responses": [
            "Hey! Nice to see you.",
            "Hello! How can I help today?",
            "Hi there!",
            "Great to see you again.",
        ],
    },
    "greeting_howareyou_variants": {
        "keywords": ["how are things", "how's it going", "hows it going",
                      "how you doing", "how do you do"],
        "responses": [
            "I'm doing well!",
            "Everything is going smoothly.",
        ],
    },
    "greeting_whatsup": {
        "keywords": ["what's up", "whats up", "wassup", "sup"],
        "responses": ["Not much! Ready to help you."],
    },
    "greeting_morning": {
        "keywords": ["good morning"],
        "responses": ["Good morning! Hope you have an amazing day."],
    },
    "greeting_afternoon": {
        "keywords": ["good afternoon"],
        "responses": ["Good afternoon!"],
    },
    "greeting_evening": {
        "keywords": ["good evening"],
        "responses": ["Good evening!"],
    },
    "greeting_night": {
        "keywords": ["good night", "goodnight"],
        "responses": ["Good night! Sleep well."],
    },
    "thanks": {
        "keywords": ["thanks", "thank you", "thx", "appreciate it"],
        "responses": ["You're welcome!", "Anytime!"],
    },
    "farewell": {
        "keywords": ["bye", "goodbye", "see you", "see ya", "catch you later"],
        "responses": ["Goodbye! See you again.", "Take care!"],
    },
}


def get_response_for_intent(intent_name: str) -> str:
    """Pick a random response for a given intent name."""
    return random.choice(INTENTS[intent_name]["responses"])

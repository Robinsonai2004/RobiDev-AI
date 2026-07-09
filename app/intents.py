"""
RobiDev AI - Intent Data
v0.3 Step 3: keyword-based intents for natural conversation variety.

HOW TO ADD A NEW INTENT:
1. Add a new key to INTENTS below, e.g. "joke": {...}
2. Give it a "keywords" list (phrases that should trigger it)
3. Give it a "responses" list (one or more possible replies)
That's it - no changes needed in chatbot.py or intent_matcher.py.

NOTE: "hello"/"hi" greetings are handled specially in chatbot.py
(they need access to memory for personalization), but they still
live here so their response variety is reusable.
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
    "wellbeing": {
        "keywords": ["how are you", "how are things", "how's it going",
                      "hows it going", "how you doing", "how do you do"],
        "responses": [
            "I'm doing well!",
            "Everything is going smoothly.",
            "I'm just code, but I'm running well!",
            "Doing great, thanks for asking!",
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
    "identity": {
        "keywords": ["your name", "who are you"],
        "responses": [
            "I'm RobiDev AI, your assistant.",
            "You can call me RobiDev AI!",
        ],
    },
    "capabilities": {
        "keywords": ["what can you do", "what do you do", "help"],
        "responses": [
            "I can chat with you, remember your name, and respond to common questions!",
            "Right now I can hold a conversation and remember who you are. More features are on the way!",
        ],
    },
    "creator": {
        "keywords": ["who made you", "who created you", "who built you"],
        "responses": [
            "I was built by Robinson as part of the RobiDev AI open-source project.",
            "Robinson created me! You can find the project on GitHub.",
        ],
    },
}


def get_response_for_intent(intent_name: str) -> str:
    """Pick a random response for a given intent name."""
    return random.choice(INTENTS[intent_name]["responses"])

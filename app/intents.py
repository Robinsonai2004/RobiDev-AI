"""
RobiDev AI - Intent Data
v0.3 Step 3: keyword-based intents for natural conversation variety.
v0.4 Step 2: added optional response-repetition avoidance and "expanded"
follow-up responses (used when the user says "tell me more").

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
            "Hello! How can I help you today?",
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
        "expanded": [
            "I'm a chatbot built in Python, running right here in Termux on Robinson's phone. I can chat, remember your name, and hold a conversation!",
        ],
    },
    "capabilities": {
        "keywords": ["what can you do", "what do you do", "help"],
        "responses": [
            "I can chat with you, remember your name, and respond to common questions!",
            "Right now I can hold a conversation and remember who you are. More features are on the way!",
        ],
        "expanded": [
            "More specifically: I can learn and remember your name, forget everything if you ask me to, recognize greetings, and keep track of what we were just talking about so you can ask follow-up questions like 'tell me more'.",
        ],
    },
    "creator": {
        "keywords": ["who made you", "who created you", "who built you"],
        "responses": [
            "I was built by Robinson as part of the RobiDev AI open-source project.",
            "Robinson created me! You can find the project on GitHub.",
        ],
        "expanded": [
            "The project is open-source and hosted at github.com/Robinsonai2004/RobiDev-AI, built step by step directly from a Termux terminal on Android.",
        ],
    },
}


def get_response_for_intent(intent_name: str, avoid: str = None) -> str:
    """
    Pick a response for a given intent. If 'avoid' is given and the intent
    has more than one possible response, tries not to repeat that exact
    response back-to-back. Returns None if the intent doesn't exist.
    """
    data = INTENTS.get(intent_name)
    if not data:
        return None

    responses = data["responses"]
    if avoid and len(responses) > 1:
        choices = [r for r in responses if r != avoid]
        if choices:
            return random.choice(choices)

    return random.choice(responses)


def get_expanded_response_for_intent(intent_name: str):
    """
    Pick a "tell me more" style follow-up response for a given intent,
    if one exists. Returns None if the intent has no expanded content.
    """
    data = INTENTS.get(intent_name)
    if not data:
        return None

    expanded = data.get("expanded")
    if not expanded:
        return None

    return random.choice(expanded)

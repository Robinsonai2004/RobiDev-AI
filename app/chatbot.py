"""
RobiDev AI - Chatbot Logic
v0.3: Rule-based responses, now with basic memory support
(remembers the user's name across sessions) and improved
intro-phrase detection.
v0.3 Step 2: added flexible keyword-based intent matching for
greetings, thanks, and farewells - with response variety.
"""

from intent_matcher import match_intent
from intents import get_response_for_intent


def get_response(user_input: str, memory: dict) -> str:
    text = user_input.lower()

    # --- Learn the user's name from several common phrasings ---
    direct_triggers = ["my name is", "call me", "you can call me"]
    guarded_triggers = ["i am", "i'm"]

    non_name_words = {
        "hungry", "tired", "fine", "good", "okay", "ok", "doing",
        "not", "just", "here", "sorry", "happy", "sad", "busy",
        "back", "done", "ready", "confused", "bored", "excited"
    }

    name = None

    for trigger in direct_triggers:
        idx = text.find(trigger)
        if idx != -1:
            remainder = user_input[idx + len(trigger):].strip()
            if remainder:
                name = remainder.split(" ")[0]
            break

    if name is None:
        for trigger in guarded_triggers:
            idx = text.find(trigger)
            if idx != -1:
                remainder = user_input[idx + len(trigger):].strip()
                if remainder:
                    candidate = remainder.split(" ")[0]
                    if candidate.lower().strip(".,!?") not in non_name_words:
                        name = candidate
                break

    if name:
        name = name.strip(".,!?").capitalize()
        memory["user_name"] = name
        return f"Nice to meet you, {name}! I'll remember that."

    # --- Personalized greeting if we already know their name ---
    if "hello" in text or "hi" in text:
        if memory.get("user_name"):
            return f"Hello {memory['user_name']}! How can I help you today?"
        # Don't know their name yet: use varied greeting + ask for name
        varied = get_response_for_intent("greeting_hello")
        return f"{varied} What's your name?"

    elif "your name" in text:
        return "I'm RobiDev AI, your assistant."

    elif "how are you" in text:
        return "I'm just code, but I'm running well!"

    # --- Flexible intent matching (thanks, farewells, other greetings) ---
    intent_reply = match_intent(user_input)
    if intent_reply:
        return intent_reply

    return "I heard you, but I don't have a smart reply for that yet."

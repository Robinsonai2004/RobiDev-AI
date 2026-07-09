"""
RobiDev AI - Chatbot Logic
v0.4 Step 1: added memory reset ("forget me") support and basic
input normalization (extra whitespace, repeated punctuation) before
intent matching. All v0.3 behavior is preserved.
"""

import re

from intent_matcher import match_intent
from intents import get_response_for_intent
from memory import reset_memory


def normalize(user_input: str) -> str:
    """
    Clean up user input for intent matching only (does not affect
    what gets stored in memory/history). Handles extra whitespace
    and repeated punctuation (e.g. "HELLO!!!" -> "hello!").
    """
    text = user_input.strip().lower()
    text = re.sub(r"\s+", " ", text)
    text = re.sub(r"([!?.])\1+", r"\1", text)
    return text


def get_response(user_input: str, memory: dict) -> str:
    # Used for intent matching (whitespace/punctuation collapsed)
    normalized = normalize(user_input)
    # Used for name-detection position-finding (same length as
    # user_input, so slice positions stay aligned)
    lower_text = user_input.lower()

    # --- Forget me / reset memory ---
    forget_triggers = ["forget me", "reset memory", "clear memory",
                        "forget everything", "start over"]
    if any(trigger in normalized for trigger in forget_triggers):
        memory.clear()
        memory.update(reset_memory())
        return "Okay, I've forgotten everything. Let's start fresh!"

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
        idx = lower_text.find(trigger)
        if idx != -1:
            remainder = user_input[idx + len(trigger):].strip()
            if remainder:
                name = remainder.split(" ")[0]
            break

    if name is None:
        for trigger in guarded_triggers:
            idx = lower_text.find(trigger)
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
    if "hello" in normalized or "hi" in normalized:
        if memory.get("user_name"):
            return f"Hello {memory['user_name']}! How can I help you today?"
        varied = get_response_for_intent("greeting_hello")
        return f"{varied} What's your name?"

    # --- Everything else: handled by the intents system ---
    intent_reply = match_intent(normalized)
    if intent_reply:
        return intent_reply

    return "I heard you, but I don't have a smart reply for that yet."

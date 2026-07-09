"""
RobiDev AI - Chatbot Logic
v0.4 Step 1: added memory reset ("forget me") support and basic
input normalization (extra whitespace, repeated punctuation) before
intent matching. All v0.3 behavior is preserved.
v0.4 Step 2: added session context awareness (recent exchanges, last
intent/topic), follow-up understanding ("what is my name?", "tell me
more"), and response variety that avoids repeating the same reply
back-to-back. All previous behavior is preserved.
v0.4 Step 3: added broader elaboration follow-ups (why?, how?, give me
an example), correction-aware name handling ("no, my name is X"),
conversation repair detection (e.g. "that's wrong"), and split the
logic into small helper functions for readability. All previous
behavior is preserved.
"""

import re

from intent_matcher import match_intent
from intents import get_response_for_intent, get_expanded_response_for_intent
from memory import reset_memory
from context import update_session, reset_session
from skills import try_skills


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


def _is_forget_request(normalized: str) -> bool:
    forget_triggers = ["forget me", "reset memory", "clear memory",
                        "forget everything", "start over"]
    return any(trigger in normalized for trigger in forget_triggers)


def _is_name_question(normalized: str) -> bool:
    triggers = ["what is my name", "what's my name",
                "do you know my name", "who am i"]
    return any(trigger in normalized for trigger in triggers)


def _is_elaboration_request(normalized: str) -> bool:
    """
    Matches "tell me more" style follow-ups. Short, ambiguous words
    ("why", "how") require an exact match so they don't accidentally
    trigger inside unrelated phrases like "how are you".
    """
    exact_words = {"why", "how"}
    phrases = [
        "tell me more", "more please", "go on", "continue", "what else",
        "why is that", "how so", "can you explain", "explain more",
        "give me an example", "example", "what do you mean",
    ]
    stripped = normalized.strip("!.?")
    if stripped in exact_words:
        return True
    return any(phrase in normalized for phrase in phrases)


def _is_repair_feedback(normalized: str) -> bool:
    """
    Matches phrases where the user is pushing back on the bot's last
    answer. "no" requires an exact match so it doesn't misfire inside
    unrelated sentences (and so "no, my name is X" still reaches the
    name-correction logic instead of being treated as repair feedback).
    """
    phrases = [
        "that's wrong", "thats wrong", "not exactly",
        "i don't understand", "i dont understand",
        "you're mistaken", "youre mistaken",
    ]
    if normalized.strip("!.?") == "no":
        return True
    return any(phrase in normalized for phrase in phrases)


def _extract_name(user_input: str, lower_text: str):
    """Look for the user's name in several common phrasings."""
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

    return name


def _handle_elaboration(session: dict):
    """Build a 'tell me more'-style response based on the last topic."""
    last_intent = session.get("last_intent")
    if last_intent:
        expanded = get_expanded_response_for_intent(last_intent)
        if expanded:
            return expanded, last_intent
        alt = get_response_for_intent(last_intent, avoid=session.get("last_response"))
        if alt:
            return alt, last_intent
    return "I'm not sure what you'd like more on yet — ask me something first!", None


def get_response(user_input: str, memory: dict, session: dict) -> str:
    normalized = normalize(user_input)
    lower_text = user_input.lower()

    def finish(response: str, intent_name: str = None) -> str:
        update_session(session, user_input, response, intent_name)
        return response

    # --- Forget me / reset memory ---
    if _is_forget_request(normalized):
        memory.clear()
        memory.update(reset_memory())
        reset_session(session)
        return "Okay, I've forgotten everything. Let's start fresh!"

    # --- Utility skills: date/time, calculator, help, version ---
    skill_match = try_skills(normalized)
    if skill_match:
        skill_response, skill_name = skill_match
        return finish(skill_response, skill_name)

    # --- Follow-up: "what is my name?" ---
    if _is_name_question(normalized):
        if memory.get("user_name"):
            return finish(f"Your name is {memory['user_name']}!", "ask_name")
        return finish("I don't know your name yet — what should I call you?", "ask_name")

    # --- Follow-up: elaboration on the last topic ---
    if _is_elaboration_request(normalized):
        response, intent_name = _handle_elaboration(session)
        return finish(response, intent_name)

    # --- Conversation repair: user is pushing back on the last answer ---
    if _is_repair_feedback(normalized):
        repair_reply = get_response_for_intent("conversation_repair", avoid=session.get("last_response"))
        return finish(repair_reply, None)

    # --- Learn (or correct) the user's name ---
    name = _extract_name(user_input, lower_text)
    if name:
        name = name.strip(".,!?").capitalize()
        old_name = memory.get("user_name")
        memory["user_name"] = name
        if old_name and old_name != name:
            return finish(f"Got it — I'll call you {name} instead of {old_name} from now on!", "name_correction")
        return finish(f"Nice to meet you, {name}! I'll remember that.", "learn_name")

    # --- Personalized greeting if we already know their name ---
    if "hello" in normalized or "hi" in normalized:
        if memory.get("user_name"):
            return finish(f"Hello {memory['user_name']}! How can I help you today?", "greeting_hello")
        varied = get_response_for_intent("greeting_hello", avoid=session.get("last_response"))
        return finish(f"{varied} What's your name?", "greeting_hello")

    # --- Everything else: handled by the intents system ---
    match = match_intent(normalized, avoid=session.get("last_response"))
    if match:
        intent_name, intent_reply = match
        return finish(intent_reply, intent_name)

    return finish("I heard you, but I don't have a smart reply for that yet.", None)

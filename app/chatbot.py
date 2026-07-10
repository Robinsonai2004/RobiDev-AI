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
v0.5 Step 1: added a utility skills dispatcher (date/time, calculator,
help, version) via skills.py.
v0.5 Step 2: added a personal knowledge system (learn/recall/update/
forget arbitrary facts, plus a profile summary) via facts.py. All
previous behavior is preserved.
v0.5 Step 3: all follow-up/context logic (elaboration phrases, pronoun
references like "it", and free-text subject tracking such as "I'm
learning Python") now lives in context.py. chatbot.py just calls into
it, keeping this file focused on conversational routing. Also fixed a
latent bug where phrases like "I'm learning Python" or "I'm using X"
could have been misread as name-learning attempts - subject-tracking
now runs before name-learning to take precedence correctly. All
previous behavior is preserved.
"""

import re

from intent_matcher import match_intent
from intents import get_response_for_intent
from memory import reset_memory
from context import (
    update_session,
    reset_session,
    is_elaboration_request,
    handle_followup,
    try_track_subject,
    is_pronoun_reference,
    build_pronoun_followup,
    has_focus,
)
from skills import try_skills
from facts import try_facts


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

    # --- Personal knowledge: learn, recall, update, forget facts ---
    fact_match = try_facts(normalized, user_input, lower_text, memory)
    if fact_match:
        fact_response, fact_topic = fact_match
        return finish(fact_response, fact_topic)

    # --- Follow-up: "what is my name?" ---
    if _is_name_question(normalized):
        if memory.get("user_name"):
            return finish(f"Your name is {memory['user_name']}!", "ask_name")
        return finish("I don't know your name yet — what should I call you?", "ask_name")

    # --- Follow-up: elaboration on the current topic ---
    if is_elaboration_request(normalized):
        response = handle_followup(session)
        return finish(response, None)

    # --- Conversation repair: user is pushing back on the last answer ---
    if _is_repair_feedback(normalized):
        repair_reply = get_response_for_intent("conversation_repair", avoid=session.get("last_response"))
        return finish(repair_reply, None)

    # --- Track free-text subjects (e.g. "I'm learning Python", "explain recursion") ---
    # NOTE: this runs BEFORE name-learning on purpose - phrases like
    # "I'm learning Python" or "I'm using Termux" would otherwise be
    # misread by the guarded name triggers below ("i'm" + next word).
    subject_ack = try_track_subject(user_input, lower_text, session)
    if subject_ack:
        return finish(subject_ack, None)

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

    # --- Last resort: a bare pronoun reference to something we discussed ---
    if is_pronoun_reference(normalized) and has_focus(session):
        return finish(build_pronoun_followup(session), None)

    return finish("I heard you, but I don't have a smart reply for that yet.", None)

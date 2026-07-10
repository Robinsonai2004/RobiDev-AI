"""
RobiDev AI - Conversation Context
v0.4 Step 2: temporary, in-session conversation context (recent
exchanges, last intent/topic, last response given). This is NOT saved
to disk and is separate from the persistent long-term memory in
memory.py. It exists only to make the current conversation flow
better (avoid repeating replies, understand simple follow-ups).
v0.5 Step 3: added a unified "current focus" concept (topic_kind),
free-text subject tracking (e.g. "I'm learning Python" -> subject =
"Python"), pronoun resolution ("it"/"that"/"this"), and a broader set
of follow-up phrases. All previous behavior is preserved - chatbot.py
now delegates ALL follow-up/context decisions to this module.
"""

import re

from intents import get_expanded_response_for_intent, get_response_for_intent

MAX_RECENT = 8


# --- Session lifecycle ------------------------------------------------------

def init_session() -> dict:
    """Create a fresh, empty session context for the current run."""
    return {
        "recent": [],          # list of {"user":..., "bot":...}, in-session only
        "last_intent": None,   # the matched intent/skill/fact name, if any
        "last_subject": None,  # free-text subject, e.g. "Python"
        "last_topic": None,    # human-readable label of the current focus
        "topic_kind": None,    # "intent" or "subject" - which one is current
        "last_response": None,
    }


def reset_session(session: dict):
    """Clear session context in place (used when the user says 'forget me')."""
    session["recent"] = []
    session["last_intent"] = None
    session["last_subject"] = None
    session["last_topic"] = None
    session["topic_kind"] = None
    session["last_response"] = None


def _record_exchange(session: dict, user_input: str, bot_response: str):
    """Append the exchange to the rolling history, trimming old entries."""
    session["recent"].append({"user": user_input, "bot": bot_response})
    if len(session["recent"]) > MAX_RECENT:
        session["recent"] = session["recent"][-MAX_RECENT:]
    session["last_response"] = bot_response


def update_session(session: dict, user_input: str, bot_response: str, intent_name: str = None):
    """
    Record the latest exchange. If intent_name is given, it becomes the
    current focus (an "intent"-style topic, e.g. 'capabilities' or
    'skill_datetime'). If intent_name is omitted, the current focus is
    left untouched (whatever was set before still applies).
    """
    _record_exchange(session, user_input, bot_response)
    if intent_name:
        session["last_intent"] = intent_name
        session["last_topic"] = intent_name
        session["topic_kind"] = "intent"


def update_subject(session: dict, subject: str):
    """
    Set a free-text subject (e.g. "Python", "Lenovo laptop") as the
    current focus (a "subject"-style topic). The caller still records
    the exchange itself via update_session(..., intent_name=None).
    """
    session["last_subject"] = subject
    session["last_topic"] = subject
    session["topic_kind"] = "subject"


def has_focus(session: dict) -> bool:
    """Whether there's a current topic to refer back to."""
    return bool(session.get("last_topic"))


# --- Follow-up phrase detection ---------------------------------------------

_ELABORATION_EXACT_WORDS = {"why", "how"}
_ELABORATION_PHRASES = [
    "tell me more", "more please", "go on", "continue", "what else",
    "why is that", "how so", "can you explain", "explain more",
    "explain again", "give me an example", "give an example", "example",
    "what do you mean", "can you simplify", "simplify it",
]

_PRONOUN_PATTERN = re.compile(r"\b(it|that|this)\b", re.IGNORECASE)


def is_elaboration_request(normalized: str) -> bool:
    """
    Matches "tell me more" style follow-ups. Short, ambiguous words
    ("why", "how") require an exact match so they don't accidentally
    trigger inside unrelated phrases like "how are you".
    """
    stripped = normalized.strip("!.?")
    if stripped in _ELABORATION_EXACT_WORDS:
        return True
    return any(phrase in normalized for phrase in _ELABORATION_PHRASES)


def is_pronoun_reference(normalized: str) -> bool:
    """Whether the text contains a referring pronoun (it/that/this)."""
    return bool(_PRONOUN_PATTERN.search(normalized))


# --- Building follow-up responses -------------------------------------------

def _build_intent_followup(session: dict) -> str:
    """Elaborate on the last matched intent/skill/fact, if possible."""
    last_intent = session.get("last_intent")
    expanded = get_expanded_response_for_intent(last_intent)
    if expanded:
        return expanded
    alt = get_response_for_intent(last_intent, avoid=session.get("last_response"))
    if alt:
        return alt
    return "I don't have more detail to add on that, but feel free to ask me something else!"


def _build_subject_followup(session: dict) -> str:
    """
    Honestly acknowledge a free-text subject the user asked about,
    without fabricating knowledge RobiDev AI doesn't actually have.
    """
    subject = session.get("last_subject")
    return (
        f"I don't have detailed knowledge about {subject} yet, but I know "
        f"that's what we're discussing. Feel free to teach me more about "
        f"it, or ask me something else!"
    )


def handle_followup(session: dict) -> str:
    """
    Build a response for a follow-up question (e.g. "tell me more",
    "why?", "can you simplify it?") based on the current conversation
    focus. Returns a graceful clarification request if there's no
    context to go on yet.
    """
    kind = session.get("topic_kind")
    if kind == "intent":
        return _build_intent_followup(session)
    if kind == "subject":
        return _build_subject_followup(session)
    return "I'm not sure what you'd like more on yet — ask me something first!"


def build_pronoun_followup(session: dict) -> str:
    """
    Build a response when the user refers back to something with a
    bare pronoun ("it"/"that"/"this") outside of a recognized
    elaboration phrase. Only call this when has_focus(session) is True.
    """
    return handle_followup(session)


# --- Free-text subject tracking ----------------------------------------------

_SUBJECT_STOPWORDS = {"it", "that", "this", "more", "again", "clearly", ""}

_SUBJECT_PATTERNS = [
    {
        "triggers": ["i'm learning", "i am learning"],
        "ack": "That's great! Learning {subject} is a solid choice.",
    },
    {
        "triggers": ["i'm studying", "i am studying"],
        "ack": "That's great! Studying {subject} sounds interesting.",
    },
    {
        "triggers": ["i bought a", "i bought an", "i got a", "i got an"],
        "ack": "Nice choice! {subject} sounds great.",
    },
    {
        "triggers": ["i'm using", "i am using"],
        "ack": "Got it — {subject} noted!",
    },
    {
        "triggers": ["i have a", "i have an"],
        "ack": "Got it — {subject} noted!",
    },
    {
        "triggers": ["i'm working on", "i am working on", "working on"],
        "ack": "Nice — {subject} sounds interesting!",
    },
    {
        "triggers": ["explain", "tell me about"],
        "ack": (
            "Sure — let's talk about {subject}. I don't have a detailed "
            "explanation ready yet, but feel free to teach me or ask "
            "something specific!"
        ),
    },
]


def _extract_subject(user_input: str, lower_text: str, triggers: list):
    """Find the first matching trigger and return the text after it."""
    for trigger in triggers:
        idx = lower_text.find(trigger)
        if idx != -1:
            remainder = user_input[idx + len(trigger):].strip().strip(".,!?").strip()
            return remainder if remainder else None
    return None


def try_track_subject(user_input: str, lower_text: str, session: dict):
    """
    Detect statements that introduce a new free-text subject (e.g.
    "I'm learning Python", "explain recursion"). If one matches, marks
    it as the session's current focus and returns a friendly
    acknowledgment. Returns None if nothing matched, so the caller can
    move on to other handlers.
    """
    for pattern in _SUBJECT_PATTERNS:
        subject = _extract_subject(user_input, lower_text, pattern["triggers"])
        if not subject:
            continue
        if subject.split()[0].lower().strip(".,!?") in _SUBJECT_STOPWORDS:
            continue
        update_subject(session, subject)
        return pattern["ack"].format(subject=subject)
    return None

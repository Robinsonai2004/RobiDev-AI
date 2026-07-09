"""
RobiDev AI - Session Context
v0.4 Step 2: temporary, in-session conversation context (recent exchanges,
last intent/topic, last response given). This is NOT saved to disk and is
separate from the persistent long-term memory in memory.py. It exists only
to make the current conversation flow better (avoid repeating replies,
understand simple follow-ups like "tell me more").
"""

MAX_RECENT = 8


def init_session() -> dict:
    """Create a fresh, empty session context for the current run."""
    return {
        "recent": [],        # list of {"user":..., "bot":...}, in-session only
        "last_intent": None,
        "last_topic": None,
        "last_response": None,
    }


def update_session(session: dict, user_input: str, bot_response: str, intent_name: str = None):
    """Record the latest exchange and update last-known intent/topic/response."""
    session["recent"].append({"user": user_input, "bot": bot_response})
    if len(session["recent"]) > MAX_RECENT:
        session["recent"] = session["recent"][-MAX_RECENT:]

    session["last_response"] = bot_response
    if intent_name:
        session["last_intent"] = intent_name
        session["last_topic"] = intent_name


def reset_session(session: dict):
    """Clear session context in place (used when the user says 'forget me')."""
    session["recent"] = []
    session["last_intent"] = None
    session["last_topic"] = None
    session["last_response"] = None

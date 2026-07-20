"""
RobiDev AI - Capability Router
v0.6 Step 1: the central dispatcher for every user request. Instead of
chatbot.py deciding what to do, it builds a small request context and
hands it to this router, which tries each registered capability in
turn and returns the first response it gets.

    User message -> chatbot.py -> capability_router.py -> {
        skills, facts, conversation (core), intents,
        knowledge (future), plugins (future), ...
    } -> final response

HOW TO ADD A NEW CAPABILITY (e.g. weather.py):
1. Write weather.py with a handler function following this contract:

       def handle(ctx: dict):
           if <this request isn't about weather>:
               return None
           ...
           return response_text, "weather"   # topic_name, or None

2. Import it below and add it to CAPABILITIES, in the position where
   it should be tried.

That's it. chatbot.py doesn't change. No other capability's code
needs to change either.

THE CONTEXT DICT (ctx) passed to every handler contains:
    "user_input" - the raw text the user typed
    "normalized" - lowercased, whitespace/punctuation-collapsed text
    "lower_text" - the raw text, lowercased only (preserves original
                    casing/positions, used for name/subject extraction)
    "memory"     - the persistent memory dict (name, history, facts)
    "session"    - the in-session conversation context dict

NOTE ON EXISTING MODULES: skills.py and facts.py were built (in v0.5)
with slightly different function signatures than the ctx-based
contract above. Rather than risk changing already-tested code, they
are wired in below via tiny adapter functions. Any brand-new
capability should be written directly against the ctx contract and
won't need an adapter at all.

"forget me" is handled as a special pre-check before the registry
loop, since resetting everything needs to bypass normal topic-
recording entirely (see route() below).

FAULT ISOLATION: each handler runs inside a try/except. A future
capability that hits the network (weather, web_search) or otherwise
throws should not be able to crash the whole router - it's skipped
and the next capability in line gets a chance instead.
"""

import re

from context import update_session
from skills import try_skills
from facts import try_facts
from intent_matcher import match_intent
from weather import handle as handle_weather
from notes import handle as handle_notes
from echo import handle as handle_echo
from conversation import (
    is_forget_request,
    handle_forget,
    handle_name_question,
    handle_elaboration,
    handle_repair,
    handle_subject_tracking,
    handle_name_learning,
    handle_greeting,
    handle_pronoun_fallback,
)


def normalize(user_input: str) -> str:
    text = user_input.strip().lower()
    text = re.sub(r"\s+", " ", text)
    text = re.sub(r"([!?.])\1+", r"\1", text)
    return text


def _handle_skills(ctx: dict):
    return try_skills(ctx["normalized"])


def _handle_facts(ctx: dict):
    return try_facts(ctx["normalized"], ctx["user_input"], ctx["lower_text"], ctx["memory"])


def _handle_intents(ctx: dict):
    match = match_intent(ctx["normalized"], avoid=ctx["session"].get("last_response"))
    if not match:
        return None
    intent_name, response = match
    return response, intent_name


CAPABILITIES = [
    ("skills", _handle_skills),
    ("echo", handle_echo),
    ("facts", _handle_facts),
    ("notes", handle_notes),
    ("weather", handle_weather),
    ("name_question", handle_name_question),
    ("elaboration", handle_elaboration),
    ("repair", handle_repair),
    ("subject_tracking", handle_subject_tracking),
    ("name_learning", handle_name_learning),
    ("greeting", handle_greeting),
    ("intents", _handle_intents),
    ("pronoun_fallback", handle_pronoun_fallback),
]

FALLBACK_RESPONSE = "I heard you, but I don't have a smart reply for that yet."


def route(user_input: str, memory: dict, session: dict) -> str:
    normalized = normalize(user_input)
    ctx = {
        "user_input": user_input,
        "normalized": normalized,
        "lower_text": user_input.lower(),
        "memory": memory,
        "session": session,
    }

    if is_forget_request(normalized):
        return handle_forget(ctx)

    for _name, handler in CAPABILITIES:
        try:
            result = handler(ctx)
        except Exception:
            continue
        if result:
            response, topic_name = result
            update_session(session, user_input, response, topic_name)
            return response

    update_session(session, user_input, FALLBACK_RESPONSE, None)
    return FALLBACK_RESPONSE

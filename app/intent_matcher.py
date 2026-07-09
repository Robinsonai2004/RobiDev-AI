"""
RobiDev AI - Intent Matcher
v0.3 Step 2: matches free-form user input against keyword intents
(not exact-sentence matching).
v0.4 Step 2: now also returns which intent matched (not just the response
text), so the chatbot can remember the current topic for follow-up
questions like "tell me more". Matching logic itself is unchanged.
"""

from intents import INTENTS, get_response_for_intent


def match_intent(user_input: str, avoid: str = None):
    """
    Returns a (intent_name, response) tuple if an intent matches,
    otherwise None.
    """
    text = user_input.lower().strip()

    for intent_name, data in INTENTS.items():
        for keyword in data["keywords"]:
            if keyword in text:
                return intent_name, get_response_for_intent(intent_name, avoid=avoid)

    return None

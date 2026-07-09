"""
RobiDev AI - Intent Matcher
v0.3 Step 2: matches free-form user input against keyword intents
(not exact-sentence matching).
"""

from intents import INTENTS, get_response_for_intent


def match_intent(user_input: str):
    """
    Returns a response string if an intent matches, otherwise None.
    """
    text = user_input.lower().strip()

    for intent_name, data in INTENTS.items():
        for keyword in data["keywords"]:
            if keyword in text:
                return get_response_for_intent(intent_name)

    return None

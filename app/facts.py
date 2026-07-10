"""
RobiDev AI - Personal Knowledge System
v0.5 Step 2: learn, recall, update, and forget user-specific facts
(beyond just the user's name), stored in persistent memory under
memory["facts"]. Kept separate from chatbot.py so new fact types can
be added here without touching conversational logic.

HOW TO ADD A NEW FACT TYPE:
Add a new entry to FACT_TYPES below with:
- "key": the dictionary key used in memory["facts"]
- "label": a human-friendly name, used in profile summaries and
  default recall/not-found messages
- "learn_triggers": phrases that introduce the fact (e.g. "my X is")
- "question_triggers": phrases that ask about the fact
- "forget_triggers": phrases that ask to forget just this fact
Optional overrides:
- "answer_template": custom recall phrasing, using {value}
- "not_found_template": custom "I don't know yet" phrasing
- "value_stopwords": if the extracted value's first word is one of
  these, the match is rejected (helps avoid false positives, e.g.
  "I study hard for exams" should not set field_of_study to "hard...")
That's it - no changes needed elsewhere.
"""

FACT_TYPES = [
    {
        "key": "favorite_color",
        "label": "Favorite color",
        "learn_triggers": [
            "remember that my favorite color is",
            "remember my favorite color is",
            "my favorite color is",
        ],
        "question_triggers": [
            "what is my favorite color",
            "what's my favorite color",
            "whats my favorite color",
        ],
        "forget_triggers": ["forget my favorite color", "remove my favorite color"],
    },
    {
        "key": "hometown",
        "label": "Hometown",
        "learn_triggers": [
            "remember that my hometown is",
            "remember my hometown is",
            "my hometown is",
        ],
        "question_triggers": [
            "what is my hometown",
            "what's my hometown",
            "whats my hometown",
        ],
        "forget_triggers": ["forget my hometown", "remove my hometown"],
    },
    {
        "key": "birthday",
        "label": "Birthday",
        "learn_triggers": [
            "remember that my birthday is",
            "remember my birthday is",
            "my birthday is",
        ],
        "question_triggers": [
            "when is my birthday",
            "what is my birthday",
            "what's my birthday",
        ],
        "forget_triggers": ["forget my birthday", "remove my birthday"],
    },
    {
        "key": "field_of_study",
        "label": "Field of study",
        "learn_triggers": [
            "remember that i study",
            "remember i study",
            "i study",
        ],
        "question_triggers": [
            "what do i study",
            "what am i studying",
            "what is my field of study",
            "what's my field of study",
        ],
        "forget_triggers": [
            "forget my field of study",
            "forget what i study",
            "remove my field of study",
        ],
        "answer_template": "You study {value}.",
        "not_found_template": "I don't know what you study yet — you can tell me by saying \"I study ...\".",
        "value_stopwords": {"hard", "often", "daily", "every", "for", "a", "lot", "sometimes", "always", "when"},
    },
    {
        "key": "favorite_programming_language",
        "label": "Favorite programming language",
        "learn_triggers": [
            "remember that my favorite programming language is",
            "remember my favorite programming language is",
            "my favorite programming language is",
        ],
        "question_triggers": [
            "what is my favorite programming language",
            "what's my favorite programming language",
            "whats my favorite programming language",
        ],
        "forget_triggers": [
            "forget my favorite programming language",
            "remove my favorite programming language",
        ],
    },
]

_TRAILING_FILLERS = {"now", "please", "actually"}

_PROFILE_TRIGGERS = [
    "what do you know about me",
    "tell me what you've learned about me",
    "tell me what you learned about me",
    "show my profile",
]


def _strip_trailing_filler(value: str) -> str:
    """Remove common trailing filler words (e.g. 'Lagos now' -> 'Lagos')."""
    words = value.split()
    while words and words[-1].lower().strip(".,!?") in _TRAILING_FILLERS:
        words.pop()
    return " ".join(words)


def _extract_value(user_input: str, lower_text: str, triggers: list):
    """Find the first matching trigger and return the text after it."""
    for trigger in triggers:
        idx = lower_text.find(trigger)
        if idx != -1:
            remainder = user_input[idx + len(trigger):].strip().strip(".,!?").strip()
            remainder = _strip_trailing_filler(remainder)
            return remainder if remainder else None
    return None


def try_forget_fact(normalized: str, memory: dict):
    """
    Forget a single stored fact if the user asks to. Returns a
    response string if a forget-fact command matched, else None.
    """
    for fact in FACT_TYPES:
        if any(trigger in normalized for trigger in fact["forget_triggers"]):
            facts = memory.get("facts", {})
            if fact["key"] in facts:
                del facts[fact["key"]]
                return f"Okay, I've forgotten your {fact['label'].lower()}."
            return f"I didn't have your {fact['label'].lower()} stored anyway!"
    return None


def try_profile_summary(normalized: str, memory: dict):
    """Show everything currently remembered about the user."""
    if not any(trigger in normalized for trigger in _PROFILE_TRIGGERS):
        return None

    facts = memory.get("facts", {})
    lines = []

    if memory.get("user_name"):
        lines.append(f"Name: {memory['user_name']}")

    for fact in FACT_TYPES:
        value = facts.get(fact["key"])
        if value:
            lines.append(f"{fact['label']}: {value}")

    if not lines:
        return "I don't know much about you yet — teach me something, like \"my favorite color is blue\"!"

    return "Here's what I know about you:\n\n" + "\n".join(lines)


def try_recall_fact(normalized: str, memory: dict):
    """Answer a recall question about a stored fact, if one matches."""
    facts = memory.get("facts", {})
    for fact in FACT_TYPES:
        if any(trigger in normalized for trigger in fact["question_triggers"]):
            value = facts.get(fact["key"])
            if value:
                template = fact.get("answer_template", "Your {label_lower} is {value}.")
                return template.format(value=value, label_lower=fact["label"].lower())
            not_found = fact.get(
                "not_found_template",
                f"I don't know your {fact['label'].lower()} yet — you can tell me by saying \"my {fact['label'].lower()} is ...\".",
            )
            return not_found
    return None


def try_learn_fact(user_input: str, lower_text: str, memory: dict):
    """
    Learn or update a fact if the user states one. Returns a
    confirmation string if a fact was learned/updated, else None.
    """
    for fact in FACT_TYPES:
        value = _extract_value(user_input, lower_text, fact["learn_triggers"])
        if not value:
            continue

        stopwords = fact.get("value_stopwords")
        if stopwords and value.split()[0].lower().strip(".,!?") in stopwords:
            continue

        facts = memory.setdefault("facts", {})
        old_value = facts.get(fact["key"])
        facts[fact["key"]] = value
        label_lower = fact["label"].lower()
        if old_value and old_value.lower() != value.lower():
            return f"Got it — I've updated your {label_lower} to {value} (was {old_value})."
        return f"Got it! I'll remember that your {label_lower} is {value}."
    return None


def try_facts(normalized: str, user_input: str, lower_text: str, memory: dict):
    """
    Try each fact-related capability (forget, profile summary, recall,
    then learn) in that order. Returns (response, topic_name) for the
    first one that matches, or None if nothing matches.
    """
    response = try_forget_fact(normalized, memory)
    if response:
        return response, "fact_forget"

    response = try_profile_summary(normalized, memory)
    if response:
        return response, "fact_profile"

    response = try_recall_fact(normalized, memory)
    if response:
        return response, "fact_recall"

    response = try_learn_fact(user_input, lower_text, memory)
    if response:
        return response, "fact_learn"

    return None

"""
RobiDev AI - Utility Skills
v0.5 Step 1: built-in utility skills (date/time, calculator, help,
version/about). Kept separate from chatbot.py's conversational logic
so new skills can be added here without touching intent matching.

HOW TO ADD A NEW SKILL:
1. Write a `try_<skill>(normalized: str)` function that returns a
   response string if it matches, or None if it doesn't.
2. Add it to the SKILLS list at the bottom of this file, in the order
   it should be checked.
"""

import re
from datetime import datetime


# --- Date & Time ---------------------------------------------------------

_TIME_TRIGGERS = ["what time is it", "tell me the time", "current time",
                   "what's the time", "whats the time"]
_DATE_TRIGGERS = ["what is today's date", "what's the date today",
                   "whats the date today", "today's date", "todays date",
                   "what is the date", "what's todays date"]
_DAY_TRIGGERS = ["day of the week", "what day is today", "what day is it"]


def try_datetime(normalized: str):
    """Answer simple date/time questions using the system clock."""
    if any(trigger in normalized for trigger in _TIME_TRIGGERS):
        now = datetime.now()
        return f"It's currently {now.strftime('%I:%M %p')}."

    if any(trigger in normalized for trigger in _DATE_TRIGGERS):
        now = datetime.now()
        return f"Today's date is {now.strftime('%A, %B %d, %Y')}."

    if any(trigger in normalized for trigger in _DAY_TRIGGERS):
        now = datetime.now()
        return f"Today is {now.strftime('%A')}."

    return None


# --- Calculator ------------------------------------------------------------

_WORD_OPERATORS = {
    "multiplied by": "*",
    "divided by": "/",
    "plus": "+",
    "minus": "-",
    "times": "*",
}

_OPERATIONS = {
    "+": lambda a, b: a + b,
    "-": lambda a, b: a - b,
    "*": lambda a, b: a * b,
    "/": lambda a, b: a / b,
}

# Broad "does this look like an attempted calculation" check: just a
# digit followed by a recognized operator token. Deliberately loose so
# that incomplete/malformed expressions (e.g. "5 + cat") still get
# routed here for a helpful error, instead of falling through silently.
_CALC_HINT_PATTERN = re.compile(
    r"\d\s*(\+|-|\*|/|x|plus|minus|times|multiplied by|divided by)",
    re.IGNORECASE,
)

# Strict check for a genuinely valid "number operator number" expression.
_CALC_PATTERN = re.compile(
    r"^\s*(-?\d+(?:\.\d+)?)\s*([+\-*/])\s*(-?\d+(?:\.\d+)?)\s*$"
)


def _normalize_operators(text: str) -> str:
    """Convert word-based operators and 'x' multiplication into symbols."""
    result = text
    for word, symbol in _WORD_OPERATORS.items():
        result = re.sub(rf"\b{word}\b", symbol, result, flags=re.IGNORECASE)
    result = re.sub(r"(\d)\s*x\s*(-?\d)", r"\1*\2", result, flags=re.IGNORECASE)
    return result


def _format_number(value: float) -> str:
    """Format a number as an int when it's a whole number, else rounded."""
    if value == int(value):
        return str(int(value))
    return str(round(value, 6))


def try_calculate(normalized: str):
    """
    Attempt to evaluate a simple two-number arithmetic expression
    (e.g. "5 + 8", "12 x 15", "7 plus 4"). Returns a response string if
    the input looks like a calculation attempt (valid or invalid), or
    None if it doesn't look like math at all so other handlers can
    process it instead.
    """
    if not _CALC_HINT_PATTERN.search(normalized):
        return None

    expression = _normalize_operators(normalized)
    match = _CALC_PATTERN.match(expression)
    if not match:
        return "I couldn't understand that calculation. Try something like '5 + 8' or '12 x 15'."

    left, operator, right = match.groups()
    try:
        a, b = float(left), float(right)
    except ValueError:
        return "I couldn't understand that calculation. Try something like '5 + 8'."

    if operator == "/" and b == 0:
        return "I can't divide by zero!"

    try:
        result = _OPERATIONS[operator](a, b)
    except ZeroDivisionError:
        return "I can't divide by zero!"

    return f"{_format_number(a)} {operator} {_format_number(b)} = {_format_number(result)}"


# --- Help -------------------------------------------------------------------

_HELP_EXACT = {"help", "commands"}
_HELP_PHRASES = ["what can you do"]


def try_help(normalized: str):
    """Return a categorized capabilities list if the user asks for help."""
    stripped = normalized.strip("!.?")
    if stripped in _HELP_EXACT or any(phrase in normalized for phrase in _HELP_PHRASES):
        return (
            "Here's what I can do:\n\n"
            "Conversation:\n"
            "- Greetings, small talk, and farewells\n"
            "- Remembering and correcting your name\n"
            "- Follow-ups like 'tell me more', 'why?', 'how?'\n"
            "- Recovering gracefully if I get something wrong\n\n"
            "Memory:\n"
            "- Remembering your name across sessions\n"
            "- 'forget me' to reset everything\n\n"
            "Utilities:\n"
            "- Date and time ('what time is it', 'today's date')\n"
            "- Simple math ('5 + 8', '12 x 15', '7 plus 4')\n"
            "- 'version' or 'about' for info on this build\n\n"
            "Just type naturally — I'll do my best to understand!"
        )
    return None


# --- Version / About ---------------------------------------------------------

_VERSION_EXACT = {"version", "about", "system info"}


def try_version(normalized: str):
    """Return version/about info if the user asks for it."""
    if normalized.strip("!.?") in _VERSION_EXACT:
        return (
            "RobiDev AI\n"
            "Version: v0.5 Step 1\n\n"
            "A personal, open-source chatbot-turned-assistant built in "
            "Python and run in Termux. Supports conversation memory, "
            "follow-up understanding, and utility skills (date/time, "
            "calculator)."
        )
    return None


# --- Dispatcher ---------------------------------------------------------------

SKILLS = [try_datetime, try_calculate, try_help, try_version]


def try_skills(normalized: str):
    """
    Try each registered skill in order. Returns (response, skill_name)
    for the first skill that matches, or None if no skill matches.
    """
    for skill in SKILLS:
        response = skill(normalized)
        if response:
            return response, f"skill_{skill.__name__.replace('try_', '')}"
    return None

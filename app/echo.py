"""
RobiDev AI - Echo Capability (architectural proof-of-concept)
v0.6 Step 2: this module exists to validate that a new capability can
be added to RobiDev AI with nothing more than (1) writing this file
and (2) registering one line in capability_router.py's CAPABILITIES
list. No other application code should need to change.

Trigger: a message that is exactly "echo", or starts with "echo "
(case-insensitive). Behavior: repeats back whatever text follows the
trigger word, or asks for input if none was given.

    You: echo hello there
    RobiDev AI: hello there

    You: echo
    RobiDev AI: Echo what? Try: echo <something>

This follows the standard ctx-based handler contract used by every
capability registered with the router:

    handle(ctx: dict) -> (response: str, topic_name: str or None) or None
"""

_TRIGGER_WORD = "echo"


def handle(ctx: dict):
    normalized = ctx["normalized"]
    if normalized != _TRIGGER_WORD and not normalized.startswith(_TRIGGER_WORD + " "):
        return None

    # Pull the payload from the original (non-normalized) input so
    # casing and punctuation the user actually typed are preserved.
    payload = ctx["user_input"].strip()[len(_TRIGGER_WORD):].strip()
    if not payload:
        return "Echo what? Try: echo <something>", "echo"

    return payload, "echo"

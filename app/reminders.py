"""
RobiDev AI - Reminders
v0.6 Step 7: add, view, complete, delete, and clear personal
reminders, stored persistently in memory["reminders"]. Follows the
same shape as notes.py for CRUD-style operations.

Storage:
    memory["reminders"] = [
        {"id": 1, "text": "study Python", "due": "<ISO datetime>",
         "created": "<ISO datetime>", "completed": False},
    ]

DESIGN NOTE - no background process: RobiDev AI is a synchronous
REPL with no scheduler, timer, or daemon. A reminder can't fire on
its own the moment it's due. Instead, check_due_reminders() is
called by capability_router.route() at the start of EVERY message,
before the normal response is decided - so a due reminder surfaces
as a banner above whatever the user actually asked about, rather
than being a capability that only responds when directly triggered.

This keeps the reminder DATA MODEL (the dicts above) completely
separate from HOW a due reminder gets surfaced. A future GUI or
mobile version could swap check_due_reminders()'s caller for a real
background notification system without this file changing at all -
the stored data and its shape stay exactly the same either way.

TRADEOFF, flagged deliberately: a due reminder keeps reappearing on
every message until it's completed or deleted, since there's no
other way to guarantee it isn't silently missed with no background
process to fall back on.

Follows the same ctx-based handler contract as every other
capability for the add/view/complete/delete/clear commands:

    handle(ctx: dict) -> (response: str, topic_name: str or None) or None
"""

import re
from datetime import datetime, timedelta

_TIME_PATTERN = re.compile(r"at (\d{1,2})(?::(\d{2}))?\s*(am|pm)")
_ISO_FORMAT = "%Y-%m-%dT%H:%M:%S"

_CLEAR_TRIGGERS = ["clear reminders", "delete all reminders", "remove all reminders"]
_COMPLETE_PATTERN = re.compile(r"(?:complete|mark) reminder\s*#?\s*(\d+)")
_DELETE_PATTERN = re.compile(r"(?:delete|remove) reminder\s*#?\s*(\d+)")
_VIEW_TRIGGERS = ["reminders", "show reminders", "list reminders", "my reminders"]
_ADD_TRIGGER = "remind me"


def _to_iso(dt: datetime) -> str:
    return dt.strftime(_ISO_FORMAT)


def _from_iso(text: str) -> datetime:
    return datetime.strptime(text, _ISO_FORMAT)


def _renumber(reminders: list):
    """Keep each reminder's "id" in sync with its position after a deletion."""
    for i, reminder in enumerate(reminders):
        reminder["id"] = i + 1


def _parse_reminder(user_input: str, lower_text: str):
    """
    Extract (text, due_datetime) from a "remind me ..." message, or
    None if no parseable time was found. Rolls the time to tomorrow
    if it's already passed today and "tomorrow" wasn't said, so a
    reminder is never created already overdue by accident.
    """
    if not lower_text.startswith(_ADD_TRIGGER):
        return None

    time_match = _TIME_PATTERN.search(lower_text)
    if not time_match:
        return None

    hour = int(time_match.group(1))
    minute = int(time_match.group(2) or 0)
    ampm = time_match.group(3)
    if ampm == "pm" and hour != 12:
        hour += 12
    if ampm == "am" and hour == 12:
        hour = 0

    said_tomorrow = "tomorrow" in lower_text

    start, end = time_match.span()
    text = user_input[:start] + user_input[end:]
    text = text.lower().replace("remind me", "").replace("tomorrow", "").replace("today", "")
    text = text.strip()
    if text.startswith("to "):
        text = text[3:]
    text = text.strip(" ,.!?").strip()
    if not text:
        text = "Reminder"

    now = datetime.now()
    due = now.replace(hour=hour, minute=minute, second=0, microsecond=0)
    if said_tomorrow or due <= now:
        due += timedelta(days=1)

    return text, due


def try_add_reminder(user_input: str, lower_text: str, memory: dict):
    parsed = _parse_reminder(user_input, lower_text)
    if not parsed:
        if lower_text.strip().startswith(_ADD_TRIGGER):
            return "What time should I remind you? Try: remind me to <something> at 8 pm", "reminders_add"
        return None

    text, due = parsed
    reminders = memory.setdefault("reminders", [])
    reminders.append({
        "id": len(reminders) + 1,
        "text": text,
        "due": _to_iso(due),
        "created": _to_iso(datetime.now()),
        "completed": False,
    })
    return f'Got it — I\'ll remind you to "{text}" at {due.strftime("%I:%M %p").lstrip("0")}' \
           f'{" tomorrow" if due.date() > datetime.now().date() else ""}.', "reminders_add"


def try_view_reminders(normalized: str, memory: dict):
    if not any(t in normalized for t in _VIEW_TRIGGERS):
        return None
    reminders = memory.get("reminders", [])
    pending = [r for r in reminders if not r["completed"]]
    completed = [r for r in reminders if r["completed"]]

    if not pending and not completed:
        return 'You don\'t have any reminders yet — try "remind me to <something> at 8 pm".', "reminders_view"

    lines = []
    if pending:
        lines.append("Pending:")
        for r in pending:
            due_dt = _from_iso(r["due"])
            lines.append(f'{r["id"]}. {r["text"]} — {due_dt.strftime("%b %d, %I:%M %p").lstrip("0")}')
    if completed:
        if lines:
            lines.append("")
        lines.append("Completed:")
        for r in completed:
            lines.append(f'{r["id"]}. {r["text"]}')

    return "\n".join(lines), "reminders_view"


def try_complete_reminder(normalized: str, memory: dict):
    match = _COMPLETE_PATTERN.search(normalized)
    if not match:
        return None
    index = int(match.group(1))
    reminders = memory.get("reminders", [])
    if index < 1 or index > len(reminders):
        return f"I couldn't find reminder {index} — you have {len(reminders)} reminder(s).", "reminders_complete"
    reminders[index - 1]["completed"] = True
    return f'Marked reminder {index} ("{reminders[index - 1]["text"]}") as done.', "reminders_complete"


def try_delete_reminder(normalized: str, memory: dict):
    match = _DELETE_PATTERN.search(normalized)
    if not match:
        return None
    index = int(match.group(1))
    reminders = memory.setdefault("reminders", [])
    if index < 1 or index > len(reminders):
        return f"I couldn't find reminder {index} — you have {len(reminders)} reminder(s).", "reminders_delete"
    removed = reminders.pop(index - 1)
    _renumber(reminders)
    return f'Deleted reminder {index}: "{removed["text"]}".', "reminders_delete"


def try_clear_reminders(normalized: str, memory: dict):
    if not any(t in normalized for t in _CLEAR_TRIGGERS):
        return None
    reminders = memory.setdefault("reminders", [])
    count = len(reminders)
    reminders.clear()
    if count == 0:
        return "You don't have any reminders to clear.", "reminders_clear"
    plural = "reminder" if count == 1 else "reminders"
    return f"Cleared all {count} {plural}.", "reminders_clear"


def handle(ctx: dict):
    normalized = ctx["normalized"]
    memory = ctx["memory"]

    result = try_clear_reminders(normalized, memory)
    if result:
        return result
    result = try_complete_reminder(normalized, memory)
    if result:
        return result
    result = try_delete_reminder(normalized, memory)
    if result:
        return result
    result = try_view_reminders(normalized, memory)
    if result:
        return result
    result = try_add_reminder(ctx["user_input"], ctx["lower_text"], memory)
    if result:
        return result
    return None


def check_due_reminders(memory: dict):
    """
    Called by the router before normal dispatch, on every message.
    Returns a banner string listing any pending reminder whose due
    time has passed, or None if nothing is due. Does not mark
    anything as completed or seen - a due reminder keeps appearing
    until the user explicitly completes or deletes it (see the
    module docstring for why).
    """
    now = datetime.now()
    reminders = memory.get("reminders", [])
    due = [r for r in reminders if not r["completed"] and _from_iso(r["due"]) <= now]
    if not due:
        return None

    lines = ["🔔 Reminder:"]
    for r in due:
        due_dt = _from_iso(r["due"])
        lines.append(f'{r["text"]} ({due_dt.strftime("%I:%M %p").lstrip("0")})')
    return "\n".join(lines)

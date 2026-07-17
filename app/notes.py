"""
RobiDev AI - Notes
v0.6 Step 3: the first real capability built on the plug-in
architecture. Lets the user add, view, delete, clear, and count
personal notes, stored in persistent memory under memory["notes"].

Storage shape (extends the existing memory structure additively):

    memory["notes"] = [
        {"id": 1, "text": "Buy milk"},
        {"id": 2, "text": "Finish Python project"},
    ]

"id" always matches the note's current 1-based position in the list
(see _renumber). It exists so future features - editing, searching,
categorizing - have something stable to reference besides raw index.

Checked in this order: clear, delete, count, view, add. Clear and
delete are checked before add so their trigger words never get
mistaken for note content; view and count are narrow phrase matches
checked before add's much broader trigger set, which is intentionally
tried last as the most permissive match.

Follows the same ctx-based handler contract as every other capability:

    handle(ctx: dict) -> (response: str, topic_name: str or None) or None
"""

import re

_CLEAR_TRIGGERS = ["clear my notes", "delete all notes", "remove all notes", "clear notes"]
_DELETE_PATTERN = re.compile(r"(?:delete|remove|erase) note\s*#?\s*(\d+)")
_COUNT_TRIGGERS = ["how many notes do i have", "note count", "count my notes"]
_VIEW_TRIGGERS = ["show my notes", "list my notes", "what notes do i have", "show notes", "list notes"]
_ADD_TRIGGERS = ["take note", "add note", "remember this", "save a note", "save note"]


def _renumber(notes: list):
    """Keep each note's "id" in sync with its position after a deletion."""
    for i, note in enumerate(notes):
        note["id"] = i + 1


def try_clear_notes(normalized: str, memory: dict):
    if not any(t in normalized for t in _CLEAR_TRIGGERS):
        return None
    notes = memory.setdefault("notes", [])
    count = len(notes)
    notes.clear()
    if count == 0:
        return "You don't have any notes to clear.", "notes_clear"
    plural = "note" if count == 1 else "notes"
    return f"Cleared all {count} {plural}.", "notes_clear"


def try_delete_note(normalized: str, memory: dict):
    match = _DELETE_PATTERN.search(normalized)
    if not match:
        return None
    index = int(match.group(1))
    notes = memory.setdefault("notes", [])
    if index < 1 or index > len(notes):
        return f"I couldn't find note {index} — you have {len(notes)} note(s).", "notes_delete"
    removed = notes.pop(index - 1)
    _renumber(notes)
    return f'Deleted note {index}: "{removed["text"]}".', "notes_delete"


def try_note_count(normalized: str, memory: dict):
    if not any(t in normalized for t in _COUNT_TRIGGERS):
        return None
    count = len(memory.get("notes", []))
    if count == 0:
        return "You don't have any notes yet.", "notes_count"
    plural = "note" if count == 1 else "notes"
    return f"You have {count} {plural}.", "notes_count"


def try_view_notes(normalized: str, memory: dict):
    if not any(t in normalized for t in _VIEW_TRIGGERS):
        return None
    notes = memory.get("notes", [])
    if not notes:
        return 'You don\'t have any notes yet — try "take note <something>" to add one.', "notes_view"
    lines = [f"{i + 1}. {note['text']}" for i, note in enumerate(notes)]
    return "\n\n".join(lines), "notes_view"


def try_add_note(user_input: str, lower_text: str, memory: dict):
    """
    Uses lower_text (not normalized) to find the trigger, since
    normalized text may have collapsed whitespace/punctuation and no
    longer lines up position-for-position with the original input.
    """
    for trigger in _ADD_TRIGGERS:
        idx = lower_text.find(trigger)
        if idx == -1:
            continue
        remainder = user_input[idx + len(trigger):].strip().strip(".,!?").strip()
        if not remainder:
            return "What would you like to note down?", "notes_add"
        notes = memory.setdefault("notes", [])
        notes.append({"id": len(notes) + 1, "text": remainder})
        return f'Got it — noted: "{remainder}".', "notes_add"
    return None


def handle(ctx: dict):
    normalized = ctx["normalized"]
    memory = ctx["memory"]

    result = try_clear_notes(normalized, memory)
    if result:
        return result
    result = try_delete_note(normalized, memory)
    if result:
        return result
    result = try_note_count(normalized, memory)
    if result:
        return result
    result = try_view_notes(normalized, memory)
    if result:
        return result
    result = try_add_note(ctx["user_input"], ctx["lower_text"], memory)
    if result:
        return result
    return None

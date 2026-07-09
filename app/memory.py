"""
RobiDev AI - Memory
Handles loading and saving persistent conversation memory.
Memory is stored as JSON in the data/ folder.
"""

import json
import os
from config import MEMORY_FILE, DATA_DIR


def load_memory():
    """
    Load memory from disk. If no memory file exists yet
    (first time running the app), return a default empty structure.
    """
    if not os.path.exists(MEMORY_FILE):
        return {"user_name": None, "history": []}

    with open(MEMORY_FILE, "r") as f:
        return json.load(f)


def save_memory(memory):
    """
    Save the current memory dictionary to disk as JSON.
    Creates the data/ folder if it doesn't exist yet.
    """
    os.makedirs(DATA_DIR, exist_ok=True)

    with open(MEMORY_FILE, "w") as f:
        json.dump(memory, f, indent=2)


def reset_memory():
    """
    Return a fresh, empty memory structure.
    Used by the "forget me" command to clear stored data.
    """
    return {"user_name": None, "history": []}

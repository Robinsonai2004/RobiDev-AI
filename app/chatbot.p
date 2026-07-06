def get_response(user_input: str, memory: dict) -> str:
    text = user_input.lower()

    # --- Learn the user's name from several common phrasings ---
    # Triggers that are safe to trust directly (unambiguous)
    direct_triggers = ["my name is", "call me", "you can call me"]

    # Triggers that need a safeguard, since "I'm"/"I am" often introduce
    # feelings or states, not names (e.g. "I'm hungry", "I'm tired")
    guarded_triggers = ["i am", "i'm"]

    # Words that mean the sentence is NOT actually an introduction
    non_name_words = {
        "hungry", "tired", "fine", "good", "okay", "ok", "doing",
        "not", "just", "here", "sorry", "happy", "sad", "busy",
        "back", "done", "ready", "confused", "bored", "excited"
    }

    name = None

    for trigger in direct_triggers:
        if trigger in text:
            name = user_input.split(trigger, maxsplit=1)[-1].strip().split(" ")[0]
            break

    if name is None:
        for trigger in guarded_triggers:
            if trigger in text:
                candidate = user_input.split(trigger, maxsplit=1)[-1].strip().split(" ")[0]
                if candidate.lower().strip(".,!?") not in non_name_words:
                    name = candidate
                break

    if name:
        name = name.strip(".,!?").capitalize()
        memory["user_name"] = name
        return f"Nice to meet you, {name}! I'll remember that."

    # --- Personalized greeting if we already know their name ---
    if "hello" in text or "hi" in text:
        if memory.get("user_name"):
            return f"Hello {memory['user_name']}! How can I help you today?"
        return "Hello! What's your name?"

    elif "your name" in text:
        return "I'm RobiDev AI, your assistant."

    elif "how are you" in text:
        return "I'm just code, but I'm running well!"

    else:
        return "I heard you, but I don't have a smart reply for that yet."

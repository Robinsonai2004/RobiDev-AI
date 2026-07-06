"""
RobiDev AI - Chatbot Logic
v0.2: Rule-based responses, now with basic memory support
(remembers the user's name across sessions).
"""


def get_response(user_input: str, memory: dict) -> str:
    text = user_input.lower()

    # --- Learn the user's name if they introduce themselves ---
    if "my name is" in text:
        # Extract whatever comes after "my name is"
        name = user_input.split("my name is")[-1].strip().split(" ")[0]
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

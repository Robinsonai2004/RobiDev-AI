"""
RobiDev AI - Chatbot Logic
v0.1: Simple rule-based responses.
Will be replaced with real AI logic in a future version.
"""

def get_response(user_input: str) -> str:
    text = user_input.lower()

    if "hello" in text or "hi" in text:
        return "Hello Robinson! How can I help you today?"
    elif "your name" in text:
        return "I'm RobiDev AI, your assistant."
    elif "how are you" in text:
        return "I'm just code, but I'm running well!"
    else:
        return "I heard you, but I don't have a smart reply for that yet."

if __name__ == "__main__":
    # Quick manual test without running main.py
    print(get_response("hello"))

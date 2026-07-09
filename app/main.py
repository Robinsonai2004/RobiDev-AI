"""
RobiDev AI - Entry Point
Handles the main input/output loop.
v0.4 Step 1: memory is now saved after every exchange, not just on
exit, to protect against data loss from crashes or force-closes.
v0.4 Step 2: added in-session conversation context (separate from the
persistent memory) so the bot can understand simple follow-ups.
"""

from chatbot import get_response
from config import BOT_NAME, VERSION
from memory import load_memory, save_memory
from context import init_session

def main():
    # Load previous memory when the app starts
    memory = load_memory()
    # Create fresh, in-session-only conversation context (not saved to disk)
    session = init_session()

    print(f"{BOT_NAME} {VERSION} — type 'exit' to quit")
    # If we already know the user's name, greet them right away
    if memory.get("user_name"):
        print(f"RobiDev AI: Welcome back, {memory['user_name']}!")

    while True:
        user_input = input("You: ").strip()

        if user_input.lower() in ("exit", "quit"):
            print("RobiDev AI: Goodbye!")
            break

        response = get_response(user_input, memory, session)
        print(f"RobiDev AI: {response}")

        # Save each exchange to conversation history
        memory["history"].append({"user": user_input, "bot": response})

        # Auto-save after every exchange, not just on exit
        save_memory(memory)

    # Final save on exit (covers the case where history changed
    # but nothing else needed saving after the last message)
    save_memory(memory)

if __name__ == "__main__":
    main()
EO
cat > app/main.py << 'EOF'
"""
RobiDev AI - Entry Point
Handles the main input/output loop.
v0.4 Step 1: memory is now saved after every exchange, not just on
exit, to protect against data loss from crashes or force-closes.
v0.4 Step 2: added in-session conversation context (separate from the
persistent memory) so the bot can understand simple follow-ups.
"""

from chatbot import get_response
from config import BOT_NAME, VERSION
from memory import load_memory, save_memory
from context import init_session

def main():
    # Load previous memory when the app starts
    memory = load_memory()
    # Create fresh, in-session-only conversation context (not saved to disk)
    session = init_session()

    print(f"{BOT_NAME} {VERSION} — type 'exit' to quit")
    # If we already know the user's name, greet them right away
    if memory.get("user_name"):
        print(f"RobiDev AI: Welcome back, {memory['user_name']}!")

    while True:
        user_input = input("You: ").strip()

        if user_input.lower() in ("exit", "quit"):
            print("RobiDev AI: Goodbye!")
            break

        response = get_response(user_input, memory, session)
        print(f"RobiDev AI: {response}")

        # Save each exchange to conversation history
        memory["history"].append({"user": user_input, "bot": response})

        # Auto-save after every exchange, not just on exit
        save_memory(memory)

    # Final save on exit (covers the case where history changed
    # but nothing else needed saving after the last message)
    save_memory(memory)

if __name__ == "__main__":
    main()
EO

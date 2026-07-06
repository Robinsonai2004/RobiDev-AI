"""
RobiDev AI - Entry Point
Handles the main input/output loop.
"""

from chatbot import get_response
from memory import load_memory, save_memory

def main():
    # Load previous memory when the app starts
    memory = load_memory()

    print("RobiDev AI v0.1 — type 'exit' to quit")

    # If we already know the user's name, greet them right away
    if memory.get("user_name"):
        print(f"RobiDev AI: Welcome back, {memory['user_name']}!")

    while True:
        user_input = input("You: ").strip()

        if user_input.lower() in ("exit", "quit"):
            print("RobiDev AI: Goodbye!")
            break

        response = get_response(user_input, memory)
        print(f"RobiDev AI: {response}")

        # Save each exchange to conversation history
        memory["history"].append({"user": user_input, "bot": response})

    # Save memory to disk before exiting
    save_memory(memory)

if __name__ == "__main__":
    main()

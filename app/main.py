"""
RobiDev AI - Entry Point
Handles the main input/output loop.
"""

from chatbot import get_response

def main():
    print("RobiDev AI v0.1 — type 'exit' to quit")

    while True:
        user_input = input("You: ").strip()
        print(repr(user_input))
        if user_input.lower() in ("exit", "quit"):
            print("RobiDev AI: Goodbye!")
            break

        response = get_response(user_input)
        print(f"RobiDev AI: {response}")

if __name__ == "__main__":
    main()

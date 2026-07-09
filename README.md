# RobiDev AI

A modular, extensible AI assistant — built incrementally from v0.1, with clean architecture and professional software engineering practices.

## Current Version: v0.3

RobiDev AI is a rule-based conversational assistant that remembers who you are and responds naturally to a variety of everyday phrases.

## Features

- Persistent memory: remembers your name and full conversation history across sessions (stored in `data/memory.json`)
- Flexible name recognition: understands "my name is...", "call me...", "you can call me...", "I am...", and "I'm..."
- Personalized greetings once your name is known
- Keyword-based intent system with natural response variety (no repeated replies every time)
- Supported topics: greetings, time-of-day greetings, wellbeing ("how are you"), identity, capabilities/help, creator info, thanks, farewells
- Clean, modular architecture designed for easy extension

## Project Structure
## Installation

```bash
git clone https://github.com/Robinsonai2004/RobiDev-AI.git
cd RobiDev-AI
python -m venv venv
source venv/bin/activate
```

## Running the Chatbot

```bash
python app/main.py
```

## Example Conversation

```
RobiDev AI v0.3 — type 'exit' to quit
You: hi
RobiDev AI: Hello! How can I help today? What's your name?
You: my name is Robinson
RobiDev AI: Nice to meet you, Robinson! I'll remember that.
You: how are you
RobiDev AI: I'm doing well!
You: exit
RobiDev AI: Goodbye!
```

## Roadmap

- v0.4: Save memory after every exchange, forget-me command, input normalization
- v0.5: Expanded intent library, more casual phrases
- v0.6+: Explore replacing the rule-based core with a real language model
- v1.0: Stable, well-documented, extensible assistant

## Contributing

This is an open-source learning project built incrementally. Contributions and suggestions are welcome via GitHub issues or pull requests. Please preserve existing functionality when adding features.

## License

MIT License (planned) - see LICENSE for details.

```
RobiDev-AI/
├── app/
│   ├── main.py            # Entry point: input/output loop
│   ├── chatbot.py         # Name detection + personalization + routing
│   ├── intents.py         # Intent definitions and response variants
│   ├── intent_matcher.py  # Matches user input against intents
│   ├── memory.py          # Load/save persistent memory (JSON)
│   ├── config.py          # Centralized settings and file paths
│   └── utils.py
├── data/
│   └── memory.json        # Gitignored — personal conversation memory
├── docs/
│   └── INTENTS.md         # Guide to the intent system
├── README.md
├── LICENSE
├── TODO.md
├── requirements.txt
└── venv/

# RobiDev AI

A modular, extensible AI assistant — built incrementally from v0.1, with clean architecture and professional software engineering practices.

## Current Version: v0.6

RobiDev AI is a registry-based conversational assistant. A central capability router dispatches every user message to whichever plug-in module can handle it — greetings, personal facts, notes, weather, web search, and more — without any single file needing to know about all the others.

## Features

- Persistent memory: remembers your name, personal facts, and notes across sessions (stored in `data/memory.json`)
- Flexible name recognition and personalized greetings
- Conversation context: follow-up understanding ("tell me more", pronoun references like "what about it?"), conversation repair, and free-text subject tracking
- Personal facts system: learn, recall, update, and forget things like your favorite color, hometown, or birthday
- Notes: add, view, delete, clear, and count personal notes
- Weather lookups by city, via OpenWeatherMap
- Web search: general topic search, question-style queries, and "latest X news" phrasing, via Firecrawl
- Built-in utility skills: date, time, calculator, help, version
- "Forget me" command to reset everything and start fresh
- Clean, plug-in architecture designed for easy extension

## Architecture

RobiDev AI routes every message through app/capability_router.py, a registry-based dispatcher. Each capability handles a message or hands it off to the next one in line. chatbot.py stays a thin entry point and hasn't needed to change since this architecture was introduced.

### Adding a new capability

1. Write a new module (e.g. app/reminders.py) with a handle(ctx) function that returns None if it does not apply, or a (response_text, topic_name) tuple if it does.
2. Import it in capability_router.py and add one line to the CAPABILITIES list, in the position where it should be tried relative to the others.

That's it - no other file needs to change.

## Project Structure

RobiDev-AI/
  app/
    main.py               - Entry point: input/output loop
    chatbot.py             - Thin wrapper delegating to the router
    capability_router.py   - Central dispatcher / plug-in registry
    conversation.py        - Core conversational capabilities
    context.py             - In-session conversation context
    skills.py               - Date, time, calculator, help, version
    facts.py                - Personal facts system
    notes.py                - Notes capability
    weather.py              - Weather lookups (OpenWeatherMap)
    web_search.py           - Web search (Firecrawl)
    echo.py                  - Minimal plug-in reference example
    intents.py              - Intent definitions and response variants
    intent_matcher.py       - Matches user input against intents
    memory.py                - Load/save persistent memory (JSON)
    config.py                - Centralized settings and file paths
  data/
    memory.json           - Gitignored, personal conversation memory
  docs/
    INTENTS.md            - Guide to the intent system
  README.md
  CHANGELOG.md
  LICENSE
  TODO.md
  requirements.txt

## Installation

git clone https://github.com/Robinsonai2004/RobiDev-AI.git
cd RobiDev-AI
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

Weather and web search require API keys, set as environment variables and never hardcoded:

echo export OPENWEATHER_API_KEY=your_key_here >> ~/.bashrc
echo export FIRECRAWL_API_KEY=your_key_here >> ~/.bashrc
source ~/.bashrc

## Running the Chatbot

python app/main.py

## Roadmap

- v0.6: Registry-based plug-in architecture; echo, notes, weather, and web search capabilities
- v0.7+: Additional capabilities such as reminders, and beyond
- v1.0: Stable, well-documented, extensible assistant

## Contributing

This is an open-source learning project built incrementally. Contributions and suggestions are welcome via GitHub issues or pull requests. Please preserve existing functionality when adding features.

## License

MIT License (planned) - see LICENSE for details.

# RobiDev-AI

A modular, extensible AI assistant — built incrementally from v0.1

## Current Version: v0.2

A minimal assistant that:
- Accepts user input via terminal
- Returns rule-based responses
- Remembers the user's name across sessions using persistent JSON memory
- Has a clean, extensible project structure

### v0.2 additions
- `config.py` — centralized file paths and settings
- `memory.py` — loads/saves conversation memory as JSON in `data/memory.json`
- Chatbot now detects "my name is ___" and personalizes greetings
## Project Structure

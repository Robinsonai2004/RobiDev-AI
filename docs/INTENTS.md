# Intent System Guide

This document explains how RobiDev AI understands and responds to different topics using its intent system (`app/intents.py` + `app/intent_matcher.py`).

## Purpose

Instead of writing a new if/elif branch in chatbot.py for every topic, RobiDev AI stores topics as data in `intents.py`. This keeps conversation logic separate from conversation content, so new topics can be added without touching the core chatbot code.

## How Matching Works

Each intent has a list of keyword phrases and a list of possible responses. `match_intent()` in intent_matcher.py lowercases the user input, then checks each intent's keywords for a substring match. The first matching intent wins, and a random response from its list is returned.

## Response Variety

Each intent can have multiple responses. `get_response_for_intent()` picks one at random using `random.choice()`, so the bot does not repeat the exact same line every time.

## How to Add a New Intent

1. Open app/intents.py
2. Add a new key to the INTENTS dictionary
3. Give it a "keywords" list of trigger phrases
4. Give it a "responses" list with one or more replies
5. No changes needed in chatbot.py or intent_matcher.py

## Example

```python
"joke": {
    "keywords": ["tell me a joke", "make me laugh"],
    "responses": [
        "Why did the function return early? It had a good reason!",
    ],
},
```

## Best Practices

- Keep keywords lowercase, since input is lowercased before matching
- Avoid keywords that are common substrings of unrelated phrases
- Provide at least 2-3 response variants for natural variety
- Topics needing access to memory (like personalized greetings) belong in chatbot.py, not here

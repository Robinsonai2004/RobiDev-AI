# Changelog

All notable changes to RobiDev AI are documented here.

## v0.6 - Registry Architecture and New Capabilities

This release introduces the plug-in architecture that all future capabilities will build on, plus four new capabilities built on top of it.

### Added
- Capability router: a registry-based dispatcher in capability_router.py that tries each registered capability in turn and returns the first response it gets. New capabilities plug in with one module plus one line in the registry, with no changes needed to chatbot.py or any other existing module.
- conversation.py: the core conversational capabilities (forgetting, name learning and correction, greetings, elaboration follow-ups, conversation repair, subject tracking, pronoun fallback) extracted into their own module, following the same handler contract as every other capability.
- echo.py: a minimal reference capability demonstrating the plug-in contract end-to-end.
- notes.py: add, view, delete, clear, and count personal notes, stored persistently and backward-compatible with older memory files.
- weather.py: current weather conditions by city (temperature, feels-like, humidity, wind, condition), via OpenWeatherMap.
- web_search.py: general topic search, question-style queries, and latest-news phrasing, via Firecrawl, returning a concise summary with title, source, and link.

### Changed
- Version string unified: config.py is now the single source of truth for the app version, and skills.py reads it directly instead of duplicating a separate hardcoded string.
- README.md rewritten to describe the current architecture and all current capabilities.

### Stability
- Every capability handler runs inside the router's try/except, so a failure in one capability cannot crash the whole assistant.
- All external-API capabilities (weather, web_search) handle missing API keys, connection errors, timeouts, non-200 responses, and malformed JSON gracefully, with a specific message for each case rather than a crash.
- Full regression testing performed after every step; no existing feature was removed or altered in behavior throughout this release.

## v0.5 - Skills and Personal Facts

### Added
- skills.py: built-in utility skills (date, time, calculator, help, version).
- facts.py: a personal knowledge system that learns, recalls, updates, and forgets user-specific facts such as favorite color, hometown, birthday, field of study, and favorite programming language.
- Free-text subject tracking and pronoun follow-up resolution.

## v0.4 - Conversation Memory Improvements

### Added
- Memory now saves after every exchange, not just on exit, to protect against data loss from crashes or force-closes.
- In-session conversation context, separate from persistent memory, for simple follow-up understanding.
- Graceful Ctrl+C exit with a final save.

## v0.3 - Greeting and Intent Improvements

### Added
- Keyword-based intent system with response variety.
- Personalized greetings once the user's name is known.

## v0.2 - Configuration and Memory

### Added
- Centralized configuration (config.py).
- Persistent memory saved to and loaded from disk as JSON.

## v0.1 - Base Chatbot

### Added
- Initial chatbot with basic name detection and conversational responses.

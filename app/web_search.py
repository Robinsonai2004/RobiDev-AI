"""
RobiDev AI - Web Search
v0.6 Step 5: looks up a topic on the web using the Firecrawl search
API and returns the single most relevant result as a short, readable
summary - title, a trimmed description, the source domain, and a
link. Like weather.py, every failure mode is handled explicitly so
nothing here ever reaches the user as a crash or raw JSON.

Trigger phrasing:
    search <topic>
    search for <topic>
    who invented <thing>
    who is/was <person>
    tell me about <topic>
    find information about <topic>
    latest <topic> news

This is intentionally the broadest, most permissive capability in
the router - it should be registered near the end of CAPABILITIES so
narrower, more specific handlers (skills, facts, intents, etc.) all
get first refusal on a message before this catches it.

Follows the same ctx-based handler contract as every other capability:

    handle(ctx: dict) -> (response: str, topic_name: str or None) or None
"""

import re
import requests
from urllib.parse import urlparse
from config import FIRECRAWL_API_KEY

_API_URL = "https://api.firecrawl.dev/v1/search"
_TIMEOUT_SECONDS = 8
_MAX_DESCRIPTION_LENGTH = 220

_NEWS_PATTERN = re.compile(r"latest (.+) news")

# Checked in order; longer/more specific phrasing first ("search for "
# before "search ") so the shorter trigger doesn't swallow "for" as
# part of the query.
_TRIGGERS = [
    "search for ",
    "search ",
    "who invented ",
    "who is ",
    "who was ",
    "find information about ",
    "find information on ",
]

_BARE_TRIGGERS = {"search", "latest news", "latest"}


def _extract_query(user_input: str, lower_text: str):
    """
    Returns (query, matched). matched is True if this message was
    search-related at all, so a bare "search" with no topic can be
    told to ask for one rather than falling through to None and
    letting some other capability misread it.
    """
    news_match = _NEWS_PATTERN.search(lower_text)
    if news_match:
        topic = news_match.group(1).strip().strip("?.!,")
        if topic:
            return f"{topic} news", True
        return None, True

    if lower_text.strip().strip("?.!,") in _BARE_TRIGGERS:
        return None, True

    for trigger in _TRIGGERS:
        idx = lower_text.find(trigger)
        if idx != -1:
            remainder = user_input[idx + len(trigger):].strip().strip("?.!,").strip()
            return (remainder if remainder else None), True

    return None, False


def _format_result(query: str, result: dict) -> str:
    """Build a short, readable summary from the top search result."""
    title = result.get("title") or "Untitled result"
    description = result.get("description") or ""
    url = result.get("url") or ""

    if len(description) > _MAX_DESCRIPTION_LENGTH:
        description = description[: _MAX_DESCRIPTION_LENGTH - 3].rstrip() + "..."

    domain = urlparse(url).netloc if url else None

    parts = [f'Here\'s what I found about "{query}":', title]
    if description:
        parts.append(description)
    source_line = []
    if domain:
        source_line.append(f"Source: {domain}")
    if url:
        source_line.append(url)
    if source_line:
        parts.append(" — ".join(source_line))

    return "\n\n".join(parts)


def handle(ctx: dict):
    query, matched = _extract_query(ctx["user_input"], ctx["lower_text"])
    if not matched:
        return None

    if not query:
        return "Sure — what would you like me to search for?", "web_search"

    if not FIRECRAWL_API_KEY:
        return (
            "Web search isn't set up yet — an API key is missing. "
            "Ask my developer to configure FIRECRAWL_API_KEY.",
            "web_search",
        )

    try:
        response = requests.post(
            _API_URL,
            headers={
                "Authorization": f"Bearer {FIRECRAWL_API_KEY}",
                "Content-Type": "application/json",
            },
            json={"query": query},
            timeout=_TIMEOUT_SECONDS,
        )
    except requests.exceptions.Timeout:
        return f"The search service took too long to respond for \"{query}\". Try again in a bit?", "web_search"
    except requests.exceptions.ConnectionError:
        return "I can't reach the search service right now — check your internet connection.", "web_search"
    except requests.exceptions.RequestException:
        return f"Something went wrong reaching the search service for \"{query}\".", "web_search"

    if response.status_code == 401:
        return "The search service rejected my API key — it may be invalid or expired.", "web_search"
    if response.status_code == 429:
        return "I've hit the search service's rate limit — try again in a little while.", "web_search"
    if response.status_code != 200:
        return f"The search service had a problem (status {response.status_code}). Try again shortly.", "web_search"

    try:
        payload = response.json()
    except ValueError:
        return f"I got a response for \"{query}\", but couldn't make sense of it.", "web_search"

    if not payload.get("success"):
        return f"The search for \"{query}\" didn't come back successfully. Try rephrasing it?", "web_search"

    results = payload.get("data") or []
    if not results:
        return f"I couldn't find anything about \"{query}\".", "web_search"

    try:
        return _format_result(query, results[0]), "web_search"
    except (KeyError, IndexError, AttributeError):
        return f"I got results for \"{query}\", but couldn't format them properly.", "web_search"

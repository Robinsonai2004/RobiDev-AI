"""
RobiDev AI - Weather
v0.6 Step 4: looks up current weather conditions for a city using the
OpenWeatherMap API. This is the first capability with an external
network dependency, so every failure mode is handled explicitly -
no exception here should ever propagate up and crash the assistant
(the router's per-handler try/except is a safety net, not a
substitute for handling known failure cases with a helpful message).

Trigger phrasing:
    weather
    weather in <city>
    temperature in <city>
    forecast for <city>
    is it raining in <city>?

If no city is given, ask for one rather than guessing.

Follows the same ctx-based handler contract as every other capability:

    handle(ctx: dict) -> (response: str, topic_name: str or None) or None
"""

import re
import requests
from config import OPENWEATHER_API_KEY

_API_URL = "https://api.openweathermap.org/data/2.5/weather"
_TIMEOUT_SECONDS = 6

# Each pattern captures the city name in group 1. Checked in order;
# the bare "weather"/"forecast" (no city) case is handled separately.
_CITY_PATTERNS = [
    re.compile(r"weather (?:in|for|at) (.+)"),
    re.compile(r"temperature (?:in|for|at) (.+)"),
    re.compile(r"forecast (?:for|in) (.+)"),
    re.compile(r"is it raining in (.+?)\??$"),
]

_BARE_TRIGGERS = ["weather", "forecast"]


def _extract_city(normalized: str):
    """
    Returns (city, matched) where matched is True if this message was
    weather-related at all (so a bare "weather" with no city can be
    told to ask for one, rather than falling through to None and
    letting some other capability misinterpret it).
    """
    for pattern in _CITY_PATTERNS:
        match = pattern.search(normalized)
        if match:
            city = match.group(1).strip().strip("?.!,")
            return city, True

    if normalized in _BARE_TRIGGERS or any(
        normalized.startswith(t + " ") for t in _BARE_TRIGGERS
    ):
        return None, True

    return None, False


def _describe(data: dict) -> str:
    """Build the natural-language response from a successful API payload."""
    city = data.get("name", "that area")
    main = data.get("main", {})
    weather_list = data.get("weather", [])
    wind = data.get("wind", {})

    condition = weather_list[0]["description"] if weather_list else "unknown conditions"
    temp = main.get("temp")
    feels_like = main.get("feels_like")
    humidity = main.get("humidity")
    wind_speed = wind.get("speed")

    parts = [f"Right now in {city}, it's {condition}"]
    if temp is not None:
        parts.append(f"at {temp}°C")
    response = " ".join(parts) + "."

    extras = []
    if feels_like is not None:
        extras.append(f"feels like {feels_like}°C")
    if humidity is not None:
        extras.append(f"{humidity}% humidity")
    if wind_speed is not None:
        extras.append(f"wind {wind_speed} m/s")

    if extras:
        response += " " + ", ".join(extras).capitalize() + "."

    return response


def handle(ctx: dict):
    normalized = ctx["normalized"]
    city, matched = _extract_city(normalized)
    if not matched:
        return None

    if not city:
        return "Sure — which city's weather would you like?", "weather"

    if not OPENWEATHER_API_KEY:
        return (
            "Weather lookups aren't set up yet — an API key is missing. "
            "Ask my developer to configure OPENWEATHER_API_KEY.",
            "weather",
        )

    try:
        response = requests.get(
            _API_URL,
            params={"q": city, "appid": OPENWEATHER_API_KEY, "units": "metric"},
            timeout=_TIMEOUT_SECONDS,
        )
    except requests.exceptions.Timeout:
        return f"The weather service took too long to respond for {city}. Try again in a bit?", "weather"
    except requests.exceptions.ConnectionError:
        return "I can't reach the weather service right now — check your internet connection.", "weather"
    except requests.exceptions.RequestException:
        return f"Something went wrong reaching the weather service for {city}.", "weather"

    if response.status_code == 401:
        return "The weather service rejected my API key — it may be invalid or not yet active.", "weather"
    if response.status_code == 404:
        return f"I couldn't find a city called \"{city}\" — could you check the spelling?", "weather"
    if response.status_code != 200:
        return f"The weather service had a problem (status {response.status_code}). Try again shortly.", "weather"

    try:
        data = response.json()
        return _describe(data), "weather"
    except (ValueError, KeyError, IndexError):
        return f"I got a response for {city}, but couldn't make sense of it.", "weather"

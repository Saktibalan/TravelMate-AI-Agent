"""
Weather tool — wraps OpenWeather's API to give the Research Agent
context on expected conditions during the trip.
"""

import logging
import httpx
from backend.config import settings

logger = logging.getLogger(__name__)

WEATHER_URL = "https://api.openweathermap.org/data/2.5/forecast"


async def get_weather_summary(destination: str) -> dict:
    """
    Returns a short weather summary dict for the destination.
    Falls back to a neutral placeholder if the API key is missing
    or the request fails, so it never blocks the rest of the pipeline.
    """
    if not settings.OPENWEATHER_API_KEY:
        logger.warning("OPENWEATHER_API_KEY missing - returning placeholder weather.")
        return {"summary": "Weather data unavailable", "avg_temp_c": None}

    params = {
        "q": destination,
        "appid": settings.OPENWEATHER_API_KEY,
        "units": "metric",
    }

    try:
        async with httpx.AsyncClient(timeout=10) as client:
            resp = await client.get(WEATHER_URL, params=params)
            resp.raise_for_status()
            data = resp.json()
    except httpx.HTTPError as exc:
        logger.error(f"Weather lookup failed: {exc}")
        return {"summary": "Weather data unavailable", "avg_temp_c": None}

    forecasts = data.get("list", [])
    if not forecasts:
        return {"summary": "No forecast available", "avg_temp_c": None}

    avg_temp = sum(f["main"]["temp"] for f in forecasts) / len(forecasts)
    conditions = forecasts[0]["weather"][0]["description"]

    return {
        "summary": f"Expect {conditions}, average around {avg_temp:.1f}°C",
        "avg_temp_c": round(avg_temp, 1),
    }

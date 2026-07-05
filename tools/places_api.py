"""
Places tool — wraps Google Places API (Text Search) to find attractions,
restaurants, and points of interest matching user interests.

When GOOGLE_PLACES_API_KEY is not configured, falls back to the AI-powered
ai_places.py tool which uses Anthropic Claude to return real, verified places
instead of the old placeholder stub data.
"""

import logging
import httpx
from urllib.parse import quote_plus
from backend.config import settings
from backend.schemas import ActivityItem
from backend.tools.ai_places import ai_search_places

logger = logging.getLogger(__name__)

PLACES_URL = "https://maps.googleapis.com/maps/api/place/textsearch/json"


async def search_places(
    destination: str,
    interest: str,
    limit: int = 5,
    place_type: str = "attraction",
) -> list[ActivityItem]:
    """
    Searches for places matching a given interest (e.g. "museums",
    "street food", "hiking") in the destination city.

    Falls back to Claude AI recommendations (real places) when the Google
    Places API key is not configured — never returns stub/placeholder data.
    """
    if not settings.GOOGLE_PLACES_API_KEY:
        logger.info(
            "GOOGLE_PLACES_API_KEY not set - using Claude AI for real place recommendations."
        )
        return await ai_search_places(destination, interest, limit=limit, place_type=place_type)

    params = {
        "query": f"{interest} in {destination}",
        "key": settings.GOOGLE_PLACES_API_KEY,
    }

    try:
        async with httpx.AsyncClient(timeout=15) as client:
            resp = await client.get(PLACES_URL, params=params)
            resp.raise_for_status()
            results = resp.json().get("results", [])[:limit]
    except httpx.HTTPError as exc:
        logger.error(f"Google Places search failed: {exc} - falling back to Claude AI.")
        return await ai_search_places(destination, interest, limit=limit, place_type=place_type)

    items: list[ActivityItem] = []
    for place in results:
        name = place.get("name", "")
        address = place.get("formatted_address", "")
        rating = place.get("rating")
        maps_url = (
            f"https://maps.google.com/?q={quote_plus(name + ' ' + destination)}"
        )
        items.append(
            ActivityItem(
                name=name,
                category=interest,
                estimated_cost=_estimate_cost(place.get("price_level")),
                duration_hours=2.0,
                notes=address,
                place_type=place_type,
                address=address,
                rating=rating,
                google_maps_url=maps_url,
            )
        )
    return items


def _estimate_cost(price_level: int | None) -> float:
    """Google's price_level is 0-4; convert to a rough USD estimate."""
    mapping = {0: 0.0, 1: 10.0, 2: 25.0, 3: 50.0, 4: 90.0}
    return mapping.get(price_level, 15.0)

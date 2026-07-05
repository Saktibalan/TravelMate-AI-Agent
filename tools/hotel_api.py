"""
Hotel search tool. Structured to plug into Booking.com's Rapid API
(via RapidAPI) or Amadeus Hotel Search — swap the implementation of
_call_provider() without touching the rest of the app.
"""

import logging
import httpx
from backend.config import settings
from backend.schemas import HotelOption
from backend.tools.ai_places import ai_search_hotels

logger = logging.getLogger(__name__)


async def search_hotels(
    destination: str,
    max_price_per_night: float,
    min_rating: float = 3.0,
) -> list[HotelOption]:
    """
    Returns hotel options within budget, sorted by rating descending.
    """
    if not settings.BOOKING_API_KEY:
        logger.warning("BOOKING_API_KEY missing — using Claude AI for real hotel recommendations.")
        return await ai_search_hotels(destination, max_price_per_night, min_rating)

    try:
        results = await _call_provider(destination, max_price_per_night)
    except Exception as exc:
        logger.error(f"Hotel search failed: {exc} - falling back to Claude AI.")
        return await ai_search_hotels(destination, max_price_per_night, min_rating)

    filtered = [h for h in results if h.rating is None or h.rating >= min_rating]
    return sorted(filtered, key=lambda h: h.rating or 0, reverse=True)


async def _call_provider(destination: str, max_price: float) -> list[HotelOption]:
    """Placeholder for real provider integration (Booking.com / Amadeus)."""
    # Example shape for a real implementation:
    # async with httpx.AsyncClient(timeout=15) as client:
    #     resp = await client.get(PROVIDER_URL, headers=..., params=...)
    #     resp.raise_for_status()
    #     return [HotelOption(**item) for item in resp.json()["results"]]
    return _mock_hotels(destination, max_price)


def _mock_hotels(destination: str, max_price: float) -> list[HotelOption]:
    return [
        HotelOption(
            name=f"{destination} Central Hotel",
            price_per_night=min(85.0, max_price),
            rating=4.2,
            address=f"123 Main St, {destination}",
        ),
        HotelOption(
            name=f"{destination} Budget Inn",
            price_per_night=min(45.0, max_price),
            rating=3.6,
            address=f"45 Traveler Ave, {destination}",
        ),
    ]

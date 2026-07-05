"""
Flight search tool — wraps the Amadeus Flight Offers Search API.
Falls back to mock data if API keys are not configured, so the app
is runnable end-to-end during development without live credentials.
"""

import logging
from datetime import date
import httpx
from backend.config import settings
from backend.schemas import FlightOption

logger = logging.getLogger(__name__)

AMADEUS_TOKEN_URL = "https://test.api.amadeus.com/v1/security/oauth2/token"
AMADEUS_FLIGHT_URL = "https://test.api.amadeus.com/v2/shopping/flight-offers"


async def _get_amadeus_token() -> str | None:
    if not settings.AMADEUS_API_KEY or not settings.AMADEUS_API_SECRET:
        return None
    async with httpx.AsyncClient(timeout=10) as client:
        resp = await client.post(
            AMADEUS_TOKEN_URL,
            data={
                "grant_type": "client_credentials",
                "client_id": settings.AMADEUS_API_KEY,
                "client_secret": settings.AMADEUS_API_SECRET,
            },
        )
        resp.raise_for_status()
        return resp.json()["access_token"]


async def search_flights(
    origin: str,
    destination: str,
    departure_date: date,
    return_date: date | None = None,
    travelers: int = 1,
) -> list[FlightOption]:
    """
    Returns a list of FlightOption objects sorted by price ascending.
    Raises no exceptions to the caller — errors are logged and an
    empty list is returned so the orchestrator can decide how to proceed.
    """
    try:
        token = await _get_amadeus_token()
    except Exception as exc:
        logger.error(f"Failed to get Amadeus token: {exc} - falling back to mock flight data.")
        return _mock_flights(origin, destination)

    if token is None:
        logger.warning("AMADEUS credentials missing - returning mock flight data.")
        return _mock_flights(origin, destination)

    params = {
        "originLocationCode": origin,
        "destinationLocationCode": destination,
        "departureDate": departure_date.isoformat(),
        "adults": travelers,
        "currencyCode": "USD",
        "max": 5,
    }
    if return_date:
        params["returnDate"] = return_date.isoformat()

    try:
        async with httpx.AsyncClient(timeout=15) as client:
            resp = await client.get(
                AMADEUS_FLIGHT_URL,
                headers={"Authorization": f"Bearer {token}"},
                params=params,
            )
            resp.raise_for_status()
            data = resp.json().get("data", [])
    except httpx.HTTPError as exc:
        logger.error(f"Flight search failed: {exc}")
        return []

    results = []
    for offer in data:
        itinerary = offer["itineraries"][0]
        segments = itinerary["segments"]
        results.append(
            FlightOption(
                airline=segments[0]["carrierCode"],
                price=float(offer["price"]["total"]),
                departure_time=segments[0]["departure"]["at"],
                arrival_time=segments[-1]["arrival"]["at"],
                duration=itinerary["duration"],
                stops=len(segments) - 1,
            )
        )
    return sorted(results, key=lambda f: f.price)


def _mock_flights(origin: str, destination: str) -> list[FlightOption]:
    return [
        FlightOption(
            airline="MockAir",
            price=349.00,
            departure_time="08:00",
            arrival_time="14:30",
            duration="PT6H30M",
            stops=0,
        ),
        FlightOption(
            airline="BudgetJet",
            price=219.00,
            departure_time="22:15",
            arrival_time="09:45",
            duration="PT11H30M",
            stops=1,
        ),
    ]

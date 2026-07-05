"""
Hotel Agent — finds a suitable stay within the remaining budget
after flights have been priced.
"""

import logging
from backend.schemas import AgentState
from backend.tools.hotel_api import search_hotels

logger = logging.getLogger(__name__)


async def run_hotel_agent(state: AgentState) -> AgentState:
    req = state["trip_request"]
    trip_days = max((req.end_date - req.start_date).days, 1)

    flights_cost = sum(f.price for f in state["flights"][:1])  # cheapest option
    remaining_budget = req.budget - flights_cost
    max_per_night = max(remaining_budget * 0.4 / trip_days, 20.0)

    logger.info(f"[HotelAgent] Searching hotels in {req.destination}, max/night={max_per_night:.2f}")

    try:
        hotels = await search_hotels(
            destination=req.destination,
            max_price_per_night=max_per_night,
        )
        if hotels:
            state["hotel"] = hotels[0]
        else:
            state["warnings"].append("No hotels found within budget.")
    except Exception as exc:
        logger.error(f"[HotelAgent] Failed: {exc}")
        state["errors"].append(f"Hotel search failed: {exc}")

    return state

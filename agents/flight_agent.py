"""
Flight Agent — finds and ranks flight options for the trip.
"""

import logging
from backend.schemas import AgentState
from backend.tools.flight_api import search_flights

logger = logging.getLogger(__name__)


async def run_flight_agent(state: AgentState) -> AgentState:
    req = state["trip_request"]
    logger.info(f"[FlightAgent] Searching flights {req.origin} -> {req.destination}")

    try:
        flights = await search_flights(
            origin=req.origin,
            destination=req.destination,
            departure_date=req.start_date,
            return_date=req.end_date,
            travelers=req.travelers,
        )
        state["flights"] = flights
        if not flights:
            state["warnings"].append("No flights found for the selected dates.")
    except Exception as exc:
        logger.error(f"[FlightAgent] Failed: {exc}")
        state["errors"].append(f"Flight search failed: {exc}")

    return state

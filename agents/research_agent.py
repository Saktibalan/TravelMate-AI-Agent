"""
Research Agent — gathers destination context: weather, and any
general notes that later agents (Itinerary, Budget) will use.
"""

import logging
from backend.schemas import AgentState
from backend.tools.weather_api import get_weather_summary

logger = logging.getLogger(__name__)


async def run_research_agent(state: AgentState) -> AgentState:
    logger.info(f"[ResearchAgent] Researching {state['trip_request'].destination}")

    try:
        weather = await get_weather_summary(state["trip_request"].destination)
        state["research_notes"]["weather"] = weather
    except Exception as exc:
        logger.error(f"[ResearchAgent] Failed to fetch weather: {exc}")
        state["warnings"].append("Could not fetch weather data for destination.")

    state["research_notes"]["destination"] = state["trip_request"].destination
    state["research_notes"]["trip_length_days"] = (
        state["trip_request"].end_date - state["trip_request"].start_date
    ).days

    return state

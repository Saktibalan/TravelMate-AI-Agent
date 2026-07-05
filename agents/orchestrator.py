"""
Orchestrator — wires all agents into a LangGraph state machine.

Flow:
  recall_preferences -> research -> flights -> hotel -> itinerary
  -> budget -> store_memory -> END

Each node mutates and returns the shared AgentState. If a node adds
to state.errors, the graph still continues (agents degrade gracefully
rather than crashing the whole run) — the final Itinerary will surface
warnings/errors to the user.
"""

import logging
from langgraph.graph import StateGraph, END

from backend.schemas import AgentState, TripRequest, Itinerary, WeatherInfo
from backend.agents.memory_agent import recall_preferences, store_trip_memory
from backend.agents.research_agent import run_research_agent
from backend.agents.flight_agent import run_flight_agent
from backend.agents.hotel_agent import run_hotel_agent
from backend.agents.itinerary_agent import run_itinerary_agent
from backend.agents.budget_agent import run_budget_agent

logger = logging.getLogger(__name__)


def build_graph():
    graph = StateGraph(AgentState)

    graph.add_node("recall_preferences", recall_preferences)
    graph.add_node("research", run_research_agent)
    graph.add_node("search_flights", run_flight_agent)
    graph.add_node("search_hotels", run_hotel_agent)
    graph.add_node("build_itinerary", run_itinerary_agent)
    graph.add_node("calculate_budget", run_budget_agent)
    graph.add_node("store_memory", store_trip_memory)

    graph.set_entry_point("recall_preferences")
    graph.add_edge("recall_preferences", "research")
    graph.add_edge("research", "search_flights")
    graph.add_edge("search_flights", "search_hotels")
    graph.add_edge("search_hotels", "build_itinerary")
    graph.add_edge("build_itinerary", "calculate_budget")
    graph.add_edge("calculate_budget", "store_memory")
    graph.add_edge("store_memory", END)

    return graph.compile()


_compiled_graph = build_graph()


async def plan_trip(trip_request: TripRequest) -> Itinerary:
    """
    Main entry point used by the FastAPI route.
    Runs the full multi-agent pipeline and returns a validated Itinerary.
    """
    initial_state = AgentState(
        trip_request=trip_request,
        research_notes={},
        flights=[],
        hotel=None,
        days=[],
        budget_summary=None,
        warnings=[],
        errors=[],
    )

    logger.info(f"[Orchestrator] Starting trip planning for {trip_request.destination}")
    final_state: AgentState = await _compiled_graph.ainvoke(initial_state)

    weather_data = final_state.get("research_notes", {}).get("weather", {})
    weather = (
        WeatherInfo(**weather_data)
        if weather_data and "summary" in weather_data
        else None
    )

    itinerary = Itinerary(
        trip_request=trip_request,
        flights=final_state.get("flights", []),
        hotel=final_state.get("hotel"),
        days=final_state.get("days", []),
        budget_summary=final_state.get("budget_summary"),
        weather=weather,
        warnings=final_state.get("warnings", []) + final_state.get("errors", []),
    )

    logger.info(
        f"[Orchestrator] Completed with {len(final_state.get('warnings', []))} warnings, "
        f"{len(final_state.get('errors', []))} errors."
    )
    return itinerary

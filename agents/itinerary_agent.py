"""
Itinerary Agent — builds a day-by-day plan using the user's interests,
pulling candidate activities via the Places tool and distributing them
evenly across the trip length.
"""

import logging
from datetime import timedelta
from backend.schemas import AgentState, DayPlan, ActivityItem
from backend.tools.places_api import search_places

logger = logging.getLogger(__name__)

DEFAULT_MEALS = ["Breakfast", "Lunch", "Dinner"]


async def run_itinerary_agent(state: AgentState) -> AgentState:
    req = state["trip_request"]
    trip_days = max((req.end_date - req.start_date).days, 1)
    interests = req.interests or ["sightseeing"]

    logger.info(f"[ItineraryAgent] Building {trip_days}-day plan for interests={interests}")

    all_activities: list[ActivityItem] = []
    for interest in interests:
        try:
            activities = await search_places(req.destination, interest, limit=trip_days)
            all_activities.extend(activities)
        except Exception as exc:
            logger.error(f"[ItineraryAgent] Places search failed for '{interest}': {exc}")
            state["warnings"].append(f"Could not fetch activities for interest: {interest}")

    if not all_activities:
        state["warnings"].append("No activities found - itinerary will only include meals.")

    days: list[DayPlan] = []
    for day_index in range(trip_days):
        day_activities = all_activities[day_index :: trip_days] if all_activities else []
        day_cost = sum(a.estimated_cost for a in day_activities)
        days.append(
            DayPlan(
                day_number=day_index + 1,
                date=req.start_date + timedelta(days=day_index),
                activities=day_activities,
                meals=DEFAULT_MEALS,
                estimated_day_cost=day_cost,
            )
        )

    state["days"] = days
    return state

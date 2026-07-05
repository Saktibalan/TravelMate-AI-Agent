"""
Budget Agent — totals up all costs collected by prior agents and
flags whether the trip is within the user's stated budget.
"""

import logging
from backend.schemas import AgentState, BudgetSummary

logger = logging.getLogger(__name__)

ESTIMATED_FOOD_COST_PER_DAY = 30.0


async def run_budget_agent(state: AgentState) -> AgentState:
    req = state["trip_request"]
    trip_days = max((req.end_date - req.start_date).days, 1)

    flights_cost = state["flights"][0].price if state["flights"] else 0.0
    hotel_cost = (state["hotel"].price_per_night * trip_days) if state["hotel"] else 0.0
    activities_cost = sum(day.estimated_day_cost for day in state["days"])
    food_cost = ESTIMATED_FOOD_COST_PER_DAY * trip_days * req.travelers

    total = flights_cost + hotel_cost + activities_cost + food_cost
    remaining = req.budget - total

    summary = BudgetSummary(
        total_budget=req.budget,
        flights_cost=flights_cost,
        hotel_cost=hotel_cost,
        activities_cost=activities_cost,
        food_cost=food_cost,
        remaining=remaining,
        over_budget=remaining < 0,
    )

    if summary.over_budget:
        state["warnings"].append(
            f"Estimated trip cost (${total:.2f}) exceeds budget "
            f"(${req.budget:.2f}) by ${abs(remaining):.2f}."
        )

    logger.info(f"[BudgetAgent] Total estimated cost: ${total:.2f} (budget ${req.budget:.2f})")
    state["budget_summary"] = summary
    return state

"""
Shared data models used across agents, tools, and API routes.
Using Pydantic ensures every agent hands off clean, validated data.
"""

from typing import Optional, TypedDict
from pydantic import BaseModel, Field
from datetime import date


class WeatherInfo(BaseModel):
    summary: str
    avg_temp_c: Optional[float] = None


class TripRequest(BaseModel):
    destination: str
    origin: str
    start_date: date
    end_date: date
    budget: float
    currency: str = "USD"
    travelers: int = 1
    interests: list[str] = Field(default_factory=list)
    user_id: Optional[str] = None


class FlightOption(BaseModel):
    airline: str
    price: float
    departure_time: str
    arrival_time: str
    duration: str
    stops: int
    booking_link: Optional[str] = None


class HotelOption(BaseModel):
    name: str
    price_per_night: float
    rating: Optional[float] = None
    address: str
    booking_link: Optional[str] = None
    # Rich fields added for real AI-powered recommendations
    description: Optional[str] = None
    google_maps_url: Optional[str] = None
    why_visit: Optional[str] = None
    amenities: list[str] = Field(default_factory=list)
    opening_hours: Optional[str] = None


class ActivityItem(BaseModel):
    name: str
    category: str
    estimated_cost: float
    duration_hours: float
    notes: Optional[str] = None
    # Rich fields added for real AI-powered recommendations
    place_type: str = "attraction"   # "attraction" | "restaurant" | "shopping"
    address: Optional[str] = None
    rating: Optional[float] = None
    opening_hours: Optional[str] = None
    google_maps_url: Optional[str] = None
    why_visit: Optional[str] = None


class DayPlan(BaseModel):
    day_number: int
    date: date
    activities: list[ActivityItem] = Field(default_factory=list)
    restaurants: list[ActivityItem] = Field(default_factory=list)
    shopping: list[ActivityItem] = Field(default_factory=list)
    meals: list[str] = Field(default_factory=list)
    estimated_day_cost: float = 0.0


class BudgetSummary(BaseModel):
    total_budget: float
    flights_cost: float = 0.0
    hotel_cost: float = 0.0
    activities_cost: float = 0.0
    food_cost: float = 0.0
    remaining: float = 0.0
    over_budget: bool = False


class Itinerary(BaseModel):
    trip_request: TripRequest
    flights: list[FlightOption] = Field(default_factory=list)
    hotel: Optional[HotelOption] = None
    days: list[DayPlan] = Field(default_factory=list)
    budget_summary: Optional[BudgetSummary] = None
    weather: Optional[WeatherInfo] = None
    warnings: list[str] = Field(default_factory=list)


class AgentState(TypedDict):
    """The shared state object passed between nodes in the LangGraph."""
    trip_request: TripRequest
    research_notes: dict
    flights: list[FlightOption]
    hotel: Optional[HotelOption]
    days: list[DayPlan]
    budget_summary: Optional[BudgetSummary]
    warnings: list[str]
    errors: list[str]

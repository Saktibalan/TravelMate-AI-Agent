"""
FastAPI application entrypoint for TravelMate AI.
Run with: uvicorn backend.main:app --reload
"""

import os
import logging
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from backend.config import validate_settings
from backend.schemas import TripRequest, Itinerary
from backend.agents.orchestrator import plan_trip

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="TravelMate AI", version="1.0.0")

# Build allowed origins: always include localhost for dev, plus FRONTEND_URL for production
allowed_origins = ["http://localhost:5173", "http://localhost:3000", "http://localhost"]
frontend_url = os.getenv("FRONTEND_URL", "")
if frontend_url:
    allowed_origins.append(frontend_url)

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
async def on_startup():
    missing = validate_settings()
    if missing:
        logger.warning(f"Missing environment variables (mock data will be used): {missing}")


@app.get("/health")
async def health_check():
    return {"status": "ok"}


@app.post("/api/plan-trip", response_model=Itinerary)
async def plan_trip_route(request: TripRequest):
    if request.end_date <= request.start_date:
        raise HTTPException(status_code=400, detail="end_date must be after start_date")
    if request.budget <= 0:
        raise HTTPException(status_code=400, detail="budget must be greater than zero")

    try:
        itinerary = await plan_trip(request)
        return itinerary
    except Exception as exc:
        logger.exception("Trip planning failed")
        raise HTTPException(status_code=500, detail=f"Trip planning failed: {exc}")

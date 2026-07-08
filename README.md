# TravelMate AI — Agentic Travel Planner

An agentic AI system that plans complete trips (flights, hotels, day-by-day
itinerary, and budget tracking) using a multi-agent pipeline orchestrated
with LangGraph.
DEMO LINK : 
https://amazing-churros-516a77.netlify.app/

## Architecture

```
User Request
     │
     ▼
Orchestrator (LangGraph state machine)
     │
     ├─► Memory Agent      (recall past preferences)
     ├─► Research Agent    (weather, destination context)
     ├─► Flight Agent      (Amadeus API)
     ├─► Hotel Agent       (Booking-style API)
     ├─► Itinerary Agent   (Google Places API)
     ├─► Budget Agent      (cost aggregation + budget check)
     └─► Memory Agent      (store trip summary)
     │
     ▼
Structured Itinerary (JSON) → Frontend
```

Every agent degrades gracefully: if an API key is missing or a call fails,
mock data is used and a warning is attached to the final itinerary instead
of crashing the pipeline.

## Prerequisites

- Python 3.11+
- Node.js 18+ (for frontend)
- PostgreSQL 14+ (optional for MVP — mock/no-op if not configured)

## Backend Setup

```bash
cd backend
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp ../.env.example ../.env      # then fill in your API keys
uvicorn main:app --reload
```

API will be live at `http://localhost:8000`. Interactive docs at
`http://localhost:8000/docs`.

## Frontend Setup

```bash
cd frontend
npm install
npm run dev
```

Frontend will be live at `http://localhost:5173`.

## Environment Variables

See `.env.example` for the full list. At minimum, the app runs fully
with **mock data** and no keys configured — useful for local development.
For real results, obtain free/test-tier keys from:

- **Anthropic** — https://console.anthropic.com
- **Amadeus** (flights) — https://developers.amadeus.com (free self-service tier)
- **Google Places** — https://console.cloud.google.com
- **OpenWeather** — https://openweathermap.org/api

## API Usage

```bash
curl -X POST http://localhost:8000/api/plan-trip \
  -H "Content-Type: application/json" \
  -d '{
    "origin": "JFK",
    "destination": "Tokyo",
    "start_date": "2026-09-01",
    "end_date": "2026-09-07",
    "budget": 2500,
    "travelers": 1,
    "interests": ["food", "temples", "shopping"]
  }'
```

Returns a full `Itinerary` JSON object with flights, hotel, a day-by-day
plan, and a budget summary.

## Project Structure

```
travelmate-ai/
├── backend/
│   ├── agents/          # One file per agent
│   ├── tools/           # One file per external API integration
│   ├── main.py          # FastAPI app + routes
│   ├── config.py        # Env var loading
│   ├── schemas.py        # Pydantic models shared across agents
│   └── requirements.txt
├── frontend/            # React + Tailwind UI
├── database/
│   └── schema.sql
└── .env.example
```

## Next Steps / Extension Ideas

- Add a Booking.com or Expedia real integration in `tools/hotel_api.py`
- Add streaming responses so the frontend shows agent progress live
- Add a "replan" endpoint that re-runs only the Budget + Itinerary agents
  when the user tweaks their budget after seeing results
- Add authentication so `user_id` in `TripRequest` maps to real accounts

## Deployment

## Docker Compose (Local Production Test)

```bash
# Build and run all services (Postgres, backend, frontend)
docker compose up --build
```

- The backend will be reachable at `http://localhost:8000`.
- The frontend will be served on port `80` (http://localhost).
- The PostgreSQL database is initialized with the provided `schema.sql`.

## Render (Free‑Tier Cloud Deployment)

1. Push this repository to a new GitHub (or GitLab) repo.
2. In the Render dashboard, select **New > Blueprint** and upload the `render.yaml` file located at the repository root.
3. Render will automatically create:
   - A free PostgreSQL instance.
   - A Docker web service for the FastAPI backend.
   - A static site for the React frontend.
4. Add any real API keys (Anthropic, Amadeus, Google Places, OpenWeather, Booking.com) in the **Environment** tab of the backend service.
5. Deploy – Render will provide you with HTTPS URLs for both services.

## CORS Configuration

The backend now reads `FRONTEND_URL` from the environment to allow cross‑origin requests from the deployed frontend. For local development, the default localhost origins remain.

## Environment Variables

| Variable | Description | Default |
|---|---|---|
| `ANTHROPIC_API_KEY` | Anthropic LLM API key | (empty – mock mode) |
| `LLM_MODEL` | Model name for the LLM | `claude-sonnet-4-6` |
| `AMADEUS_API_KEY` / `AMADEUS_API_SECRET` | Amadeus flight API credentials | (empty – mock mode) |
| `GOOGLE_PLACES_API_KEY` | Places API key | (empty – mock mode) |
| `OPENWEATHER_API_KEY` | Weather API key | (empty – mock mode) |
| `BOOKING_API_KEY` | Hotel booking API key | (empty – mock mode) |
| `FRONTEND_URL` | URL of the deployed frontend (auto‑set by Render) | `http://localhost` |
| `DATABASE_URL` | PostgreSQL connection string | set by Docker Compose / Render |
| `CHROMA_PERSIST_DIR` | Path for local vector store | `./chroma_store` |

### Verify Deployment

- `curl http://<backend-url>/health` should return `{"status":"ok"}`.
- Open the frontend URL in a browser and run a trip plan – the full agent pipeline should execute and display results.

---

*The rest of the original README remains unchanged.*

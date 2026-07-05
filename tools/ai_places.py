"""
AI-powered place search tool — uses Anthropic Claude to return real,
verified place recommendations when live API keys are unavailable.

This replaces the old mock stub functions that returned placeholder names
like "Tokyo Food Spot #1". Claude is prompted with structured JSON output
requirements and knowledge of real-world places, restaurants, and hotels.
"""

import json
import logging
import anthropic
from backend.config import settings
from backend.schemas import ActivityItem, HotelOption

logger = logging.getLogger(__name__)

# Reusable Anthropic client (initialized lazily)
_client: anthropic.AsyncAnthropic | None = None


def _get_client() -> anthropic.AsyncAnthropic:
    global _client
    if _client is None:
        _client = anthropic.AsyncAnthropic(api_key=settings.ANTHROPIC_API_KEY)
    return _client


PLACES_SYSTEM_PROMPT = """You are a professional travel curator with expert knowledge of real-world destinations.
When asked to recommend places, ALWAYS return real, well-known, verified locations only.
NEVER invent fictional names or use placeholder text.
Return your response as a valid JSON array and nothing else — no markdown, no explanation."""

HOTELS_SYSTEM_PROMPT = """You are a professional hotel concierge with expert knowledge of real hotels worldwide.
When asked to recommend hotels, ALWAYS return real, well-known, verified hotels only.
NEVER invent fictional hotel names or use placeholder text.
Return your response as a valid JSON array and nothing else — no markdown, no explanation."""


from urllib.parse import quote_plus

MOCK_PLACES_DB = {
    "tokyo": {
        "sightseeing": [
            {
                "name": "Senso-ji Temple",
                "category": "temple",
                "description": "Tokyo's oldest and most iconic Buddhist temple in Asakusa.",
                "address": "2-3-1 Asakusa, Taito City, Tokyo",
                "rating": 4.7,
                "opening_hours": "6:00 AM - 5:00 PM",
                "estimated_cost_usd": 0.0,
                "duration_hours": 1.5,
                "why_visit": "Immerse yourself in traditional Japanese culture and walk through the historic Kaminarimon Gate."
            },
            {
                "name": "Meiji Jingu Shrine",
                "category": "shrine",
                "description": "A serene Shinto shrine dedicated to Emperor Meiji, nested within a dense forest.",
                "address": "1-1 Yoyogikamizonocho, Shibuya, Tokyo",
                "rating": 4.6,
                "opening_hours": "5:20 AM - 6:00 PM",
                "estimated_cost_usd": 0.0,
                "duration_hours": 1.5,
                "why_visit": "A peaceful escape from the bustling city, located right next to Harajuku."
            },
            {
                "name": "Tokyo Skytree",
                "category": "observatory",
                "description": "The tallest structure in Japan, offering panoramic views of the entire Tokyo metropolis.",
                "address": "1-1-2 Oshiage, Sumida City, Tokyo",
                "rating": 4.5,
                "opening_hours": "10:00 AM - 9:00 PM",
                "estimated_cost_usd": 25.0,
                "duration_hours": 2.0,
                "why_visit": "Catch breath-taking panoramic views of the city, and on clear days, even Mount Fuji."
            }
        ],
        "food": [
            {
                "name": "Tsukiji Outer Market",
                "category": "market",
                "description": "A vibrant street market packed with fresh seafood stalls, sushi restaurants, and local snacks.",
                "address": "4-16-2 Tsukiji, Chuo City, Tokyo",
                "rating": 4.4,
                "opening_hours": "5:00 AM - 2:00 PM",
                "estimated_cost_usd": 15.0,
                "duration_hours": 2.0,
                "why_visit": "Sample legendary street foods like fresh uni, Wagyu skewers, and Japanese rolled omelet."
            },
            {
                "name": "Shinjuku Omoide Yokocho",
                "category": "alleyway",
                "description": "A narrow alleyway near Shinjuku Station famous for its rustic yakitori stalls and retro vibe.",
                "address": "1-2 Nishishinjuku, Shinjuku City, Tokyo",
                "rating": 4.3,
                "opening_hours": "5:00 PM - 12:00 AM",
                "estimated_cost_usd": 20.0,
                "duration_hours": 1.5,
                "why_visit": "Experience authentic Tokyo nightlife and enjoy charcoal-grilled skewers with locals."
            }
        ],
        "shopping": [
            {
                "name": "Ginza Six",
                "category": "shopping mall",
                "description": "A luxury shopping complex featuring high-end boutiques, art installations, and a rooftop garden.",
                "address": "6-10-1 Ginza, Chuo City, Tokyo",
                "rating": 4.4,
                "opening_hours": "10:30 AM - 8:30 PM",
                "estimated_cost_usd": 50.0,
                "duration_hours": 2.0,
                "why_visit": "Indulge in premium shopping and admire stunning avant-garde art installations by Yayoi Kusama."
            },
            {
                "name": "Takeshita Street",
                "category": "shopping street",
                "description": "The colorful, bustling epicenter of Tokyo's Harajuku youth culture and quirky fashion boutiques.",
                "address": "1-17 Jingumae, Shibuya City, Tokyo",
                "rating": 4.0,
                "opening_hours": "10:00 AM - 8:00 PM",
                "estimated_cost_usd": 10.0,
                "duration_hours": 1.5,
                "why_visit": "Explore crazy fashion trends, check out rainbow-colored crepes, and enjoy the energetic street vibe."
            }
        ]
    },
    "paris": {
        "sightseeing": [
            {
                "name": "Eiffel Tower",
                "category": "landmark",
                "description": "The quintessential symbol of Paris, offering stunning views from its observation decks.",
                "address": "Champ de Mars, 5 Avenue Anatole France, Paris",
                "rating": 4.7,
                "opening_hours": "9:30 AM - 11:45 PM",
                "estimated_cost_usd": 28.0,
                "duration_hours": 2.5,
                "why_visit": "Climb Paris's most famous landmark for a breathtaking look across the River Seine."
            },
            {
                "name": "Louvre Museum",
                "category": "museum",
                "description": "The world's largest art museum, home to the Mona Lisa and thousands of historic treasures.",
                "address": "Rue de Rivoli, Paris",
                "rating": 4.7,
                "opening_hours": "9:00 AM - 6:00 PM",
                "estimated_cost_usd": 22.0,
                "duration_hours": 3.0,
                "why_visit": "Marvel at masterpieces of art history and the iconic glass pyramid entrance."
            }
        ],
        "food": [
            {
                "name": "Le Comptoir de La Gastronomie",
                "category": "bistro",
                "description": "A historic French bistro and gourmet deli serving legendary duck confit and foie gras.",
                "address": "34 Rue Montmartre, Paris",
                "rating": 4.5,
                "opening_hours": "12:00 PM - 11:00 PM",
                "estimated_cost_usd": 35.0,
                "duration_hours": 2.0,
                "why_visit": "Enjoy classic, rich French dishes in a cozy, traditional Parisian atmosphere."
            }
        ],
        "shopping": [
            {
                "name": "Galeries Lafayette Haussmann",
                "category": "department store",
                "description": "An upscale French department store under a stunning neo-byzantine glass dome.",
                "address": "40 Boulevard Haussmann, Paris",
                "rating": 4.5,
                "opening_hours": "10:00 AM - 8:00 PM",
                "estimated_cost_usd": 40.0,
                "duration_hours": 2.5,
                "why_visit": "Shop fashion brands, admire the beautiful glass dome, and visit the free rooftop terrace."
            }
        ]
    },
    "new york": {
        "sightseeing": [
            {
                "name": "Central Park",
                "category": "park",
                "description": "The green heart of Manhattan, spanning 843 acres of lawns, lakes, and walking paths.",
                "address": "Central Park, New York, NY",
                "rating": 4.8,
                "opening_hours": "6:00 AM - 1:00 AM",
                "estimated_cost_usd": 0.0,
                "duration_hours": 2.5,
                "why_visit": "Stroll or bike through iconic locations like Bethesda Fountain and Bow Bridge."
            },
            {
                "name": "Empire State Building",
                "category": "landmark",
                "description": "A world-famous Art Deco skyscraper with 360-degree open-air observation decks.",
                "address": "20 W 34th St, New York, NY",
                "rating": 4.7,
                "opening_hours": "9:00 AM - 12:00 AM",
                "estimated_cost_usd": 45.0,
                "duration_hours": 2.0,
                "why_visit": "See spectacular views of the Manhattan skyline from the 86th floor."
            }
        ],
        "food": [
            {
                "name": "Chelsea Market",
                "category": "food hall",
                "description": "An enclosed food and shopping hall located in the historic Chelsea district.",
                "address": "75 9th Ave, New York, NY",
                "rating": 4.6,
                "opening_hours": "7:00 AM - 10:00 PM",
                "estimated_cost_usd": 15.0,
                "duration_hours": 2.0,
                "why_visit": "Sample diverse cuisines from artisanal tacos to fresh lobsters under one roof."
            }
        ],
        "shopping": [
            {
                "name": "Fifth Avenue",
                "category": "shopping district",
                "description": "One of the most famous and expensive shopping streets in the world.",
                "address": "5th Ave, New York, NY",
                "rating": 4.5,
                "opening_hours": "10:00 AM - 8:00 PM",
                "estimated_cost_usd": 60.0,
                "duration_hours": 2.0,
                "why_visit": "Window-shop iconic luxury flagship stores and landmarks like Rockefeller Center."
            }
        ]
    }
}

GENERIC_PLACES = {
    "sightseeing": [
        {"name": "{destination} Landmark Plaza", "category": "sightseeing", "description": "The main historical gathering place and symbol of the city.", "estimated_cost_usd": 0.0, "duration_hours": 1.5, "why_visit": "Take photos at the heart of the city's architectural heritage."},
        {"name": "{destination} Heritage Museum", "category": "museum", "description": "Exhibits detailing the rich history, art, and evolution of the region.", "estimated_cost_usd": 12.0, "duration_hours": 2.0, "why_visit": "Learn about the fascinating local history and cultural artifacts."},
        {"name": "Scenic {destination} Vista Point", "category": "lookout", "description": "A high-altitude vantage point providing sweeping views of the city skyline.", "estimated_cost_usd": 8.0, "duration_hours": 1.0, "why_visit": "Enjoy beautiful views and capture panoramic scenery."}
    ],
    "food": [
        {"name": "{destination} Gourmet Street Market", "category": "food", "description": "A collection of local food stalls serving regional delicacies and street eats.", "estimated_cost_usd": 15.0, "duration_hours": 2.0, "why_visit": "Try authentic local flavors in an energetic market environment."},
        {"name": "The {destination} Bistro & Grill", "category": "restaurant", "description": "A highly rated restaurant offering classic local cuisine made with fresh ingredients.", "estimated_cost_usd": 30.0, "duration_hours": 1.5, "why_visit": "Experience fine dining in a relaxed and inviting setting."}
    ],
    "shopping": [
        {"name": "{destination} Artisanal Passage", "category": "shopping", "description": "A boutique shopping arcade featuring handmade local goods and souvenirs.", "estimated_cost_usd": 25.0, "duration_hours": 1.5, "why_visit": "Find unique gifts, local crafts, and specialty fashion pieces."},
        {"name": "{destination} Central Promenade", "category": "shopping district", "description": "A popular pedestrian street lined with popular retail shops and boutiques.", "estimated_cost_usd": 0.0, "duration_hours": 2.0, "why_visit": "Enjoy shopping and coffee along a lively pedestrian walk."}
    ],
    "nature": [
        {"name": "{destination} Botanical Garden", "category": "park", "description": "A sprawling garden showcasing native plants, glass houses, and calm ponds.", "estimated_cost_usd": 5.0, "duration_hours": 2.0, "why_visit": "Relax amidst beautiful greenery and exotic plant collections."},
        {"name": "{destination} Ridge Hiking Trail", "category": "hiking", "description": "A scenic trail tracing local hills with views of the natural landscape.", "estimated_cost_usd": 0.0, "duration_hours": 3.0, "why_visit": "Get active in nature and take in fresh air."}
    ]
}


def _mock_places(
    destination: str,
    interest: str,
    limit: int = 5,
    place_type: str = "attraction",
) -> list[ActivityItem]:
    dest_lower = destination.lower().strip()
    interest_lower = interest.lower().strip()

    interest_category = "sightseeing"
    if "food" in interest_lower or "din" in interest_lower or "eat" in interest_lower or "restau" in interest_lower:
        interest_category = "food"
    elif "shop" in interest_lower or "market" in interest_lower:
        interest_category = "shopping"
    elif "natur" in interest_lower or "park" in interest_lower or "hike" in interest_lower or "beach" in interest_lower:
        interest_category = "nature"

    places_list = []
    matched_dest = None
    for k in MOCK_PLACES_DB:
        if k in dest_lower or dest_lower in k:
            matched_dest = k
            break

    if matched_dest:
        db_dest = MOCK_PLACES_DB[matched_dest]
        matched_interest = None
        for i_key in db_dest:
            if i_key == interest_category:
                matched_interest = i_key
                break
        if matched_interest:
            places_list = db_dest[matched_interest]

    if not places_list:
        templates = GENERIC_PLACES.get(interest_category, GENERIC_PLACES["sightseeing"])
        places_list = []
        for t in templates:
            places_list.append({
                "name": t["name"].format(destination=destination),
                "category": interest,
                "description": t["description"].format(destination=destination),
                "address": f"Central District, {destination}",
                "rating": 4.5,
                "opening_hours": "9 AM - 6 PM",
                "estimated_cost_usd": t["estimated_cost_usd"],
                "duration_hours": t["duration_hours"],
                "why_visit": t["why_visit"].format(destination=destination),
            })

    results = []
    for item in places_list[:limit]:
        results.append(
            ActivityItem(
                name=item.get("name", "Unknown Place"),
                category=item.get("category", interest),
                estimated_cost=float(item.get("estimated_cost_usd", 15.0)),
                duration_hours=float(item.get("duration_hours", 2.0)),
                notes=item.get("description", ""),
                place_type=place_type,
                address=item.get("address", destination),
                rating=item.get("rating", 4.5),
                opening_hours=item.get("opening_hours", "Open 24 hours"),
                google_maps_url=item.get("google_maps_url") or f"https://maps.google.com/?q={quote_plus(item.get('name', '') + ' ' + destination)}",
                why_visit=item.get("why_visit"),
            )
        )
    return results


async def ai_search_places(
    destination: str,
    interest: str,
    limit: int = 5,
    place_type: str = "attraction",
) -> list[ActivityItem]:
    """
    Uses Claude to return real place recommendations for a destination + interest.
    Falls back to an empty list with a logged warning if the API key is missing.
    """
    if not settings.ANTHROPIC_API_KEY:
        logger.warning("[AiPlaces] ANTHROPIC_API_KEY missing - returning mock places fallback.")
        return _mock_places(destination, interest, limit=limit, place_type=place_type)

    # Determine prompt instructions based on place type
    if place_type == "restaurant":
        item_instructions = (
            f'Return {limit} real, popular restaurants in {destination} '
            f'matching "{interest}" cuisine or dining style. '
            'Each item must have: name (string), category (cuisine type), '
            'description (1–2 sentence description), address (full street address), '
            'rating (float 1.0–5.0), opening_hours (e.g. "11 AM – 11 PM"), '
            'estimated_cost_usd (per person, as float), '
            'google_maps_url (https://maps.google.com/?q=URL+encoded+name+city), '
            'why_visit (1 sentence compelling reason), '
            'duration_hours (float, typical visit length).'
        )
    elif place_type == "shopping":
        item_instructions = (
            f'Return {limit} real, well-known shopping destinations in {destination} '
            f'for "{interest}". '
            'Each item must have: name (string), category (type of shopping), '
            'description (1–2 sentence description), address (full street address), '
            'rating (float 1.0–5.0), opening_hours (e.g. "10 AM – 9 PM"), '
            'estimated_cost_usd (average spend, as float), '
            'google_maps_url (https://maps.google.com/?q=URL+encoded+name+city), '
            'why_visit (1 sentence compelling reason), '
            'duration_hours (float, typical visit length).'
        )
    else:
        item_instructions = (
            f'Return {limit} real, top-rated attractions in {destination} '
            f'related to "{interest}". '
            'Each item must have: name (string), category (attraction type), '
            'description (1–2 sentence description), address (full street address), '
            'rating (float 1.0–5.0), opening_hours (e.g. "9 AM – 6 PM" or "Open 24 hours"), '
            'estimated_cost_usd (entry fee as float, 0.0 if free), '
            'google_maps_url (https://maps.google.com/?q=URL+encoded+name+city), '
            'why_visit (1 sentence compelling reason), '
            'duration_hours (float, typical visit length).'
        )

    user_prompt = (
        f"{item_instructions}\n\n"
        f"Respond ONLY with a valid JSON array. Example format:\n"
        f'[{{"name": "Example Place", "category": "Museum", "description": "...", '
        f'"address": "123 Example St, {destination}", "rating": 4.5, '
        f'"opening_hours": "9 AM – 6 PM", "estimated_cost_usd": 15.0, '
        f'"google_maps_url": "https://maps.google.com/?q=Example+Place+{destination.replace(" ", "+")}", '
        f'"why_visit": "...", "duration_hours": 2.0}}]'
    )

    try:
        client = _get_client()
        message = await client.messages.create(
            model=settings.LLM_MODEL,
            max_tokens=2048,
            system=PLACES_SYSTEM_PROMPT,
            messages=[{"role": "user", "content": user_prompt}],
        )
        raw = message.content[0].text.strip()

        # Strip markdown code fences if present
        if raw.startswith("```"):
            raw = raw.split("```")[1]
            if raw.startswith("json"):
                raw = raw[4:]
        raw = raw.strip()

        data = json.loads(raw)
        results: list[ActivityItem] = []
        for item in data[:limit]:
            results.append(
                ActivityItem(
                    name=item.get("name", "Unknown"),
                    category=item.get("category", interest),
                    estimated_cost=float(item.get("estimated_cost_usd", 0.0)),
                    duration_hours=float(item.get("duration_hours", 2.0)),
                    notes=item.get("description", ""),
                    place_type=place_type,
                    address=item.get("address"),
                    rating=item.get("rating"),
                    opening_hours=item.get("opening_hours"),
                    google_maps_url=item.get("google_maps_url"),
                    why_visit=item.get("why_visit"),
                )
            )
        logger.info(f"[AiPlaces] Claude returned {len(results)} real {place_type}s for '{interest}' in {destination}")
        return results

    except json.JSONDecodeError as exc:
        logger.error(f"[AiPlaces] Failed to parse Claude JSON response: {exc}")
        return []
    except anthropic.APIError as exc:
        logger.error(f"[AiPlaces] Anthropic API error: {exc}")
        return []
    except Exception as exc:
        logger.error(f"[AiPlaces] Unexpected error: {exc}")
        return []


async def ai_search_hotels(
    destination: str,
    max_price_per_night: float,
    min_rating: float = 3.0,
) -> list[HotelOption]:
    """
    Uses Claude to return real hotel recommendations for a destination within budget.
    """
    if not settings.ANTHROPIC_API_KEY:
        logger.warning("[AiPlaces] ANTHROPIC_API_KEY missing — cannot fetch real hotels.")
        return []

    user_prompt = (
        f"Return 3 real, well-known hotels in {destination} that cost under "
        f"${max_price_per_night:.0f} per night and have a rating of at least {min_rating}/5. "
        "Each item must have: name (string), price_per_night (float USD), "
        "rating (float 1.0–5.0), address (full street address), "
        "description (1–2 sentence description), "
        "google_maps_url (https://maps.google.com/?q=URL+encoded+hotel+name+city), "
        "why_visit (1 sentence why it's a great choice), "
        "amenities (array of strings, 3–5 items like ['WiFi', 'Pool', 'Spa']), "
        "opening_hours (e.g. '24/7 Front Desk'). "
        "Respond ONLY with a valid JSON array. No markdown, no explanation."
    )

    try:
        client = _get_client()
        message = await client.messages.create(
            model=settings.LLM_MODEL,
            max_tokens=1024,
            system=HOTELS_SYSTEM_PROMPT,
            messages=[{"role": "user", "content": user_prompt}],
        )
        raw = message.content[0].text.strip()

        if raw.startswith("```"):
            raw = raw.split("```")[1]
            if raw.startswith("json"):
                raw = raw[4:]
        raw = raw.strip()

        data = json.loads(raw)
        results: list[HotelOption] = []
        for item in data:
            if float(item.get("rating", 0)) >= min_rating:
                results.append(
                    HotelOption(
                        name=item.get("name", "Unknown Hotel"),
                        price_per_night=float(item.get("price_per_night", max_price_per_night)),
                        rating=float(item.get("rating", 4.0)),
                        address=item.get("address", destination),
                        description=item.get("description"),
                        google_maps_url=item.get("google_maps_url"),
                        why_visit=item.get("why_visit"),
                        amenities=item.get("amenities", []),
                        opening_hours=item.get("opening_hours", "24/7 Front Desk"),
                    )
                )
        logger.info(f"[AiPlaces] Claude returned {len(results)} real hotels in {destination}")
        return sorted(results, key=lambda h: h.rating or 0, reverse=True)

    except json.JSONDecodeError as exc:
        logger.error(f"[AiPlaces] Failed to parse Claude hotel JSON: {exc}")
        return []
    except anthropic.APIError as exc:
        logger.error(f"[AiPlaces] Anthropic API error (hotels): {exc}")
        return []
    except Exception as exc:
        logger.error(f"[AiPlaces] Unexpected error (hotels): {exc}")
        return []

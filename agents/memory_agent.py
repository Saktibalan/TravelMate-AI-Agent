"""
Memory Agent — stores and recalls user preferences across sessions
using a local Chroma vector store, keyed by user_id.

Called twice per run:
  - recall_preferences() BEFORE planning, to enrich the trip request
  - store_trip_memory() AFTER planning, to save what was learned
"""

import logging
import chromadb
from backend.config import settings
from backend.schemas import AgentState

logger = logging.getLogger(__name__)

_client = chromadb.PersistentClient(path=settings.CHROMA_PERSIST_DIR)
_collection = _client.get_or_create_collection(name="user_preferences")


async def recall_preferences(state: AgentState) -> AgentState:
    user_id = state["trip_request"].user_id
    if not user_id:
        return state

    try:
        results = _collection.query(
            query_texts=[f"travel preferences for {state['trip_request'].destination}"],
            where={"user_id": user_id},
            n_results=3,
        )
        docs = results.get("documents", [[]])[0]
        if docs:
            state["research_notes"]["past_preferences"] = docs
            logger.info(f"[MemoryAgent] Recalled {len(docs)} past preference notes.")
    except Exception as exc:
        logger.warning(f"[MemoryAgent] Recall failed (likely empty store): {exc}")

    return state


async def store_trip_memory(state: AgentState) -> AgentState:
    user_id = state["trip_request"].user_id
    if not user_id:
        return state

    summary = (
        f"User planned a trip to {state['trip_request'].destination} "
        f"with interests {state['trip_request'].interests} "
        f"and budget {state['trip_request'].budget} {state['trip_request'].currency}."
    )

    try:
        _collection.add(
            documents=[summary],
            metadatas=[{"user_id": user_id, "destination": state["trip_request"].destination}],
            ids=[f"{user_id}-{state['trip_request'].destination}-{state['trip_request'].start_date}"],
        )
        logger.info("[MemoryAgent] Stored trip memory.")
    except Exception as exc:
        logger.error(f"[MemoryAgent] Failed to store memory: {exc}")

    return state

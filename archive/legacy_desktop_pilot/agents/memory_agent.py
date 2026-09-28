"""
memory_agent.py — Retrieves and updates persistent memory for sessions.
"""
from __future__ import annotations

import logging
from typing import Any

from graph.state import AgentState
from memory.db import get_session_memory, save_session_state

logger = logging.getLogger(__name__)


async def memory_agent_node(state: AgentState) -> dict[str, Any]:
    """LangGraph node: injects persistent memory into state and saves session state."""
    session_id = state.get("session_id", "default_session")
    messages = state.get("messages", [])

    try:
        # Retrieve existing memory
        memory_ctx = await get_session_memory(session_id)

        # Save updated conversation state to DB asynchronously
        await save_session_state(session_id, messages, memory_summary=memory_ctx)

        return {
            "memory_context": memory_ctx,
            "execution_trace": [
                {
                    "agent": "memory_agent",
                    "status": "success",
                    "message": "Memory context retrieved and session state persisted.",
                }
            ],
        }
    except Exception as exc:
        logger.exception("Memory agent error: %s", exc)
        return {
            "execution_trace": [
                {
                    "agent": "memory_agent",
                    "status": "error",
                    "message": f"Memory agent error: {exc}",
                }
            ],
        }

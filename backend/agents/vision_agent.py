"""
vision_agent.py — Placeholder vision execution node.
"""
from __future__ import annotations

from typing import Any
from graph.state import AgentState


async def vision_agent_node(state: AgentState) -> dict[str, Any]:
    return {
        "last_execution_result": {
            "success": False,
            "error": "Vision capability is currently offline.",
            "agent_type": "vision_agent",
        },
        "current_step": state.get("current_step", 0) + 1,
        "execution_trace": [
            {
                "agent": "vision_agent",
                "status": "skipped",
                "message": "Vision capability is offline.",
            }
        ],
    }

"""
vision_agent.py — Stub for multimodal screenshot analysis and UI element locating.
"""
from __future__ import annotations

import logging
from typing import Any

from graph.state import AgentState

logger = logging.getLogger(__name__)


async def vision_agent_node(state: AgentState) -> dict[str, Any]:
    """LangGraph node: handles visual desktop inspection and screenshot reasoning."""
    plan = state.get("plan") or []
    current_step_idx = state.get("current_step", 0)

    if current_step_idx >= len(plan):
        return {
            "execution_trace": [
                {
                    "agent": "vision_agent",
                    "status": "skipped",
                    "message": "No vision step to execute.",
                }
            ]
        }

    step = plan[current_step_idx]

    # Vision agent stub response
    msg = f"Vision agent processed visual inspection step: {step.get('action')}"
    return {
        "last_execution_result": {"success": True, "message": msg},
        "execution_trace": [
            {
                "agent": "vision_agent",
                "status": "success",
                "message": msg,
            }
        ],
    }

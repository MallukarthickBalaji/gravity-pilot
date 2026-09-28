"""
task_coordinator.py — Coordinates the sequential execution of plan steps across execution agents.
"""
from __future__ import annotations

import logging
from typing import Any

from graph.state import AgentState

logger = logging.getLogger(__name__)


async def task_coordinator_node(state: AgentState) -> dict[str, Any]:
    """LangGraph node: steps through plan steps and delegates to specialized execution agents."""
    plan = state.get("plan") or []
    current_step_idx = state.get("current_step", 0)

    if not plan:
        return {
            "target_agent": "",
            "final_response": "No execution plan steps found.",
            "execution_trace": [
                {
                    "agent": "task_coordinator",
                    "status": "success",
                    "message": "Task coordinator completed — plan was empty.",
                }
            ],
        }

    # If we have completed all plan steps
    if current_step_idx >= len(plan):
        trace = state.get("execution_trace", [])
        successes = [t for t in trace if t.get("status") == "success"]
        summary = (
            f"Successfully executed {len(plan)} plan step(s).\n"
            + "\n".join(f"- {s.get('message')}" for s in successes[-len(plan):])
        )
        return {
            "target_agent": "",
            "final_response": summary,
            "execution_trace": [
                {
                    "agent": "task_coordinator",
                    "status": "success",
                    "message": f"Completed execution of all {len(plan)} plan step(s).",
                }
            ],
        }

    step = plan[current_step_idx]
    target_agent = step.get("agent", "")
    logger.info("TaskCoordinator setting target step %d/%d: agent=%s", current_step_idx+1, len(plan), target_agent)

    return {
        "target_agent": target_agent,
        "execution_trace": [
            {
                "agent": "task_coordinator",
                "status": "success",
                "message": f"Routing to {target_agent} for step {current_step_idx+1}.",
            }
        ]
    }


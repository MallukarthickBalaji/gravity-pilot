"""
task_coordinator.py — Coordinates the sequential execution of plan steps across execution agents.
"""
from __future__ import annotations

import logging
from typing import Any

from agents.browser_agent import browser_agent_node
from agents.desktop_agent import desktop_agent_node
from agents.document_agent import document_agent_node
from agents.vision_agent import vision_agent_node
from graph.state import AgentState

logger = logging.getLogger(__name__)


async def task_coordinator_node(state: AgentState) -> dict[str, Any]:
    """LangGraph node: steps through plan steps and delegates to specialized execution agents."""
    plan = state.get("plan") or []
    current_step_idx = state.get("current_step", 0)

    if not plan:
        return {
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
    logger.info("TaskCoordinator executing step %d/%d: agent=%s, action=%s", current_step_idx+1, len(plan), target_agent, step.get("action"))

    # Execute target agent
    if target_agent == "document_agent":
        agent_res = await document_agent_node(state)
    elif target_agent == "desktop_agent":
        agent_res = await desktop_agent_node(state)
    elif target_agent == "browser_agent":
        agent_res = await browser_agent_node(state)
    elif target_agent == "vision_agent":
        agent_res = await vision_agent_node(state)
    elif target_agent == "validation_agent":
        return {"current_step": current_step_idx + 1}
    else:
        agent_res = {
            "execution_trace": [
                {
                    "agent": "task_coordinator",
                    "status": "skipped",
                    "message": f"Unknown agent '{target_agent}' for step {current_step_idx+1}.",
                }
            ]
        }

    # Increment current_step
    result = dict(agent_res)
    result["current_step"] = current_step_idx + 1

    # Check if this was the last step
    if result["current_step"] >= len(plan) and not result.get("final_response"):
        result["final_response"] = (
            f"Execution finished: {len(plan)} step(s) completed."
        )

    return result

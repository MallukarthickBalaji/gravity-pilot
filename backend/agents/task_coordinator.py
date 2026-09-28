"""
task_coordinator.py — Dispatches execution steps to the appropriate specialized agents.
"""
from __future__ import annotations

import logging
from typing import Any

from graph.state import AgentState

logger = logging.getLogger(__name__)


from pathlib import Path


async def task_coordinator_node(state: AgentState) -> dict[str, Any]:
    plan = list(state.get("plan", []))
    current_step = state.get("current_step", 0)

    if not plan or current_step >= len(plan):
        return {
            "execution_trace": [
                {
                    "agent": "task_coordinator",
                    "status": "success",
                    "message": "All execution steps dispatched. Proceeding to validation.",
                }
            ]
        }

    # Cross-step parameter forwarding: link intermediate outputs to subsequent steps
    exec_results = state.get("execution_results", [])
    last_folder: str | None = None
    last_file: str | None = None
    for res in exec_results:
        out_p = res.get("output_path")
        if out_p:
            p = Path(out_p)
            if p.is_dir() or res.get("operation") == "create_folder":
                last_folder = str(p)
            elif p.is_file():
                last_file = str(p)

    step = dict(plan[current_step])
    params = dict(step.get("params", {}))
    agent = step.get("agent", "unknown")
    action = step.get("action", f"Step {current_step + 1}")

    # Forward created folder to document_agent or create_file if needed
    if last_folder and agent == "document_agent":
        if not params.get("output_dir") and not Path(params.get("output_filename", "")).is_absolute():
            params["output_dir"] = last_folder
            logger.info("TaskCoordinator forwarded output_dir '%s' to step %d", last_folder, current_step + 1)
            step["params"] = params
            plan[current_step] = step

    elif last_folder and agent == "desktop_agent":
        op = params.get("operation", "")
        if op == "create_file" and not Path(params.get("source_path", "")).is_absolute():
            # If source_path is simple filename, place inside created folder
            fname = Path(params.get("source_path", "")).name
            if fname:
                params["source_path"] = str(Path(last_folder) / fname)
                logger.info("TaskCoordinator forwarded folder '%s' to desktop create_file in step %d", last_folder, current_step + 1)
                step["params"] = params
                plan[current_step] = step

    return {
        "plan": plan,
        "execution_trace": [
            {
                "agent": "task_coordinator",
                "status": "success",
                "message": f"Dispatching step {current_step + 1}/{len(plan)}: [{agent}] {action}",
            }
        ],
    }

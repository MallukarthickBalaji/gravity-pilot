"""
desktop_agent.py — Desktop automation and filesystem orchestration node.
Orchestrates file/folder operations, desktop screenshots, and notebook inspection
by dispatching execution to deterministic tool handlers in tools.files, tools.screenshot,
and tools.notebook.
"""
from __future__ import annotations

import logging
from typing import Any

from graph.state import AgentState
from tools.files import (
    is_protected_path,
    op_copy,
    op_create_file,
    op_create_folder,
    op_delete,
    op_launch_app,
    op_move,
    op_rename,
    resolve_desktop_path,
    PROTECTED_PATHS,
)
from tools.notebook import op_open_notebook
from tools.screenshot import op_screenshot

logger = logging.getLogger(__name__)

# Re-export tool handlers for backward compatibility
__all__ = [
    "PROTECTED_PATHS",
    "is_protected_path",
    "resolve_desktop_path",
    "op_create_file",
    "op_create_folder",
    "op_copy",
    "op_move",
    "op_rename",
    "op_delete",
    "op_launch_app",
    "op_screenshot",
    "op_open_notebook",
    "desktop_agent_node",
]

_OPERATIONS = {
    "create_file": op_create_file,
    "create_folder": op_create_folder,
    "copy": op_copy,
    "move": op_move,
    "rename": op_rename,
    "delete": op_delete,
    "launch_app": op_launch_app,
    "screenshot": op_screenshot,
    "open_notebook": op_open_notebook,
}


async def desktop_agent_node(state: AgentState) -> dict[str, Any]:
    plan = state.get("plan", [])
    current_step = state.get("current_step", 0)

    if not plan or current_step >= len(plan):
        return {
            "last_execution_result": {
                "success": False,
                "error": "No desktop plan step to execute.",
            },
            "current_step": current_step + 1,
            "execution_trace": [
                {
                    "agent": "desktop_agent",
                    "status": "error",
                    "message": "No plan step available for desktop agent.",
                }
            ],
        }

    step = plan[current_step]
    params = step.get("params", {})
    operation = params.get("operation", "")
    source_path = params.get("source_path", "")
    dest_path = params.get("dest_path", "")

    exec_results = list(state.get("execution_results", []))
    artifact_paths = list(state.get("artifact_paths", []))

    op_fn = _OPERATIONS.get(operation)
    if op_fn is None:
        err = f"Unknown desktop operation: '{operation}'"
        res = {"success": False, "error": err, "operation": operation, "agent_type": "desktop_agent"}
        exec_results.append(res)
        return {
            "last_execution_result": res,
            "execution_results": exec_results,
            "artifact_paths": artifact_paths,
            "current_step": current_step + 1,
            "execution_trace": [
                {
                    "agent": "desktop_agent",
                    "status": "error",
                    "message": err,
                }
            ],
        }

    try:
        extra_params = {
            k: v
            for k, v in params.items()
            if k not in ("operation", "source_path", "dest_path")
        }
        result = op_fn(source_path=source_path, dest_path=dest_path, **extra_params)
        result["agent_type"] = "desktop_agent"
        op_label = operation.replace("_", " ").capitalize()
        trace_msg = f"{op_label}: {source_path}" + (f" -> {dest_path}" if dest_path else "")

        out_path = result.get("output_path")
        if out_path and out_path not in artifact_paths:
            artifact_paths.append(out_path)

        exec_results.append(result)

        return {
            "last_execution_result": result,
            "execution_results": exec_results,
            "artifact_paths": artifact_paths,
            "current_step": current_step + 1,
            "execution_trace": [
                {
                    "agent": "desktop_agent",
                    "status": "success",
                    "message": trace_msg,
                }
            ],
        }
    except Exception as exc:
        logger.exception("Desktop agent operation '%s' failed: %s", operation, exc)
        res = {
            "success": False,
            "error": str(exc),
            "operation": operation,
            "source_path": source_path,
            "dest_path": dest_path,
            "agent_type": "desktop_agent",
        }
        exec_results.append(res)
        return {
            "last_execution_result": res,
            "execution_results": exec_results,
            "artifact_paths": artifact_paths,
            "current_step": current_step + 1,
            "execution_trace": [
                {
                    "agent": "desktop_agent",
                    "status": "error",
                    "message": f"{operation} failed: {exc}",
                }
            ],
        }

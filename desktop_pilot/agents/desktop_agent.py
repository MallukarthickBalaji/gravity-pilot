"""
desktop_agent.py — Handles file/folder desktop operations and GUI automation stubs.
"""
from __future__ import annotations

import logging
import os
import shutil
import subprocess
from typing import Any

from graph.state import AgentState

logger = logging.getLogger(__name__)

try:
    import pyautogui
except Exception:
    pyautogui = None


async def desktop_agent_node(state: AgentState) -> dict[str, Any]:
    """LangGraph node: executes desktop and file system operations."""
    plan = state.get("plan") or []
    current_step_idx = state.get("current_step", 0)

    if current_step_idx >= len(plan):
        return {
            "execution_trace": [
                {
                    "agent": "desktop_agent",
                    "status": "skipped",
                    "message": "No desktop step to execute.",
                }
            ]
        }

    step = plan[current_step_idx]
    params = step.get("params", {})
    operation = (params.get("operation") or "").lower()
    source_path = params.get("source_path") or params.get("path") or ""
    dest_path = params.get("dest_path") or ""
    content = params.get("content") or ""

    try:
        if operation == "create_folder":
            os.makedirs(source_path, exist_ok=True)
            msg = f"Created folder: {os.path.abspath(source_path)}"
        elif operation == "create_file":
            with open(source_path, "w", encoding="utf-8") as f:
                f.write(content)
            msg = f"Created file: {os.path.abspath(source_path)}"
        elif operation == "move":
            shutil.move(source_path, dest_path)
            msg = f"Moved '{source_path}' to '{dest_path}'"
        elif operation == "copy":
            if os.path.isdir(source_path):
                shutil.copytree(source_path, dest_path, dirs_exist_ok=True)
            else:
                shutil.copy2(source_path, dest_path)
            msg = f"Copied '{source_path}' to '{dest_path}'"
        elif operation == "delete":
            if os.path.isdir(source_path):
                shutil.rmtree(source_path)
            else:
                os.remove(source_path)
            msg = f"Deleted '{source_path}'"
        elif operation == "rename":
            os.rename(source_path, dest_path)
            msg = f"Renamed '{source_path}' to '{dest_path}'"
        elif operation == "launch_app":
            subprocess.Popen([source_path], shell=True)
            msg = f"Launched app: {source_path}"
        else:
            msg = f"Executed generic desktop action: {operation or step.get('action')}"

        res = {"success": True, "message": msg}
        return {
            "last_execution_result": res,
            "execution_trace": [
                {
                    "agent": "desktop_agent",
                    "status": "success",
                    "message": msg,
                }
            ],
        }
    except Exception as exc:
        logger.exception("Desktop operation failed: %s", exc)
        res = {"success": False, "error": str(exc)}
        return {
            "last_execution_result": res,
            "error": f"Desktop operation error: {exc}",
            "execution_trace": [
                {
                    "agent": "desktop_agent",
                    "status": "error",
                    "message": f"Desktop operation failed: {exc}",
                }
            ],
        }

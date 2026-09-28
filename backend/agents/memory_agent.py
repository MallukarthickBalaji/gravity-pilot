"""
memory_agent.py — Loads and persists conversational state, task outcomes, and clarification states to SQLite.
"""
from __future__ import annotations

import logging
from typing import Any

from graph.state import AgentState
from memory.database import (
    ensure_session,
    get_task_history,
    save_message,
    save_task_history,
    update_session_task_state,
)

logger = logging.getLogger(__name__)


async def memory_agent_read_node(state: AgentState) -> dict[str, Any]:
    session_id = state.get("session_id", "default")
    await ensure_session(session_id)

    try:
        tasks = await get_task_history(session_id)
        task_summaries = [
            f"- {t['task_type']}: {t['status']} (output: {t['output_path']})"
            for t in tasks[-5:]
        ]
        context_str = "\n".join(task_summaries) if task_summaries else "No previous tasks."
    except Exception as exc:
        logger.warning("Memory read error: %s", exc)
        context_str = ""

    return {
        "memory_context": context_str,
        "execution_trace": [
            {
                "agent": "memory_agent",
                "status": "success",
                "message": "Loaded session memory context.",
            }
        ],
    }


async def memory_agent_write_node(state: AgentState) -> dict[str, Any]:
    session_id = state.get("session_id", "default")
    task_id = state.get("task_id")
    task_type = state.get("task_type", "unknown")
    clarifying_q = state.get("clarifying_question")
    requirements_complete = state.get("requirements_complete", False)
    last_res = state.get("last_execution_result") or {}
    output_path = last_res.get("output_path")
    final_response = state.get("final_response") or "Task completed."

    try:
        if clarifying_q and not requirements_complete:
            # Save clarification message to DB history
            await save_message(
                session_id=session_id,
                role="agent",
                content=clarifying_q,
                task_id=task_id,
                kind="clarification",
                agent_name="Requirement Analyzer",
                agent_color="#2E7D6B",
            )
            # Update session state to waiting_for_user
            await update_session_task_state(
                session_id=session_id,
                status="waiting_for_user",
                task_id=task_id,
                task_type=task_type,
                original_prompt=state.get("user_input"),
                clarifying_question=clarifying_q,
            )
        else:
            # Normal completion or error
            kind = "error" if state.get("error") or not last_res.get("success", True) else "normal"
            agent_name = "Validation Agent" if kind == "normal" and task_type != "general_query" else ("System" if kind == "error" else "Supervisor")
            agent_color = "#2E7D6B" if kind == "normal" and task_type != "general_query" else ("#B84040" if kind == "error" else "#1F3A5F")

            await save_message(
                session_id=session_id,
                role="agent",
                content=final_response,
                task_id=task_id,
                kind=kind,
                agent_name=agent_name,
                agent_color=agent_color,
            )

            task_status = "completed" if kind == "normal" else "failed"
            if task_type not in ("general_query", "unknown"):
                file_type = None
                if output_path:
                    from pathlib import Path
                    file_type = Path(output_path).suffix.lstrip(".")
                await save_task_history(
                    session_id=session_id,
                    task_id=task_id,
                    task_type=task_type,
                    status=task_status,
                    output_path=output_path,
                    file_type=file_type,
                )

            await update_session_task_state(
                session_id=session_id,
                status=task_status,
                task_id=task_id,
            )
    except Exception as exc:
        logger.warning("Memory write error: %s", exc)

    return {
        "execution_trace": [
            {
                "agent": "memory_agent",
                "status": "success",
                "message": "Saved session context and task history.",
            }
        ],
    }

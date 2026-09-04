"""
run_task.py — Streaming subprocess entry point.

Called by the Node.js API server to execute a user request through the
LangGraph pipeline. Writes newline-delimited JSON events to stdout so the
parent process can stream them as SSE to the browser.

Event shapes:
  {"type":"agent_update","agent":"supervisor","status":"active","detail":"Classifying…"}
  {"type":"message","agentName":"Supervisor","agentColor":"#1F3A5F","kind":"normal","text":"…","items":null}
  {"type":"done"}
  {"type":"error","message":"…"}

Usage:
  python run_task.py --input "user message" --session-id "abc123" --mode groq
"""
from __future__ import annotations

import argparse
import asyncio
import json
import sys
import uuid
from typing import Any

# ── Palette (mirrors FullApp.tsx) ─────────────────────────────────────────────
AGENT_COLOR: dict[str, str] = {
    "model_router":          "#3E6B8A",
    "memory_agent":          "#3E6B8A",
    "supervisor":            "#1F3A5F",
    "requirement_analyzer":  "#2E7D6B",
    "planning_agent":        "#C9891A",
    "task_coordinator":      "#C9891A",
    "doc_agent":             "#3E6B8A",
    "document_agent":        "#3E6B8A",
    "browser_agent":         "#3E6B8A",
    "desktop_agent":         "#3E6B8A",
    "vision_agent":          "#3E6B8A",
    "validation_agent":      "#2E7D6B",
}

AGENT_DISPLAY: dict[str, str] = {
    "model_router":          "Model Router",
    "memory_agent":          "Memory Agent",
    "supervisor":            "Supervisor",
    "requirement_analyzer":  "Requirement Analyzer",
    "planning_agent":        "Planning Agent",
    "task_coordinator":      "Task Coordinator",
    "doc_agent":             "Document Agent",
    "document_agent":        "Document Agent",
    "browser_agent":         "Browser Agent",
    "desktop_agent":         "Desktop Agent",
    "vision_agent":          "Vision Agent",
    "validation_agent":      "Validation Agent",
}


def emit(event: dict[str, Any]) -> None:
    """Write a JSON event line to stdout and flush immediately."""
    print(json.dumps(event), flush=True)


def emit_agent(agent_id: str, status: str, detail: str | None = None) -> None:
    emit({"type": "agent_update", "agent": agent_id, "status": status, "detail": detail})


def emit_message(
    agent_id: str,
    text: str,
    kind: str = "normal",
    items: list[str] | None = None,
) -> None:
    emit({
        "type":       "message",
        "agentName":  AGENT_DISPLAY.get(agent_id, agent_id),
        "agentColor": AGENT_COLOR.get(agent_id, "#3E6B8A"),
        "kind":       kind,
        "text":       text,
        "items":      items,
    })


# ── Main ──────────────────────────────────────────────────────────────────────

async def run(user_input: str, session_id: str) -> None:
    """Run the LangGraph graph and stream events."""
    from config import config  # noqa: F401 — loads .env / secrets
    from graph.state import AgentState, Capabilities
    from graph.workflow import create_graph
    from memory.db import get_task_state, save_task_state, clear_task_state

    graph = create_graph()

    # Load previous task state if any
    task_state = await get_task_state(session_id) or {}

    # Build initial state
    state: AgentState = {
        "messages":              [{"role": "user", "content": user_input}],
        "session_id":            session_id,
        "user_input":            user_input,
        "task_type":             task_state.get("task_type"),
        "current_task_info":     task_state.get("current_task_info"),
        "requirements_complete": task_state.get("requirements_complete", False),
        "clarifying_question":   None,
        "plan":                  task_state.get("plan"),
        "current_step":          task_state.get("current_step", 0),
        "status":                "executing",
        "last_execution_result": None,
        "validation_result":     None,
        "replan_reason":         None,
        "model_backend":         "unknown",
        "capabilities":          None,
        "memory_context":        None,
        "final_response":        None,
        "error":                 None,
        "execution_trace":       [],
    }

    # Stream the graph and emit agent events
    last_node: str | None = None
    final_state: dict[str, Any] = dict(state)

    try:
        async for chunk in graph.astream(state, stream_mode="updates"):
            for node_name, node_output in chunk.items():
                # Mark previous node done
                if last_node and last_node != node_name:
                    emit_agent(last_node, "done")

                last_node = node_name
                emit_agent(node_name, "active", _detail_for(node_name, node_output))
                final_state.update(node_output)

                # Emit clarifying question as message immediately
                cq = node_output.get("clarifying_question")
                if cq:
                    emit_message("requirement_analyzer", cq, kind="clarification")

        # Mark last node done
        if last_node:
            emit_agent(last_node, "done")

        # Emit final response
        final_response = final_state.get("final_response")
        error = final_state.get("error")

        if error:
            emit_message("supervisor", error, kind="error")
        elif final_response:
            # Figure out which agent produced this
            task_type = final_state.get("task_type", "general_query")
            agent_id = _response_agent(task_type)
            emit_message(agent_id, final_response)

        # Emit plan if present
        plan = final_state.get("plan")
        if plan:
            items = [
                f"[{s.get('agent','?')}] {s.get('action','?')}"
                for s in (plan if isinstance(plan, list) else [])
            ]
            if items:
                emit_message(
                    "planning_agent",
                    f"Plan ready — {len(items)} step{'s' if len(items)!=1 else ''}:",
                    kind="plan",
                    items=items,
                )

        emit({"type": "done"})

        # Save or clear task state
        if final_state.get("status") == "completed":
            await clear_task_state(session_id)
        else:
            await save_task_state(session_id, {
                "task_type": final_state.get("task_type"),
                "current_task_info": final_state.get("current_task_info"),
                "requirements_complete": final_state.get("requirements_complete"),
                "plan": final_state.get("plan"),
                "current_step": final_state.get("current_step"),
                "status": final_state.get("status")
            })

    except Exception as exc:
        emit({"type": "error", "message": str(exc)})


def _detail_for(node_name: str, output: dict[str, Any]) -> str | None:
    """Generate a short detail string for an agent update."""
    if node_name == "supervisor":
        t = output.get("task_type")
        return f"classified → {t}" if t else "Classifying…"
    if node_name == "model_router":
        b = output.get("model_backend")
        return f"backend: {b}" if b else "Detecting backend…"
    if node_name == "requirement_analyzer":
        if output.get("clarifying_question"):
            return "Missing info — asking user"
        return "Requirements complete" if output.get("requirements_complete") else "Checking…"
    if node_name == "planning_agent":
        plan = output.get("plan")
        if plan:
            return f"{len(plan)} step{'s' if len(plan)!=1 else ''} ready"
        return "Generating plan…"
    return None


def _response_agent(task_type: str | None) -> str:
    mapping = {
        "document_generation": "doc_agent",
        "browser_automation":  "browser_agent",
        "desktop_automation":  "desktop_agent",
        "general_query":       "planning_agent",
    }
    return mapping.get(task_type or "", "supervisor")


# ── Entry ──────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--input",      required=True, help="User message")
    parser.add_argument("--session-id", default=str(uuid.uuid4()), help="Session ID")
    args = parser.parse_args()

    # Change to desktop_pilot dir so relative imports work
    import os, pathlib
    os.chdir(pathlib.Path(__file__).parent)
    sys.path.insert(0, str(pathlib.Path(__file__).parent))

    asyncio.run(run(args.input, args.session_id))

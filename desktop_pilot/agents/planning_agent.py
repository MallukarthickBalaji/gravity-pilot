"""
planning_agent.py — Converts a fully-specified request into an ordered plan.

Each step is tagged with the execution agent that should run it.
This node only produces the plan — task_coordinator (Phase 4) will execute it.
"""
from __future__ import annotations

import json
import logging
from typing import Any

from langchain_core.messages import HumanMessage, SystemMessage

from agents.model_router import get_llm
from graph.state import AgentState, PlanStep

logger = logging.getLogger(__name__)

_SYSTEM_PROMPT = """\
You are a planning agent for a desktop automation AI system.

Given a fully-specified user request, produce an ordered list of execution
steps. Each step must specify which specialized agent should handle it.

Available execution agents:
  - document_agent  : Word (.docx), Excel (.xlsx), PowerPoint (.pptx) generation
  - browser_agent   : Web search, URL navigation, data extraction (Playwright)
  - desktop_agent   : File/folder operations, application launching (PyAutoGUI)

Each step must follow this schema:
  {
    "step_id": <integer starting from 1>,
    "agent": "<document_agent | browser_agent | desktop_agent>",
    "action": "<human-readable description of what to do>",
    "params": { <key-value pairs the agent needs to execute the step> }
  }

Rules:
  - Produce only the steps necessary. Don't pad the plan.
  - For document_generation tasks, params must include at minimum:
      "doc_type": "word" | "excel" | "powerpoint"
      "output_filename": "<name>.docx/.xlsx/.pptx"
      "content": { <structured content matching the doc type> }
  - For browser_automation tasks, params must include:
      "url": "<url or null>", "query": "<search query or null>",
      "extract": "<what to extract>"
  - For desktop_automation tasks, params must include:
      "operation": "create_file|create_folder|move|copy|delete|rename|launch_app"
      "source_path": "<path or app name>", "dest_path": "<path if applicable>"
  - After all execution steps, add a final validation step:
      { "step_id": N, "agent": "validation_agent", "action": "Validate result", "params": {} }

Respond with ONLY a JSON object — no prose, no markdown, no code fences:
{
  "steps": [ ...step objects... ],
  "estimated_complexity": "low | medium | high",
  "notes": "<any important caveats or assumptions — empty string if none>"
}
"""


async def planning_agent_node(state: AgentState) -> dict[str, Any]:
    """LangGraph node: generates the execution plan."""
    backend = state.get("model_backend", "none")
    task_type = state.get("task_type", "unknown")

    # ── General queries: answer directly, no execution plan needed ────────────
    if task_type == "general_query":
        llm = get_llm(backend)
        history = "\n".join(
            f"{m['role'].capitalize()}: {m['content']}"
            for m in state.get("messages", [])
        )
        try:
            resp = await llm.ainvoke(
                [
                    SystemMessage(
                        content=(
                            "You are a helpful AI assistant. "
                            "Answer the user's question clearly and concisely."
                        )
                    ),
                    HumanMessage(content=f"{history}\nUser: {state['user_input']}"),
                ]
            )
            answer = resp.content.strip()
        except Exception as exc:
            answer = f"(Error generating response: {exc})"

        return {
            "plan": [],
            "final_response": answer,
            "execution_trace": [
                {
                    "agent": "planning_agent",
                    "status": "success",
                    "message": "General query answered directly — no plan needed.",
                }
            ],
        }

    # ── Build context for the planner ─────────────────────────────────────────
    history_text = "\n".join(
        f"{m['role'].capitalize()}: {m['content']}"
        for m in state.get("messages", [])
    )
    memory_ctx = state.get("memory_context")
    memory_section = f"\nRelevant prior context:\n{memory_ctx}\n" if memory_ctx else ""

    user_msg = (
        f"Task type: {task_type}\n"
        f"{memory_section}"
        f"Conversation:\n{history_text}\n\n"
        f"Current user input: {state['user_input']}\n\n"
        f"Available capabilities: "
        f"browser={'yes' if state.get('capabilities') and state['capabilities'].browser_automation else 'no'}, "
        f"desktop={'yes' if state.get('capabilities') and state['capabilities'].desktop_automation else 'no'}, "
        f"documents={'yes' if state.get('capabilities') and state['capabilities'].document_generation else 'no'}"
    )

    llm = get_llm(backend)
    try:
        response = await llm.ainvoke(
            [SystemMessage(content=_SYSTEM_PROMPT), HumanMessage(content=user_msg)]
        )
        raw = response.content.strip()
        if raw.startswith("```"):
            raw = raw.split("```")[1]
            if raw.startswith("json"):
                raw = raw[4:]
        parsed: dict = json.loads(raw)
        steps: list[PlanStep] = parsed.get("steps", [])
        complexity: str = parsed.get("estimated_complexity", "unknown")
        notes: str = parsed.get("notes", "")
    except Exception as exc:
        logger.exception("PlanningAgent LLM call failed: %s", exc)
        steps = []
        complexity = "unknown"
        notes = f"Planning error: {exc}"

    step_summary = " → ".join(
        f"[{s.get('agent', '?')}] {s.get('action', '?')[:40]}"
        for s in steps
    )
    logger.info("PlanningAgent → %d steps (%s complexity)", len(steps), complexity)

    return {
        "plan": steps,
        "current_step": 0,
        "execution_trace": [
            {
                "agent": "planning_agent",
                "status": "success" if steps else "error",
                "message": (
                    f"Plan generated: {len(steps)} steps, {complexity} complexity."
                    + (f" Notes: {notes}" if notes else "")
                ),
            }
        ],
        "final_response": (
            None  # task_coordinator will set this after execution (Phase 4)
        ),
    }

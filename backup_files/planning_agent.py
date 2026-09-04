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

Given a fully-specified user request and COLLECTED TASK INFO, produce an ordered list of execution
steps. Each step must specify which specialized agent should handle it.

Available execution agents:
  - document_agent  : Word (.docx), Excel (.xlsx), PowerPoint (.pptx) generation
  - browser_agent   : Web search, URL navigation, data extraction (Playwright)
  - desktop_automation   : File/folder operations, application launching (PyAutoGUI)

Each step must follow this schema:
  {
    "step_id": <integer starting from 1>,
    "agent": "<document_agent | browser_agent | desktop_agent>",
    "action": "<human-readable description of what to do>",
    "params": { <key-value pairs the agent needs to execute the step> }
  }

Rules:
  - Produce exactly ONE execution step for document generation (do not create separate steps for different document types).
  - You MUST use the `document_type` and `filename` from COLLECTED TASK INFO. Do not guess or override them.
  - For document_generation tasks, params must include at minimum:
      "doc_type": "<from COLLECTED TASK INFO>"
      "output_filename": "<from COLLECTED TASK INFO>"
      "content": { 
        // For Word: {"title": "...", "sections": [{"heading": "...", "paragraph": "..."}]}
        // For Excel: {"sheet_title": "...", "columns": ["A", "B"], "rows": [["1", "2"]]}
        // For PowerPoint: {"title": "...", "slides": [{"title": "...", "body": "..."}]}
      }
      CRITICAL: You MUST write the actual full text and paragraphs inside the content block!
      CRITICAL FOR WORD: If the user requests a formal letter (e.g. leave letter, permission letter), you MUST structure the Word content as a proper formal letter with "From", "To", "Subject", "Respected Sir/Madam,", the body paragraphs, and "Yours faithfully,". Use ONLY info provided by the user. Do not invent personal info, dates, or college names.
      CRITICAL FOR POWERPOINT: The `content` object MUST contain a `slides` array. Each slide MUST have a `title` and a `body` (which can be a single string containing bullet points).
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
    current_info = state.get("current_task_info", {})

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
                            "You are DesktopPilot AI, a hierarchical multi-agent desktop automation system. "
                            "You can answer general questions, but your main capabilities include:\n"
                            "1. Document Generation: Creating Word (.docx), Excel (.xlsx), and PowerPoint (.pptx) files.\n"
                            "2. Desktop Automation: File and folder operations (create, move, copy, delete, rename, launch apps).\n"
                            "3. Browser Automation: Searching the web and extracting text from URLs.\n"
                            "Answer the user's question clearly, and let them know you can help with these automated tasks."
                        )
                    ),
                    HumanMessage(content=f"{history}\nUser: {state['user_input']}"),
                ]
            )
            answer = str(resp.content).strip()
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
        f"COLLECTED TASK INFO: {json.dumps(current_info)}\n"
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
        raw = str(response.content).strip()
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
    logger.info("PLAN: %s", step_summary)
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

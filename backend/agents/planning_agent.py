"""
planning_agent.py — Generates structured execution steps for the request.
Strictly dispatches only execution agents (document_agent, browser_agent, desktop_agent).
CRITICAL RULE: Never generates validation_agent as an execution step.
Supports replanning with failure diagnostics when invoked after validation failure.
Ensures sequential prompts maintain clean, isolated execution plans.
"""
from __future__ import annotations

import asyncio
import json
import logging
from typing import Any

from langchain_core.messages import HumanMessage, SystemMessage

from agents.json_utils import extract_json_object
from agents.model_router import get_llm
from graph.state import AgentState, PlanStep

logger = logging.getLogger(__name__)

_SYSTEM_PROMPT = """\
You are an expert Planner for a desktop automation system.
Given a user request, generate an ordered list of execution steps.

Available execution agents:
- document_agent: Creates Word (.docx), Excel (.xlsx), PowerPoint (.pptx), or code/script files.
  Params schema:
  - For Word:
    {
      "doc_type": "word",
      "output_filename": "<name>.docx",
      "content": {
        "title": "Document Title",
        "sections": [
          {"heading": "Section Heading", "paragraphs": ["Paragraph 1", "Paragraph 2"]}
        ]
      }
    }
  - For Excel:
    {
      "doc_type": "excel",
      "output_filename": "<name>.xlsx",
      "content": {
        "sheet_name": "Sheet1",
        "headers": ["Col 1", "Col 2", ...],
        "rows": [
          ["Val 1", "Val 2", ...]
        ]
      }
    }
  - For PowerPoint:
    {
      "doc_type": "powerpoint",
      "output_filename": "<name>.pptx",
      "content": {
        "title": "Presentation Title",
        "subtitle": "Presentation Subtitle",
        "slides": [
          {"title": "Slide 1 Title", "bullets": ["Point 1", "Point 2"]}
        ]
      }
    }
  - For Code / Scripts:
    {
      "doc_type": "code",
      "output_filename": "<name>.py",
      "content": {
        "code": "def fibonacci(n):\n    ..."
      }
    }

- desktop_agent: File and folder operations, desktop capture, and notebook launching on Windows.
  Params schema:
  {
    "operation": "create_file | create_folder | copy | move | rename | delete | screenshot | open_notebook | launch_app",
    "source_path": "<source file/folder/app/notebook path>",
    "dest_path": "<destination file/folder/screenshot path if applicable>",
    "content": "<optional file/script content when operation is create_file>"
  }
  Examples:
  - Screenshot:
    {"operation": "screenshot", "dest_path": "screenshot.png"}
  - Open notebook:
    {"operation": "open_notebook", "source_path": "test.ipynb"}
  - Create code/script file:
    {"operation": "create_file", "source_path": "script.py", "content": "print('hello world')"}

- browser_agent: Web searches and URL navigation/opening.
  Params schema:
  {
    "operation": "web_search | open_url",
    "query": "<search query or null>",
    "url": "<target url or null>",
    "extract": "<what information or summary to extract>"
  }
  Examples:
  - Web search:
    {"operation": "web_search", "query": "latest Python version", "extract": "summary"}
  - Open URL:
    {"operation": "open_url", "url": "https://www.google.com"}

CRITICAL RULES:
1. DO NOT include "validation_agent" in the plan. Validation is handled automatically by the workflow.
2. If replanning after a failure (e.g. destination directory did not exist), adjust the plan by adding necessary prerequisites (e.g. creating the destination directory before copying).
3. Ensure all file paths retain user intent (e.g. "my desktop" or "Desktop", "Backup").
4. For independent sequential prompts, do NOT repeat previous plans from earlier tasks! Focus exclusively on what is requested in the current prompt.

Output ONLY a JSON object:
{
  "steps": [
    {
      "step_id": 1,
      "agent": "document_agent | desktop_agent | browser_agent",
      "action": "<concise description>",
      "params": { ... }
    }
  ],
  "notes": "<optional plan notes>"
}
"""


async def planning_agent_node(state: AgentState) -> dict[str, Any]:
    task_type = state.get("task_type", "unknown")
    backend = state.get("model_backend", "none")
    user_input = (state.get("user_input") or "").strip()

    # General queries: answer directly without creating execution plan
    if task_type in ("general_query", "general"):
        llm = get_llm(backend)
        history_text = "\n".join(
            f"{m.get('role', 'user').capitalize()}: {m.get('content', '')}"
            for m in state.get("messages", [])[-4:]
        )
        try:
            resp = await llm.ainvoke(
                [
                    SystemMessage(
                        content=(
                            "You are GravityPilot AI, an intelligent desktop assistant. "
                            "Answer the user concisely and helpfully."
                        )
                    ),
                    HumanMessage(content=f"{history_text}\nUser: {user_input}"),
                ]
            )
            answer = str(resp.content).strip()
        except Exception as exc:
            answer = f"Error generating answer: {exc}"

        return {
            "plan": [],
            "final_response": answer,
            "execution_trace": [
                {
                    "agent": "planning_agent",
                    "status": "success",
                    "message": "Answered general query directly.",
                }
            ],
        }

    # Sequential isolation: Determine whether the prompt explicitly refers to earlier context
    messages = state.get("messages", [])
    last_assistant_msg = next((m for m in reversed(messages) if m.get("role") in ("assistant", "agent")), None)
    prior_user_msg = next((m for m in reversed(messages[:-1]) if m.get("role") == "user"), None)

    refers_to_past = any(
        w in user_input.lower()
        for w in ("convert that", "that file", "previous", "earlier", "rename that", "move that", "delete that", "summarize that")
    )

    if refers_to_past:
        history_text = "\n".join(
            f"{m.get('role', 'user').capitalize()}: {m.get('content', '')}"
            for m in messages[-4:]
        )
        effective_instruction = user_input
    elif last_assistant_msg and ("?" in last_assistant_msg.get("content", "") or "clarif" in last_assistant_msg.get("content", "").lower()):
        # Clarification answered for current task: combine original prompt with clarification
        prev_user_msgs = [m.get("content", "") for m in messages if m.get("role") == "user"]
        orig_req = prev_user_msgs[-2] if len(prev_user_msgs) >= 2 else (prior_user_msg.get("content", "") if prior_user_msg else "")
        history_text = f"Initial Request: {orig_req}\nClarification Details: {user_input}"
        effective_instruction = f"{orig_req}. Details: {user_input}" if orig_req else user_input
    else:
        history_text = f"Current Request: {user_input}"
        effective_instruction = user_input

    is_replanning = bool(state.get("replan_required") or state.get("replan_reason") == "execution_failure")
    replan_count = state.get("replan_count", 0)
    replan_context = ""

    previous_plan = state.get("current_plan") or state.get("plan") or []

    if is_replanning:
        val_result = state.get("validation_result") or {}
        val_errors = state.get("validation_errors") or []
        last_result = state.get("last_execution_result") or {}
        error_msg = "; ".join(val_errors) if val_errors else (val_result.get("reason") or last_result.get("error") or "Step validation failed")

        prev_plan_summary = json.dumps(previous_plan, indent=2) if previous_plan else "None"
        replan_context = (
            f"\n\n[REPLANNING ALERT - ATTEMPT {replan_count}]\n"
            f"The previous plan attempt failed validation.\n"
            f"Failure Diagnostics: {error_msg}\n"
            f"Previous Failed Plan:\n{prev_plan_summary}\n"
            "Please generate a revised, corrected execution plan that resolves these errors (for example, adjust paths, add missing prerequisites, or correct document structure)!"
        )

    user_msg = (
        f"Task Type: {task_type}\n\n"
        f"Task Context:\n{history_text}\n\n"
        f"Current Instruction: {effective_instruction}"
        f"{replan_context}"
    )

    llm = get_llm(backend)
    response = None
    for attempt in range(3):
        try:
            response = await llm.ainvoke(
                [SystemMessage(content=_SYSTEM_PROMPT), HumanMessage(content=user_msg)]
            )
            break
        except Exception as exc:
            err_str = str(exc)
            if ("429" in err_str or "rate_limit" in err_str.lower()) and attempt < 2:
                wait_sec = 4.0 * (attempt + 1)
                logger.warning("Rate limit in planning_agent; backing off for %.1fs (attempt %d/3)...", wait_sec, attempt + 1)
                await asyncio.sleep(wait_sec)
            else:
                logger.warning("PlanningAgent error: %s", exc)
                break

    try:
        raw = str(response.content).strip() if response else "{}"
        parsed = extract_json_object(raw)
        raw_steps = parsed.get("steps", [])
        notes = parsed.get("notes", "")

        # Filter out validation_agent if accidentally included by LLM
        clean_steps: list[PlanStep] = []
        for s in raw_steps:
            if s.get("agent") == "validation_agent":
                continue
            clean_steps.append(s)

    except Exception as exc:
        logger.warning("PlanningAgent error: %s", exc)
        clean_steps = []
        notes = str(exc)

    trace_msg = (
        f"Plan created with {len(clean_steps)} step(s)."
        if not is_replanning
        else f"Revised plan (attempt {replan_count}) generated with {len(clean_steps)} step(s) after failure."
    )

    return {
        "plan": clean_steps,
        "current_plan": clean_steps,
        "previous_plan": previous_plan if is_replanning else state.get("previous_plan"),
        "current_step": 0,
        "execution_results": [] if is_replanning else state.get("execution_results", []),
        "replan_required": False,
        "replan_reason": None,  # Reset replan flag once new plan is formulated
        "execution_trace": [
            {
                "agent": "planning_agent",
                "status": "success" if clean_steps else "error",
                "message": trace_msg,
            }
        ],
    }

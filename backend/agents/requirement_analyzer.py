"""
requirement_analyzer.py — Analyzes requirement completeness before planning.
If critical information is missing, asks exactly ONE clarifying question.
Supports multi-turn clarification loop continuity.
"""
from __future__ import annotations

import asyncio
import json
import logging
from typing import Any

from langchain_core.messages import HumanMessage, SystemMessage

from agents.json_utils import extract_json_object
from agents.model_router import get_llm
from graph.state import AgentState

logger = logging.getLogger(__name__)

_SYSTEM_PROMPT = """\
You are a Requirements Analyst for an AI desktop automation system.
Evaluate whether the user's request contains enough information to proceed to planning and execution.

Guidelines by task category:
- document_generation:
  1. Standard/Generic documents (COMPLETE):
     Requests like "Create an Excel attendance sheet for 10 students", "Create a Word document about Agentic AI", "Create a 5-slide PowerPoint about cloud computing", "Create a python script for fibonacci" already contain sufficient topic/purpose to generate a high quality template or document. Mark COMPLETE!
  2. Incomplete requests (INCOMPLETE):
     - Bare requests like "Create a PowerPoint" or "Create a document" with NO topic or subject at all. Ask for the topic in ONE friendly question!
     - Personal/custom letters like "Create a leave letter" or "Write a resignation letter" without recipient, date, or reason. Ask: "Sure! Who should the leave letter be addressed to, and what is the leave period or reason?"
  3. Clarified responses (COMPLETE):
     If the previous assistant message asked for missing details (such as recipient, topic, or date) and the user now answered, the requirements are now COMPLETE!

- browser_automation:
  - "Search the web for...", "Find ... online", "Open Google", "Open https://...":
    The query or target URL is known. Mark COMPLETE!

- desktop_automation:
  - "Take a screenshot", "Open notebook ...", "Copy ...", "Move ...", "Delete ...":
    If the action and target are specified, mark COMPLETE!

- general_query:
  Always COMPLETE.

Rules:
1. Do NOT ask unnecessary questions if the request can be reasonably satisfied with intelligent defaults.
2. If critical details are genuinely missing, return ONE specific, friendly clarifying question.
3. If complete, return complete=true, clarifying_question=null.

Output ONLY a JSON object:
{
  "complete": true | false,
  "missing_info": ["item1", ...],
  "clarifying_question": "<question or null>"
}
"""


async def requirement_analyzer_node(state: AgentState) -> dict[str, Any]:
    task_type = state.get("task_type", "unknown")
    backend = state.get("model_backend", "none")
    user_input = (state.get("user_input") or "").strip()

    if task_type in ("general_query", "general"):
        return {
            "requirements_complete": True,
            "clarifying_question": None,
            "execution_trace": [
                {
                    "agent": "requirement_analyzer",
                    "status": "success",
                    "message": "General query — requirements complete.",
                }
            ],
        }

    # Deterministic completeness for clarified responses (single-question limit)
    messages = state.get("messages", [])
    last_assistant_msg = next((m for m in reversed(messages[:-1]) if m.get("role") in ("assistant", "agent")), None)
    if last_assistant_msg and ("?" in last_assistant_msg.get("content", "") or "clarif" in last_assistant_msg.get("content", "").lower()):
        logger.info("RequirementAnalyzer: Clarification response received; marking requirements complete.")
        return {
            "requirements_complete": True,
            "clarifying_question": None,
            "requirements": [
                {"requirement_id": "R1", "description": f"Execute action corresponding to {task_type}"},
                {"requirement_id": "R2", "description": "Generate verified artifact on disk matching clarified intent"},
            ],
            "execution_trace": [
                {
                    "agent": "requirement_analyzer",
                    "status": "success",
                    "message": "Clarification answered — requirements complete.",
                }
            ],
        }

    # Deterministic completeness for common unambiguous tasks
    input_lower = user_input.lower()
    unambiguous_terms = (
        "screenshot", "screen shot", "capture screen", "open google", 
        "search the web", "search for ", "search ", "latest ", "official ",
        "python code", "write python", "calculate fibonacci", "fibonacci", "write code",
        "attendance sheet", "artificial intelligence", "cloud computing"
    )
    if any(k in input_lower for k in unambiguous_terms):
        return {
            "requirements_complete": True,
            "clarifying_question": None,
            "requirements": [
                {"requirement_id": "R1", "description": f"Execute action corresponding to {task_type}"},
                {"requirement_id": "R2", "description": "Generate physically verified artifact on disk matching user intent"},
            ],
            "execution_trace": [
                {
                    "agent": "requirement_analyzer",
                    "status": "success",
                    "message": f"Requirements verified for {task_type.replace('_', ' ')}.",
                }
            ],
        }

    if task_type == "unknown":
        return {
            "requirements_complete": False,
            "clarifying_question": (
                "Could you please specify what you'd like me to do? For example, "
                "\"Create a PowerPoint about AI\", \"Create an Excel attendance sheet\", or \"Take a screenshot\"."
            ),
            "final_response": (
                "Could you please specify what you'd like me to do? For example, "
                "\"Create a PowerPoint about AI\", \"Create an Excel attendance sheet\", or \"Take a screenshot\"."
            ),
            "execution_trace": [
                {
                    "agent": "requirement_analyzer",
                    "status": "pending",
                    "message": "Ambiguous request — asking for clarification.",
                }
            ],
        }

    messages = state.get("messages", [])
    history_text = "\n".join(
        f"{m.get('role', 'user').capitalize()}: {m.get('content', '')}"
        for m in messages[-6:]
    )

    user_msg = (
        f"Task Type: {task_type}\n\n"
        f"Recent Conversation:\n{history_text}\n\n"
        f"Latest User Input: {user_input}"
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
                logger.warning("Rate limit in requirement_analyzer; backing off for %.1fs (attempt %d/3)...", wait_sec, attempt + 1)
                await asyncio.sleep(wait_sec)
            else:
                logger.warning("RequirementAnalyzer error: %s", exc)
                break

    try:
        raw = str(response.content).strip() if response else "{}"
        parsed = extract_json_object(raw)
        complete = parsed.get("complete", False)
        missing = parsed.get("missing_info", [])
        question = parsed.get("clarifying_question")
    except Exception as exc:
        complete = True
        missing = []
        question = None

    if complete or not question:
        # Extract atomic criteria for validation
        extracted_reqs = [
            {"requirement_id": "R1", "description": f"Execute action corresponding to {task_type}"},
            {"requirement_id": "R2", "description": f"Generate physically verified artifact on disk matching user intent"},
        ]
        return {
            "requirements_complete": True,
            "clarifying_question": None,
            "requirements": extracted_reqs,
            "execution_trace": [
                {
                    "agent": "requirement_analyzer",
                    "status": "success",
                    "message": f"Requirements verified for {task_type.replace('_', ' ')}.",
                }
            ],
        }
    else:
        reason_str = ", ".join(missing) if missing else "Critical parameters missing"
        return {
            "requirements_complete": False,
            "clarifying_question": question,
            "final_response": question,
            "execution_trace": [
                {
                    "agent": "requirement_analyzer",
                    "status": "pending",
                    "message": f"Missing info ({reason_str}). Asking clarification.",
                }
            ],
        }

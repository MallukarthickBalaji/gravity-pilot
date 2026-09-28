"""
supervisor.py — Task classification and routing node.
Classifies user requests and manages multi-turn task continuity.
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
You are the Supervisor of an intelligent desktop automation AI system.
Classify the user's request into one of the following task categories:

1. document_generation:
   Creating, writing, or formatting Word (.docx), Excel (.xlsx), PowerPoint (.pptx), or generating code / script files (.py, .js, .html, etc.).
2. browser_automation:
   Web searches ("Search the web for...", "Find ... online", "Search for information about..."), opening Google ("Open Google"), or navigating to URLs/websites.
3. desktop_automation:
   File or folder operations on the local Windows computer (creating files/folders, copying, moving, renaming, deleting files), taking screenshots ("Take a screenshot", "Capture my screen"), or opening Jupyter notebooks ("Open notebook ...", ".ipynb").
4. general_query:
   Conversational greetings, general questions, explanations, advice, or conceptual questions that do not execute file/web/desktop operations.
5. unknown:
   Ambiguous or unrecognized intent.

CRITICAL RULES:
1. If the previous assistant message asked a clarifying question (for example asking for a presentation topic, column names, or letter recipient) and the user provides that information, classify with the same category that was being clarified (e.g. document_generation for PowerPoint or leave letter)!
2. For sequential prompts that are independent tasks, classify strictly according to the new request.

Output ONLY a JSON object:
{
  "task_type": "<document_generation | browser_automation | desktop_automation | general_query | unknown>",
  "reason": "<one sentence explanation>"
}
"""


async def supervisor_node(state: AgentState) -> dict[str, Any]:
    backend = state.get("model_backend", "none")
    capabilities = state.get("capabilities")
    user_input = (state.get("user_input") or "").strip()

    if backend == "none":
        msg = (
            "GROQ_API_KEY is missing or invalid. "
            "Please add your API key to Gravity-Pilot/.env and restart the application."
        )
        return {
            "task_type": "unknown",
            "final_response": msg,
            "execution_trace": [
                {
                    "agent": "supervisor",
                    "status": "error",
                    "message": "No active LLM backend.",
                }
            ],
        }

    # Deterministic heuristics for unambiguous intent
    input_lower = user_input.lower()
    if any(k in input_lower for k in ("screenshot", "screen shot", "capture screen", "capture my screen")):
        return {
            "task_type": "desktop_automation",
            "execution_trace": [
                {
                    "agent": "supervisor",
                    "status": "success",
                    "message": "Classified as desktop automation (screenshot).",
                }
            ],
        }

    if any(k in input_lower for k in ("reply with", "groq_test_ok", "hello", "hi", "hey")):
        return {
            "task_type": "general_query",
            "execution_trace": [
                {
                    "agent": "supervisor",
                    "status": "success",
                    "message": "Classified as general query.",
                }
            ],
        }

    if any(k in input_lower for k in ("open google", "open https://", "open http://")):
        return {
            "task_type": "browser_automation",
            "execution_trace": [
                {
                    "agent": "supervisor",
                    "status": "success",
                    "message": "Classified as browser automation (open URL).",
                }
            ],
        }

    search_keywords = (
        "search the web", "search for ", "search web", "find online", "lookup online",
        "latest ", "recent ", "official documentation", "official docs", "documentation for",
    )
    if any(k in input_lower for k in search_keywords):
        return {
            "task_type": "browser_automation",
            "execution_trace": [
                {
                    "agent": "supervisor",
                    "status": "success",
                    "message": "Classified as browser automation (web search).",
                }
            ],
        }

    if "notebook" in input_lower or ".ipynb" in input_lower:
        return {
            "task_type": "desktop_automation",
            "execution_trace": [
                {
                    "agent": "supervisor",
                    "status": "success",
                    "message": "Classified as desktop automation (notebook).",
                }
            ],
        }

    # Check if continuing an ongoing task that was awaiting user clarification
    messages = state.get("messages", [])
    last_assistant_msg = next((m for m in reversed(messages) if m.get("role") in ("assistant", "agent")), None)
    prior_user_msg = next((m for m in reversed(messages[:-1]) if m.get("role") == "user"), None)

    if last_assistant_msg and ("?" in last_assistant_msg.get("content", "") or "clarif" in last_assistant_msg.get("content", "").lower()):
        if prior_user_msg:
            p_text = prior_user_msg.get("content", "").lower()
            if any(k in p_text for k in ("powerpoint", "presentation", "slide", "document", "docx", "word", "excel", "sheet", "attendance", "letter")):
                logger.info("Supervisor resuming ongoing document_generation from clarification: %s", p_text)
                return {
                    "task_type": "document_generation",
                    "execution_trace": [
                        {
                            "agent": "supervisor",
                            "status": "success",
                            "message": "Continuing document generation task with user clarification.",
                        }
                    ],
                }
            elif any(k in p_text for k in ("copy", "move", "rename", "delete", "file", "folder", "screenshot", "notebook")):
                return {
                    "task_type": "desktop_automation",
                    "execution_trace": [
                        {
                            "agent": "supervisor",
                            "status": "success",
                            "message": "Continuing desktop automation task with user clarification.",
                        }
                    ],
                }
            elif any(k in p_text for k in ("search", "find", "google", "website", "url", "web")):
                return {
                    "task_type": "browser_automation",
                    "execution_trace": [
                        {
                            "agent": "supervisor",
                            "status": "success",
                            "message": "Continuing browser automation task with user clarification.",
                        }
                    ],
                }

    # LLM Classification
    history_text = "\n".join(
        f"{m.get('role', 'user').capitalize()}: {m.get('content', '')}"
        for m in messages[-4:]
    )

    user_msg = (
        f"Conversation History:\n{history_text}\n\n"
        f"Current User Request: {user_input}\n\n"
        "Classify the task category for this specific user request."
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
                logger.warning("Rate limit in supervisor; backing off for %.1fs (attempt %d/3)...", wait_sec, attempt + 1)
                await asyncio.sleep(wait_sec)
            else:
                logger.warning("Supervisor classification error: %s", exc)
                break

    try:
        raw = str(response.content).strip() if response else "{}"
        parsed = extract_json_object(raw)
        task_type = parsed.get("task_type", "unknown")
        reason = parsed.get("reason", "")
    except Exception as exc:
        task_type = "unknown"
        reason = str(exc)

    # Validate task capability
    if (
        capabilities is not None
        and task_type not in ("general_query", "unknown")
        and not capabilities.supports_task_type(task_type)
    ):
        return {
            "task_type": task_type,
            "final_response": f"The requested task '{task_type}' is currently unavailable in {backend} mode.",
            "execution_trace": [
                {
                    "agent": "supervisor",
                    "status": "skipped",
                    "message": f"Task '{task_type}' requires capabilities not available in {backend} mode.",
                }
            ],
        }

    return {
        "task_type": task_type,
        "execution_trace": [
            {
                "agent": "supervisor",
                "status": "success",
                "message": f"Classified as {task_type.replace('_', ' ')}. {reason}".strip(),
            }
        ],
    }

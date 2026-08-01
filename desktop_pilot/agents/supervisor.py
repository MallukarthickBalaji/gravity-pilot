"""
supervisor.py — Task classification node.

Classifies the incoming user request into a task category and decides
which downstream path to take. Does NOT execute anything itself.

If the selected model_backend is "none" (no LLM available), the supervisor
tells the user honestly rather than silently failing downstream.
"""
from __future__ import annotations

import json
import logging
from typing import Any

from langchain_core.messages import HumanMessage, SystemMessage

from agents.model_router import get_llm
from graph.state import AgentState

logger = logging.getLogger(__name__)

_SYSTEM_PROMPT = """\
You are the supervisor of a desktop automation AI system.
Your ONLY job is to classify the user's request into one of these task types:

  - document_generation  : Creating or editing Word (.docx), Excel (.xlsx), or
                           PowerPoint (.pptx) files
  - browser_automation   : Web search, URL navigation, or data extraction from
                           websites
  - desktop_automation   : File/folder operations (create, move, delete, rename)
                           or launching/controlling applications
  - general_query        : Information requests or conversational questions that
                           do NOT require file/web/desktop execution
  - unknown              : Cannot determine the intent

You will be told which capabilities are currently available.
If the user's request requires a capability that is NOT available, you MUST
still classify it correctly — do NOT change the classification to work around
the limitation. The system will inform the user.

Respond with ONLY a JSON object — no prose, no markdown, no code fences:
{
  "task_type": "<one of the five types above>",
  "reason": "<one sentence explaining your classification>"
}
"""


async def supervisor_node(state: AgentState) -> dict[str, Any]:
    """LangGraph node: classifies the user request and annotates state."""
    backend = state.get("model_backend", "none")
    capabilities = state.get("capabilities")

    # ── No backend available — bail out early ─────────────────────────────────
    if backend == "none":
        msg = (
            "No LLM backend is reachable. "
            "Please check your GROQ_API_KEY or start Ollama, then try again."
        )
        return {
            "task_type": "unknown",
            "final_response": msg,
            "execution_trace": [
                {
                    "agent": "supervisor",
                    "status": "error",
                    "message": "No backend — cannot classify request.",
                }
            ],
        }

    # ── Build prompt ──────────────────────────────────────────────────────────
    caps_summary = (
        f"browser_automation={'yes' if capabilities and capabilities.browser_automation else 'NO — offline mode'}; "
        f"desktop_automation={'yes' if capabilities and capabilities.desktop_automation else 'no'}; "
        f"document_generation={'yes' if capabilities and capabilities.document_generation else 'no'}"
    )

    user_msg = (
        f"User request: {state['user_input']}\n\n"
        f"Available capabilities in current mode: {caps_summary}"
    )

    llm = get_llm(backend)
    try:
        response = await llm.ainvoke(
            [SystemMessage(content=_SYSTEM_PROMPT), HumanMessage(content=user_msg)]
        )
        raw = response.content.strip()
        # Strip any accidental markdown code fences
        if raw.startswith("```"):
            raw = raw.split("```")[1]
            if raw.startswith("json"):
                raw = raw[4:]
        parsed: dict = json.loads(raw)
        task_type: str = parsed.get("task_type", "unknown")
        reason: str = parsed.get("reason", "")
    except Exception as exc:
        logger.exception("Supervisor LLM call failed: %s", exc)
        task_type = "unknown"
        reason = f"Classification error: {exc}"

    logger.info("Supervisor classified '%s' → %s", state["user_input"][:60], task_type)

    # ── Check capability availability ─────────────────────────────────────────
    capability_unavailable = (
        capabilities is not None
        and task_type not in ("general_query", "unknown")
        and not capabilities.supports_task_type(task_type)
    )

    if capability_unavailable:
        mode_label = "offline (Ollama)" if backend == "ollama" else "current"
        human_msg = (
            f"I can't run a **{task_type.replace('_', ' ')}** task right now — "
            f"that capability is unavailable in {mode_label} mode.\n\n"
            f"In offline mode, I can help with:\n"
            f"  • Generating Word, Excel, or PowerPoint documents\n"
            f"  • Local file and folder operations\n\n"
            f"Please connect to the internet to use browser automation, "
            f"or rephrase your request."
        )
        return {
            "task_type": task_type,
            "final_response": human_msg,
            "execution_trace": [
                {
                    "agent": "supervisor",
                    "status": "skipped",
                    "message": (
                        f"Classified as {task_type}; "
                        f"capability unavailable in {backend} mode."
                    ),
                }
            ],
        }

    return {
        "task_type": task_type,
        "execution_trace": [
            {
                "agent": "supervisor",
                "status": "success",
                "message": f"Classified as '{task_type}'. {reason}",
            }
        ],
    }

"""
requirement_analyzer.py — Requirements completeness checker.

Checks whether the current state has enough information to plan.
If information is missing, it generates ONE clarifying question and returns
control to the user (the graph routes to END so the CLI/UI can present it).

After the user replies, supervisor resumes the flow.
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
You are a requirements analyst for a task execution system.

Given a user request and its task type, determine whether you have ALL the
information needed to execute the task without ambiguity.

Required information by task type:
  document_generation:
    - Document type (Word .docx / Excel .xlsx / PowerPoint .pptx)
    - Content or data (title, headings, paragraphs, rows/columns, slide bullets)
    - Desired output filename (or acceptable to auto-generate)

  browser_automation:
    - Target URL or search query
    - What specific data to extract or action to perform

  desktop_automation:
    - Specific file paths, folder names, or application names to interact with
    - The exact operation (create / move / copy / delete / rename / launch)

  general_query:
    - Always considered complete — no execution agent is needed.

Rules:
  - If ONE piece of critical information is missing, ask for it in a single,
    friendly, specific question. Do not ask multiple questions at once.
  - If everything is clear, mark complete.
  - Do NOT assume default values silently for document content or file paths.

Respond with ONLY a JSON object — no prose, no markdown, no code fences:
{
  "complete": true | false,
  "missing_info": ["item1", "item2"],
  "clarifying_question": "<one question to ask the user, or null if complete>"
}
"""


async def requirement_analyzer_node(state: AgentState) -> dict[str, Any]:
    """LangGraph node: checks requirements completeness."""
    backend = state.get("model_backend", "none")
    task_type = state.get("task_type", "unknown")

    # ── General queries need no further analysis ───────────────────────────────
    if task_type == "general_query":
        return {
            "requirements_complete": True,
            "clarifying_question": None,
            "execution_trace": [
                {
                    "agent": "requirement_analyzer",
                    "status": "success",
                    "message": "General query — no execution requirements to check.",
                }
            ],
        }

    # ── Unknown task type — ask user to rephrase ───────────────────────────────
    if task_type == "unknown":
        return {
            "requirements_complete": False,
            "clarifying_question": (
                "I wasn't sure what you'd like me to do. "
                "Could you describe the task more specifically? "
                "For example: \"Create a Word document…\", \"Search the web for…\", "
                "or \"Move a file from…\"."
            ),
            "execution_trace": [
                {
                    "agent": "requirement_analyzer",
                    "status": "pending",
                    "message": "Task type unknown — asking user to clarify.",
                }
            ],
        }

    # ── Build context from conversation history ────────────────────────────────
    # Include all prior messages so the analyzer understands follow-up context.
    history_text = "\n".join(
        f"{m['role'].capitalize()}: {m['content']}"
        for m in state.get("messages", [])
    )

    user_msg = (
        f"Task type: {task_type}\n\n"
        f"Conversation so far:\n{history_text}\n\n"
        f"Current user input: {state['user_input']}"
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
        complete: bool = parsed.get("complete", False)
        missing: list = parsed.get("missing_info", [])
        question: str | None = parsed.get("clarifying_question")
    except Exception as exc:
        logger.exception("RequirementAnalyzer LLM call failed: %s", exc)
        complete = False
        missing = ["(analysis error)"]
        question = "I had trouble analysing your request. Could you rephrase it with more detail?"

    if complete:
        logger.info("RequirementAnalyzer → complete for task_type=%s", task_type)
        return {
            "requirements_complete": True,
            "clarifying_question": None,
            "execution_trace": [
                {
                    "agent": "requirement_analyzer",
                    "status": "success",
                    "message": f"All requirements met for {task_type}.",
                }
            ],
        }
    else:
        logger.info(
            "RequirementAnalyzer → incomplete (missing: %s)", ", ".join(missing)
        )
        return {
            "requirements_complete": False,
            "clarifying_question": question,
            "execution_trace": [
                {
                    "agent": "requirement_analyzer",
                    "status": "pending",
                    "message": f"Missing: {', '.join(missing)}. Asking user.",
                }
            ],
        }

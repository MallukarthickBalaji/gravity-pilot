"""
requirement_analyzer.py — Requirements completeness checker.

Instead of asking the LLM to reason about missing fields (which smaller models struggle with),
we ask the LLM to simply extract what IT KNOWS from the conversation into a JSON object.
Then, Python code determines if anything is missing and asks the user.
"""
from __future__ import annotations

import json
import logging
from typing import Any

from langchain_core.messages import HumanMessage, SystemMessage

from agents.model_router import get_llm
from graph.state import AgentState

logger = logging.getLogger(__name__)

_ANALYSIS_PROMPT = """\
You are an intelligent Requirements Analyzer. Read the conversation history and the current user request.
Determine if you have enough information to fulfill the user's task.

For document generation, apply these rules:
1. Formal Letter: Requires purpose, recipient, and sender name. (Do NOT be overly pedantic. "my manager" is a valid recipient. "5 days" is a valid date duration. Accept reasonable approximations without asking for exact names or exact calendar dates).
2. Report: Requires report topic and key sections/content.
3. PowerPoint: MUST require a topic. If the user just says "Create a PowerPoint", you MUST set requirements_complete to false and ask for the topic. Use sensible defaults for slide count/content if not provided.
4. Excel: Requires what should be tracked or data columns (e.g., "attendance report for 10 students" is sufficient).
5. Filename: DO NOT treat filename as a requirement unless the user explicitly asks to specify one. A meaningful filename will be auto-generated.

NEVER hallucinate or invent user-specific information (names, recipients, dates, companies, etc.). If it's missing and required, ask for it.

Output ONLY a JSON object in this exact format:
{
    "requirements_complete": true or false,
    "missing_fields": ["list", "of", "missing", "fields"],
    "clarifying_question": "A natural question asking for the missing fields, or empty string if complete",
    "collected_data": {
        "document_type": "word/excel/powerpoint/null",
        "key1": "extracted value 1"
    }
}
"""

async def requirement_analyzer_node(state: AgentState) -> dict[str, Any]:
    """LangGraph node: checks requirements completeness by using LLM to analyze missing fields."""
    backend = state.get("model_backend", "none")
    task_type = state.get("task_type", "unknown")
    current_info = state.get("current_task_info", {}) or {}

    # General queries need no further analysis
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

    if task_type == "unknown":
        return {
            "requirements_complete": False,
            "clarifying_question": "I wasn't sure what you'd like me to do. Could you describe the task more specifically?",
            "status": "waiting_for_user",
            "execution_trace": [
                {
                    "agent": "requirement_analyzer",
                    "status": "pending",
                    "message": "Task type unknown — asking user to clarify.",
                }
            ],
        }

    # Build conversation context
    history_text = "\n".join(
        f"{m['role'].capitalize()}: {m['content']}"
        for m in state.get("messages", [])
    )
    
    current_state_text = json.dumps(current_info, indent=2)

    user_msg = f"Task type: {task_type}\n\nPreviously collected data:\n{current_state_text}\n\nConversation so far:\n{history_text}\n\nCurrent user input: {state['user_input']}"

    llm = get_llm(backend)
    extracted = {}
    try:
        response = await llm.ainvoke(
            [SystemMessage(content=_ANALYSIS_PROMPT), HumanMessage(content=user_msg)]
        )
        raw = str(response.content).strip()
        
        # Use regex to find the JSON block in case there is conversational text
        import re
        match = re.search(r'```(?:json)?(.*?)```', raw, re.DOTALL)
        if match:
            raw = match.group(1).strip()
        else:
            # Fallback if no code blocks, try to find first { and last }
            start = raw.find('{')
            end = raw.rfind('}')
            if start != -1 and end != -1:
                raw = raw[start:end+1]
                
        extracted = json.loads(raw.strip())
    except Exception as exc:
        logger.exception("RequirementAnalyzer LLM extraction failed: %s", exc)
        return {
            "requirements_complete": False,
            "clarifying_question": "I had trouble understanding your request. Could you please provide the details one more time?",
            "status": "waiting_for_user",
            "execution_trace": [{"agent": "requirement_analyzer", "status": "pending", "message": "Extraction failed due to invalid LLM output."}]
        }

    # Merge extracted data into current_task_info
    new_data = extracted.get("collected_data", {})
    for k, v in new_data.items():
        if v is not None and v != "":
            current_info[k] = str(v).strip()

    # Determine default document type if missing
    if task_type == "document_generation" and not current_info.get("document_type"):
        text_lower = history_text.lower() + " " + state['user_input'].lower()
        if "presentation" in text_lower or "ppt" in text_lower or "slide" in text_lower:
            current_info["document_type"] = "powerpoint"
        elif "excel" in text_lower or "sheet" in text_lower or "csv" in text_lower:
            current_info["document_type"] = "excel"
        elif "word" in text_lower or "letter" in text_lower or "doc" in text_lower:
            current_info["document_type"] = "word"

    logger.info("RequirementAnalyzer COLLECTED DATA: %s", current_info)

    requirements_complete = extracted.get("requirements_complete", False)
    clarifying_question = extracted.get("clarifying_question", "")
    missing_fields = extracted.get("missing_fields", [])

    if requirements_complete:
        logger.info("RequirementAnalyzer → complete for task_type=%s", task_type)
        return {
            "requirements_complete": True,
            "clarifying_question": None,
            "current_task_info": current_info,
            "execution_trace": [
                {
                    "agent": "requirement_analyzer",
                    "status": "success",
                    "message": f"All requirements met for {task_type}.",
                }
            ],
        }
    else:
        logger.info("RequirementAnalyzer → incomplete (MISSING FIELDS: %s)", ", ".join(missing_fields))
        return {
            "requirements_complete": False,
            "clarifying_question": clarifying_question if clarifying_question else "Could you please provide more details?",
            "current_task_info": current_info,
            "status": "waiting_for_user",
            "execution_trace": [
                {
                    "agent": "requirement_analyzer",
                    "status": "pending",
                    "message": f"Missing: {', '.join(missing_fields)}. Asking user.",
                }
            ],
        }

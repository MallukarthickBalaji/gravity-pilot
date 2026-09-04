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

_EXTRACTION_PROMPT = """\
You are an extraction assistant. Read the conversation history and extract ONLY the requested parameters based on the task type.
Only extract what is explicitly provided. Do NOT guess or invent values. If a value is missing, set it to null.

Task: document_generation
Expected JSON format:
{
  "document_type": "word, excel, or powerpoint" (or null),
  "content": "A summary of what should be inside the document" (or null),
  "filename": "The desired file name" (or null)
}

Task: desktop_automation
Expected JSON format:
{
  "operation": "create, move, copy, delete, rename, or launch" (or null),
  "target_path": "File or folder path or app name" (or null)
}

Task: browser_automation
Expected JSON format:
{
  "target_url_or_query": "The website or search term" (or null),
  "action": "What to do or extract" (or null)
}

Output ONLY raw JSON. No markdown tags. No explanations.
"""


async def requirement_analyzer_node(state: AgentState) -> dict[str, Any]:
    """LangGraph node: checks requirements completeness by extracting fields."""
    backend = state.get("model_backend", "none")
    task_type = state.get("task_type", "unknown")
    current_info = state.get("current_task_info", {})

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

    user_msg = f"Task type: {task_type}\n\nConversation so far:\n{history_text}\n\nCurrent user input: {state['user_input']}"

    llm = get_llm(backend)
    extracted = {}
    try:
        response = await llm.ainvoke(
            [SystemMessage(content=_EXTRACTION_PROMPT), HumanMessage(content=user_msg)]
        )
        raw = str(response.content).strip()
        if raw.startswith("```"):
            raw = raw.split("```")[1]
            if raw.startswith("json"):
                raw = raw[4:]
        extracted = json.loads(raw)
    except Exception as exc:
        logger.exception("RequirementAnalyzer LLM extraction failed: %s", exc)
        return {
            "requirements_complete": False,
            "clarifying_question": "I had trouble understanding your request. Could you please provide the details one more time?",
            "execution_trace": [{"agent": "requirement_analyzer", "status": "pending", "message": "Extraction failed due to invalid LLM output."}]
        }

    # Merge extracted data into current_task_info
    for k, v in extracted.items():
        if v is not None:
            current_info[k] = str(v).strip()

    logger.info("COLLECTED DATA: %s", current_info)

    # Evaluate completeness in Python
    missing = []
    question = None

    if task_type == "document_generation":
        # Auto-infer document type if missing
        if not current_info.get("document_type"):
            text_lower = history_text.lower() + " " + state['user_input'].lower()
            if "presentation" in text_lower or "ppt" in text_lower or "slide" in text_lower:
                current_info["document_type"] = "powerpoint"
            elif "excel" in text_lower or "sheet" in text_lower or "csv" in text_lower:
                current_info["document_type"] = "excel"
            elif "word" in text_lower or "letter" in text_lower or "doc" in text_lower:
                current_info["document_type"] = "word"
        
        # Provide default filename if missing based on document type
        if not current_info.get("filename"):
            dt = current_info.get("document_type", "").lower()
            if dt == "powerpoint" or dt == "pptx":
                current_info["filename"] = "Presentation.pptx"
            elif dt == "excel" or dt == "xlsx":
                current_info["filename"] = "Spreadsheet.xlsx"
            elif dt == "word" or dt == "docx":
                current_info["filename"] = "Document.docx"
            else:
                current_info["filename"] = "Generated_Document"

        if not current_info.get("document_type"):
            missing.append("Document Type (Word/Excel/PowerPoint)")
            question = "What kind of document would you like to generate (Word, Excel, or PowerPoint)?"
        elif not current_info.get("content"):
            missing.append("Document Content")
            question = f"What specific information or content should I include in the {current_info.get('document_type')} document?"
            
    elif task_type == "desktop_automation":
        if not current_info.get("operation"):
            missing.append("Operation Type")
            question = "What exactly would you like me to do? (e.g. create a folder, move a file, open an app)"
        elif not current_info.get("target_path"):
            missing.append("Target Path/App")
            question = "What is the name of the file, folder, or application you want to interact with?"
            
    elif task_type == "browser_automation":
        if not current_info.get("target_url_or_query"):
            missing.append("URL/Query")
            question = "What website or search query should I look up?"
        elif not current_info.get("action"):
            missing.append("Action")
            question = "What specific information would you like me to extract or do on that page?"

    if not missing:
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
        logger.info("RequirementAnalyzer → incomplete (MISSING FIELDS: %s)", ", ".join(missing))
        return {
            "requirements_complete": False,
            "clarifying_question": question,
            "current_task_info": current_info,
            "execution_trace": [
                {
                    "agent": "requirement_analyzer",
                    "status": "pending",
                    "message": f"Missing: {', '.join(missing)}. Asking user.",
                }
            ],
        }

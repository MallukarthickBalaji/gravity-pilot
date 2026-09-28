"""
document_agent.py — Document generation orchestration node.
Orchestrates generation of Word (.docx), Excel (.xlsx), PowerPoint (.pptx), and code files
by dispatching execution to deterministic tool handlers in tools.documents.
"""
from __future__ import annotations

import logging
from pathlib import Path
from typing import Any

from graph.state import AgentState
from tools.documents import (
    generate_code_file,
    generate_excel_sheet,
    generate_powerpoint,
    generate_word_doc,
    GENERATORS,
)

logger = logging.getLogger(__name__)

# Re-export tools for backward compatibility
__all__ = [
    "generate_word_doc",
    "generate_excel_sheet",
    "generate_powerpoint",
    "generate_code_file",
    "GENERATORS",
    "document_agent_node",
]


async def document_agent_node(state: AgentState) -> dict[str, Any]:
    plan = state.get("plan", [])
    current_step = state.get("current_step", 0)

    if not plan or current_step >= len(plan):
        return {
            "last_execution_result": {"success": False, "error": "No document plan step available"},
            "current_step": current_step + 1,
            "execution_trace": [
                {
                    "agent": "document_agent",
                    "status": "error",
                    "message": "No document plan step available.",
                }
            ],
        }

    step = plan[current_step]
    params = step.get("params", {})
    doc_type = params.get("doc_type", "word").lower()
    filename = params.get("output_filename", f"document_{doc_type}")
    content = params.get("content", {})
    output_dir = params.get("output_dir")

    exec_results = list(state.get("execution_results", []))
    artifact_paths = list(state.get("artifact_paths", []))

    gen_fn = GENERATORS.get(doc_type)
    if not gen_fn:
        err = f"Unsupported document type: {doc_type}"
        res = {"success": False, "error": err, "agent_type": "document_agent", "doc_type": doc_type}
        exec_results.append(res)
        return {
            "last_execution_result": res,
            "execution_results": exec_results,
            "current_step": current_step + 1,
            "execution_trace": [
                {
                    "agent": "document_agent",
                    "status": "error",
                    "message": err,
                }
            ],
        }

    try:
        out_path = gen_fn(filename, content, output_dir=output_dir)
        doc_label = {
            "word": "Word document",
            "excel": "Excel spreadsheet",
            "powerpoint": "PowerPoint presentation",
            "code": "code file",
        }.get(doc_type, "Document")

        res = {
            "success": True,
            "output_path": out_path,
            "doc_type": doc_type,
            "filename": Path(out_path).name,
            "agent_type": "document_agent",
            "content_summary": {
                "title": content.get("title"),
                "sections": len(content.get("sections", [])),
                "headers": content.get("headers"),
                "rows_count": len(content.get("rows", [])),
                "slides_count": len(content.get("slides", [])),
            },
        }
        exec_results.append(res)
        if out_path not in artifact_paths:
            artifact_paths.append(out_path)

        return {
            "last_execution_result": res,
            "execution_results": exec_results,
            "artifact_paths": artifact_paths,
            "current_step": current_step + 1,
            "execution_trace": [
                {
                    "agent": "document_agent",
                    "status": "success",
                    "message": f"Created {doc_label}: {Path(out_path).name}",
                }
            ],
        }
    except Exception as exc:
        logger.exception("Document generation failed: %s", exc)
        res = {
            "success": False,
            "error": str(exc),
            "doc_type": doc_type,
            "agent_type": "document_agent",
        }
        exec_results.append(res)
        return {
            "last_execution_result": res,
            "execution_results": exec_results,
            "artifact_paths": artifact_paths,
            "current_step": current_step + 1,
            "execution_trace": [
                {
                    "agent": "document_agent",
                    "status": "error",
                    "message": f"Document generation failed: {exc}",
                }
            ],
        }

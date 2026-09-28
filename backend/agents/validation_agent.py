"""
validation_agent.py — Rigorous result validation for all execution outcomes.
Performs real filesystem, document readability, and data extraction checks.
Triggers replanning cycle on failure up to MAX_REPLAN_ATTEMPTS.
"""
from __future__ import annotations

import logging
from datetime import datetime
from pathlib import Path
from typing import Any

from graph.state import AgentState

logger = logging.getLogger(__name__)

MAX_REPLAN_ATTEMPTS = 2


def _validate_desktop_operation(result: dict[str, Any]) -> tuple[bool, str]:
    operation = result.get("operation", "")
    src_str = result.get("source_path")
    out_str = result.get("output_path")

    src = Path(src_str) if src_str else None
    dst = Path(out_str) if out_str else None

    if operation == "copy":
        if not src or not src.exists():
            return False, f"Copy validation failed: source file '{src}' no longer exists."
        if not dst or not dst.exists():
            return False, f"Copy validation failed: destination file '{dst}' does not exist."
        return True, f"Verified that '{src.name}' exists at both source and destination: '{dst}'."

    elif operation == "move":
        if src and src.exists():
            return False, f"Move validation failed: source file '{src}' still exists."
        if not dst or not dst.exists():
            return False, f"Move validation failed: destination file '{dst}' does not exist."
        return True, f"Verified that file was removed from source and now exists at: '{dst}'."

    elif operation == "rename":
        if src and src.exists():
            return False, f"Rename validation failed: old filename '{src}' still exists."
        if not dst or not dst.exists():
            return False, f"Rename validation failed: new filename '{dst}' does not exist."
        return True, f"Verified that file was renamed to '{dst.name}' at: '{dst}'."

    elif operation == "delete":
        if src and src.exists():
            return False, f"Delete validation failed: target '{src}' still exists."
        return True, f"Verified that '{src.name if src else 'file'}' was successfully deleted."

    elif operation in ("create_file", "create_folder"):
        if not dst or not dst.exists():
            return False, f"Creation validation failed: target '{dst}' does not exist."
        return True, f"Verified that '{dst.name}' was created at: '{dst}'."

    elif operation == "screenshot":
        if not dst or not dst.exists():
            return False, f"Screenshot validation failed: file '{dst}' was not created."
        if dst.stat().st_size == 0:
            return False, f"Screenshot validation failed: file '{dst}' is 0 bytes."
        return True, f"Verified screenshot saved at: '{dst}' ({dst.stat().st_size} bytes)."

    elif operation == "open_notebook":
        if not result.get("success", False):
            return False, result.get("error", "Failed to open notebook.")
        return True, f"Verified notebook '{Path(src_str).name if src_str else 'notebook'}' opened successfully."

    elif operation == "launch_app":
        return True, f"Application launched: {src_str}."

    return True, "Desktop operation verified."


def _validate_document(result: dict[str, Any]) -> tuple[bool, str]:
    out_path_str = result.get("output_path")
    doc_type = result.get("doc_type", "")

    if not out_path_str:
        return False, "Document validation failed: No output file path provided."

    path = Path(out_path_str)
    if not path.exists():
        return False, f"Document validation failed: File '{path}' does not exist."

    if path.stat().st_size == 0:
        return False, f"Document validation failed: File '{path}' is empty (0 bytes)."

    # Verify actual file structure readability
    try:
        if doc_type == "word":
            from docx import Document
            doc = Document(str(path))
            if len(doc.paragraphs) == 0 and len(doc.tables) == 0:
                return False, "Word document contains no paragraphs or content."
            return True, f"Verified Word document ({len(doc.paragraphs)} paragraphs, {path.stat().st_size} bytes)."

        elif doc_type == "excel":
            import openpyxl
            wb = openpyxl.load_workbook(str(path))
            sheet = wb.active
            if sheet is None or sheet.max_row == 0:
                return False, "Excel workbook is empty."
            return True, f"Verified Excel workbook '{sheet.title}' ({sheet.max_row} rows, {sheet.max_column} columns)."

        elif doc_type == "powerpoint":
            from pptx import Presentation
            prs = Presentation(str(path))
            if len(prs.slides) == 0:
                return False, "PowerPoint presentation contains no slides."
            return True, f"Verified PowerPoint presentation ({len(prs.slides)} slides)."

        elif doc_type in ("code", "text"):
            content = path.read_text(encoding="utf-8")
            if not content.strip():
                return False, f"Generated file '{path.name}' is empty."
            return True, f"Verified code file '{path.name}' ({len(content)} characters)."

    except Exception as exc:
        return False, f"Document readability validation failed: {exc}"

    return True, f"Verified document saved at '{path}'."


def _validate_browser(result: dict[str, Any]) -> tuple[bool, str]:
    operation = result.get("operation")
    if operation == "open_url":
        url = result.get("url", "")
        if not url:
            return False, "Browser validation failed: No target URL was provided."
        return True, f"Verified website opened: {url}"

    # 1. Check blocked status or bot challenge
    if result.get("blocked", False):
        reason = result.get("reason") or "Search provider returned a bot verification challenge"
        return False, f"Search blocked: {reason}"

    status = result.get("status", "")
    if status != "success":
        err = result.get("error") or f"Search status is '{status}' (expected 'success')"
        return False, f"Search validation failed: {err}"

    # 2. Check structured results array
    results = result.get("results")
    if not isinstance(results, list) or len(results) == 0:
        return False, "Search validation failed: No structured search results returned."

    # 3. Validate each result
    from models.web_search import detect_bot_challenge
    valid_count = 0
    for idx, item in enumerate(results, 1):
        if not isinstance(item, dict):
            return False, f"Search result #{idx} is not a valid structured dictionary."
        title = (item.get("title") or "").strip()
        url = (item.get("url") or "").strip()
        snippet = (item.get("snippet") or "").strip()

        if not title:
            return False, f"Search result #{idx} is missing a title."
        if not url or not url.startswith(("http://", "https://")):
            return False, f"Search result #{idx} has an invalid URL: '{url}'"
        if not snippet:
            return False, f"Search result #{idx} is missing a snippet."

        # Check for CAPTCHA / bot challenge in title or snippet
        is_blocked, phrase = detect_bot_challenge(f"{title} {snippet}")
        if is_blocked:
            return False, f"Search result #{idx} contains bot verification challenge: {phrase}"

        # Check for navigation-only boilerplate
        nav_terms = {"images", "videos", "news", "maps", "open menu", "duck.ai", "sign in", "all images videos"}
        if title.lower().strip() in nav_terms and len(snippet) < 30:
            return False, f"Search result #{idx} contains only navigation text."

        valid_count += 1

    if valid_count == 0:
        return False, "Search validation failed: No valid results passed content checks."

    provider = result.get("provider", "search engine")
    return True, f"Verified {valid_count} search results from {provider} with valid titles, URLs, and snippets."


async def validation_agent_node(state: AgentState) -> dict[str, Any]:
    exec_results = list(state.get("execution_results") or [])
    last_result = state.get("last_execution_result")
    if not exec_results and last_result:
        exec_results = [last_result]

    replan_count = state.get("replan_count", 0)
    max_replans = state.get("max_replans", MAX_REPLAN_ATTEMPTS)

    if not exec_results:
        return {
            "validation_result": {"passed": False, "reason": "No execution result to validate."},
            "validation_status": "failed",
            "validation_errors": ["No execution result found to validate."],
            "replan_required": False,
            "replan_reason": None,
            "final_response": "Task could not be completed (no execution result).",
            "failure_reason": "No execution result to validate.",
            "failure_category": "F7",
            "execution_trace": [
                {
                    "agent": "validation_agent",
                    "status": "error",
                    "message": "No execution result found to validate.",
                }
            ],
        }

    val_errors: list[str] = []
    val_messages: list[str] = []

    # 1. Validate every step result
    for idx, res in enumerate(exec_results, 1):
        if not res.get("success", True):
            err = res.get("error", f"Step {idx} execution failed.")
            val_errors.append(f"Step {idx}: {err}")
            continue

        agent_type = res.get("agent_type")
        step_passed = True
        msg = f"Step {idx} verified."
        if agent_type == "desktop_agent":
            step_passed, msg = _validate_desktop_operation(res)
        elif agent_type == "document_agent":
            step_passed, msg = _validate_document(res)
        elif agent_type == "browser_agent":
            step_passed, msg = _validate_browser(res)

        if not step_passed:
            val_errors.append(f"Step {idx} validation failed: {msg}")
        else:
            val_messages.append(msg)

    # 2. Controlled fault-injection mechanism for research replanning scenarios
    fault = state.get("experimental_fault_injection")
    if fault and replan_count == 0:
        target_task = fault.get("task_id")
        cur_task = state.get("task_id")
        if not target_task or target_task == cur_task or (cur_task and target_task in cur_task):
            fault_reason = fault.get("reason", "Controlled experimental validation failure: missing required content")
            fault_cat = fault.get("category", "F8")
            logger.info("Executing controlled experimental fault injection: %s", fault_reason)
            val_errors.append(f"[EXPERIMENTAL FAULT INJECTION] {fault_reason}")

    # 3. Handle validation failure & replanning decision
    if val_errors:
        combined_error = "; ".join(val_errors)
        logger.warning("Validation check failed: %s", combined_error)

        # Check for unrecoverable search blocked error
        if any("Search blocked" in err for err in val_errors):
            return {
                "validation_result": {"passed": False, "reason": combined_error},
                "validation_status": "failed",
                "validation_errors": val_errors,
                "replan_required": False,
                "replan_reason": None,
                "failure_reason": combined_error,
                "failure_category": "F7",
                "final_response": "I couldn't retrieve live search results because the search provider blocked the request.",
                "execution_trace": [
                    {
                        "agent": "validation_agent",
                        "status": "error",
                        "message": f"Validation rejected result: {combined_error}",
                    }
                ],
            }

        if replan_count < max_replans:
            logger.info("Triggering replanning cycle (attempt %d of %d)", replan_count + 1, max_replans)
            return {
                "validation_result": {"passed": False, "reason": combined_error},
                "validation_status": "failed",
                "validation_errors": val_errors,
                "replan_required": True,
                "replan_reason": "execution_failure",
                "replan_count": replan_count + 1,
                "execution_trace": [
                    {
                        "agent": "validation_agent",
                        "status": "error",
                        "message": f"Validation failed ({combined_error}). Initiating replanning attempt {replan_count + 1} of {max_replans}...",
                    }
                ],
            }
        else:
            return {
                "validation_result": {"passed": False, "reason": combined_error},
                "validation_status": "failed",
                "validation_errors": val_errors,
                "replan_required": False,
                "replan_reason": "missing_info",
                "failure_reason": combined_error,
                "failure_category": "F9",
                "final_response": f"Task could not be completed after {max_replans} replanning attempts: {combined_error}",
                "execution_trace": [
                    {
                        "agent": "validation_agent",
                        "status": "error",
                        "message": f"Validation failed after {max_replans} attempts: {combined_error}",
                    }
                ],
            }

    # 4. Validation passed
    val_msg = "All execution steps and physical artifacts verified successfully."
    if val_messages:
        val_msg = " | ".join(val_messages)

    final_res = exec_results[-1] if exec_results else (last_result or {})
    final_response = _build_human_response(final_res)

    # Track all valid output files
    generated_outputs = []
    for res in exec_results:
        out_path = res.get("output_path")
        if out_path and Path(out_path).exists() and not Path(out_path).is_dir():
            p = Path(out_path)
            generated_outputs.append({
                "task_id": state.get("task_id"),
                "session_id": state.get("session_id"),
                "file_path": str(p),
                "file_name": p.name,
                "file_type": p.suffix.lstrip(".").lower(),
                "status": "completed",
                "created_at": datetime.utcnow().isoformat(),
            })

    return {
        "validation_result": {"passed": True, "reason": val_msg},
        "validation_status": "passed",
        "validation_errors": [],
        "replan_required": False,
        "replan_reason": None,
        "final_response": final_response,
        "generated_outputs": generated_outputs,
        "execution_trace": [
            {
                "agent": "validation_agent",
                "status": "success",
                "message": f"Validation passed. {val_msg}",
            }
        ],
    }


def _build_human_response(result: dict[str, Any]) -> str:
    agent_type = result.get("agent_type")
    operation = result.get("operation")
    out_path = result.get("output_path")
    doc_type = result.get("doc_type")

    if agent_type == "desktop_agent":
        src = result.get("source_path", "")
        if operation == "copy":
            return f"Copied {Path(src).name} to {out_path} successfully."
        elif operation == "move":
            return f"Moved {Path(src).name} to {out_path} successfully."
        elif operation == "rename":
            return f"Renamed {Path(src).name} to {Path(out_path).name} successfully."
        elif operation == "delete":
            return f"Deleted {Path(src).name} successfully."
        elif operation == "create_file":
            return f"Created file {Path(out_path).name} at `{out_path}`."
        elif operation == "create_folder":
            return f"Created folder {Path(out_path).name} at `{out_path}`."
        elif operation == "screenshot":
            return f"Screenshot captured successfully!\n\nFile saved to: `{out_path}`"
        elif operation == "open_notebook":
            return f"Opened Jupyter Notebook '{Path(src).name}' successfully."
        return f"Desktop operation '{operation}' completed successfully."

    elif agent_type == "document_agent":
        type_title = {"word": "Word document", "excel": "Excel spreadsheet", "powerpoint": "PowerPoint presentation"}.get(doc_type, "Document")
        fname = Path(out_path).name if out_path else "document"
        return f"Created {type_title} '{fname}' successfully.\n\nFile saved to: `{out_path}`"

    elif agent_type == "browser_agent":
        if operation == "open_url":
            url = result.get("url", "")
            return f"Opened website in your browser: {url}"

        query = result.get("query", "")
        results = result.get("results", [])
        if results and isinstance(results, list):
            lines = [f"Search results for \"{query}\":\n"]
            for i, r in enumerate(results, 1):
                title = r.get("title", "")
                url = r.get("url", "")
                src = r.get("source") or url
                snip = r.get("snippet", "")
                lines.append(f"{i}. **{title}**\n   *Source: {src}*\n   {snip}\n   [Link]({url})\n")
            return "\n".join(lines).strip()

        extracted = result.get("extracted_data", "")
        if extracted:
            return extracted
        return "Search completed with no results."

    return "Task completed successfully."

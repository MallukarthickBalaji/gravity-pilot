"""
json_utils.py — Robust JSON extraction and repair utilities.
Extracts valid JSON objects from raw LLM completions even when surrounded
by conversational preamble, markdown code blocks, or trailing commentary.
"""
from __future__ import annotations

import json
import logging
import re
from typing import Any

logger = logging.getLogger(__name__)


def extract_json_object(text: str) -> dict[str, Any]:
    """
    Extract the first valid JSON object from arbitrary LLM output text.
    Handles:
    - Markdown code fences (```json ... ``` or ``` ...)
    - Conversational text before/after JSON
    - Trailing commas before closing braces/brackets
    """
    if not text or not text.strip():
        return {}

    cleaned = text.strip()

    # 1. Direct parse attempt
    try:
        res = json.loads(cleaned)
        if isinstance(res, dict):
            return res
    except Exception:
        pass

    # 2. Extract block within markdown code fences
    fence_pattern = r"```(?:json)?\s*([\s\S]*?)\s*```"
    match = re.search(fence_pattern, cleaned, re.IGNORECASE)
    if match:
        block = match.group(1).strip()
        try:
            res = json.loads(block)
            if isinstance(res, dict):
                return res
        except Exception:
            pass

    # 3. Locate the outermost balanced curly braces { ... }
    first_brace = cleaned.find("{")
    last_brace = cleaned.rfind("}")
    if first_brace != -1 and last_brace != -1 and last_brace > first_brace:
        candidate = cleaned[first_brace : last_brace + 1].strip()
        try:
            res = json.loads(candidate)
            if isinstance(res, dict):
                return res
        except Exception:
            # Fix common trailing comma issues
            repaired = re.sub(r",\s*([}\]])", r"\1", candidate)
            try:
                res = json.loads(repaired)
                if isinstance(res, dict):
                    return res
            except Exception:
                pass

    logger.warning("Failed to parse JSON object from text: %.100s...", cleaned)
    return {}

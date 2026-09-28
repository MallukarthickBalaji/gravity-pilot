"""
browser_agent.py — Browser automation and web search orchestration node.
Orchestrates multi-provider search fallback hierarchy and URL navigation
by dispatching execution to deterministic tool handlers in tools.web_search.
"""
from __future__ import annotations

import logging
from typing import Any

from graph.state import AgentState
from tools.web_search import (
    execute_multi_provider_search,
    open_url,
    web_search,
    decode_target_url,
    extract_domain,
    sanitize_search_query,
)

logger = logging.getLogger(__name__)

# Re-export for backward compatibility
__all__ = [
    "decode_target_url",
    "extract_domain",
    "sanitize_search_query",
    "execute_multi_provider_search",
    "open_url",
    "web_search",
    "browser_agent_node",
]


async def browser_agent_node(state: AgentState) -> dict[str, Any]:
    """Execute browser navigation or search step."""
    plan = state.get("plan", [])
    current_step = state.get("current_step", 0)

    if not plan or current_step >= len(plan):
        return {
            "last_execution_result": {
                "success": False,
                "error": "No browser plan step available",
                "agent_type": "browser_agent",
            },
            "current_step": current_step + 1,
            "execution_trace": [
                {
                    "agent": "browser_agent",
                    "status": "error",
                    "message": "No plan step available.",
                }
            ],
        }

    step = plan[current_step]
    params = step.get("params", {})
    operation = params.get("operation", "")
    query = params.get("query")
    url = params.get("url")

    user_input = state.get("user_input", "")
    is_open_url = (
        operation == "open_url"
        or (url and not query)
        or ("open google" in user_input.lower())
        or ("open " in user_input.lower() and (".com" in user_input.lower() or "http" in user_input.lower()))
    )

    if is_open_url:
        target_url = url or query or user_input
        result = await open_url(target_url)
        trace_msg = f"Opened website in browser: {result.get('url', target_url)}"
        return {
            "last_execution_result": result,
            "current_step": current_step + 1,
            "execution_trace": [
                {
                    "agent": "browser_agent",
                    "status": "success",
                    "message": trace_msg,
                }
            ],
        }

    # Execute search with fallback pipeline and collect full trace
    search_query = query or url or user_input
    search_result, traces = await execute_multi_provider_search(search_query)
    execution_result = search_result.to_execution_result()

    return {
        "last_execution_result": execution_result,
        "current_step": current_step + 1,
        "execution_trace": traces,
    }

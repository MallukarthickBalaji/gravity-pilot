"""
browser_agent.py — Web search and Playwright browser automation agent.
"""
from __future__ import annotations

import logging
from typing import Any

import httpx
from graph.state import AgentState

logger = logging.getLogger(__name__)

try:
    from playwright.async_api import async_playwright
except ImportError:
    async_playwright = None


async def _perform_web_search(query: str) -> str:
    """Perform a light web search using DuckDuckGo HTML API via httpx."""
    url = "https://html.duckduckgo.com/html/"
    async with httpx.AsyncClient(timeout=10.0, follow_redirects=True) as client:
        resp = await client.post(url, data={"q": query})
        if resp.status_code == 200:
            text = resp.text
            # Basic snippet extraction
            from bs4 import BeautifulSoup
            soup = BeautifulSoup(text, "html.parser")
            snippets = []
            for a in soup.find_all("a", class_="result__snippet", limit=5):
                snippets.append(a.get_text(strip=True))
            return "\n".join(snippets) if snippets else text[:500]
        return f"Search HTTP {resp.status_code}"


async def browser_agent_node(state: AgentState) -> dict[str, Any]:
    """LangGraph node: executes web search and browser steps."""
    plan = state.get("plan") or []
    current_step_idx = state.get("current_step", 0)

    if current_step_idx >= len(plan):
        return {
            "execution_trace": [
                {
                    "agent": "browser_agent",
                    "status": "skipped",
                    "message": "No browser step to execute.",
                }
            ]
        }

    step = plan[current_step_idx]
    params = step.get("params", {})
    url = params.get("url")
    query = params.get("query")
    extract = params.get("extract", "text")

    try:
        extracted_data = ""

        # 1. Search query mode
        if query and not url:
            try:
                extracted_data = await _perform_web_search(query)
                msg = f"Searched web for '{query}'"
            except Exception as e:
                extracted_data = f"Web search fallback: {e}"
                msg = f"Attempted search for '{query}'"

        # 2. Playwright URL navigation mode (if available)
        elif url and async_playwright is not None:
            async with async_playwright() as p:
                browser = await p.chromium.launch(headless=True)
                page = await browser.new_page()
                await page.goto(url, timeout=15000)
                if extract == "text":
                    extracted_data = await page.inner_text("body")
                    extracted_data = extracted_data[:1500]
                elif extract == "title":
                    extracted_data = await page.title()
                else:
                    extracted_data = await page.content()
                    extracted_data = extracted_data[:1500]
                await browser.close()
            msg = f"Navigated to '{url}' and extracted content"

        # 3. HTTP Client fallback if Playwright is missing
        elif url:
            async with httpx.AsyncClient(timeout=10.0, follow_redirects=True) as client:
                resp = await client.get(url)
                extracted_data = resp.text[:1500]
            msg = f"Fetched URL '{url}' via HTTP fallback"
        else:
            msg = f"Browser action completed: {step.get('action')}"
            extracted_data = "No target URL or search query specified."

        res = {"success": True, "data": extracted_data, "message": msg}
        return {
            "last_execution_result": res,
            "execution_trace": [
                {
                    "agent": "browser_agent",
                    "status": "success",
                    "message": msg,
                }
            ],
        }
    except Exception as exc:
        logger.exception("Browser automation failed: %s", exc)
        res = {"success": False, "error": str(exc)}
        return {
            "last_execution_result": res,
            "error": f"Browser agent error: {exc}",
            "execution_trace": [
                {
                    "agent": "browser_agent",
                    "status": "error",
                    "message": f"Browser agent failed: {exc}",
                }
            ],
        }

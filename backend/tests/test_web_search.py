"""
test_web_search.py — Comprehensive tests for Web Search tools, fallback pipeline, and bot detection.
"""
from __future__ import annotations

import asyncio
import sys
from pathlib import Path

backend_dir = Path(__file__).resolve().parent.parent
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

from models.web_search import SearchResult, WebSearchResult, detect_bot_challenge
from tools.web_search import execute_multi_provider_search, sanitize_search_query


async def test_web_search_suite():
    print("=== Testing Web Search Tools & Bot Detection ===")

    # 1. Canonical Schema
    item = SearchResult(
        title="Example Result",
        url="https://example.com/page",
        snippet="A valid search result description.",
        source="example.com",
    )
    assert item.is_valid()
    web_res = WebSearchResult(query="test query", status="success", provider="TestProvider", results=[item])
    exec_dict = web_res.to_execution_result()
    assert exec_dict["status"] == "success"
    assert len(exec_dict["results"]) == 1
    print("  [OK] Canonical schema & serialization verified")

    # 2. CAPTCHA & Bot Challenge Detection
    sample_captcha = (
        "Unfortunately, bots use DuckDuckGo too. "
        "Please complete the following challenge to confirm this search was made by a human."
    )
    is_blocked, phrase = detect_bot_challenge(sample_captcha)
    assert is_blocked and "bots use DuckDuckGo too" in phrase
    print("  [OK] CAPTCHA / bot challenge pattern correctly detected")

    # 3. Query Sanitization
    raw_query = "search the web for latest Python version"
    clean = sanitize_search_query(raw_query)
    assert clean == "latest Python version"
    print("  [OK] Search query sanitized cleanly")

    # 4. Multi-provider search execution
    result, traces = await execute_multi_provider_search("Python programming language")
    assert result.status == "success", f"Search failed: {result.error}"
    assert len(result.results) > 0, "No results returned"
    top = result.results[0]
    assert top.title and top.url.startswith("http")
    print(f"  [OK] Search retrieved {len(result.results)} structured results from {result.provider}")
    print(f"       Top result: '{top.title[:45]}...' ({top.url})")

    print("[SUCCESS] Web search tool & pipeline verified successfully!\n")


if __name__ == "__main__":
    asyncio.run(test_web_search_suite())

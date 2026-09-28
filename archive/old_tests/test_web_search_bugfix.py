"""
test_web_search_bugfix.py — Comprehensive automated test suite verifying:
1. Structured WebSearchResult & SearchResult canonical schema
2. CAPTCHA / bot challenge detection (rejects "Select squares containing a duck", etc.)
3. Validation Agent strictly rejects CAPTCHA / blocked / raw HTML results
4. Multi-provider fallback architecture
5. Execution and verification of all 5 required queries:
   - "latest Telugu movie"
   - "latest Python version"
   - "official LangGraph documentation"
   - "search for OpenAI"
   - "search the web for Rajalakshmi Engineering College"
"""
import asyncio
import sys
from pathlib import Path

backend_dir = Path(__file__).parent
sys.stdout.reconfigure(encoding="utf-8")
sys.path.insert(0, str(backend_dir))

from models.web_search import SearchResult, WebSearchResult, detect_bot_challenge
from agents.browser_agent import execute_multi_provider_search, web_search
from agents.validation_agent import _validate_browser, validation_agent_node
from agents.supervisor import supervisor_node
from agents.requirement_analyzer import requirement_analyzer_node
from agents.planning_agent import planning_agent_node


def test_schema_and_models():
    print("=== [TEST 1] Testing Canonical Models & Schema ===")
    res1 = SearchResult(
        title="Telugu Movies 2026",
        url="https://example.com/telugu",
        snippet="List of Telugu releases for 2026.",
        source="example.com",
    )
    assert res1.is_valid(), "Valid SearchResult should pass is_valid()"

    # Invalid cases
    res_bad_url = SearchResult(title="Title", url="not_a_url", snippet="Snippet")
    assert not res_bad_url.is_valid(), "Invalid URL should fail is_valid()"

    res_empty_title = SearchResult(title="", url="https://example.com", snippet="Snippet")
    assert not res_empty_title.is_valid(), "Empty title should fail is_valid()"

    # Test WebSearchResult to_execution_result
    web_res = WebSearchResult(
        query="latest Telugu movie",
        status="success",
        provider="DuckDuckGo Lite",
        results=[res1],
    )
    exec_dict = web_res.to_execution_result()
    assert exec_dict["success"] is True
    assert exec_dict["operation"] == "web_search"
    assert exec_dict["provider"] == "DuckDuckGo Lite"
    assert len(exec_dict["results"]) == 1
    assert "1. **Telugu Movies 2026**" in exec_dict["extracted_data"]
    print("✓ Canonical schema & serialization PASSED")


def test_captcha_detection():
    print("\n=== [TEST 2] Testing CAPTCHA & Bot Challenge Detection ===")
    # Exact user error string
    user_captcha = (
        "DuckDuckGo Open menu All Images Videos News Maps Duck.ai\n"
        "Unfortunately, bots use DuckDuckGo too.\n"
        "Please complete the following challenge to confirm this search was made by a human.\n"
        "Select all squares containing a duck:\n"
        "Submit"
    )
    is_blocked, phrase = detect_bot_challenge(user_captcha)
    assert is_blocked, f"User CAPTCHA page MUST be detected as blocked! Got {is_blocked}"
    print(f"✓ Detected user CAPTCHA phrase: '{phrase}'")

    # Additional phrases
    samples = [
        "Please complete the following challenge",
        "Select all squares containing a duck",
        "Verify that you are human to proceed",
        "Access denied. Cloudflare Ray ID: 8934759",
    ]
    for sample in samples:
        blocked, p = detect_bot_challenge(sample)
        assert blocked, f"Expected '{sample}' to be detected as bot challenge!"

    # Clean text should NOT be detected
    clean = "Latest Telugu films 2026: Game Changer, Devara Part 1, Pushpa 2 release dates."
    blocked, _ = detect_bot_challenge(clean)
    assert not blocked, "Clean content must NOT be flagged as bot challenge"
    print("✓ CAPTCHA and Bot challenge detection PASSED")


async def test_validation_agent_rejection():
    print("\n=== [TEST 3] Testing Validation Agent Rejection Rules ===")
    # 1. Validation must REJECT blocked search
    blocked_result = {
        "operation": "web_search",
        "agent_type": "browser_agent",
        "query": "latest Telugu movie",
        "status": "blocked",
        "blocked": True,
        "provider": "DuckDuckGo",
        "reason": "Search provider returned a bot verification challenge",
        "results": [],
    }
    passed, reason = _validate_browser(blocked_result)
    assert not passed, f"Blocked search MUST fail validation! Got passed={passed}"
    print(f"✓ Blocked search properly rejected by validator: '{reason}'")

    # Test full validation_agent_node behavior with blocked search
    state = {
        "last_execution_result": blocked_result,
        "replan_count": 0,
        "user_input": "latest Telugu movie",
    }
    val_node_res = await validation_agent_node(state)
    assert val_node_res["validation_result"]["passed"] is False
    assert val_node_res["replan_reason"] is None, "Should NOT trigger infinite replan loop for blocked search"
    assert "blocked the request" in val_node_res["final_response"]
    print("✓ Validation node returned polite non-hallucinatory message:", val_node_res["final_response"])

    # 2. Validation must REJECT raw CAPTCHA dumped in results
    captcha_dump = {
        "operation": "web_search",
        "agent_type": "browser_agent",
        "query": "latest Telugu movie",
        "status": "success",
        "provider": "DuckDuckGo",
        "results": [
            {
                "title": "Select all squares containing a duck",
                "url": "https://duckduckgo.com",
                "snippet": "Unfortunately, bots use DuckDuckGo too. Please complete challenge.",
            }
        ],
    }
    passed2, reason2 = _validate_browser(captcha_dump)
    assert not passed2, "CAPTCHA dumped inside results MUST fail validation!"
    print(f"✓ CAPTCHA in result items rejected: '{reason2}'")

    # 3. Validation must REJECT empty results
    empty_result = {
        "operation": "web_search",
        "agent_type": "browser_agent",
        "query": "test query",
        "status": "empty",
        "results": [],
    }
    passed3, reason3 = _validate_browser(empty_result)
    assert not passed3, "Empty search results MUST fail validation!"
    print(f"✓ Empty results rejected: '{reason3}'")


async def test_required_queries():
    print("\n=== [TEST 4] Testing 5 Required Queries with Actual Extraction ===")
    test_queries = [
        "latest Telugu movie",
        "latest Python version",
        "official LangGraph documentation",
        "search for OpenAI",
        "search the web for Rajalakshmi Engineering College",
    ]

    for idx, query in enumerate(test_queries, 1):
        print(f"\n--- Testing Query {idx}: '{query}' ---")
        
        # 1. Supervisor classification
        sup_state = {"user_input": query, "model_backend": "groq", "messages": []}
        sup_res = await supervisor_node(sup_state)
        task_type = sup_res.get("task_type")
        print(f"  [Supervisor] Classified as: {task_type}")
        assert task_type == "browser_automation", f"Query '{query}' should be classified as browser_automation"

        # 2. Requirement Analyzer
        req_state = {"user_input": query, "task_type": task_type, "model_backend": "groq"}
        req_res = await requirement_analyzer_node(req_state)
        assert req_res.get("requirements_complete") is True, f"Requirements for '{query}' should be complete"
        print(f"  [Requirement Analyzer] Requirements complete: {req_res.get('requirements_complete')}")

        # 3. Multi-provider Search Execution
        search_result, traces = await execute_multi_provider_search(query)
        print(f"  [Search Execution] Provider used: {search_result.provider}")
        print(f"  [Search Execution] Status: {search_result.status}, Blocked: {search_result.blocked}")
        print(f"  [Search Execution] Results count: {len(search_result.results)}")
        print(f"  [Search Execution] Trace steps generated: {len(traces)}")

        assert search_result.status == "success", f"Search for '{query}' should succeed. Error: {search_result.error}"
        assert len(search_result.results) > 0, f"Expected non-empty results for '{query}'"
        assert not search_result.blocked, f"Search result must not be marked blocked"

        # Verify top result
        top_res = search_result.results[0]
        print(f"  [Top Result Title]: {top_res.title[:70]}")
        print(f"  [Top Result URL]: {top_res.url}")
        print(f"  [Top Result Snippet]: {top_res.snippet[:90]}...")
        assert top_res.url.startswith("http"), f"Result URL must be valid HTTP/HTTPS: {top_res.url}"
        assert len(top_res.title) > 0, "Title must not be empty"
        assert len(top_res.snippet) > 0, "Snippet must not be empty"

        # 4. Validation Agent Check
        exec_payload = search_result.to_execution_result()
        val_passed, val_msg = _validate_browser(exec_payload)
        assert val_passed, f"Validation MUST pass for valid search result! Msg: {val_msg}"
        print(f"  [Validation Agent] {val_msg}")

        # 5. Full Validation Node & Response Construction
        node_val_res = await validation_agent_node({
            "last_execution_result": exec_payload,
            "replan_count": 0,
            "user_input": query,
        })
        assert node_val_res["validation_result"]["passed"] is True
        final_resp = node_val_res["final_response"]
        assert f'Search results for "{query}":' in final_resp
        assert top_res.title in final_resp
        print(f"  [Final Response preview]:\n    " + final_resp.split("\n")[0])
        print(f"    " + final_resp.split("\n")[2][:80] + "...")

    print("\n✓ ALL 5 REQUIRED QUERIES PASSED VERIFICATION!")


async def main():
    test_schema_and_models()
    test_captcha_detection()
    await test_validation_agent_rejection()
    await test_required_queries()
    print("\n=======================================================")
    print("ALL WEB SEARCH BUGFIX TESTS PASSED SUCCESSFULLY!")
    print("=======================================================")


if __name__ == "__main__":
    asyncio.run(main())

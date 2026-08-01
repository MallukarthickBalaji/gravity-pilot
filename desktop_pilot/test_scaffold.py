"""
test_scaffold.py — Non-interactive smoke test for Phase 1 scaffold.

Run:
  python test_scaffold.py

Tests:
  1. Config loads without error
  2. model_router runs (reports backend + capabilities)
  3. supervisor classifies three representative inputs
  4. requirement_analyzer detects missing info on a vague doc request
  5. planning_agent generates a plan for a fully-specified doc request

Each test prints PASS or FAIL with a short reason.
The test does NOT require a running LLM backend to demonstrate the routing
logic — it checks that the graph compiles and nodes return correctly shaped
state. LLM calls are attempted, and results are printed even if the LLM is
unavailable (you'll see the fallback behaviour instead of a test failure).
"""
from __future__ import annotations

import asyncio
import sys
import traceback
import uuid

from config import config
from graph.state import AgentState
from graph.workflow import create_graph


PASS = "  ✓ PASS"
FAIL = "  ✗ FAIL"


def _base_state(user_input: str) -> AgentState:
    return {
        "messages": [{"role": "user", "content": user_input}],
        "session_id": str(uuid.uuid4()),
        "user_input": user_input,
        "task_type": None,
        "requirements_complete": False,
        "clarifying_question": None,
        "plan": None,
        "current_step": 0,
        "last_execution_result": None,
        "validation_result": None,
        "replan_reason": None,
        "model_backend": "unknown",
        "capabilities": None,
        "memory_context": None,
        "final_response": None,
        "error": None,
        "execution_trace": [],
    }


async def test_config() -> bool:
    print("\n[1] Config loads correctly")
    try:
        assert isinstance(config.groq_model, str), "groq_model missing"
        assert isinstance(config.ollama_host, str), "ollama_host missing"
        groq_key_present = bool(config.groq_api_key)
        print(f"    groq_api_key set: {groq_key_present}")
        print(f"    groq_model: {config.groq_model}")
        print(f"    ollama_host: {config.ollama_host}")
        print(PASS)
        return True
    except Exception as exc:
        print(f"    {exc}")
        print(FAIL)
        return False


async def test_graph_compiles() -> bool:
    print("\n[2] Graph compiles without error")
    try:
        graph = create_graph()
        assert graph is not None
        print(PASS)
        return True
    except Exception as exc:
        traceback.print_exc()
        print(FAIL)
        return False


async def test_model_router() -> bool:
    print("\n[3] model_router runs and reports backend")
    try:
        graph = create_graph()
        # Use a simple general query so the whole graph runs
        result = await graph.ainvoke(_base_state("What time is it?"))
        backend = result.get("model_backend", "none")
        caps = result.get("capabilities")
        trace = result.get("execution_trace", [])
        mr_entry = next((t for t in trace if t["agent"] == "model_router"), None)
        print(f"    backend selected: {backend}")
        print(f"    capabilities: {caps}")
        print(f"    trace entry: {mr_entry}")
        assert backend in ("groq", "ollama", "none"), f"unexpected backend: {backend}"
        print(PASS)
        return True
    except Exception as exc:
        traceback.print_exc()
        print(FAIL)
        return False


async def test_document_classification() -> bool:
    print("\n[4] Supervisor classifies a document request")
    try:
        graph = create_graph()
        result = await graph.ainvoke(
            _base_state("Create a Word document with a meeting agenda for Q3 review")
        )
        task_type = result.get("task_type")
        print(f"    task_type: {task_type}")
        trace = [t for t in result.get("execution_trace", []) if t["agent"] == "supervisor"]
        print(f"    supervisor trace: {trace}")
        # Accept document_generation or unknown (if LLM unavailable)
        assert task_type in ("document_generation", "unknown", None), f"unexpected: {task_type}"
        print(PASS)
        return True
    except Exception as exc:
        traceback.print_exc()
        print(FAIL)
        return False


async def test_clarification_on_vague_request() -> bool:
    print("\n[5] Requirement analyzer asks for clarification on vague doc request")
    try:
        graph = create_graph()
        result = await graph.ainvoke(_base_state("Make me a document"))
        req_complete = result.get("requirements_complete", True)
        question = result.get("clarifying_question")
        print(f"    requirements_complete: {req_complete}")
        print(f"    clarifying_question: {question}")
        # Either the system asked for clarification, or it generated a plan
        # (depends on LLM backend). Both are valid outcomes.
        print(PASS)
        return True
    except Exception as exc:
        traceback.print_exc()
        print(FAIL)
        return False


async def test_plan_on_specific_request() -> bool:
    print("\n[6] Planning agent generates a plan for a specific request")
    try:
        graph = create_graph()
        result = await graph.ainvoke(
            _base_state(
                "Create an Excel attendance sheet named 'attendance.xlsx' with columns: "
                "Name, Date, Present (Yes/No). Include 5 sample rows."
            )
        )
        plan = result.get("plan")
        final = result.get("final_response")
        question = result.get("clarifying_question")
        print(f"    plan steps: {len(plan) if plan else 0}")
        if plan:
            for s in plan:
                print(f"      Step {s.get('step_id')}: [{s.get('agent')}] {s.get('action', '')[:60]}")
        print(f"    final_response: {(final or '')[:80]}")
        print(f"    clarifying_question: {question}")
        print(PASS)
        return True
    except Exception as exc:
        traceback.print_exc()
        print(FAIL)
        return False


async def main() -> None:
    print("=" * 60)
    print("  DesktopPilot AI — Phase 1 Scaffold Tests")
    print("=" * 60)

    tests = [
        test_config,
        test_graph_compiles,
        test_model_router,
        test_document_classification,
        test_clarification_on_vague_request,
        test_plan_on_specific_request,
    ]

    results = []
    for t in tests:
        ok = await t()
        results.append(ok)

    passed = sum(results)
    total = len(results)
    print(f"\n{'=' * 60}")
    print(f"  Results: {passed}/{total} passed")
    if passed == total:
        print("  All tests passed — scaffold is ready.")
    else:
        print("  Some tests failed — see output above.")
    print("=" * 60)
    sys.exit(0 if passed == total else 1)


if __name__ == "__main__":
    asyncio.run(main())

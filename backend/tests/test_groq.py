"""
test_groq.py — Verifies Groq cloud LLM connectivity and agent execution.
"""
from __future__ import annotations

import asyncio
import os
import sys
import uuid
from pathlib import Path

backend_dir = Path(__file__).resolve().parent.parent
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

from agents.model_router import _check_groq, model_router_node
from graph.state import AgentState
from graph.workflow import create_graph


async def test_groq_suite():
    print("=== Testing Groq Cloud LLM Backend ===")

    # 1. Connectivity Check
    is_groq_ok = await _check_groq()
    if not is_groq_ok:
        print("  [SKIP] GROQ_API_KEY is not set or network unavailable. Skipping live turn.")
        return

    print("  [OK] Groq API connectivity verified")

    # 2. Model Router Verification
    state_groq: AgentState = {"model_backend": "groq"}
    res_router = await model_router_node(state_groq)
    assert res_router["model_backend"] == "groq"
    assert res_router["capabilities"].document_generation is True
    print("  [OK] Model router correctly routed to Groq")

    # 3. Simple Agent Query
    graph = create_graph()
    test_state: AgentState = {
        "messages": [{"role": "user", "content": "Reply with exactly: GROQ_TEST_OK"}],
        "session_id": str(uuid.uuid4()),
        "task_id": f"task_{uuid.uuid4().hex[:8]}",
        "task_status": "analyzing",
        "user_input": "Reply with exactly: GROQ_TEST_OK",
        "task_type": "general",
        "requirements_complete": True,
        "clarifying_question": None,
        "plan": None,
        "current_step": 0,
        "last_execution_result": None,
        "validation_result": None,
        "generated_outputs": [],
        "replan_reason": None,
        "replan_count": 0,
        "model_backend": "groq",
        "capabilities": None,
        "memory_context": None,
        "final_response": None,
        "error": None,
        "execution_trace": [],
    }

    result = await graph.ainvoke(test_state)
    resp = (result.get("final_response") or "").strip()
    assert "GROQ_TEST_OK" in resp or "groq_test_ok" in resp.lower(), f"Unexpected: {resp}"
    print(f"  [OK] Groq agent response received: '{resp}'")

    print("[SUCCESS] Groq Cloud LLM verified successfully!\n")


if __name__ == "__main__":
    asyncio.run(test_groq_suite())

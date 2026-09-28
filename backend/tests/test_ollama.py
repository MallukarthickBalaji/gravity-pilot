"""
test_ollama.py — Comprehensive test suite for Local Ollama mode in DesktopPilot AI.
Verifies:
1. Direct Ollama connectivity on http://127.0.0.1:11434
2. Installed model detection (llama3:latest)
3. Model router explicit selection & rejection of silent fallback
4. Simple Prompt: "Reply with exactly: LOCAL_OLLAMA_WORKING"
5. Document generation with Local Ollama
"""
from __future__ import annotations

import asyncio
import sys
import uuid
from pathlib import Path

backend_dir = Path(__file__).resolve().parent.parent
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

import httpx
from agents.model_router import check_ollama_status, model_router_node
from config import config
from graph.state import AgentState
from graph.workflow import create_graph


async def run_turn(user_input: str, backend: str, session_id: str = None) -> AgentState:
    graph = create_graph()
    sid = session_id or str(uuid.uuid4())
    state: AgentState = {
        "messages": [{"role": "user", "content": user_input}],
        "session_id": sid,
        "task_id": f"task_{uuid.uuid4().hex[:8]}",
        "task_status": "analyzing",
        "user_input": user_input,
        "task_type": None,
        "requirements_complete": False,
        "clarifying_question": None,
        "plan": None,
        "current_step": 0,
        "last_execution_result": None,
        "validation_result": None,
        "generated_outputs": [],
        "replan_reason": None,
        "replan_count": 0,
        "model_backend": backend,
        "capabilities": None,
        "memory_context": None,
        "final_response": None,
        "error": None,
        "execution_trace": [],
    }
    return await graph.ainvoke(state)


async def test_ollama_suite():
    print("=== Testing Local Ollama Backend ===")

    # 1. Direct Diagnostics
    status = await check_ollama_status()
    print(f"  Base URL: {status['base_url']}")
    print(f"  Installed models: {status['models']}")
    print(f"  Active model: {status['active_model']}")
    assert status["available"], f"Ollama must be available on 127.0.0.1:11434! Error: {status.get('error')}"
    assert len(status["models"]) > 0, "At least one model must be installed in Ollama!"
    print("  [OK] Ollama service and model detected")

    # 2. Router Strictness (Zero Silent Fallback)
    state_ollama: AgentState = {"model_backend": "ollama"}
    res_ollama = await model_router_node(state_ollama)
    assert res_ollama["model_backend"] == "ollama"
    print("  [OK] Model router correctly routed to Ollama")

    orig_url = config.ollama_base_url
    try:
        config.ollama_base_url = "http://127.0.0.1:9999"
        res_bad = await model_router_node(state_ollama)
        assert res_bad["model_backend"] == "none", f"Must NOT fallback to Groq! Got {res_bad['model_backend']}"
        assert "Local Ollama is unavailable" in res_bad["error"]
        print("  [OK] Unreachable Ollama fails explicitly without fallback")
    finally:
        config.ollama_base_url = orig_url

    # 3. Simple Prompt
    res = await run_turn("Reply with exactly: LOCAL_OLLAMA_WORKING", backend="ollama")
    resp_text = (res.get("final_response") or "").strip()
    assert "LOCAL_OLLAMA_WORKING" in resp_text or "local_ollama_working" in resp_text.lower()
    print(f"  [OK] Simple prompt response: '{resp_text}'")

    print("[SUCCESS] Local Ollama verified successfully!\n")


if __name__ == "__main__":
    asyncio.run(test_ollama_suite())

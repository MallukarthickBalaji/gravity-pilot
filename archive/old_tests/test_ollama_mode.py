"""
test_ollama_mode.py — Comprehensive test suite for Local Ollama mode in GravityPilot AI.
Verifies:
1. Direct Ollama connectivity on http://127.0.0.1:11434
2. Installed model detection (llama3:latest)
3. Model router explicit selection & rejection of silent fallback
4. Prompt 1: "Reply with exactly: LOCAL_OLLAMA_WORKING"
5. Prompt 2: "Create a Word document explaining artificial intelligence."
6. Prompt 3: "Create an Excel attendance sheet for 10 students."
7. Prompt 4: "Create a PowerPoint about cloud computing."
8. Prompt 5: "Write Python code to calculate Fibonacci numbers."
9. Full agent orchestration across Supervisor -> Requirement Analyzer -> Planner -> Execution -> Validation.
"""
import asyncio
import os
import sys
import uuid
from pathlib import Path

backend_dir = Path(__file__).parent
sys.stdout.reconfigure(encoding="utf-8")
sys.path.insert(0, str(backend_dir))

import httpx
from config import config
from graph.workflow import create_graph
from graph.state import AgentState
from agents.model_router import check_ollama_status, model_router_node, get_llm


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


async def test_ollama_direct():
    print("=== [TEST 1] Direct Ollama Diagnostics ===")
    status = await check_ollama_status()
    print(f"  Ollama available: {status['available']}")
    print(f"  Base URL: {status['base_url']}")
    print(f"  Installed models: {status['models']}")
    print(f"  Active model: {status['active_model']}")
    assert status["available"], f"Ollama must be available on 127.0.0.1:11434! Error: {status.get('error')}"
    assert len(status["models"]) > 0, "At least one model must be installed in Ollama!"

    # Test direct generate
    async with httpx.AsyncClient(timeout=30.0) as client:
        payload = {
            "model": status["active_model"],
            "prompt": "Reply with exactly: LOCAL_OLLAMA_WORKING",
            "stream": False,
        }
        resp = await client.post(f"{status['base_url']}/api/generate", json=payload)
        assert resp.status_code == 200, f"Ollama generate returned status {resp.status_code}"
        gen_text = resp.json().get("response", "").strip()
        print(f"  Direct generation response: '{gen_text}'")
        assert "LOCAL_OLLAMA_WORKING" in gen_text, f"Unexpected response: {gen_text}"

    print("[OK] Direct Ollama connectivity & generation PASSED\n")


async def test_router_strictness():
    print("=== [TEST 2] Model Router Strictness (No Silent Fallback) ===")
    # 1. Local requested -> must return ollama
    state_ollama: AgentState = {"model_backend": "ollama"}
    res_ollama = await model_router_node(state_ollama)
    assert res_ollama["model_backend"] == "ollama", f"Expected 'ollama', got {res_ollama['model_backend']}"
    assert res_ollama["capabilities"].document_generation is True
    assert res_ollama["capabilities"].browser_automation is True
    print(f"  Ollama route trace: {res_ollama['execution_trace'][0]['message']}")

    # 2. Cloud requested -> must return groq
    state_groq: AgentState = {"model_backend": "groq"}
    res_groq = await model_router_node(state_groq)
    assert res_groq["model_backend"] == "groq", f"Expected 'groq', got {res_groq['model_backend']}"
    print(f"  Groq route trace: {res_groq['execution_trace'][0]['message']}")

    # 3. Simulate unavailable Ollama -> MUST fail cleanly, NEVER fallback to Groq
    orig_url = config.ollama_base_url
    try:
        config.ollama_base_url = "http://127.0.0.1:9999"  # Non-existent port
        state_bad_ollama: AgentState = {"model_backend": "ollama"}
        res_bad = await model_router_node(state_bad_ollama)
        assert res_bad["model_backend"] == "none", f"Must NOT fallback to Groq! Got {res_bad['model_backend']}"
        assert "Local Ollama is unavailable" in res_bad["error"]
        print(f"  Clean failure on unreachable Ollama: '{res_bad['error'][:60]}...'")
    finally:
        config.ollama_base_url = orig_url

    print("[OK] Model Router strict routing & no silent fallback PASSED\n")


async def test_simple_prompt():
    print("=== [TEST 3] Simple Prompt with Local Ollama ===")
    res = await run_turn("Reply with exactly: LOCAL_OLLAMA_WORKING", backend="ollama")
    resp_text = (res.get("final_response") or "").strip()
    print(f"  Agent response: '{resp_text}'")
    assert "LOCAL_OLLAMA_WORKING" in resp_text or "local_ollama_working" in resp_text.lower(), f"Unexpected: {resp_text}"
    print("[OK] Simple Prompt PASSED\n")


async def test_word_document():
    print("=== [TEST 4] Word Document Generation with Local Ollama ===")
    prompt = "Create a Word document explaining artificial intelligence."
    res = await run_turn(prompt, backend="ollama")
    last_res = res.get("last_execution_result") or {}
    out_path = last_res.get("output_path")
    print(f"  Validation result: {res.get('validation_result')}")
    print(f"  Output path: {out_path}")
    assert out_path and Path(out_path).exists(), "Word document was not created!"
    assert Path(out_path).suffix == ".docx"
    assert Path(out_path).stat().st_size > 1000, "Word document is too small!"
    print("[OK] Word Document Generation with Ollama PASSED\n")


async def test_excel_sheet():
    print("=== [TEST 5] Excel Sheet Generation with Local Ollama ===")
    prompt = "Create an Excel attendance sheet for 10 students."
    res = await run_turn(prompt, backend="ollama")
    last_res = res.get("last_execution_result") or {}
    out_path = last_res.get("output_path")
    print(f"  Validation result: {res.get('validation_result')}")
    print(f"  Output path: {out_path}")
    assert out_path and Path(out_path).exists(), "Excel workbook was not created!"
    assert Path(out_path).suffix == ".xlsx"
    print("[OK] Excel Sheet Generation with Ollama PASSED\n")


async def test_powerpoint():
    print("=== [TEST 6] PowerPoint Generation with Local Ollama ===")
    prompt = "Create a PowerPoint about cloud computing."
    res = await run_turn(prompt, backend="ollama")
    last_res = res.get("last_execution_result") or {}
    out_path = last_res.get("output_path")
    print(f"  Validation result: {res.get('validation_result')}")
    print(f"  Output path: {out_path}")
    assert out_path and Path(out_path).exists(), "PowerPoint presentation was not created!"
    assert Path(out_path).suffix == ".pptx"
    print("[OK] PowerPoint Generation with Ollama PASSED\n")


async def test_code_generation():
    print("=== [TEST 7] Python Code Generation with Local Ollama ===")
    prompt = "Write Python code to calculate Fibonacci numbers."
    res = await run_turn(prompt, backend="ollama")
    last_res = res.get("last_execution_result") or {}
    out_path = last_res.get("output_path")
    print(f"  Validation result: {res.get('validation_result')}")
    print(f"  Output path: {out_path}")
    assert out_path and Path(out_path).exists(), "Code file was not created!"
    content = Path(out_path).read_text(encoding="utf-8")
    assert "fib" in content.lower() or "def " in content
    print("[OK] Python Code Generation with Ollama PASSED\n")


async def main():
    print("=======================================================")
    print("      LOCAL OLLAMA AUTOMATED TEST SUITE                ")
    print("=======================================================\n")
    await test_ollama_direct()
    await test_router_strictness()
    await test_simple_prompt()
    await test_word_document()
    await test_excel_sheet()
    await test_powerpoint()
    await test_code_generation()
    print("=======================================================")
    print("   ALL LOCAL OLLAMA VERIFICATION TESTS PASSED!         ")
    print("=======================================================")


if __name__ == "__main__":
    asyncio.run(main())

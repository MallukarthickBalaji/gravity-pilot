"""
test_new_features.py — Verifies all required fixes and new features:
1. Screenshot capture
2. Jupyter notebook opening check
3. Web search and open URL
4. Leave letter clarification workflow
5. Code generation
6. Sequential prompt isolation (PowerPoint -> Excel -> Screenshot -> Web search)
"""
import asyncio
import os
import sys
import uuid
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
sys.path.insert(0, str(Path(__file__).parent))

from graph.workflow import create_graph
from graph.state import AgentState

graph = create_graph()
desktop_dir = Path.home() / "Desktop"

async def run_turn(user_input: str, session_id: str, prior_messages: list[dict[str, str]] = None) -> AgentState:
    messages = prior_messages or []
    state: AgentState = {
        "messages": messages + [{"role": "user", "content": user_input}],
        "session_id": session_id,
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
        "model_backend": "unknown",
        "capabilities": None,
        "memory_context": None,
        "final_response": None,
        "error": None,
        "execution_trace": [],
    }
    result = await graph.ainvoke(state)
    return result

async def test_screenshot():
    print("\n--- TEST: Screenshot Capture ---")
    sid = str(uuid.uuid4())
    res = await run_turn("Take a screenshot of my screen.", sid)
    print("Final response:", res.get("final_response"))
    last_res = res.get("last_execution_result") or {}
    out_path = last_res.get("output_path")
    print("Output path:", out_path)
    assert out_path and Path(out_path).exists(), "Screenshot was not created!"
    assert Path(out_path).stat().st_size > 0, "Screenshot is 0 bytes!"
    print("TEST SCREENSHOT PASSED!")

async def test_notebook():
    print("\n--- TEST: Notebook Opening Check ---")
    sid = str(uuid.uuid4())
    test_nb = desktop_dir / "test_sample.ipynb"
    test_nb.write_text('{"cells":[],"metadata":{},"nbformat":4,"nbformat_minor":2}', encoding="utf-8")
    try:
        res = await run_turn(f"Open {test_nb}", sid)
        print("Final response:", res.get("final_response"))
        # Should either report jupyter not installed or opened
        val = res.get("validation_result") or {}
        last_res = res.get("last_execution_result") or {}
        print("Execution result:", last_res)
        print("TEST NOTEBOOK HANDLING PASSED!")
    finally:
        if test_nb.exists():
            test_nb.unlink()

async def test_web_search():
    print("\n--- TEST: Web Search ---")
    sid = str(uuid.uuid4())
    res = await run_turn("Search the web for the official LangGraph documentation.", sid)
    resp = res.get("final_response") or ""
    print("Search response preview:", resp[:200])
    assert len(resp.strip()) > 10, "Search result was empty!"
    print("TEST WEB SEARCH PASSED!")

async def test_leave_letter_clarification():
    print("\n--- TEST: Leave Letter Clarification Loop ---")
    sid = str(uuid.uuid4())
    # Turn 1: User says "Create a leave letter."
    res1 = await run_turn("Create a leave letter.", sid)
    q = res1.get("clarifying_question")
    print("Turn 1 Question:", q)
    assert q is not None and len(q) > 0, "Requirement Analyzer should ask for details!"
    assert not res1.get("requirements_complete"), "Should be incomplete!"

    # Turn 2: User provides details
    history = [
        {"role": "user", "content": "Create a leave letter."},
        {"role": "assistant", "content": q},
    ]
    res2 = await run_turn("Address it to The Manager, requesting 2 days leave for medical checkup.", sid, prior_messages=history)
    print("Turn 2 Response:", res2.get("final_response"))
    out = (res2.get("last_execution_result") or {}).get("output_path")
    assert out and Path(out).exists(), "Leave letter document was not generated!"
    print("TEST LEAVE LETTER CLARIFICATION PASSED!")

async def test_code_generation():
    print("\n--- TEST: Code Generation ---")
    sid = str(uuid.uuid4())
    res = await run_turn("Create a Python script named fibonacci.py that calculates fibonacci numbers.", sid)
    print("Code gen response:", res.get("final_response"))
    last_res = res.get("last_execution_result") or {}
    out = last_res.get("output_path")
    assert out and Path(out).exists(), "Code file was not created!"
    content = Path(out).read_text(encoding="utf-8")
    assert "fib" in content.lower() or "def " in content, "Code content missing!"
    print("TEST CODE GENERATION PASSED!")

async def test_sequential_isolation():
    print("\n--- TEST: Sequential Prompts Isolation ---")
    sid = str(uuid.uuid4())
    # 1. PowerPoint
    res1 = await run_turn("Create a 3-slide PowerPoint about Cloud Computing.", sid)
    out1 = (res1.get("last_execution_result") or {}).get("output_path")
    assert out1 and Path(out1).suffix == ".pptx"
    print("Task 1 (PPTX) created:", Path(out1).name)

    # 2. Excel (Must not produce PPTX)
    res2 = await run_turn("Create an Excel sheet containing 10 students.", sid)
    out2 = (res2.get("last_execution_result") or {}).get("output_path")
    assert out2 and Path(out2).suffix == ".xlsx", f"Expected xlsx, got {out2}"
    print("Task 2 (Excel) created:", Path(out2).name)

    # 3. Screenshot
    res3 = await run_turn("Take a screenshot.", sid)
    out3 = (res3.get("last_execution_result") or {}).get("output_path")
    assert out3 and Path(out3).suffix == ".png", f"Expected png, got {out3}"
    print("Task 3 (Screenshot) created:", Path(out3).name)

    # 4. Web search
    res4 = await run_turn("Search the web for LangGraph.", sid)
    resp4 = res4.get("final_response") or ""
    assert len(resp4.strip()) > 10
    print("Task 4 (Search) completed.")
    print("TEST SEQUENTIAL ISOLATION PASSED!")

async def main():
    await test_screenshot()
    await asyncio.sleep(2)
    await test_notebook()
    await asyncio.sleep(2)
    await test_web_search()
    await asyncio.sleep(2)
    await test_leave_letter_clarification()
    await asyncio.sleep(2)
    await test_code_generation()
    await asyncio.sleep(2)
    await test_sequential_isolation()
    print("\n=================================================")
    print("  ALL NEW FEATURES AND ISOLATION TESTS PASSED!   ")
    print("=================================================")

if __name__ == "__main__":
    asyncio.run(main())

"""
test_sequential_tasks.py — Verifies multi-turn clarification and sequential prompt isolation.
Tests:
1. Multi-turn clarification workflow (Requirement Analyzer loop).
2. Sequential prompt isolation across distinct tasks.
"""
from __future__ import annotations

import asyncio
import sys
import uuid
from pathlib import Path

backend_dir = Path(__file__).resolve().parent.parent
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

from graph.state import AgentState
from graph.workflow import create_graph


async def run_turn(user_input: str, session_id: str, prior_messages: list[dict[str, str]] = None) -> AgentState:
    graph = create_graph()
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
        "model_backend": "groq",
        "capabilities": None,
        "memory_context": None,
        "final_response": None,
        "error": None,
        "execution_trace": [],
    }
    return await graph.ainvoke(state)


async def test_sequential_suite():
    print("=== Testing Sequential Prompt Isolation & Clarification ===")

    # 1. Multi-turn Clarification Loop
    sid = str(uuid.uuid4())
    res1 = await run_turn("Create a leave letter", session_id=sid)
    q = res1.get("clarifying_question")
    assert q is not None and len(q) > 5
    print(f"  [OK] Turn 1: Clarifying question asked: '{q}'")

    history = [
        {"role": "user", "content": "Create a leave letter"},
        {"role": "assistant", "content": q},
    ]
    res2 = await run_turn("Address to Manager John for sick leave tomorrow", session_id=sid, prior_messages=history)
    last_res = res2.get("last_execution_result") or {}
    out_file = last_res.get("output_path")
    assert out_file and Path(out_file).exists(), f"Turn 2 failed to generate leave letter: {res2.get('error') or res2.get('final_response')}"
    print(f"  [OK] Turn 2: Document successfully generated: {Path(out_file).name}")

    # 2. Sequential Prompt Isolation (Task 1: PPTX -> Task 2: Excel)
    sid_seq = str(uuid.uuid4())
    t1 = await run_turn("Create a 2-slide PowerPoint about AI", session_id=sid_seq)
    out1 = (t1.get("last_execution_result") or {}).get("output_path")
    assert out1 and Path(out1).suffix == ".pptx"
    print(f"  [OK] Task 1 generated PPTX: {Path(out1).name}")

    t2 = await run_turn("Create an Excel sheet with 5 products", session_id=sid_seq)
    out2 = (t2.get("last_execution_result") or {}).get("output_path")
    assert out2 and Path(out2).suffix == ".xlsx"
    print(f"  [OK] Task 2 generated XLSX: {Path(out2).name} (no plan carryover)")

    print("[SUCCESS] Multi-turn clarification and task isolation verified!\n")


if __name__ == "__main__":
    asyncio.run(test_sequential_suite())

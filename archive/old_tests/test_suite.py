"""
test_suite.py — Automated end-to-end verification of all GravityPilot requirements.
Tests:
  1. Word document generation
  2. Excel sheet generation
  3. PowerPoint presentation generation
  4. Desktop copy operation
  5. Desktop move operation
  6. Desktop rename operation
  7. Desktop delete operation
  8. Browser web search and extraction
  9. Multi-turn clarification workflow (Create PowerPoint -> Topic clarification -> Presentation created)
  10. Validation failure and re-planning cycle
"""
from __future__ import annotations

import asyncio
import os
import shutil
import sys
import uuid
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent))

from graph.state import AgentState
from graph.workflow import create_graph
from memory.database import ensure_session, get_all_messages, save_message

import builtins

_real_print = builtins.print
def print(*args, **kwargs):
    kwargs.setdefault("flush", True)
    _real_print(*args, **kwargs)

graph = create_graph()
desktop_dir = Path.home() / "Desktop"


async def run_turn(user_input: str, session_id: str, prior_messages: list[dict[str, str]] = None) -> AgentState:
    messages = prior_messages or []
    state: AgentState = {
        "messages": messages + [{"role": "user", "content": user_input}],
        "session_id": session_id,
        "user_input": user_input,
        "task_type": None,
        "requirements_complete": False,
        "clarifying_question": None,
        "plan": None,
        "current_step": 0,
        "last_execution_result": None,
        "validation_result": None,
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


async def test_1_word_generation():
    print("\n--- TEST 1: Word Document Generation ---")
    session_id = str(uuid.uuid4())
    res = await run_turn("Create a Word document about Agentic AI.", session_id)
    out_path = (res.get("last_execution_result") or {}).get("output_path")
    print(f"Result: {res.get('final_response')}")
    print(f"Output path: {out_path}")
    assert out_path and Path(out_path).exists(), "Word document was not created!"
    assert Path(out_path).stat().st_size > 0, "Word document is empty!"
    print("TEST 1 PASSED: Word document created and verified.")


async def test_2_excel_generation():
    print("\n--- TEST 2: Excel Attendance Sheet Generation ---")
    session_id = str(uuid.uuid4())
    res = await run_turn(
        "Create an Excel attendance sheet with Name, Register Number, Day 1, Day 2 and Day 3.",
        session_id,
    )
    out_path = (res.get("last_execution_result") or {}).get("output_path")
    print(f"Result: {res.get('final_response')}")
    print(f"Output path: {out_path}")
    assert out_path and Path(out_path).exists(), "Excel sheet was not created!"
    assert Path(out_path).stat().st_size > 0, "Excel sheet is empty!"
    print("TEST 2 PASSED: Excel attendance sheet created and verified.")


async def test_3_powerpoint_generation():
    print("\n--- TEST 3: PowerPoint Generation ---")
    session_id = str(uuid.uuid4())
    res = await run_turn("Create a 5-slide PowerPoint about Agentic AI.", session_id)
    out_path = (res.get("last_execution_result") or {}).get("output_path")
    print(f"Result: {res.get('final_response')}")
    print(f"Output path: {out_path}")
    assert out_path and Path(out_path).exists(), "PowerPoint was not created!"
    assert Path(out_path).stat().st_size > 0, "PowerPoint is empty!"
    print("TEST 3 PASSED: PowerPoint presentation created and verified.")


async def test_4_5_6_7_desktop_operations():
    print("\n--- TESTS 4-7: Desktop File Operations (Copy, Move, Rename, Delete) ---")
    test_file = desktop_dir / "test.txt"
    backup_folder = desktop_dir / "Backup"
    copied_file = backup_folder / "test.txt"
    renamed_file = backup_folder / "final_test.txt"

    # Setup clean state
    if test_file.exists():
        test_file.unlink()
    if backup_folder.exists():
        shutil.rmtree(backup_folder)

    test_file.write_text("GravityPilot Test File Content", encoding="utf-8")
    assert test_file.exists(), "Setup failed: test.txt could not be created."
    print("Setup: Created test.txt on Desktop.")

    # 4. Copy test.txt to Backup folder
    print("\n[Sub-test 4: Copy]")
    s4 = str(uuid.uuid4())
    res_copy = await run_turn("Copy test.txt from my Desktop to the Backup folder.", s4)
    print(f"Copy Response: {res_copy.get('final_response')}")
    assert test_file.exists(), "Source test.txt must still exist after copy!"
    assert copied_file.exists(), f"Destination {copied_file} must exist after copy!"
    print("TEST 4 PASSED: Copy validated (source and destination both exist).")

    # 5. Move test.txt from Desktop to Backup folder
    print("\n[Sub-test 5: Move]")
    # First remove the copied file in backup so move can test cleanly
    copied_file.unlink()
    s5 = str(uuid.uuid4())
    res_move = await run_turn("Move test.txt from the Desktop to the Backup folder.", s5)
    print(f"Move Response: {res_move.get('final_response')}")
    assert not test_file.exists(), "Source test.txt must NOT exist after move!"
    assert copied_file.exists(), f"Destination {copied_file} must exist after move!"
    print("TEST 5 PASSED: Move validated (source removed, destination exists).")

    # 6. Rename test.txt to final_test.txt
    print("\n[Sub-test 6: Rename]")
    s6 = str(uuid.uuid4())
    res_rename = await run_turn(f"Rename {copied_file} to final_test.txt.", s6)
    print(f"Rename Response: {res_rename.get('final_response')}")
    assert not copied_file.exists(), "Old file test.txt must NOT exist after rename!"
    assert renamed_file.exists(), f"New file {renamed_file} must exist after rename!"
    print("TEST 6 PASSED: Rename validated (old removed, new exists).")

    # 7. Delete final_test.txt
    print("\n[Sub-test 7: Delete]")
    s7 = str(uuid.uuid4())
    res_delete = await run_turn(f"Delete {renamed_file}.", s7)
    print(f"Delete Response: {res_delete.get('final_response')}")
    assert not renamed_file.exists(), f"Target {renamed_file} must NOT exist after delete!"
    print("TEST 7 PASSED: Delete validated (target no longer exists).")

    # Cleanup backup folder
    if backup_folder.exists():
        shutil.rmtree(backup_folder)


async def test_8_browser_search():
    print("\n--- TEST 8: Browser Web Search & Summarization ---")
    session_id = str(uuid.uuid4())
    res = await run_turn("Search the web for Agentic AI and summarize the results.", session_id)
    ans = res.get("final_response") or ""
    print(f"Search Response Preview: {ans[:200]}...")
    assert len(ans.strip()) > 20, "Web search did not return meaningful text!"
    print("TEST 8 PASSED: Browser search and extraction verified.")


async def test_9_clarification_multiturn():
    print("\n--- TEST 9: Clarification Workflow & Multi-turn Conversation ---")
    session_id = str(uuid.uuid4())

    # Turn 1: Incomplete request "Create a PowerPoint."
    print("Turn 1: User says 'Create a PowerPoint.'")
    res1 = await run_turn("Create a PowerPoint.", session_id)
    q = res1.get("clarifying_question")
    print(f"Requirement Analyzer Question: {q}")
    assert q is not None and len(q) > 0, "Requirement analyzer should have asked for topic!"
    assert not res1.get("requirements_complete"), "Requirements must not be marked complete without a topic!"

    # Turn 2: User provides topic: "Agentic AI in healthcare."
    print("\nTurn 2: User answers 'Agentic AI in healthcare.'")
    history = [
        {"role": "user", "content": "Create a PowerPoint."},
        {"role": "assistant", "content": q},
    ]
    res2 = await run_turn("Agentic AI in healthcare.", session_id, prior_messages=history)
    print(f"Turn 2 Response: {res2.get('final_response')}")
    out_path = (res2.get("last_execution_result") or {}).get("output_path")
    assert out_path and Path(out_path).exists(), "PowerPoint should have been created on turn 2!"
    assert Path(out_path).suffix == ".pptx", "Created document must be a .pptx presentation!"
    print("TEST 9 PASSED: Multi-turn clarification continued the original task and generated the presentation.")


async def test_10_replanning_cycle():
    print("\n--- TEST 10: Validation Failure and Re-planning Cycle ---")
    session_id = str(uuid.uuid4())
    # Request copying a file to a non-existent subfolder.
    # The planner generates a plan, validation tests outcome, and if failure occurs, replanning corrects it.
    test_f = desktop_dir / "replan_test.txt"
    test_f.write_text("Replanning test", encoding="utf-8")
    dest_dir = desktop_dir / "NewSubDir" / "NestedFolder"

    try:
        res = await run_turn(f"Copy {test_f} to {dest_dir}", session_id)
        print(f"Replan Turn Response: {res.get('final_response')}")
        dest_f = dest_dir / test_f.name
        assert dest_f.exists(), f"Replanned execution should ensure destination file exists at {dest_f}!"
        print("TEST 10 PASSED: Complex operation completed and validated.")
    finally:
        if test_f.exists():
            test_f.unlink()
        if (desktop_dir / "NewSubDir").exists():
            shutil.rmtree(desktop_dir / "NewSubDir")


async def main():
    print("================================================================")
    print("      GRAVITYPILOT FULL AUTOMATED VERIFICATION SUITE           ")
    print("================================================================")

    await test_1_word_generation()
    await asyncio.sleep(2.5)
    await test_2_excel_generation()
    await asyncio.sleep(2.5)
    await test_3_powerpoint_generation()
    await asyncio.sleep(2.5)
    await test_4_5_6_7_desktop_operations()
    await asyncio.sleep(2.5)
    await test_8_browser_search()
    await asyncio.sleep(2.5)
    await test_9_clarification_multiturn()
    await asyncio.sleep(2.5)
    await test_10_replanning_cycle()

    print("\n================================================================")
    print("      ALL TESTS PASSED SUCCESSFULLY!                           ")
    print("================================================================")


if __name__ == "__main__":
    asyncio.run(main())

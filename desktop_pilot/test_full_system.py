"""
test_full_system.py — Comprehensive integration test suite for DesktopPilot AI.

Run:
  python test_full_system.py
"""
from __future__ import annotations

import asyncio
import os
import sys
import uuid

from graph.state import AgentState
from graph.workflow import create_graph
from memory.db import init_db, save_session_state, get_session_memory
from agents.document_agent import generate_word_document, generate_excel_document
from agents.desktop_agent import desktop_agent_node
from agents.vision_agent import vision_agent_node

PASS = "  [OK]"
FAIL = "  [X]"


async def test_full_graph_compile() -> bool:
    print("\n[1] Testing complete LangGraph state graph compilation")
    try:
        graph = create_graph()
        assert graph is not None
        print(PASS)
        return True
    except Exception as exc:
        print(f"    Error: {exc}")
        print(FAIL)
        return False


async def test_document_generation() -> bool:
    print("\n[2] Testing Document Generation Agent (Word & Excel)")
    try:
        docx_file = generate_word_document(
            "test_doc.docx",
            {"title": "Test Word Doc", "sections": [{"heading": "Header 1", "paragraph": "Paragraph content"}]}
        )
        assert os.path.exists(docx_file), "Word document not created"

        xlsx_file = generate_excel_document(
            "test_sheet.xlsx",
            {"sheet_title": "Data", "columns": ["Name", "Score"], "rows": [["Alice", 95], ["Bob", 88]]}
        )
        assert os.path.exists(xlsx_file), "Excel spreadsheet not created"

        print(f"    Created Word doc: {docx_file}")
        print(f"    Created Excel sheet: {xlsx_file}")

        # Cleanup
        os.remove(docx_file)
        os.remove(xlsx_file)

        print(PASS)
        return True
    except Exception as exc:
        print(f"    Error: {exc}")
        print(FAIL)
        return False


async def test_desktop_and_vision_agents() -> bool:
    print("\n[3] Testing Desktop & Vision Agent nodes")
    try:
        test_dir = "test_desktop_op_dir"
        state: AgentState = {
            "messages": [],
            "session_id": str(uuid.uuid4()),
            "user_input": "inspect screen",
            "task_type": "desktop_automation",
            "requirements_complete": True,
            "clarifying_question": None,
            "plan": [
                {
                    "step_id": 1,
                    "agent": "desktop_agent",
                    "action": "Create folder",
                    "params": {"operation": "create_folder", "source_path": test_dir},
                },
                {
                    "step_id": 2,
                    "agent": "vision_agent",
                    "action": "Inspect screen",
                    "params": {},
                }
            ],
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

        res_desktop = await desktop_agent_node(state)
        assert os.path.exists(test_dir), "Folder was not created"
        os.rmdir(test_dir)

        state["current_step"] = 1
        res_vision = await vision_agent_node(state)
        assert res_vision["last_execution_result"]["success"] is True

        print(PASS)
        return True
    except Exception as exc:
        print(f"    Error: {exc}")
        print(FAIL)
        return False


async def test_sqlite_memory() -> bool:
    print("\n[4] Testing SQLite persistent memory layer")
    try:
        session_id = f"test_session_{uuid.uuid4().hex[:8]}"
        await init_db()
        await save_session_state(session_id, [{"role": "user", "content": "Hello memory"}], memory_summary="Test context")
        mem = await get_session_memory(session_id)
        assert mem == "Test context", f"Retrieved memory mismatch: {mem}"
        print(f"    Successfully stored and retrieved memory summary: '{mem}'")
        print(PASS)
        return True
    except Exception as exc:
        print(f"    Error: {exc}")
        print(FAIL)
        return False


async def test_fastapi_app_and_endpoints() -> bool:
    print("\n[5] Testing FastAPI App & GET /api/chat endpoint")
    try:
        from api.server import app, chat_get_info
        assert app.title == "DesktopPilot AI API"
        info = await chat_get_info()
        assert info["method_required"] == "POST"
        print(f"    GET /api/chat info response verified: {info['message']}")
        print(PASS)
        return True
    except Exception as exc:
        print(f"    Error: {exc}")
        print(FAIL)
        return False


async def main():
    print("=" * 60)
    print("  DesktopPilot AI — Full System Integration Tests")
    print("=" * 60)

    tests = [
        test_full_graph_compile,
        test_document_generation,
        test_desktop_and_vision_agents,
        test_sqlite_memory,
        test_fastapi_app_and_endpoints,
    ]

    results = []
    for test in tests:
        res = await test()
        results.append(res)

    passed = sum(results)
    total = len(results)
    print(f"\n{'=' * 60}")
    print(f"  Results: {passed}/{total} passed")
    if passed == total:
        print("  All full system integration tests passed successfully!")
    else:
        print("  Some tests failed — see output above.")
    print("=" * 60)
    sys.exit(0 if passed == total else 1)


if __name__ == "__main__":
    asyncio.run(main())

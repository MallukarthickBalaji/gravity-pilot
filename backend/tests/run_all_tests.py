"""
run_all_tests.py — Master test runner for DesktopPilot / GravityPilot AI.
Executes all functional and regression test suites across tools, agents, and LLM backends.
Usage:
    python backend/tests/run_all_tests.py
"""
from __future__ import annotations

import asyncio
import sys
import time
from pathlib import Path

backend_dir = Path(__file__).resolve().parent.parent
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))
    
# pyrefly: ignore [missing-attribute]
sys.stdout.reconfigure(encoding="utf-8")
# pyrefly: ignore [missing-import]
from tests.test_file_tools import test_filesystem_operations
# pyrefly: ignore [missing-import]
from tests.test_documents import test_document_tools
# pyrefly: ignore [missing-import]
from tests.test_screenshot import test_screenshot_tool
# pyrefly: ignore [missing-import]
from tests.test_notebook import test_notebook_tool
# pyrefly: ignore [missing-import]
from tests.test_web_search import test_web_search_suite
# pyrefly: ignore [missing-import]
from tests.test_groq import test_groq_suite
# pyrefly: ignore [missing-import]
from tests.test_ollama import test_ollama_suite
# pyrefly: ignore [missing-import]
from tests.test_sequential_tasks import test_sequential_suite
from tests.test_replanning import TestReplanningPipeline


async def _run_replanning_suite():
    print("=== Testing Replanning & Self-Correction Pipeline ===")
    suite = TestReplanningPipeline()
    await suite.test_validation_to_replanning_transition()
    await suite.test_replanning_generates_new_plan()
    await suite.test_replanned_execution()
    await suite.test_replanning_recovery()
    await suite.test_max_replanning_limit()
    print("[SUCCESS] All replanning and self-correction tests verified successfully!")


async def main():
    start_time = time.time()
    print("=======================================================")
    print("        DESKTOPPILOT AI — MASTER TEST SUITE            ")
    print("=======================================================\n")

    passed = 0
    failed = 0
    suites = [
        ("1. Filesystem Tools", lambda: test_filesystem_operations()),
        ("2. Document Generation Tools", lambda: test_document_tools()),
        ("3. Screenshot Capture", lambda: test_screenshot_tool()),
        ("4. Notebook Inspection", lambda: test_notebook_tool()),
        ("5. Web Search & Bot Detection", lambda: test_web_search_suite()),
        ("6. Cloud LLM (Groq)", lambda: test_groq_suite()),
        ("7. Local LLM (Ollama)", lambda: test_ollama_suite()),
        ("8. Sequential Isolation & Clarification", lambda: test_sequential_suite()),
        ("9. Replanning & Self-Correction", lambda: _run_replanning_suite()),
    ]

    for name, runner in suites:
        print(f"--- Running Suite: {name} ---")
        try:
            res = runner()
            if asyncio.iscoroutine(res):
                await res
            passed += 1
        except Exception as exc:
            failed += 1
            import traceback
            traceback.print_exc()
            print(f"[FAIL] Suite '{name}' failed with error: {exc}\n")

    elapsed = time.time() - start_time
    print("=======================================================")
    print(f"TEST RESULTS: {passed} PASSED | {failed} FAILED | {elapsed:.2f}s")
    print("=======================================================")

    if failed > 0:
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())

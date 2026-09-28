"""
test_replanning.py — Rigorous verification of the LangGraph replanning & self-correction cycle.
Tests:
  1. test_validation_to_replanning_transition()
  2. test_replanning_generates_new_plan()
  3. test_replanned_execution()
  4. test_replanning_recovery()
  5. test_max_replanning_limit()
"""
from __future__ import annotations

import asyncio
from pathlib import Path
import sys
import unittest

# Ensure backend root is on path
BACKEND_DIR = Path(__file__).resolve().parent.parent
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from agents.document_agent import document_agent_node
from agents.planning_agent import planning_agent_node
from agents.task_coordinator import task_coordinator_node
from agents.validation_agent import validation_agent_node, MAX_REPLAN_ATTEMPTS
from graph.state import AgentState
from graph.workflow import create_graph, route_after_validation_agent


class TestReplanningPipeline(unittest.IsolatedAsyncioTestCase):
    """Exhaustive test suite for validation-driven cyclic replanning."""

    async def test_validation_to_replanning_transition(self):
        """Test that validation failure sets replan flags and routes to planning_agent."""
        state: AgentState = {
            "session_id": "test_replan_sess_1",
            "task_id": "test_replan_t1",
            "task_type": "document_generation",
            "replan_count": 0,
            "max_replans": 2,
            "replan_required": False,
            "replan_reason": None,
            "last_execution_result": {
                "success": False,
                "error": "Word document failed validation: missing required section 'Architecture Overview'",
                "agent_type": "document_agent",
            },
            "execution_results": [
                {
                    "success": False,
                    "error": "Word document failed validation: missing required section 'Architecture Overview'",
                    "agent_type": "document_agent",
                }
            ],
            "execution_trace": [],
        }

        # Run validation agent node
        val_update = await validation_agent_node(state)
        merged_state = {**state, **val_update}

        # Verify state updates
        self.assertFalse(val_update["validation_result"]["passed"])
        self.assertEqual(val_update["validation_status"], "failed")
        self.assertTrue(val_update["replan_required"])
        self.assertEqual(val_update["replan_reason"], "execution_failure")
        self.assertEqual(val_update["replan_count"], 1)

        # Verify LangGraph routing conditional edge
        next_node = route_after_validation_agent(merged_state)
        self.assertEqual(next_node, "planning_agent", "Expected routing back to planning_agent for replanning")
        print("  [OK] test_validation_to_replanning_transition passed successfully!")

    async def test_replanning_generates_new_plan(self):
        """Test that planning_agent incorporates failure diagnostics and outputs a revised plan."""
        state: AgentState = {
            "session_id": "test_replan_sess_2",
            "task_id": "test_replan_t2",
            "task_type": "document_generation",
            "user_input": "Create a Word document about Cloud Computing overview.",
            "model_backend": "groq",
            "replan_count": 1,
            "max_replans": 2,
            "replan_required": True,
            "replan_reason": "execution_failure",
            "validation_errors": ["Word document omitted required section 'Security & Privacy'"],
            "previous_plan": [
                {
                    "step_id": 1,
                    "agent": "document_agent",
                    "action": "Create initial doc",
                    "params": {"doc_type": "word", "output_filename": "cloud_overview.docx"},
                }
            ],
            "execution_trace": [],
        }

        plan_update = await planning_agent_node(state)
        new_plan = plan_update.get("plan", [])

        self.assertTrue(len(new_plan) >= 1, "Planning agent should generate at least one corrected plan step")
        self.assertEqual(plan_update["current_step"], 0, "Current step must reset to 0 for revised execution")
        self.assertFalse(plan_update["replan_required"], "replan_required must reset to False after planning")
        self.assertIsNone(plan_update["replan_reason"], "replan_reason must reset to None")
        self.assertIsNotNone(plan_update["previous_plan"], "previous_plan must be preserved for trajectory audit")
        print("  [OK] test_replanning_generates_new_plan passed successfully!")

    async def test_replanned_execution(self):
        """Test that task coordinator and execution agent execute the revised plan correctly."""
        revised_plan = [
            {
                "step_id": 1,
                "agent": "document_agent",
                "action": "Create corrected Word doc with Security section",
                "params": {
                    "doc_type": "word",
                    "output_filename": "cloud_overview_corrected.docx",
                    "content": {
                        "title": "Cloud Computing Overview",
                        "sections": [
                            {"heading": "Introduction", "paragraphs": ["Cloud overview content."]},
                            {"heading": "Security & Privacy", "paragraphs": ["Detailed cloud security architecture."]},
                        ],
                    },
                },
            }
        ]

        state: AgentState = {
            "session_id": "test_replan_sess_3",
            "task_id": "test_replan_t3",
            "plan": revised_plan,
            "current_step": 0,
            "execution_results": [],
            "artifact_paths": [],
            "execution_trace": [],
        }

        # Step 1: Coordinator dispatches
        coord_update = await task_coordinator_node(state)
        merged_state = {**state, **coord_update}

        # Step 2: Document agent executes corrected step
        doc_update = await document_agent_node(merged_state)
        final_state = {**merged_state, **doc_update}

        self.assertTrue(doc_update["last_execution_result"]["success"])
        out_path = Path(doc_update["last_execution_result"]["output_path"])
        self.assertTrue(out_path.exists(), f"Output file must exist on disk: {out_path}")
        self.assertIn(str(out_path), final_state["artifact_paths"])
        print("  [OK] test_replanned_execution passed successfully!")

    async def test_replanning_recovery(self):
        """Test full end-to-end graph recovery via controlled fault injection."""
        graph = create_graph()

        # Define controlled fault injection on Attempt 1:
        # Fails validation on attempt 1 with specific diagnostic error,
        # then passes on attempt 2 after replanning.
        initial_state: AgentState = {
            "messages": [{"role": "user", "content": "Create an Excel spreadsheet of 5 IT products and prices."}],
            "session_id": "test_replan_recovery_sess",
            "task_id": "test_recovery_t1",
            "task_status": "analyzing",
            "user_input": "Create an Excel spreadsheet of 5 IT products and prices.",
            "task_type": "document_generation",
            "requirements_complete": True,
            "clarifying_question": None,
            "plan": None,
            "current_step": 0,
            "last_execution_result": None,
            "execution_results": [],
            "artifact_paths": [],
            "validation_result": None,
            "replan_reason": None,
            "replan_count": 0,
            "max_replans": 2,
            "model_backend": "groq",
            "execution_trace": [],
            "experimental_fault_injection": {
                "task_id": "test_recovery_t1",
                "reason": "Missing required 'Tax_Amount' column in spreadsheet",
                "category": "F8",
            },
        }

        # Execute full LangGraph
        result = await graph.ainvoke(initial_state)

        # Verification of complete recovery trajectory
        self.assertEqual(result.get("validation_status"), "passed", "Final validation status must be 'passed'")
        self.assertTrue(result.get("replan_count", 0) >= 1, "Must have entered replanning loop (replan_count >= 1)")
        self.assertIsNotNone(result.get("previous_plan"), "Must preserve previous plan from attempt 1")
        self.assertTrue(len(result.get("generated_outputs", [])) >= 1, "Must produce physical file on disk")
        print(f"  [OK] test_replanning_recovery passed successfully! (Replan count = {result.get('replan_count')})")

    async def test_max_replanning_limit(self):
        """Test that reaching MAX_REPLAN_ATTEMPTS terminates gracefully without endless loops."""
        state: AgentState = {
            "session_id": "test_replan_sess_5",
            "task_id": "test_replan_t5",
            "task_type": "desktop_automation",
            "replan_count": 2,
            "max_replans": 2,
            "replan_required": False,
            "replan_reason": None,
            "last_execution_result": {
                "success": False,
                "error": "Persistent permission denied error on target file",
                "agent_type": "desktop_agent",
            },
            "execution_results": [
                {
                    "success": False,
                    "error": "Persistent permission denied error on target file",
                    "agent_type": "desktop_agent",
                }
            ],
            "execution_trace": [],
        }

        val_update = await validation_agent_node(state)
        merged_state = {**state, **val_update}

        self.assertFalse(val_update["validation_result"]["passed"])
        self.assertFalse(val_update["replan_required"], "replan_required must be False when max attempts reached")
        self.assertEqual(val_update["replan_reason"], "missing_info")
        self.assertEqual(val_update["failure_category"], "F9")

        # Routing must terminate to memory_agent_write instead of planning_agent
        next_node = route_after_validation_agent(merged_state)
        self.assertEqual(next_node, "requirement_analyzer", "Expected routing to graceful completion or user feedback")
        print("  [OK] test_max_replanning_limit passed successfully!")


if __name__ == "__main__":
    unittest.main()

"""
main.py — CLI entry point for DesktopPilot AI (Phase 1 testing).

Run:
  python main.py

The CLI keeps a single session alive across turns. If the system needs
clarification it prints the question and waits for your reply (which is
appended to messages and fed back through the graph).

Type 'quit' or 'exit' to stop. Type 'trace' to see the last execution trace.
Type 'reset' to start a new session.
"""
from __future__ import annotations

import asyncio
import logging
import sys
import uuid
from typing import Any

from config import config
from graph.state import AgentState, Capabilities
from graph.workflow import create_graph

# ── Logging ───────────────────────────────────────────────────────────────────
logging.basicConfig(
    level=getattr(logging, config.log_level.upper(), logging.INFO),
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger(__name__)


# ── Helpers ───────────────────────────────────────────────────────────────────

def _print_trace(trace: list[dict[str, Any]]) -> None:
    if not trace:
        return
    print("\n  Execution trace:")
    for entry in trace:
        icon = {"success": "✓", "error": "✗", "pending": "→", "skipped": "○"}.get(
            entry.get("status", ""), "·"
        )
        print(f"    {icon} [{entry['agent']}] {entry['message']}")


def _print_plan(plan: list[dict[str, Any]]) -> None:
    if not plan:
        return
    print("\n  Generated plan:")
    for step in plan:
        print(
            f"    Step {step.get('step_id', '?')}: "
            f"[{step.get('agent', '?')}] {step.get('action', '?')}"
        )
        params = step.get("params", {})
        if params:
            for k, v in params.items():
                print(f"        {k}: {v}")


def _build_initial_state(
    user_input: str,
    session_id: str,
    messages: list[dict[str, str]],
) -> AgentState:
    """Construct fresh state for each graph invocation."""
    return {
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
        "model_backend": "unknown",
        "capabilities": None,
        "memory_context": None,
        "final_response": None,
        "error": None,
        "execution_trace": [],
    }


# ── Main REPL ─────────────────────────────────────────────────────────────────

async def run_cli() -> None:
    print("=" * 60)
    print("  DesktopPilot AI — Phase 1 CLI")
    print("  Commands: quit | exit | trace | reset")
    print("=" * 60)
    print()

    graph = create_graph()
    session_id = str(uuid.uuid4())
    messages: list[dict[str, str]] = []
    last_trace: list[dict[str, Any]] = []

    while True:
        try:
            user_input = input("You: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nGoodbye.")
            break

        if not user_input:
            continue

        if user_input.lower() in ("quit", "exit"):
            print("Goodbye.")
            break

        if user_input.lower() == "reset":
            session_id = str(uuid.uuid4())
            messages = []
            last_trace = []
            print("  [Session reset]\n")
            continue

        if user_input.lower() == "trace":
            if last_trace:
                _print_trace(last_trace)
            else:
                print("  (no trace yet)")
            print()
            continue

        # ── Run the graph ──────────────────────────────────────────────────────
        state = _build_initial_state(user_input, session_id, messages)

        try:
            result: AgentState = await graph.ainvoke(state)
        except Exception as exc:
            logger.exception("Graph execution error: %s", exc)
            print(f"\n  [Error] {exc}\n")
            continue

        last_trace = result.get("execution_trace", [])
        backend = result.get("model_backend", "?")

        print(f"\n  Mode: {backend.upper()}")
        _print_trace(last_trace)

        # ── Response handling ─────────────────────────────────────────────────
        if result.get("error") and not result.get("final_response"):
            print(f"\nSystem: {result['error']}\n")

        elif result.get("clarifying_question"):
            question = result["clarifying_question"]
            print(f"\nAssistant (needs clarification): {question}\n")
            # Append assistant question to messages so the next turn has context
            messages = result.get("messages", messages)
            messages.append({"role": "assistant", "content": question})
            continue  # Don't append user message twice — it's already in result

        elif result.get("final_response"):
            print(f"\nAssistant: {result['final_response']}\n")
            messages = result.get("messages", messages)
            messages.append({"role": "assistant", "content": result["final_response"]})

        elif result.get("plan"):
            _print_plan(result["plan"])
            plan_summary = (
                f"Plan ready: {len(result['plan'])} steps. "
                "(Execution agents will be wired in Phase 4.)"
            )
            print(f"\nAssistant: {plan_summary}\n")
            messages = result.get("messages", messages)
            messages.append({"role": "assistant", "content": plan_summary})

        else:
            print("\nAssistant: (no response — check trace above)\n")
            messages = result.get("messages", messages)


if __name__ == "__main__":
    asyncio.run(run_cli())

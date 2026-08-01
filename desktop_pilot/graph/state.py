"""
state.py — Shared AgentState for the DesktopPilot LangGraph StateGraph.

All nodes read from and write to this typed state. LangGraph merges updates
from each node; list fields use the `add` reducer (append-only) so traces
and messages accumulate across nodes rather than overwriting.
"""
from __future__ import annotations

from operator import add
from typing import Annotated, Any, Optional
from typing_extensions import TypedDict
from pydantic import BaseModel


# ── Capability flags (set by model_router) ────────────────────────────────────

class Capabilities(BaseModel):
    """Which execution capabilities are available in the current backend mode."""
    browser_automation: bool = False
    desktop_automation: bool = False
    document_generation: bool = False
    # vision_agent is a Phase 1 stub — always False until Phase 9
    vision_agent: bool = False

    def supports_task_type(self, task_type: str) -> bool:
        mapping = {
            "browser_automation": self.browser_automation,
            "desktop_automation": self.desktop_automation,
            "document_generation": self.document_generation,
            "general_query": True,  # always available — no execution agent needed
        }
        return mapping.get(task_type, False)


# ── Execution plan step ────────────────────────────────────────────────────────

class PlanStep(TypedDict):
    step_id: int
    agent: str          # e.g. "document_agent", "browser_agent", "desktop_agent"
    action: str         # human-readable description
    params: dict[str, Any]


# ── Trace entry ───────────────────────────────────────────────────────────────

class TraceEntry(TypedDict):
    agent: str
    status: str         # "success" | "error" | "pending" | "skipped"
    message: str


# ── Main graph state ──────────────────────────────────────────────────────────

class AgentState(TypedDict):
    # ── Conversation ──────────────────────────────────────────────────────────
    # Accumulated with `add` — each node appends new messages, never overwrites.
    messages: Annotated[list[dict[str, str]], add]
    session_id: str
    user_input: str                  # the raw current user message

    # ── Classification (set by supervisor) ───────────────────────────────────
    task_type: Optional[str]         # document_generation | browser_automation |
                                     # desktop_automation | general_query | unknown

    # ── Requirements analysis (set by requirement_analyzer) ──────────────────
    requirements_complete: bool
    clarifying_question: Optional[str]   # non-None ⟹ route back to user

    # ── Planning (set by planning_agent) ──────────────────────────────────────
    plan: Optional[list[PlanStep]]
    current_step: int                    # used by task_coordinator in later phases

    # ── Execution (set by task_coordinator + execution agents) ───────────────
    last_execution_result: Optional[dict[str, Any]]  # output from last agent

    # ── Validation (set by validation_agent) ─────────────────────────────────
    validation_result: Optional[dict[str, Any]]
    replan_reason: Optional[str]         # non-None ⟹ validation wants a replan

    # ── Backend / capabilities (set by model_router) ─────────────────────────
    model_backend: str                   # "groq" | "ollama" | "none"
    capabilities: Optional[Capabilities]

    # ── Memory (set by memory_agent) ─────────────────────────────────────────
    memory_context: Optional[str]        # relevant prior context injected pre-plan

    # ── Final output ──────────────────────────────────────────────────────────
    final_response: Optional[str]
    error: Optional[str]

    # ── Accumulated execution trace ───────────────────────────────────────────
    # Accumulated with `add` — each node appends, never overwrites.
    execution_trace: Annotated[list[TraceEntry], add]

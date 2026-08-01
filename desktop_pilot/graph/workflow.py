"""
workflow.py — LangGraph StateGraph definition for DesktopPilot AI.

Phase 1 graph:
  START → model_router → supervisor → requirement_analyzer → planning_agent → END

Cyclic edges added in later phases:
  validation_agent → planning_agent     (Phase 4 — replan on failure)
  validation_agent → requirement_analyzer  (Phase 4 — reask on ambiguous failure)
  requirement_analyzer → supervisor     (after clarification is collected)

Routing functions are kept here (not in individual agent files) so the full
edge topology is visible in one place.
"""
from __future__ import annotations

import logging
from typing import Literal

from langgraph.graph import StateGraph, START, END

from agents.model_router import model_router_node
from agents.supervisor import supervisor_node
from agents.requirement_analyzer import requirement_analyzer_node
from agents.planning_agent import planning_agent_node
from graph.state import AgentState

logger = logging.getLogger(__name__)


# ── Routing functions ─────────────────────────────────────────────────────────

def route_after_model_router(
    state: AgentState,
) -> Literal["supervisor", "__end__"]:
    """If no backend is reachable, stop immediately."""
    if state.get("model_backend") == "none":
        return "__end__"
    return "supervisor"


def route_after_supervisor(
    state: AgentState,
) -> Literal["requirement_analyzer", "__end__"]:
    """
    If the supervisor already produced a final_response (capability unavailable),
    we're done. Otherwise, proceed to requirement analysis.
    """
    if state.get("final_response"):
        return "__end__"
    return "requirement_analyzer"


def route_after_requirement_analyzer(
    state: AgentState,
) -> Literal["planning_agent", "__end__"]:
    """
    If requirements are incomplete, the clarifying_question is set and we
    surface it to the user by routing to END. The user's next message will
    restart the graph from the beginning (supervisor will re-run with new
    context already in messages).

    If requirements are met, proceed to planning.
    """
    if state.get("requirements_complete"):
        return "planning_agent"
    return "__end__"


# ── Graph factory ─────────────────────────────────────────────────────────────

def create_graph():
    """
    Build and compile the DesktopPilot StateGraph.

    Returns a compiled LangGraph graph ready for ainvoke() / astream().
    """
    builder = StateGraph(AgentState)

    # ── Register nodes ────────────────────────────────────────────────────────
    builder.add_node("model_router", model_router_node)
    builder.add_node("supervisor", supervisor_node)
    builder.add_node("requirement_analyzer", requirement_analyzer_node)
    builder.add_node("planning_agent", planning_agent_node)

    # ── Phase 4 nodes (stubs — will be wired in a later phase) ───────────────
    # task_coordinator, desktop_agent, browser_agent, document_agent,
    # vision_agent, validation_agent, memory_agent

    # ── Edges ─────────────────────────────────────────────────────────────────
    builder.add_edge(START, "model_router")

    builder.add_conditional_edges(
        "model_router",
        route_after_model_router,
        {"supervisor": "supervisor", "__end__": END},
    )

    builder.add_conditional_edges(
        "supervisor",
        route_after_supervisor,
        {"requirement_analyzer": "requirement_analyzer", "__end__": END},
    )

    builder.add_conditional_edges(
        "requirement_analyzer",
        route_after_requirement_analyzer,
        {"planning_agent": "planning_agent", "__end__": END},
    )

    builder.add_edge("planning_agent", END)

    # ── Phase 4 cyclic edges (commented out until implemented) ────────────────
    # builder.add_conditional_edges("validation_agent", route_after_validation, {
    #     "planning_agent": "planning_agent",          # replan on execution failure
    #     "requirement_analyzer": "requirement_analyzer",  # reask on ambiguous failure
    #     "__end__": END,
    # })
    # builder.add_edge("requirement_analyzer_resume", "supervisor")

    return builder.compile()

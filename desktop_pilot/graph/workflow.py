"""
workflow.py — LangGraph StateGraph definition for DesktopPilot AI.

Full execution graph:
  START → model_router → memory_agent → supervisor → requirement_analyzer
        → planning_agent → task_coordinator → validation_agent
        ↳ (cyclic replan if validation fails) → planning_agent
        ↳ (on completion / failure) → END
"""
from __future__ import annotations

import logging
from typing import Literal

from langgraph.graph import StateGraph, START, END

from agents.model_router import model_router_node
from agents.memory_agent import memory_agent_node
from agents.supervisor import supervisor_node
from agents.requirement_analyzer import requirement_analyzer_node
from agents.planning_agent import planning_agent_node
from agents.task_coordinator import task_coordinator_node
from agents.validation_agent import validation_agent_node
from agents.browser_agent import browser_agent_node
from agents.desktop_agent import desktop_agent_node
from agents.document_agent import document_agent_node
from agents.vision_agent import vision_agent_node
from graph.state import AgentState

logger = logging.getLogger(__name__)


# ── Routing functions ─────────────────────────────────────────────────────────

def route_after_model_router(
    state: AgentState,
) -> Literal["memory_agent", "__end__"]:
    """If no backend is reachable, stop immediately."""
    if state.get("model_backend") == "none":
        return "__end__"
    return "memory_agent"


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
    If requirements are incomplete, route to END to wait for user reply.
    If requirements are met, proceed to planning.
    """
    if state.get("requirements_complete"):
        return "planning_agent"
    return "__end__"


def route_after_planning_agent(
    state: AgentState,
) -> Literal["task_coordinator", "__end__"]:
    """
    If planning produced a final_response (e.g. general query direct answer),
    we're done. Otherwise proceed to task execution.
    """
    if state.get("final_response"):
        return "__end__"
    return "task_coordinator"


def route_after_task_coordinator(
    state: AgentState,
) -> Literal["document_agent", "browser_agent", "desktop_agent", "vision_agent", "memory_agent", "__end__"]:
    """Route to the next agent based on the coordinator's target."""
    target = state.get("target_agent")
    if target in ["document_agent", "browser_agent", "desktop_agent", "vision_agent"]:
        return target
    
    # If no valid agent target, we are either done with the plan or skipped
    return "memory_agent"


def route_after_execution_agent(
    state: AgentState,
) -> Literal["validation_agent"]:
    """After any execution agent finishes, validate the result."""
    return "validation_agent"


def route_after_validation(
    state: AgentState,
) -> Literal["planning_agent", "task_coordinator", "memory_agent"]:
    """
    If validation requested a replan, route back to planning_agent.
    If there are more steps, route back to task_coordinator.
    Otherwise, route to memory_agent.
    """
    if state.get("replan_reason"):
        return "planning_agent"
    
    plan = state.get("plan") or []
    current_step = state.get("current_step", 0)
    
    if current_step < len(plan):
        return "task_coordinator"
        
    return "memory_agent"


# ── Graph factory ─────────────────────────────────────────────────────────────

def create_graph():
    """
    Build and compile the DesktopPilot StateGraph.

    Returns a compiled LangGraph graph ready for ainvoke() / astream().
    """
    builder = StateGraph(AgentState)

    # ── Register nodes ────────────────────────────────────────────────────────
    builder.add_node("model_router", model_router_node)
    builder.add_node("memory_agent", memory_agent_node)
    builder.add_node("supervisor", supervisor_node)
    builder.add_node("requirement_analyzer", requirement_analyzer_node)
    builder.add_node("planning_agent", planning_agent_node)
    builder.add_node("task_coordinator", task_coordinator_node)
    builder.add_node("validation_agent", validation_agent_node)
    
    # Execution nodes
    builder.add_node("document_agent", document_agent_node)
    builder.add_node("browser_agent", browser_agent_node)
    builder.add_node("desktop_agent", desktop_agent_node)
    builder.add_node("vision_agent", vision_agent_node)

    # ── Edges ─────────────────────────────────────────────────────────────────
    builder.add_edge(START, "model_router")

    builder.add_conditional_edges(
        "model_router",
        route_after_model_router,
        {"memory_agent": "memory_agent", "__end__": END},
    )

    builder.add_edge("memory_agent", "supervisor")

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

    builder.add_conditional_edges(
        "planning_agent",
        route_after_planning_agent,
        {"task_coordinator": "task_coordinator", "__end__": END},
    )

    builder.add_conditional_edges(
        "task_coordinator",
        route_after_task_coordinator,
        {
            "document_agent": "document_agent",
            "browser_agent": "browser_agent",
            "desktop_agent": "desktop_agent",
            "vision_agent": "vision_agent",
            "memory_agent": "memory_agent",
            "__end__": END
        },
    )

    builder.add_edge("document_agent", "validation_agent")
    builder.add_edge("browser_agent", "validation_agent")
    builder.add_edge("desktop_agent", "validation_agent")
    builder.add_edge("vision_agent", "validation_agent")

    builder.add_conditional_edges(
        "validation_agent",
        route_after_validation,
        {"planning_agent": "planning_agent", "task_coordinator": "task_coordinator", "memory_agent": "memory_agent"},
    )

    return builder.compile()

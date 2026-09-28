"""
workflow.py — LangGraph StateGraph definition for GravityPilot.
Coordinates multi-agent execution, cyclic replanning loops, and persistence.
"""
from __future__ import annotations

import logging
from typing import Literal

from langgraph.graph import StateGraph, START, END

from agents.model_router import model_router_node
from agents.supervisor import supervisor_node
from agents.requirement_analyzer import requirement_analyzer_node
from agents.memory_agent import memory_agent_read_node, memory_agent_write_node
from agents.planning_agent import planning_agent_node
from agents.task_coordinator import task_coordinator_node
from agents.document_agent import document_agent_node
from agents.browser_agent import browser_agent_node
from agents.desktop_agent import desktop_agent_node
from agents.vision_agent import vision_agent_node
from agents.validation_agent import validation_agent_node
from graph.state import AgentState

logger = logging.getLogger(__name__)


def route_after_model_router(state: AgentState) -> Literal["supervisor", "__end__"]:
    if state.get("model_backend") == "none":
        return "__end__"
    return "supervisor"


def route_after_supervisor(state: AgentState) -> Literal["requirement_analyzer", "__end__"]:
    if state.get("final_response"):
        return "__end__"
    return "requirement_analyzer"


def route_after_requirement_analyzer(state: AgentState) -> Literal["memory_agent_read", "memory_agent_write"]:
    if state.get("requirements_complete"):
        return "memory_agent_read"
    return "memory_agent_write"


def route_after_planning_agent(state: AgentState) -> Literal["task_coordinator", "__end__"]:
    if state.get("final_response"):
        return "__end__"
    plan = state.get("plan")
    if not plan:
        return "__end__"
    return "task_coordinator"


def route_after_task_coordinator(
    state: AgentState,
) -> Literal["document_agent", "browser_agent", "desktop_agent", "vision_agent", "validation_agent", "__end__"]:
    plan = state.get("plan", [])
    current_step = state.get("current_step", 0)

    if not plan or current_step >= len(plan):
        return "validation_agent"

    agent = plan[current_step].get("agent", "")
    valid_agents = {
        "document_agent": "document_agent",
        "browser_agent": "browser_agent",
        "desktop_agent": "desktop_agent",
        "vision_agent": "vision_agent",
    }
    return valid_agents.get(agent, "validation_agent")  # type: ignore[return-value]


def route_after_execution_agent(state: AgentState) -> Literal["task_coordinator"]:
    return "task_coordinator"


def route_after_validation_agent(
    state: AgentState,
) -> Literal["planning_agent", "requirement_analyzer", "memory_agent_write"]:
    replan_required = state.get("replan_required", False)
    replan_reason = state.get("replan_reason")
    replan_count = state.get("replan_count", 0)
    max_replans = state.get("max_replans", 2)

    if (replan_required or replan_reason == "execution_failure") and replan_count <= max_replans:
        logger.info("Validation -> PlanningAgent (replanning attempt %d of %d)", replan_count, max_replans)
        return "planning_agent"
    elif replan_reason == "missing_info":
        logger.info("Validation -> RequirementAnalyzer (missing info)")
        return "requirement_analyzer"
    return "memory_agent_write"


def create_graph():
    builder = StateGraph(AgentState)

    builder.add_node("model_router", model_router_node)
    builder.add_node("supervisor", supervisor_node)
    builder.add_node("requirement_analyzer", requirement_analyzer_node)
    builder.add_node("memory_agent_read", memory_agent_read_node)
    builder.add_node("planning_agent", planning_agent_node)
    builder.add_node("task_coordinator", task_coordinator_node)
    builder.add_node("document_agent", document_agent_node)
    builder.add_node("browser_agent", browser_agent_node)
    builder.add_node("desktop_agent", desktop_agent_node)
    builder.add_node("vision_agent", vision_agent_node)
    builder.add_node("validation_agent", validation_agent_node)
    builder.add_node("memory_agent_write", memory_agent_write_node)

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
        {"memory_agent_read": "memory_agent_read", "memory_agent_write": "memory_agent_write"},
    )

    builder.add_edge("memory_agent_read", "planning_agent")

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
            "validation_agent": "validation_agent",
            "__end__": END,
        },
    )

    for exec_node in ("document_agent", "browser_agent", "desktop_agent", "vision_agent"):
        builder.add_conditional_edges(
            exec_node,
            route_after_execution_agent,
            {"task_coordinator": "task_coordinator"},
        )

    builder.add_conditional_edges(
        "validation_agent",
        route_after_validation_agent,
        {
            "planning_agent": "planning_agent",
            "requirement_analyzer": "requirement_analyzer",
            "memory_agent_write": "memory_agent_write",
        },
    )

    builder.add_edge("memory_agent_write", END)

    return builder.compile()

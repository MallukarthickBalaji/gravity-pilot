"""
server.py — FastAPI backend server for GravityPilot AI.
Provides REST and Server-Sent Events (SSE) streaming endpoints with real-time agent trace events,
per-task ID isolation, explicit session lifecycle, and generated outputs tracking.
"""
from __future__ import annotations

import asyncio
import json
import logging
import os
import uuid
from typing import Any, AsyncGenerator, Optional

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

from config import config
from graph.state import AgentState
from graph.workflow import create_graph
from memory.database import (
    delete_session,
    ensure_session,
    get_all_messages,
    get_all_sessions,
    get_recent_messages,
    get_session_outputs,
    get_session_task_state,
    get_task_history,
    reset_session_task_state,
    save_message,
    update_session_task_state,
)

logger = logging.getLogger(__name__)

app = FastAPI(
    title="GravityPilot AI API",
    description="Agentic AI Desktop Automation Engine",
    version="2.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

_graph = None


def get_compiled_graph():
    global _graph
    if _graph is None:
        _graph = create_graph()
    return _graph


# Canonical Agent Mapping
NODE_TO_CANONICAL_AGENT = {
    "model_router": "model_router",
    "supervisor": "supervisor",
    "requirement_analyzer": "requirement_analyzer",
    "memory_agent_read": "memory_agent",
    "planning_agent": "planning_agent",
    "task_coordinator": "task_coordinator",
    "document_agent": "document_agent",
    "desktop_agent": "desktop_agent",
    "browser_agent": "browser_agent",
    "validation_agent": "validation_agent",
    "memory_agent_write": "memory_agent",
}


from models.schemas import ChatRequest, ChatResponse


@app.get("/api/ollama/health")
async def ollama_health_endpoint():
    """Dedicated Ollama connectivity and installed models health check."""
    from agents.model_router import check_ollama_status
    return await check_ollama_status()


@app.get("/health")
async def health():
    """System health and LLM connectivity status."""
    from agents.model_router import _check_groq, check_ollama_status, _build_capabilities

    groq_ok = await _check_groq()
    ollama_info = await check_ollama_status()
    ollama_ok = ollama_info.get("available", False)
    backend = "groq" if groq_ok else ("ollama" if ollama_ok else "none")
    caps = _build_capabilities(backend)

    return {
        "status": "ok",
        "backend": True,
        "langgraph": True,
        "model": backend != "none",
        "model_backend": backend,
        "groq_available": groq_ok,
        "ollama_available": ollama_ok,
        "ollama_info": ollama_info,
        "capabilities": caps.model_dump() if backend != "none" else None,
    }


@app.get("/api/chat/status")
async def chat_status():
    """Endpoint for frontend status bar."""
    from agents.model_router import _check_groq, _check_ollama

    groq_ok = await _check_groq()
    ollama_ok = await _check_ollama()
    mode = "groq" if groq_ok else ("ollama" if ollama_ok else "none")
    return {
        "mode": mode,
        "browserAutomation": groq_ok,
        "desktopAutomation": True,
        "documentGeneration": True,
    }


@app.get("/sessions")
@app.get("/api/chat/sessions")
async def list_sessions():
    sessions = await get_all_sessions()
    return {"sessions": sessions}


@app.post("/sessions")
@app.post("/api/chat/sessions")
async def create_session_endpoint():
    new_id = str(uuid.uuid4())
    await ensure_session(new_id, title="New Chat")
    await reset_session_task_state(new_id)
    return {"id": new_id, "title": "New Chat", "status": "idle"}


@app.get("/session/{session_id}/history")
@app.get("/api/chat/sessions/{session_id}/messages")
async def session_history(session_id: str):
    msgs = await get_all_messages(session_id)
    task_state = await get_session_task_state(session_id)
    outputs = await get_session_outputs(session_id)
    return {
        "session_id": session_id,
        "messages": msgs,
        "task_state": task_state,
        "outputs": outputs,
    }


@app.delete("/session/{session_id}")
@app.delete("/api/chat/sessions/{session_id}")
async def remove_session(session_id: str):
    await delete_session(session_id)
    return {"status": "deleted", "session_id": session_id}


@app.post("/session/{session_id}/reset")
@app.post("/api/chat/sessions/{session_id}/reset")
async def reset_session_endpoint(session_id: str):
    await reset_session_task_state(session_id)
    return {"status": "reset", "session_id": session_id, "task_status": "idle"}


@app.get("/session/{session_id}/tasks")
async def session_tasks(session_id: str):
    tasks = await get_task_history(session_id)
    outputs = await get_session_outputs(session_id)
    return {"session_id": session_id, "tasks": tasks, "outputs": outputs}


async def _run_graph_turn(
    user_text: str,
    session_id: str,
    task_id: str | None = None,
    model_backend: str | None = None,
    experimental_fault_injection: dict[str, Any] | None = None,
) -> AgentState:
    tid = task_id or f"task_{uuid.uuid4().hex[:10]}"
    sess_state = await get_session_task_state(session_id)

    # Check if answering ongoing clarification
    is_answering_clarification = (
        sess_state is not None
        and sess_state.get("status") == "waiting_for_user"
        and sess_state.get("pending_clarifying_question") is not None
    )

    task_type = sess_state.get("pending_task_type") if is_answering_clarification else None

    await save_message(session_id, "user", user_text, task_id=tid)
    await update_session_task_state(session_id, status="analyzing", task_id=tid, task_type=task_type)

    prior_messages = await get_recent_messages(session_id, limit=12)
    if prior_messages and prior_messages[-1].get("content") == user_text:
        prior_messages = prior_messages[:-1]

    initial_state: AgentState = {
        "messages": prior_messages + [{"role": "user", "content": user_text}],
        "session_id": session_id,
        "task_id": tid,
        "task_status": "analyzing",
        "user_input": user_text,
        "task_type": task_type,
        "requirements_complete": False,
        "clarifying_question": None,
        "plan": None,
        "current_step": 0,
        "last_execution_result": None,
        "validation_result": None,
        "generated_outputs": [],
        "replan_reason": None,
        "replan_count": 0,
        "model_backend": model_backend or "unknown",
        "capabilities": None,
        "memory_context": None,
        "final_response": None,
        "error": None,
        "execution_trace": [],
        "experimental_fault_injection": experimental_fault_injection,
    }

    graph = get_compiled_graph()
    result = await graph.ainvoke(initial_state)
    return result


@app.post("/chat", response_model=ChatResponse)
async def chat_endpoint(req: ChatRequest):
    user_text = (req.message or req.user_input or "").strip()
    if not user_text:
        raise HTTPException(status_code=400, detail="Empty message received.")

    session_id = req.session_id or str(uuid.uuid4())
    await ensure_session(session_id, title=user_text[:40])
    task_id = req.task_id or f"task_{uuid.uuid4().hex[:10]}"
    chosen_backend = req.model_backend or req.backend

    try:
        result = await _run_graph_turn(
            user_text,
            session_id,
            task_id=task_id,
            model_backend=chosen_backend,
            experimental_fault_injection=req.experimental_fault_injection,
        )
        return ChatResponse(
            session_id=session_id,
            task_id=task_id,
            response=result.get("final_response"),
            clarifying_question=result.get("clarifying_question"),
            execution_trace=result.get("execution_trace", []),
            generated_outputs=result.get("generated_outputs", []),
            model_backend=result.get("model_backend", "unknown"),
            task_type=result.get("task_type"),
            plan=result.get("plan"),
            previous_plan=result.get("previous_plan"),
            validation_result=result.get("validation_result"),
            replan_count=result.get("replan_count", 0),
            replan_required=result.get("replan_required", False),
            error=result.get("error"),
        )
    except Exception as exc:
        logger.exception("Chat endpoint execution error: %s", exc)
        raise HTTPException(status_code=500, detail=str(exc))


# ── Real-time SSE Stream Endpoint ─────────────────────────────────────────────

async def _stream_graph_events(
    user_text: str,
    session_id: str,
    task_id: str,
    model_backend: str | None = None,
) -> AsyncGenerator[str, None]:
    await ensure_session(session_id, title=user_text[:40])

    sess_state = await get_session_task_state(session_id)
    is_answering_clarification = (
        sess_state is not None
        and sess_state.get("status") == "waiting_for_user"
        and sess_state.get("pending_clarifying_question") is not None
    )

    task_type = sess_state.get("pending_task_type") if is_answering_clarification else None

    await save_message(session_id, "user", user_text, task_id=task_id)
    await update_session_task_state(session_id, status="analyzing", task_id=task_id, task_type=task_type)

    prior_messages = await get_recent_messages(session_id, limit=12)
    if prior_messages and prior_messages[-1].get("content") == user_text:
        prior_messages = prior_messages[:-1]

    initial_state: AgentState = {
        "messages": prior_messages + [{"role": "user", "content": user_text}],
        "session_id": session_id,
        "task_id": task_id,
        "task_status": "analyzing",
        "user_input": user_text,
        "task_type": task_type,
        "requirements_complete": False,
        "clarifying_question": None,
        "plan": None,
        "current_step": 0,
        "last_execution_result": None,
        "validation_result": None,
        "generated_outputs": [],
        "replan_reason": None,
        "replan_count": 0,
        "model_backend": model_backend or "unknown",
        "capabilities": None,
        "memory_context": None,
        "final_response": None,
        "error": None,
        "execution_trace": [],
    }

    graph = get_compiled_graph()

    # Emit initial task start event
    yield f"data: {json.dumps({'type': 'task_start', 'task_id': task_id, 'session_id': session_id, 'status': 'analyzing'})}\n\n"
    yield f"data: {json.dumps({'type': 'agent_update', 'task_id': task_id, 'session_id': session_id, 'agent': 'model_router', 'status': 'active', 'detail': 'Routing model backend...'})}\n\n"

    try:
        final_state = dict(initial_state)
        async for output in graph.astream(initial_state, stream_mode="updates"):
            for node_name, node_update in output.items():
                final_state.update(node_update)

                canonical_agent = NODE_TO_CANONICAL_AGENT.get(node_name, node_name)

                # Extract latest trace item if present
                latest_trace = None
                if "execution_trace" in node_update and node_update["execution_trace"]:
                    latest_trace = node_update["execution_trace"][-1]

                detail_msg = latest_trace.get("message", f"{canonical_agent} completed") if latest_trace else f"{canonical_agent} active"
                status = "done"

                # Check for replanning event
                if node_name == "validation_agent" and node_update.get("replan_reason") == "execution_failure":
                    status = "failed"
                    yield f"data: {json.dumps({'type': 'agent_update', 'task_id': task_id, 'session_id': session_id, 'agent': 'validation_agent', 'status': 'failed', 'detail': detail_msg})}\n\n"
                    yield f"data: {json.dumps({'type': 'agent_update', 'task_id': task_id, 'session_id': session_id, 'agent': 'planning_agent', 'status': 'retrying', 'detail': 'Replanning revised execution steps...'})}\n\n"
                    continue

                if node_name == "requirement_analyzer" and not node_update.get("requirements_complete"):
                    status = "done"

                yield f"data: {json.dumps({'type': 'agent_update', 'task_id': task_id, 'session_id': session_id, 'agent': canonical_agent, 'status': status, 'detail': detail_msg})}\n\n"

        # Determine final message to stream to chat
        clarifying_q = final_state.get("clarifying_question")
        final_resp = final_state.get("final_response")
        error_resp = final_state.get("error")
        generated_files = final_state.get("generated_outputs", [])

        if clarifying_q and not final_state.get("requirements_complete"):
            yield f"data: {json.dumps({'type': 'message', 'task_id': task_id, 'session_id': session_id, 'role': 'agent', 'agentName': 'Requirement Analyzer', 'agentColor': '#2E7D6B', 'kind': 'clarification', 'text': clarifying_q})}\n\n"
            yield f"data: {json.dumps({'type': 'task_state', 'task_id': task_id, 'session_id': session_id, 'status': 'waiting_for_user'})}\n\n"
        elif final_resp:
            yield f"data: {json.dumps({'type': 'message', 'task_id': task_id, 'session_id': session_id, 'role': 'agent', 'agentName': 'Validation Agent', 'agentColor': '#2E7D6B', 'kind': 'normal', 'text': final_resp, 'generated_files': generated_files})}\n\n"
            yield f"data: {json.dumps({'type': 'task_state', 'task_id': task_id, 'session_id': session_id, 'status': 'completed'})}\n\n"
        elif error_resp:
            yield f"data: {json.dumps({'type': 'message', 'task_id': task_id, 'session_id': session_id, 'role': 'agent', 'agentName': 'System', 'agentColor': '#B84040', 'kind': 'error', 'text': error_resp})}\n\n"
            yield f"data: {json.dumps({'type': 'task_state', 'task_id': task_id, 'session_id': session_id, 'status': 'failed'})}\n\n"
        else:
            yield f"data: {json.dumps({'type': 'message', 'task_id': task_id, 'session_id': session_id, 'role': 'agent', 'agentName': 'Supervisor', 'agentColor': '#1F3A5F', 'kind': 'normal', 'text': 'Task completed successfully.', 'generated_files': generated_files})}\n\n"
            yield f"data: {json.dumps({'type': 'task_state', 'task_id': task_id, 'session_id': session_id, 'status': 'completed'})}\n\n"

        yield f"data: {json.dumps({'type': 'done', 'task_id': task_id, 'session_id': session_id})}\n\n"

    except Exception as exc:
        logger.exception("Error in SSE stream: %s", exc)
        yield f"data: {json.dumps({'type': 'message', 'task_id': task_id, 'session_id': session_id, 'role': 'agent', 'agentName': 'System', 'agentColor': '#B84040', 'kind': 'error', 'text': f'An error occurred: {str(exc)}'})}\n\n"
        yield f"data: {json.dumps({'type': 'task_state', 'task_id': task_id, 'session_id': session_id, 'status': 'failed'})}\n\n"
        yield f"data: {json.dumps({'type': 'done', 'task_id': task_id, 'session_id': session_id})}\n\n"


@app.post("/api/chat/sessions/{session_id}/stream")
@app.post("/chat/stream")
async def chat_stream_endpoint(session_id: str, req: ChatRequest):
    user_text = (req.message or req.user_input or "").strip()
    if not user_text:
        raise HTTPException(status_code=400, detail="Empty message received.")

    task_id = req.task_id or f"task_{uuid.uuid4().hex[:10]}"
    chosen_backend = req.model_backend or req.backend

    return StreamingResponse(
        _stream_graph_events(user_text, session_id, task_id, model_backend=chosen_backend),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )


if __name__ == "__main__":
    import uvicorn

    port = int(os.environ.get("PORT", config.api_port))
    uvicorn.run("api.server:app", host=config.api_host, port=port, reload=False)

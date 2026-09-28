"""
server.py — FastAPI backend server for DesktopPilot AI.

Run:
  uvicorn api.server:app --port 8000
"""
from __future__ import annotations

import logging
import uuid
from typing import Any, Optional

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from graph.state import AgentState
from graph.workflow import create_graph
from memory.db import get_session_memory, init_db

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="DesktopPilot AI API",
    description="Hierarchical Multi-Agent Desktop Automation Engine API",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

graph = create_graph()


class ChatRequest(BaseModel):
    user_input: str
    session_id: Optional[str] = None
    messages: Optional[list[dict[str, str]]] = None


class ChatResponse(BaseModel):
    session_id: str
    backend: str
    task_type: Optional[str] = None
    requirements_complete: bool = False
    clarifying_question: Optional[str] = None
    plan: Optional[list[dict[str, Any]]] = None
    final_response: Optional[str] = None
    execution_trace: list[dict[str, Any]] = []
    error: Optional[str] = None


@app.on_event("startup")
async def startup_event():
    logger.info("Initializing DesktopPilot database...")
    await init_db()


@app.get("/")
async def root():
    return {
        "service": "DesktopPilot AI Engine API",
        "status": "online",
        "endpoints": {
            "health": "GET /health",
            "chat": "POST /api/chat (JSON body: {'user_input': '...'})",
            "session": "GET /api/sessions/{session_id}",
            "docs": "GET /docs",
        },
    }


@app.get("/health")
async def health():
    return {"status": "ok", "service": "DesktopPilot AI"}


@app.get("/api/chat")
async def chat_get_info():
    """Friendly response for browser GET requests to /api/chat endpoint."""
    return {
        "message": "DesktopPilot AI Chat Endpoint",
        "method_required": "POST",
        "usage": "Send a POST request with JSON payload: {'user_input': 'Your command here'}",
        "example_payload": {
            "user_input": "Create an Excel file named scores.xlsx with columns Name, Score",
            "session_id": "optional-session-id",
        },
    }


@app.post("/api/chat", response_model=ChatResponse)
async def chat_endpoint(req: ChatRequest):
    session_id = req.session_id or str(uuid.uuid4())
    user_messages = req.messages or []

    state: AgentState = {
        "messages": user_messages + [{"role": "user", "content": req.user_input}],
        "session_id": session_id,
        "user_input": req.user_input,
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

    try:
        result: AgentState = await graph.ainvoke(state)
        return ChatResponse(
            session_id=session_id,
            backend=result.get("model_backend", "unknown"),
            task_type=result.get("task_type"),
            requirements_complete=result.get("requirements_complete", False),
            clarifying_question=result.get("clarifying_question"),
            plan=result.get("plan"),
            final_response=result.get("final_response"),
            execution_trace=result.get("execution_trace", []),
            error=result.get("error"),
        )
    except Exception as exc:
        logger.exception("Error executing graph in FastAPI chat endpoint: %s", exc)
        raise HTTPException(status_code=500, detail=str(exc))


@app.get("/api/sessions/{session_id}")
async def get_session_endpoint(session_id: str):
    memory = await get_session_memory(session_id)
    return {"session_id": session_id, "memory_context": memory}

"""
schemas.py — Shared Pydantic data schemas for API requests and responses.
"""
from __future__ import annotations

from typing import Any, Optional
from pydantic import BaseModel, ConfigDict


class ChatRequest(BaseModel):
    """Incoming user chat request payload."""
    message: Optional[str] = None
    user_input: Optional[str] = None
    session_id: Optional[str] = None
    task_id: Optional[str] = None
    model_backend: Optional[str] = None
    backend: Optional[str] = None
    experimental_fault_injection: Optional[dict[str, Any]] = None


class ChatResponse(BaseModel):
    """Outgoing chat response payload."""
    model_config = ConfigDict(protected_namespaces=())

    session_id: str
    task_id: Optional[str] = None
    response: Optional[str] = None
    clarifying_question: Optional[str] = None
    execution_trace: list[dict[str, Any]] = []
    generated_outputs: list[dict[str, Any]] = []
    model_backend: str = "unknown"
    task_type: Optional[str] = None
    plan: Optional[list[dict[str, Any]]] = None
    previous_plan: Optional[list[dict[str, Any]]] = None
    validation_result: Optional[dict[str, Any]] = None
    replan_count: int = 0
    replan_required: bool = False
    error: Optional[str] = None


class OllamaHealthResponse(BaseModel):
    """Ollama health check response payload."""
    available: bool
    base_url: str
    models: list[str] = []
    active_model: Optional[str] = None
    error: Optional[str] = None

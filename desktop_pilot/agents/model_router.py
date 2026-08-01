"""
model_router.py — Connectivity check and LLM backend selection.

This is a utility node, not a reasoning agent.
It pings the Groq endpoint, selects the active backend (Groq or Ollama),
and annotates state with available capabilities for this run.
"""
from __future__ import annotations

import logging
from typing import TYPE_CHECKING

import httpx

from config import config
from graph.state import AgentState, Capabilities

if TYPE_CHECKING:
    pass

logger = logging.getLogger(__name__)


# ── Connectivity checks ────────────────────────────────────────────────────────

async def _check_groq() -> bool:
    """Ping the Groq models endpoint. Returns True if reachable and key is valid."""
    if not config.groq_api_key:
        logger.warning("GROQ_API_KEY is not set — offline mode forced.")
        return False
    try:
        async with httpx.AsyncClient(timeout=config.groq_ping_timeout) as client:
            resp = await client.get(
                "https://api.groq.com/openai/v1/models",
                headers={"Authorization": f"Bearer {config.groq_api_key}"},
            )
            return resp.status_code == 200
    except Exception as exc:
        logger.debug("Groq ping failed: %s", exc)
        return False


async def _check_ollama() -> bool:
    """Ping the local Ollama server. Returns True if running."""
    try:
        async with httpx.AsyncClient(timeout=config.ollama_ping_timeout) as client:
            resp = await client.get(f"{config.ollama_host}/api/tags")
            return resp.status_code == 200
    except Exception as exc:
        logger.debug("Ollama ping failed: %s", exc)
        return False


# ── Capability matrix ──────────────────────────────────────────────────────────

def _build_capabilities(backend: str) -> Capabilities:
    """
    Returns capability flags based on the selected backend.

    Offline mode (Ollama) degrades gracefully:
    - browser_automation disabled  — Playwright requires network and a capable model
    - desktop_automation enabled   — file ops are fully local
    - document_generation enabled  — python-docx / openpyxl / python-pptx are local
    - vision_agent disabled        — stub only in Phase 1 regardless
    """
    if backend == "groq":
        return Capabilities(
            browser_automation=True,
            desktop_automation=True,
            document_generation=True,
            vision_agent=False,  # stub in Phase 1 regardless of backend
        )
    else:  # ollama / offline
        return Capabilities(
            browser_automation=False,
            desktop_automation=True,
            document_generation=True,
            vision_agent=False,
        )


# ── LLM factory ───────────────────────────────────────────────────────────────

def get_llm(backend: str):
    """Return the appropriate LangChain chat model for the given backend string."""
    if backend == "groq":
        from langchain_groq import ChatGroq
        return ChatGroq(
            model=config.groq_model,
            api_key=config.groq_api_key,
            temperature=0,
        )
    else:
        try:
            from langchain_ollama import ChatOllama
        except ImportError:
            from langchain_community.chat_models import ChatOllama  # type: ignore[no-redef]
        return ChatOllama(
            model=config.ollama_model,
            base_url=config.ollama_host,
        )


# ── LangGraph node ─────────────────────────────────────────────────────────────

async def model_router_node(state: AgentState) -> AgentState:
    """
    LangGraph node: selects the active LLM backend and sets capability flags.

    Decision order:
    1. Try Groq (primary). If reachable → use Groq, set full capabilities.
    2. Try Ollama (fallback). If reachable → use Ollama, set degraded capabilities.
    3. Neither reachable → mark error, no capabilities available.
    """
    groq_ok = await _check_groq()

    if groq_ok:
        backend = "groq"
        capabilities = _build_capabilities("groq")
        trace_msg = f"Online (Groq / {config.groq_model})"
        logger.info("ModelRouter → groq (%s)", config.groq_model)
    else:
        ollama_ok = await _check_ollama()
        if ollama_ok:
            backend = "ollama"
            capabilities = _build_capabilities("ollama")
            trace_msg = (
                f"Offline (Ollama / {config.ollama_model}) — "
                "browser_automation disabled"
            )
            logger.info("ModelRouter → ollama (%s)", config.ollama_model)
        else:
            backend = "none"
            capabilities = Capabilities(
                browser_automation=False,
                desktop_automation=False,
                document_generation=False,
                vision_agent=False,
            )
            trace_msg = "No LLM backend reachable. Check GROQ_API_KEY or start Ollama."
            logger.error("ModelRouter → no backend available")

    return {
        **state,
        "model_backend": backend,
        "capabilities": capabilities,
        "execution_trace": state["execution_trace"] + [
            {
                "agent": "model_router",
                "status": "success" if backend != "none" else "error",
                "message": trace_msg,
            }
        ],
        "error": None if backend != "none" else trace_msg,
    }

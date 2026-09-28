"""
model_router.py — Connectivity check and LLM backend selection.
Features:
- Dedicated Ollama health check & model tags inspection.
- Explicit user backend routing (Groq vs Ollama) with ZERO silent fallback.
- Helpful diagnostics if Ollama or model is unavailable.
- Clean ChatOllama & ChatGroq instantiations.
"""
from __future__ import annotations

import logging
from typing import Any
import httpx

from config import config
from graph.state import AgentState, Capabilities

logger = logging.getLogger(__name__)


async def _check_groq() -> bool:
    """Check if Groq endpoint is reachable and API key is valid."""
    key = config.groq_api_key.strip()
    if not key:
        return False
    try:
        async with httpx.AsyncClient(timeout=config.groq_ping_timeout) as client:
            resp = await client.get(
                "https://api.groq.com/openai/v1/models",
                headers={"Authorization": f"Bearer {key}"},
            )
            return resp.status_code == 200
    except Exception as exc:
        logger.debug("Groq ping check failed: %s", exc)
        return False


async def check_ollama_status() -> dict[str, Any]:
    """
    Check Ollama availability, list installed models, and verify active model.
    Returns status dict with 'available', 'base_url', 'models', 'active_model', 'error'.
    """
    base_url = (getattr(config, "ollama_base_url", None) or getattr(config, "ollama_host", None) or "http://127.0.0.1:11434").rstrip("/")
    configured_model = getattr(config, "ollama_model", "llama3:latest")

    try:
        async with httpx.AsyncClient(timeout=config.ollama_ping_timeout) as client:
            resp = await client.get(f"{base_url}/api/tags")
            if resp.status_code != 200:
                return {
                    "available": False,
                    "base_url": base_url,
                    "models": [],
                    "active_model": configured_model,
                    "error": f"Ollama HTTP check returned status {resp.status_code}",
                }

            data = resp.json()
            models_list = [m.get("name") for m in data.get("models", []) if m.get("name")]

            if not models_list:
                return {
                    "available": False,
                    "base_url": base_url,
                    "models": [],
                    "active_model": configured_model,
                    "error": "Ollama is running, but no models are installed. Run 'ollama pull llama3' in your terminal.",
                }

            # Check if configured model is installed (or prefix match without tag)
            clean_name = configured_model.split(":")[0]
            matched_model = None
            for m in models_list:
                if m == configured_model:
                    matched_model = m
                    break
                if m.split(":")[0] == clean_name:
                    matched_model = m
                    break

            if not matched_model:
                matched_model = models_list[0]

            return {
                "available": True,
                "base_url": base_url,
                "models": models_list,
                "active_model": matched_model,
                "error": None,
            }

    except Exception as exc:
        err_str = str(exc)
        if "ConnectError" in err_str or "connection refused" in err_str.lower():
            friendly_err = f"Ollama is not running or unreachable at {base_url}. Start Ollama and verify port 11434 is listening."
        elif "Timeout" in err_str:
            friendly_err = f"Connection to Ollama at {base_url} timed out."
        else:
            friendly_err = f"Could not connect to Ollama at {base_url}: {err_str}"

        return {
            "available": False,
            "base_url": base_url,
            "models": [],
            "active_model": configured_model,
            "error": friendly_err,
        }


async def _check_ollama() -> bool:
    """Convenience bool check for Ollama connectivity."""
    status = await check_ollama_status()
    return status.get("available", False)


def _build_capabilities(backend: str) -> Capabilities:
    """Return system capabilities for active backend."""
    return Capabilities(
        browser_automation=True,
        desktop_automation=True,
        document_generation=True,
        vision_agent=False,
    )


def get_llm(backend: str):
    """
    Return LangChain chat model for active backend.
    STRICT: Never silently falls back from Ollama to Groq.
    """
    if backend == "groq":
        from langchain_groq import ChatGroq
        return ChatGroq(
            model=config.groq_model,
            api_key=config.groq_api_key,
            temperature=0,
            max_retries=5,
        )
    elif backend == "ollama":
        from langchain_ollama import ChatOllama
        base_url = (getattr(config, "ollama_base_url", None) or getattr(config, "ollama_host", None) or "http://127.0.0.1:11434").rstrip("/")
        return ChatOllama(
            model=config.ollama_model,
            base_url=base_url,
            temperature=0,
        )
    else:
        raise RuntimeError(f"Unknown or unavailable model backend: '{backend}'.")


async def model_router_node(state: AgentState) -> dict[str, Any]:
    """
    LangGraph node for model routing.
    Honors the user-selected backend (Groq vs Ollama).
    Does NOT silently fall back to Groq if Ollama is selected!
    """
    requested = (state.get("model_backend") or "").lower().strip()

    # 1. User explicitly selected Ollama / Local
    if requested in ("ollama", "local"):
        status = await check_ollama_status()
        if not status["available"]:
            err_msg = f"Local Ollama is unavailable: {status['error']}"
            logger.warning("Local Ollama requested but unavailable: %s", status['error'])
            return {
                "model_backend": "none",
                "capabilities": Capabilities(
                    browser_automation=False,
                    desktop_automation=False,
                    document_generation=False,
                    vision_agent=False,
                ),
                "final_response": err_msg,
                "error": err_msg,
                "execution_trace": [
                    {
                        "agent": "model_router",
                        "status": "error",
                        "message": err_msg,
                    }
                ],
            }

        # Valid Ollama
        backend = "ollama"
        capabilities = _build_capabilities("ollama")
        trace_msg = f"Connected to Local Ollama ({status['active_model']} at {status['base_url']})"
        logger.info("ModelRouter -> Local Ollama (%s)", status['active_model'])
        return {
            "model_backend": backend,
            "capabilities": capabilities,
            "execution_trace": [
                {
                    "agent": "model_router",
                    "status": "success",
                    "message": trace_msg,
                }
            ],
            "error": None,
        }

    # 2. User explicitly selected Groq / Cloud
    elif requested in ("groq", "cloud"):
        groq_ok = await _check_groq()
        if not groq_ok:
            err_msg = "Cloud Groq is unavailable: Invalid API key or service unreachable. Check GROQ_API_KEY in .env."
            logger.warning("Cloud Groq requested but unavailable")
            return {
                "model_backend": "none",
                "capabilities": Capabilities(
                    browser_automation=False,
                    desktop_automation=False,
                    document_generation=False,
                    vision_agent=False,
                ),
                "final_response": err_msg,
                "error": err_msg,
                "execution_trace": [
                    {
                        "agent": "model_router",
                        "status": "error",
                        "message": err_msg,
                    }
                ],
            }

        backend = "groq"
        capabilities = _build_capabilities("groq")
        trace_msg = f"Connected to Groq ({config.groq_model})"
        logger.info("ModelRouter -> Groq (%s)", config.groq_model)
        return {
            "model_backend": backend,
            "capabilities": capabilities,
            "execution_trace": [
                {
                    "agent": "model_router",
                    "status": "success",
                    "message": trace_msg,
                }
            ],
            "error": None,
        }

    # 3. Default auto-detection (when no backend was specified)
    groq_ok = await _check_groq()
    if groq_ok:
        backend = "groq"
        capabilities = _build_capabilities("groq")
        trace_msg = f"Connected to Groq ({config.groq_model})"
    else:
        status = await check_ollama_status()
        if status["available"]:
            backend = "ollama"
            capabilities = _build_capabilities("ollama")
            trace_msg = f"Connected to Local Ollama ({status['active_model']})"
        else:
            backend = "none"
            capabilities = Capabilities(
                browser_automation=False,
                desktop_automation=False,
                document_generation=False,
                vision_agent=False,
            )
            trace_msg = "No LLM backend available. Check GROQ_API_KEY or start Ollama."

    return {
        "model_backend": backend,
        "capabilities": capabilities,
        "execution_trace": [
            {
                "agent": "model_router",
                "status": "success" if backend != "none" else "error",
                "message": trace_msg,
            }
        ],
        "error": None if backend != "none" else trace_msg,
    }

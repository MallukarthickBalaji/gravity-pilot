"""
session.py — Session state and persistence management.
Re-exports database session operations with clean interfaces.
"""
from __future__ import annotations

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

__all__ = [
    "delete_session",
    "ensure_session",
    "get_all_messages",
    "get_all_sessions",
    "get_recent_messages",
    "get_session_outputs",
    "get_session_task_state",
    "get_task_history",
    "reset_session_task_state",
    "save_message",
    "update_session_task_state",
]

"""
db.py — Persistent SQLite database storage for sessions and execution logs using SQLAlchemy & aiosqlite.
"""
from __future__ import annotations

import json
import logging
import os
from datetime import datetime
from typing import Any, Optional

from sqlalchemy import Column, DateTime, Integer, String, Text, create_engine
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import declarative_base

logger = logging.getLogger(__name__)

DB_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "desktop_pilot.db"))
DATABASE_URL = f"sqlite+aiosqlite:///{DB_PATH}"

Base = declarative_base()


class SessionRecord(Base):
    __tablename__ = "sessions"

    id = Column(Integer, primary_key=True, autoincrement=True)
    session_id = Column(String(64), unique=True, index=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    messages_json = Column(Text, default="[]")
    memory_summary = Column(Text, nullable=True)


class ExecutionLogRecord(Base):
    __tablename__ = "execution_logs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    session_id = Column(String(64), index=True, nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow)
    agent = Column(String(64), nullable=False)
    status = Column(String(32), nullable=False)
    message = Column(Text, nullable=False)


# Async Engine & Sessionmaker
engine = create_async_engine(DATABASE_URL, echo=False)
async_session_factory = async_sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)


async def init_db():
    """Create all tables if they do not exist."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def save_session_state(session_id: str, messages: list[dict[str, str]], memory_summary: Optional[str] = None):
    """Save or update session messages in SQLite."""
    await init_db()
    async with async_session_factory() as session:
        from sqlalchemy import select
        stmt = select(SessionRecord).where(SessionRecord.session_id == session_id)
        res = await session.execute(stmt)
        record = res.scalar_one_or_none()

        messages_str = json.dumps(messages)

        if record:
            record.messages_json = messages_str
            if memory_summary:
                record.memory_summary = memory_summary
            record.updated_at = datetime.utcnow()
        else:
            record = SessionRecord(
                session_id=session_id,
                messages_json=messages_str,
                memory_summary=memory_summary,
            )
            session.add(record)

        await session.commit()


async def get_session_memory(session_id: str) -> Optional[str]:
    """Retrieve session memory summary or prior context from SQLite."""
    await init_db()
    async with async_session_factory() as session:
        from sqlalchemy import select
        stmt = select(SessionRecord).where(SessionRecord.session_id == session_id)
        res = await session.execute(stmt)
        record = res.scalar_one_or_none()
        if record:
            return record.memory_summary
        return None


async def log_execution(session_id: str, agent: str, status: str, message: str):
    """Log execution trace entry to SQLite."""
    await init_db()
    async with async_session_factory() as session:
        record = ExecutionLogRecord(
            session_id=session_id,
            agent=agent,
            status=status,
            message=message,
        )
        session.add(record)
        await session.commit()

# DesktopPilot AI

A hierarchical multi-agent desktop automation system. Users give a natural-language instruction; the system clarifies, plans, executes (document generation, browser automation, desktop/file ops), validates, and persists memory across sessions.

## Run & Operate

### Python (DesktopPilot)
- `cd desktop_pilot && python main.py` — interactive CLI (Phase 1+)
- `cd desktop_pilot && python test_scaffold.py` — non-interactive smoke test
- `cd desktop_pilot && uvicorn api.server:app --port 8000` — FastAPI backend (Phase 7+)
- Required env: `Groq_API_KEY` — Groq API key (set as Replit Secret)
- Optional env: `OLLAMA_HOST` (default: http://localhost:11434), `OLLAMA_MODEL`

### JS/TS workspace
- `pnpm --filter @workspace/api-server run dev` — Node API server (port 5000)
- `pnpm run typecheck` — full typecheck

## Stack

### Python project (`desktop_pilot/`)
- Python 3.11+, LangGraph (StateGraph with cyclic edges), LangChain
- FastAPI (async backend, Phase 7), PySide6 (desktop GUI, Phase 8 — run locally)
- Primary LLM: Groq `llama-3.3-70b-versatile`; Fallback: Ollama `llama3.1:8b-instruct`
- Document gen: python-docx, openpyxl, python-pptx
- Automation: PyAutoGUI (desktop), Playwright (browser)
- Memory: SQLite via SQLAlchemy

### JS/TS workspace
- pnpm workspaces, Node.js 24, TypeScript 5.9, Express 5

## Where things live

```
desktop_pilot/
├── config.py                    — env/config (pydantic-settings)
├── main.py                      — interactive CLI entry point
├── test_scaffold.py             — non-interactive smoke test
├── requirements.txt             — all deps (install with pip)
├── requirements-gui.txt         — PySide6 (local only)
├── agents/
│   ├── model_router.py          — connectivity check, backend selection
│   ├── supervisor.py            — task classification
│   ├── requirement_analyzer.py  — completeness check, clarifying questions
│   └── planning_agent.py        — ordered execution plan generation
├── graph/
│   ├── state.py                 — AgentState TypedDict (source of truth)
│   └── workflow.py              — LangGraph StateGraph + routing
└── memory/                      — SQLite memory (Phase 6)
```

## Architecture decisions

- **LangGraph StateGraph** with explicit cyclic edges: `validation_agent → planning_agent` (replan on failure) and `validation_agent → requirement_analyzer` (reask on ambiguous failure). Not a linear pipeline.
- **Graceful capability degradation**: model_router sets `Capabilities` flags; supervisor checks them and tells the user honestly when a capability is unavailable rather than failing silently mid-run.
- **Single clarifying question per turn**: requirement_analyzer asks exactly one question if info is missing, then routes to END. Next user reply restarts from supervisor with accumulated message history.
- **PySide6 runs locally only**: requires a system display; not executable in Replit's headless environment.

## Build order (phases)

| Phase | Status | What |
|---|---|---|
| 1 | ✅ Done | Scaffold + model_router + supervisor + requirement_analyzer + planning_agent |
| 2 | Next | document_agent (Word, Excel, PowerPoint) |
| 3 | — | task_coordinator + validation_agent + cyclic edges |
| 4 | — | desktop_agent + browser_agent |
| 5 | — | memory_agent + SQLite wiring |
| 6 | — | FastAPI layer |
| 7 | — | PySide6 frontend |
| 8 | — | vision_agent stub |

## Gotchas

- Run `python test_scaffold.py` from inside `desktop_pilot/` (not workspace root) — imports are relative.
- `Groq_API_KEY` secret name has capital G (set by user); pydantic-settings is case-insensitive so it resolves to `groq_api_key`.
- PySide6 and PyAutoGUI both require a display — they cannot run on Replit's headless server. Test the GUI locally.
- Playwright requires `playwright install chromium` after pip install.

## User preferences

_Populate as you build._

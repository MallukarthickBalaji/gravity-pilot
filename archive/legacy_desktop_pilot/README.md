# DesktopPilot AI

A hierarchical multi-agent desktop automation system built with LangGraph, FastAPI, and PySide6.

A user gives a natural-language instruction; the system clarifies missing details, plans a sequence of steps, executes them using specialised agents (document generation, browser automation, desktop/file operations), validates the result, and returns a verified response — with persistent memory across sessions.

---

## Setup

### 1. Prerequisites

- Python 3.11+
- pip

### 2. Install dependencies

```bash
cd desktop_pilot
pip install -r requirements.txt
```

For the GUI frontend (run **locally** — requires a system display):

```bash
pip install -r requirements-gui.txt
```

For browser automation (after pip install):

```bash
playwright install chromium
```

### 3. Configure environment

```bash
cp .env.example .env
# Edit .env and set GROQ_API_KEY (and optionally OLLAMA_HOST)
```

Or set `GROQ_API_KEY` as an environment variable / Replit Secret directly.

### 4. (Optional) Start Ollama for offline mode

```bash
ollama serve
ollama pull llama3.1:8b-instruct
```

---

## Running

### CLI test (Phase 1 — interactive)

```bash
cd desktop_pilot
python main.py
```

CLI commands: `quit` · `exit` · `trace` · `reset`

### Smoke tests (non-interactive)

```bash
cd desktop_pilot
python test_scaffold.py
```

### FastAPI backend (Phase 7+)

```bash
cd desktop_pilot
uvicorn api.server:app --host 0.0.0.0 --port 8000
```

### PySide6 desktop GUI (Phase 8+ — run locally)

```bash
cd desktop_pilot
python frontend/app.py
```

---

## Architecture

```
user input
    │
    ▼
model_router ──── connectivity check ──── Groq (online) | Ollama (offline)
    │
    ▼
supervisor ──── classify task type ──── capability check
    │
    ▼
requirement_analyzer ──── all info present? ──── NO → clarifying question → user
    │ YES
    ▼
planning_agent ──── ordered step list
    │                         (Phase 4+)
    ▼
task_coordinator
    ├── document_agent   (python-docx / openpyxl / python-pptx)
    ├── browser_agent    (Playwright)
    ├── desktop_agent    (PyAutoGUI)
    └── vision_agent     (pytesseract stub — Phase 9)
    │
    ▼
validation_agent ──── success? ──── NO → replan | reask
    │ YES
    ▼
memory_agent ──── write to SQLite
    │
    ▼
  response
```

### Cyclic edges (Phase 4)

- `validation_agent → planning_agent` on execution failure (triggers replanning)
- `validation_agent → requirement_analyzer` on ambiguous/missing-input failure
- `requirement_analyzer → supervisor` after clarification is collected

---

## Build order

| Phase | What |
|---|---|
| 1 ✅ | Scaffold + model_router + minimal graph (supervisor → req_analyzer → planner) |
| 2 | document_agent (Word, Excel, PowerPoint generation) |
| 3 | task_coordinator + validation_agent + cyclic edges |
| 4 | desktop_agent + browser_agent |
| 5 | memory_agent + SQLite wiring |
| 6 | FastAPI layer (POST /chat, GET /session/{id}/history, GET /health) |
| 7 | PySide6 frontend |
| 8 | vision_agent stub |

---

## What's tested vs. untested in Phase 1

**Tested (smoke test covers):**
- Config loading
- Graph compilation
- model_router connectivity check and backend selection
- supervisor classification
- requirement_analyzer clarification logic
- planning_agent plan generation

**Not yet wired:**
- Actual document/file/browser execution (no execution agents yet)
- Validation and cyclic replay
- SQLite memory persistence
- FastAPI endpoints
- PySide6 GUI

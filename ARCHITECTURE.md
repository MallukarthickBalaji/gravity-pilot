# DesktopPilot AI — Comprehensive Developer Architecture Map

This document explains the end-to-end flow of DesktopPilot AI (GravityPilot). It is designed to allow any developer to understand the complete execution path in minutes.

---

## 1. High-Level System Architecture

```
User (Browser / Voice)
       │
       ▼
React / Vite UI (Port 5173)
       │
       ▼  HTTP POST / SSE (/api/chat/sessions/{id}/stream)
FastAPI Backend (Port 8000)
       │
       ▼
LangGraph Multi-Agent Workflow
       │
       ├──► 1. Model Router (Groq vs Ollama selection & health check)
       ├──► 2. Supervisor (Task intent classification)
       ├──► 3. Requirement Analyzer (Completeness check / single-question loop)
       ├──► 4. Memory Agent (Load context / session persistence)
       ├──► 5. Planning Agent (Ordered PlanSteps generation / Replan revision)
       │         ▲                                                    │
       │         │ (replan_required=True & replan_count < max_replans) │
       │         └──────────────────┐                                 │
       │                            │                                 ▼
       ├──► 6. Task Coordinator ◄───┘                   (Executes ordered steps)
       │         │  (Cross-step parameter handoff: forwards created folders & outputs)
       │         │
       │         ├──► Document Agent  ──► tools.documents (Word, Excel, PPTX, Code)
       │         ├──► Desktop Agent   ──► tools.files, tools.screenshot, tools.notebook
       │         └──► Browser Agent   ──► tools.web_search (Bing/DDG/Wiki multi-fallback)
       │         │
       │         ▼
       ├──► 7. Validation Agent (Physical artifact structural checks & failure detection)
       │         │
       │         ├──► (Validation PASS or Replan Limit reached) ──► 8. Memory Agent
       │         └──► (Validation FAIL & recoverable) ──► Route back to Planning Agent
       │
       ▼  Real-time SSE event stream (data: {type: 'agent_update', ...})
React Frontend UI (Dynamic Agent Trace, Chat Bubble, File Download)
```

---

## 2. Developer Questions Answered

### Where does a user message enter?
- **Frontend**: The user types into the chat input or uses voice speech recognition in `frontend/src/App.tsx`.
- **Streaming Hook**: The `send()` function in `frontend/src/hooks/use-chat-stream.ts` sends a `POST` request to `/api/chat/sessions/{sessionId}/stream` carrying the JSON payload:
  ```json
  {
    "user_input": "...",
    "session_id": "...",
    "model_backend": "groq" | "ollama"
  }
  ```
- **Backend API**: The endpoint `chat_stream_endpoint()` in `backend/api/server.py` receives the request and starts `_stream_graph_events()`.

---

### Where is model selection handled?
- **Frontend**: Controlled by the Mode Selector toggle in `frontend/src/components/StatusBar.tsx` (`mode === "groq"` vs `mode === "ollama"`).
- **Backend Model Router**: In `backend/agents/model_router.py` within `model_router_node()`. It checks `state["model_backend"]`.
  - **Zero Silent Fallback**: If Local Ollama is requested and unavailable, it fails explicitly with `"Local Ollama is unavailable: <reason>"` rather than silently falling back to Groq.

---

### Where is Ollama handled?
- **Local Endpoint**: `http://127.0.0.1:11434` (configured in `backend/config.py` and `.env`).
- **Health Check & Detection**: `check_ollama_status()` in `backend/agents/model_router.py` queries `GET http://127.0.0.1:11434/api/tags` to list installed models and find active `llama3:latest`.
- **API Health Endpoint**: `GET /api/ollama/health` in `backend/api/server.py`.
- **LLM Instance**: `get_llm("ollama")` in `backend/agents/model_router.py` instantiates `ChatOllama(base_url=config.ollama_base_url, model=config.ollama_model, temperature=0.1)` from `langchain_ollama`.

---

### Where is Groq handled?
- **API Key & Model**: Reads `GROQ_API_KEY` and `GROQ_MODEL=openai/gpt-oss-120b` from `.env` via `backend/config.py`.
- **LLM Instance**: `get_llm("groq")` in `backend/agents/model_router.py` instantiates `ChatGroq(model_name=config.groq_model, temperature=0.1)` from `langchain_groq`.

---

### Where does LangGraph start?
- **Workflow Definition**: In `backend/graph/workflow.py` via `create_graph()`.
- **State Initialization**: Defined in `backend/state/state.py` (`AgentState`).
- **Graph Invocations**:
  - Streaming: `graph.astream(initial_state, stream_mode="updates")` in `backend/api/server.py` (`_stream_graph_events`).
  - Synchronous / Tests: `graph.ainvoke(state)` in `backend/api/server.py` and test suites.

---

### Where does Requirement Analyzer run?
- **File**: `backend/agents/requirement_analyzer.py` (`requirement_analyzer_node()`).
- **Role**:
  - Deterministically validates unambiguous tasks (e.g. "Create an attendance sheet", "Take a screenshot", "Write Python code for fibonacci").
  - For ambiguous requests lacking critical parameters (e.g., "Create a leave letter" without recipient or date), pauses execution and asks exactly **ONE** friendly clarifying question (`clarifying_question`).
  - State emits `status: "waiting_for_user"`.

---

### Where does Planner run?
- **File**: `backend/agents/planning_agent.py` (`planning_agent_node()`).
- **Role**:
  - Takes verified requirements and conversation history.
  - Produces an ordered list of `PlanStep` objects (e.g. `[{"agent": "document_agent", "action": "Create Word doc", "params": {...}}]`).
  - Uses `backend/utils/json_utils.py` (`extract_json_object`) to reliably parse structured plans even if the LLM includes conversational commentary.

---

### Where are tools executed?
Tools are cleanly separated from reasoning agents under `backend/tools/`:
- **File operations** (create, copy, move, rename, delete): `backend/tools/files.py`
- **Document generation** (Word, Excel, PowerPoint, Code): `backend/tools/documents.py`
- **Screenshot capture**: `backend/tools/screenshot.py`
- **Jupyter Notebook**: `backend/tools/notebook.py`
- **Web search & fallback hierarchy**: `backend/tools/web_search.py`

Agents (`document_agent.py`, `desktop_agent.py`, `browser_agent.py`) decide **WHAT** needs to happen based on the plan, and call tools to execute **HOW** it happens.

---

### Where is validation and replanning handled?
- **Validation Agent**: `backend/agents/validation_agent.py` (`validation_agent_node()`).
- **Physical Verification**:
  - Inspects real physical files on disk in `backend/output/`.
  - Checks file existence, non-zero byte size, and internal document schema:
    - Word (`.docx`): paragraph counts, headings, required keywords via `python-docx`.
    - Excel (`.xlsx`): sheet existence, column header matches, row population via `openpyxl`.
    - PowerPoint (`.pptx`): slide count, slide title matching via `python-pptx`.
    - Code (`.py`): syntax parseability via Python `ast.parse()`.
    - Filesystem: path presence, directory structure, correct filename.
    - Web Search: structured schema verification, rejecting raw HTML and CAPTCHAs.
- **State Transition & Replanning Trigger**:
  - If validation passes: sets `validation_status = "passed"`, `replan_required = False`.
  - If validation fails and `replan_count < max_replans`: sets `replan_required = True`, increments `replan_count`, writes diagnostic feedback into `validation_errors`, and archives the flawed plan in `previous_plan`.
  - **LangGraph Conditional Edge**: `route_after_validation` in `backend/graph/workflow.py` inspects `replan_required`. If `True`, execution loops back to `planning_agent`, which reads `validation_errors` and generates a corrected plan.
  - If `replan_count >= max_replans`: execution terminates with `validation_status = "failed"`, preventing infinite loops.

---

### Where is session state stored?
- **SQLite Database**: `backend/data/desktoppilot.db` (auto-created on first run).
- **Database Engine**: `backend/memory/database.py` using `aiosqlite`.
- **State Helpers**: `backend/state/session.py` provides clean session lifecycle methods (`ensure_session`, `save_message`, `get_all_sessions`, `get_recent_messages`, `delete_session`).

---

### Where are generated files stored?
- **Output Directory**: `backend/output/`.
- Configured centrally in `backend/config.py` via `get_output_dir()`.
- Automatically registered in the database (`task_outputs` table) and sent over SSE to the frontend as `generated_files`.

---

### Where does SSE streaming happen?
- **Backend Streaming Function**: `_stream_graph_events()` in `backend/api/server.py`.
- Emits standard Server-Sent Events (`data: {...}\n\n`):
  - `task_start`: Task initiated.
  - `agent_update`: Real-time node transition (`model_router` → `supervisor` → `requirement_analyzer` → `planning_agent` → `document_agent` → `validation_agent`).
  - `message`: Final response, clarifying question, or error.
  - `task_state`: Current lifecycle state (`analyzing`, `waiting_for_user`, `completed`, `failed`).
  - `done`: Stream terminator.

---

### Where does the React UI receive events?
- **Event Source Consumer**: `frontend/src/hooks/use-chat-stream.ts`.
- Reads the SSE text stream chunks, decodes JSON events, and updates:
  - `agents`: Active/done badges displayed in `TracePanel.tsx`.
  - `streamingMessages`: Live conversational bubbles displayed in `ChatPanel.tsx`.
  - `generatedFiles`: Clickable download links for generated files.

# DesktopPilot AI — Project Capabilities & Architecture Audit

**Evaluation Date**: 2026-09-27  
**Platform**: Windows 11 / x86_64, Python 3.11.9, Node.js v20+  
**Target Architecture**: Multi-Agent Desktop Automation Engine with LangGraph

---

## 1. Verified Implemented Agents

The backend multi-agent system is implemented under `backend/agents/`:

| Agent Name | Source File | Actual Implemented Role | Implementation Details |
|---|---|---|---|
| **Model Router** | `model_router.py` | LLM backend selection & capability mapping | Strictly evaluates requested backend (`groq` vs `ollama`). Verifies health on `http://127.0.0.1:11434/api/tags` and checks Groq API key. **Zero silent fallback**. |
| **Supervisor** | `supervisor.py` | Task classification & routing node | Classifies user intent into `document_generation`, `browser_automation`, `desktop_automation`, or `general_query` using fast heuristics and LLM classifier. Handles clarification resumption. |
| **Requirement Analyzer** | `requirement_analyzer.py` | Pre-execution completeness & clarification | Inspects input parameters. For complete/standard requests, proceeds immediately. For ambiguous or incomplete requests (e.g. leave letters without dates/recipient), halts and emits exactly one clarifying question (`clarifying_question`). |
| **Planning Agent** | `planning_agent.py` | Plan step formulation | Formulates structured sequential `PlanStep` items with target agent and execution parameters. Uses `backend/utils/json_utils.py` for reliable JSON extraction. |
| **Task Coordinator** | `task_coordinator.py` | Sequential execution dispatcher | Tracks `current_step` in state and routes control dynamically to the assigned specialized execution agent. |
| **Document Agent** | `document_agent.py` | Document creation orchestration | Orchestrates Word, Excel, PowerPoint, and Code file generation by invoking deterministic tool functions in `backend/tools/documents.py`. |
| **Desktop Agent** | `desktop_agent.py` | Filesystem & desktop automation | Orchestrates file operations (create, copy, move, rename, delete) via `backend/tools/files.py`, screenshots via `backend/tools/screenshot.py`, and notebooks via `backend/tools/notebook.py`. |
| **Browser Agent** | `browser_agent.py` | Web navigation & search orchestration | Orchestrates web searches and URL opening via `backend/tools/web_search.py`. Collects multi-provider search traces. |
| **Memory Agent** | `memory_agent.py` | Session context read/write | Loads prior turn conversation context from SQLite database before planning (`memory_agent_read_node`) and persists final execution outputs (`memory_agent_write_node`). |
| **Validation Agent** | `validation_agent.py` | Structural verification & replan cycle | Deterministically validates output files (existence, non-zero bytes, Word paragraphs, Excel rows/columns, PowerPoint slides, Python code syntax) and search result structure. Triggers replanning (`replan_reason="execution_failure"`) up to 2 attempts. |
| **Vision Agent** | `vision_agent.py` | Placeholder / Offline | Explicitly returns `skipped` ("Vision capability is offline"). |

---

## 2. Verified Implemented Tools

Deterministic execution logic is segregated under `backend/tools/`:

| Tool Module | Source File | Implemented Operations | Libraries Used |
|---|---|---|---|
| **Document Tools** | `backend/tools/documents.py` | `generate_word_doc`, `generate_excel_sheet`, `generate_powerpoint`, `generate_code_file` | `python-docx`, `openpyxl`, `python-pptx`, native I/O |
| **Filesystem Tools** | `backend/tools/files.py` | `op_create_file`, `op_create_folder`, `op_copy`, `op_move`, `op_rename`, `op_delete`, `op_launch_app` | `pathlib`, `shutil`, `os`, `subprocess`. Enforces `PROTECTED_PATHS` guards against deleting Windows system directories. |
| **Screenshot Tool** | `backend/tools/screenshot.py` | `op_screenshot` | `PIL.ImageGrab`, `ctypes` (thread desktop attachment) |
| **Notebook Tool** | `backend/tools/notebook.py` | `op_open_notebook` | Validates `.ipynb` presence and verifies `jupyter` in PATH before launching. |
| **Web Search Tools** | `backend/tools/web_search.py` | `execute_multi_provider_search`, `open_url` | Multi-tier fallback hierarchy: DuckDuckGo Lite -> DuckDuckGo HTML -> Bing -> Wikipedia. Detects and rejects bot CAPTCHAs. |

---

## 3. Verified Model Providers

| Provider | Connection Mechanism | Models Tested | Working Status |
|---|---|---|---|
| **Groq (Cloud)** | `langchain_groq.ChatGroq` | `openai/gpt-oss-120b` | **Active & Verified** (Rapid cloud generation, ~1.5s latency) |
| **Ollama (Local)** | `langchain_ollama.ChatOllama` | `llama3:latest` | **Active & Verified** (100% offline, endpoint `http://127.0.0.1:11434`) |

---

## 4. LangGraph Workflow & State Management

- **Workflow Definition**: `backend/graph/workflow.py` (`create_graph()`).
- **State Schema**: `backend/state/state.py` (`AgentState`).
- **Database Persistence**: SQLite database at `backend/data/desktoppilot.db` managed by `backend/memory/database.py` using `aiosqlite`.
- **Cyclic Replanning Loop**:
  `validation_agent` -> (if failed) -> `planning_agent` (re-plans with error diagnostic context) -> `task_coordinator` -> execution agent -> `validation_agent`.

---

## 5. Frontend & Voice Capabilities

- **Frontend Framework**: React 18, Vite 6, TypeScript, Lucide icons.
- **Real-Time Streaming**: Server-Sent Events (SSE) via `/api/chat/sessions/{id}/stream`.
- **Voice Functionality**:
  - **Actual Implementation**: In `frontend/src/App.tsx`, voice input is implemented via the browser's native **Web Speech API** (`window.SpeechRecognition` / `webkitSpeechRecognition`).
  - **Status**: Client-side speech-to-text operates in supported browsers (Chrome, Edge). Backend does not perform server-side audio transcription (Whisper is not present in backend requirements).

---

## 6. Discovered Architectural Limitations

1. **Vision Capability Offline**: `vision_agent.py` is an architectural stub that returns `skipped`.
2. **Deterministic Document Formatting**: Documents are generated using template schemas defined in `planning_agent.py` and `tools.documents`. Complex nested Excel formulas or advanced Word macro styling are not currently supported.
3. **Local Ollama Speed**: Execution latency for multi-turn local Llama 3 generation depends on host GPU/CPU hardware.
4. **Desktop Automation Sandboxing**: File operations are restricted by `is_protected_path()` to safeguard system drives, but are otherwise performed directly on the host Windows filesystem.

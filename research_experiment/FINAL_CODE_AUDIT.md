# Comprehensive Code & Architecture Audit: DesktopPilot AI (GravityPilot)

**Audit Date:** September 28, 2026  
**Auditor:** Lead Software Engineer & Research Experiment Manager  
**Scope:** Full repository audit (`backend/`, `frontend/`, `agents/`, `graph/`, `state/`, `models/`, `tools/`, `memory/`, `tests/`, `research_experiment/`)  
**Status:** Audit Complete — Actionable Improvement Plan Formulated

---

## 1. Actual System Architecture

DesktopPilot AI / GravityPilot implements an agentic desktop automation system using **LangGraph StateGraph** for backend agent orchestration, **FastAPI** for API and real-time Server-Sent Events (SSE) streaming, and **React 18 / Vite 5** with TypeScript for the desktop interface.

### End-to-End Real Execution Flow
```
User Request (Web UI or Voice Input)
       │
       ▼
HTTP POST /api/chat/sessions/{id}/stream (or /chat)
       │
       ▼
[Model Router] ──► Checks Groq API key / Ollama daemon at 127.0.0.1:11434
       │
       ▼ (if model available)
[Supervisor] ────► Classifies intent (document_generation, desktop_automation, browser_automation, general_query)
       │
       ▼
[Requirement Analyzer] ──► Evaluates parameter completeness
       │
       ├──► [Incomplete / Ambiguous] ──► Pauses execution, asks 1 clarifying question ──► [User Turn 2]
       │
       ▼ [Complete]
[Memory Agent (Read)] ──► Retrieves recent session messages & active task state from SQLite
       │
       ▼
[Planning Agent] ───────► Generates ordered PlanStep JSON list
       │
       ▼
[Task Coordinator] ◄────────────────────────────────────────┐
       │ (Dispatches current_step)                          │
       ├──► [Document Agent]  ──► tools.documents (docx, xlsx, pptx, py)
       ├──► [Desktop Agent]   ──► tools.files (create, copy, move, rename, delete)
       ├──► [Browser Agent]   ──► tools.web_search (DuckDuckGo Lite, Yahoo, Qwant)
       └──► [Vision Agent]    ──► tools.screenshot
       │                                                    │
       ▼ (Step Completed, current_step++)                   │
       └────────────────────────────────────────────────────┘
       │
       ▼ (All steps dispatched: current_step >= len(plan))
[Validation Agent] ──► Inspects physical files on disk & execution results
       │
       ├──► [Valid Result] ──► [Memory Agent (Write)] ──► Persist to DB ──► Return SUCCESS
       │
       └──► [Recoverable Failure & replan_count < max_replans]
                 │
                 ▼
            Trigger Replanning (replan_required=True)
                 │
                 ▼
            [Planning Agent] ──► Emits revised PlanStep list with failure diagnostics
                 │
                 ▼
            [Task Coordinator] ──► Dispatches revised steps from step 0
                 │
                 ▼
            [Validation Agent] ──► Validates corrected execution
```

---

## 2. Actual Agent Responsibilities

| Agent Node | Source File | Actual Implementation Responsibilities |
|:---|:---|:---|
| **`model_router`** | `backend/agents/model_router.py` | Performs live health checks for Groq Cloud API and local Ollama (`http://127.0.0.1:11434/api/tags`). Sets `capabilities` and routes to `supervisor`, or halts if requested backend is unavailable. |
| **`supervisor`** | `backend/agents/supervisor.py` | Categorizes intent into four canonical task domains. For general queries without desktop action, sets `final_response` directly. |
| **`requirement_analyzer`** | `backend/agents/requirement_analyzer.py` | Analyzes whether the request has sufficient parameters for execution. If ambiguous (e.g. leave letter without dates/recipient), emits exactly one clarifying question and sets `requirements_complete=False`. |
| **`memory_agent` (Read/Write)** | `backend/agents/memory_agent.py` | Reads context from SQLite (`desktoppilot.db`) prior to planning, and writes execution results, trace logs, and generated output metadata upon completion. |
| **`planning_agent`** | `backend/agents/planning_agent.py` | Calls LLM with structured system prompt to emit ordered `PlanStep` JSON list. Contains logic to incorporate `replan_context` when replanning is active. |
| **`task_coordinator`** | `backend/agents/task_coordinator.py` | Dispatches execution steps sequentially based on `current_step`. Advances `current_step` after each agent execution until all steps complete. |
| **`document_agent`** | `backend/agents/document_agent.py` | Dispatches document tasks to deterministic Python tools (`generate_word_doc`, `generate_excel_sheet`, `generate_powerpoint`, `generate_code_file`). |
| **`desktop_agent`** | `backend/agents/desktop_agent.py` | Dispatches file and directory operations (`create_file`, `create_folder`, `copy`, `move`, `rename`, `delete`) to `tools.files`, screenshots to `tools.screenshot`, and notebooks to `tools.notebook`. Enforces `PROTECTED_PATHS` system safety. |
| **`browser_agent`** | `backend/agents/browser_agent.py` | Dispatches web searches through `tools.web_search` with CAPTCHA/bot challenge filtering and multi-engine failover (DuckDuckGo Lite, Yahoo, Qwant). |
| **`vision_agent`** | `backend/agents/vision_agent.py` | Verification node for UI screenshot inspection (supports future multimodal extensions). |
| **`validation_agent`** | `backend/agents/validation_agent.py` | Inspects execution outcomes and physical filesystem artifacts (`python-docx`, `openpyxl`, `python-pptx`, `Path.exists()`). If invalid, sets `replan_reason` and increments `replan_count`. |

---

## 3. Actual Tool Contracts & Deterministic Execution

All physical file and filesystem mutations are strictly handled by deterministic Python libraries rather than LLM text fabrication:

1. **Word Documents (`tools.documents.generate_word_doc`):**
   - Uses `python-docx` to create `.docx` files with centered title, level-1 headings, and paragraphs.
   - Saves to `backend/output/` by default.
2. **Excel Workbooks (`tools.documents.generate_excel_sheet`):**
   - Uses `openpyxl` to create `.xlsx` files with colored header cells (`#1F4E79`), bold white text, data rows, and auto-adjusted column widths.
3. **PowerPoint Presentations (`tools.documents.generate_powerpoint`):**
   - Uses `python-pptx` with standard title and content slide layouts, bulleted text frames, and subtitle configuration.
4. **Code / Script Files (`tools.documents.generate_code_file`):**
   - Writes raw UTF-8 scripts (`.py`, `.sh`, `.json`, etc.) to disk.
5. **Filesystem Operations (`tools.files`):**
   - Uses native `pathlib.Path`, `os`, and `shutil` with `resolve_desktop_path()` resolving `Desktop`, `Downloads`, `Documents`, etc.
   - Enforces `PROTECTED_PATHS` blocking operations targeting `C:\`, `C:\Windows`, `C:\Windows\System32`, `C:\Program Files`, or user home root.
6. **Web Search (`tools.web_search`):**
   - Headless HTTP queries via `urllib.request` / `httpx` to DuckDuckGo Lite, Yahoo, and Qwant.
   - Evaluates response text through `detect_bot_challenge()` to reject CAPTCHAs and bot challenge HTML pages.

---

## 4. Actual State Flow & LangGraph Edges

Defined in `backend/graph/workflow.py`:

```python
# Edges:
START -> model_router
model_router --(if available)--> supervisor
supervisor --(if not answered)--> requirement_analyzer
requirement_analyzer --(if complete)--> memory_agent_read
requirement_analyzer --(if incomplete)--> memory_agent_write -> END
memory_agent_read -> planning_agent
planning_agent --(if plan exists)--> task_coordinator
planning_agent --(if no plan)--> END
task_coordinator --(dispatches step)--> [document_agent | desktop_agent | browser_agent | vision_agent]
[document_agent | desktop_agent | browser_agent | vision_agent] -> task_coordinator
task_coordinator --(all steps done)--> validation_agent
validation_agent --(valid)--> memory_agent_write -> END
validation_agent --(replan_reason == 'execution_failure')--> planning_agent
validation_agent --(replan_reason == 'missing_info')--> requirement_analyzer
```

---

## 5. Root Cause Analysis: Why Replanning Events Were 0 in Previous Benchmark

The previous experimental report observed: `Replanning events = 0`. An exhaustive inspection of the code revealed three specific architectural reasons:

1. **Superficial Single-Step Validation:**
   `validation_agent_node` only inspected `state["last_execution_result"]` (the single most recent step). For single-step tasks (DT001–DT040), the deterministic tool (`python-docx`, `openpyxl`, `python-pptx`, `os.mkdir`) successfully executed on attempt 1 and created the file on disk. `_validate_document` verified that the file had paragraphs or rows and marked it `passed = True`. The validator never cross-checked whether secondary user requirements (e.g. 5 specific headings vs 4) were satisfied.
2. **Workflow Parameter Decoupling Bypassed Validation:**
   In multi-step workflows (DT041–DT050), Step 1 created a directory (e.g., `output/Client_Alpha`), but Step 2 (create Word doc) ran in the default `output/` directory because `task_coordinator` did not forward Step 1's output folder to Step 2's parameters. However, because Step 2 *did* create a valid Word document in `output/`, `last_execution_result` had `success: True`. `validation_agent` only inspected Step 2, confirmed the Word doc existed, and declared `passed = True`! The fact that the document was in the wrong folder was never detected by `validation_agent` because it didn't inspect the overall plan requirements or intermediate artifacts.
3. **Empty / Failed Plans Routed to `__end__`:**
   In `workflow.py`, `route_after_planning_agent` contained:
   ```python
   plan = state.get("plan")
   if not plan:
       return "__end__"
   ```
   If the planning agent failed to parse JSON on turn 1 (e.g., DT043, DT044), it routed straight to `END`, completely bypassing the validation agent and replanning loop.

---

## 6. Frontend / Backend Communication & SSE Flow

1. **Chat Request:** React UI (`frontend/src/hooks/use-chat-stream.ts`) initiates `POST /api/chat/sessions/{sessionId}/stream` with `user_input` and `model_backend`.
2. **Server SSE Generator:** `_stream_graph_events()` in `backend/api/server.py` iterates over `graph.astream(initial_state, stream_mode="updates")`.
3. **SSE Event Protocol:**
   - `task_start`: Emitted with `task_id` and initial status.
   - `agent_update`: Emitted after each node execution with `agent`, `status` (`active`, `done`, `failed`, `retrying`), and `detail` message.
   - `message`: Emitted with agent role, name, color, kind (`normal`, `clarification`, `error`), text response, and `generated_files`.
   - `task_state`: Emitted with updated session status (`analyzing`, `waiting_for_user`, `completed`, `failed`).
   - `done`: Signals end of SSE stream.
4. **Replanning UI Visualization:** When `validation_agent` emits `replan_reason == 'execution_failure'`, the SSE stream sends `agent_update` with `status: "failed"` for `validation_agent` and `status: "retrying"` for `planning_agent`. The frontend `TracePanel.tsx` visualizes this with a curved SVG arc connecting the validator back to the planner.

---

## 7. Known Technical Weaknesses & Deficiencies

| Component | Technical Weakness | Impact |
|:---|:---|:---|
| **State Schema** | `state.py` lacks explicit fields for `replan_required`, `validation_errors`, `validation_status`, `max_replans`, `current_plan`, `previous_plan`, `execution_results` (accumulated list of all steps), `artifact_paths`, and `requirements`. | Multi-step context is lost; replanning cannot compare new vs old plans. |
| **State Accumulation** | `execution_trace` in `state.py` is overwritten by each node rather than preserved across multi-agent cycles. | Multi-step and replanning execution traces get truncated in the final output. |
| **Task Coordinator** | Steps are dispatched in strict isolation without parameter propagation. If Step 1 creates folder `X`, Step 2 does not receive `X` as its working directory. | Composite workflows fail to nest artifacts inside created folders (F14 failure mode). |
| **Validation Agent** | Only inspects `last_execution_result` instead of validating all artifacts against the task requirements. | Cannot detect missing intermediate steps or missing required columns/sections. |
| **Planning Agent** | When replanning, prompt context was brief and did not include structured previous plan vs error comparison. | Replanning could repeat the same mistake. |
| **Benchmark Runner** | Trajectory logging relied on string pattern matching in trace messages to detect replanning. | Brittleness in recording replanning events. |

---

## 8. Proposed Architectural Improvements

1. **State Schema Refactoring (`backend/state/state.py`):**
   - Add explicit fields: `validation_status`, `validation_errors`, `replan_required`, `replan_count`, `max_replans`, `current_plan`, `previous_plan`, `execution_results`, `artifact_paths`, `requirements`, `satisfied_requirements`, `unsatisfied_requirements`, `failure_reason`, `failure_category`.
   - Implement trace and execution result preservation so history across turns and replans is never lost.
2. **Cross-Step Parameter Propagation in Task Coordinator (`backend/agents/task_coordinator.py`):**
   - When Step $N+1$ executes, inspect previous results in `execution_results`.
   - If a previous step created a directory, automatically supply that directory path to subsequent file/document generation steps.
3. **Comprehensive Multi-Step Validation (`backend/agents/validation_agent.py`):**
   - Validate ALL artifacts produced across all plan steps.
   - For Word: inspect paragraph count, headings, and specific required section titles.
   - For Excel: inspect row count, column count, and required column headers.
   - For PowerPoint: inspect slide count and slide titles.
   - For File Operations: inspect both source and destination existence and placement.
   - If an error is detected and `replan_count < max_replans`, set `replan_required = True` and transition to `planning_agent`.
4. **Diagnostic Replanning in Planning Agent (`backend/agents/planning_agent.py`):**
   - Provide the planner with `previous_plan`, `validation_errors`, and explicit instructions on what needs to be fixed.
   - Reset `current_step = 0` to execute the revised plan from start to finish.
5. **Controlled Fault-Injection Test Scenarios in Research Harness:**
   - Implement Scenarios A–E to test genuine replanning and recovery under controlled conditions without modifying production behavior.
6. **Dedicated Replanning Test Suite (`backend/tests/test_replanning.py`):**
   - Implement `test_validation_to_replanning_transition()`, `test_replanning_generates_new_plan()`, `test_replanned_execution()`, `test_replanning_recovery()`, `test_max_replanning_limit()`.

# Experimental Research Report: Evaluating a Requirement-Aware Multi-Agent Architecture for Long-Horizon Desktop Productivity Tasks

**Project:** DesktopPilot AI / GravityPilot  
**Author / Experimental Engineer:** DeepMind Agentic Pair Programmer  
**Date of Evaluation:** September 28, 2026  
**System Architecture:** LangGraph StateGraph + FastAPI Backend + React/Vite Desktop Client  
**Model Provider:** Groq Cloud API (`openai/gpt-oss-120b`) / Local Fallback (`llama3:latest` on Ollama)  
**Execution Environment:** Windows 11 x86_64, Python 3.11, LangGraph 0.2+, FastAPI 0.115+  

---

## 1. Research Objective

The primary objective of this empirical study is to evaluate whether a requirement-aware, multi-agent architecture incorporating structured planning, specialized deterministic tool execution, physical artifact validation, and cyclic self-correction improves the reliability, accuracy, and requirement satisfaction of desktop productivity tasks across diverse domains (documents, spreadsheets, presentations, filesystem operations, and long-horizon composite workflows).

---

## 2. Research Questions

This experimental evaluation investigates six core research questions:

- **RQ1 (Multi-Agent Orchestration):** How does physical desktop task execution under full multi-agent orchestration (Condition E, N = 50) compare descriptively to a zero-tool direct LLM baseline (Condition A, N = 5)? (Note: Condition A used N = 5 while Condition E used N = 50; the comparison is descriptive, not a controlled matched 50-task comparison, and no causal improvement claim is made.)
- **RQ2 (Requirement-Aware Planning):** Does front-loading requirement completeness analysis and interactive clarification prevent downstream execution failures on ambiguous or under-specified requests?
- **RQ3 (Physical Output Validation):** Does independent programmatic inspection of generated artifacts (via `python-docx`, `openpyxl`, `python-pptx`, and `ast.parse`) reveal discrepancies between file creation and multi-requirement task completion?
- **RQ4 (Self-Correction & Replanning):** Does the implemented cyclic replanning feedback loop trigger and recover from execution failures encountered during the benchmark?
- **RQ5 (Task Complexity Scaling):** How does task success rate scale across easy, medium, and hard multi-step workflows with sequential dependencies?
- **RQ6 (Dominant Failure Modes):** What failure categories dominate across desktop automation workflows under the IEEE F1–F14 taxonomy?

---

## 3. System Under Evaluation

The evaluated system, **DesktopPilot AI / GravityPilot**, implements an agentic architecture orchestrated via LangGraph. The system enforces strict separation between stochastic reasoning nodes and deterministic execution tools:

```
[User Input]
     │
     ▼
[Model Router] ──(Detects Groq / Ollama / Fallbacks)
     │
     ▼
[Supervisor] ──(Categorizes Task Domain & Intent)
     │
     ▼
[Requirement Analyzer] ◄───────────────┐ (Missing Info Loop)
     │                                 │
     ├──[Incomplete]──► [Clarification Prompt] ──► [User Turn 2]
     │
     ▼ [Complete]
[Memory Agent (Read)]
     │
     ▼
[Planning Agent] ◄─────────────────────┐ (Execution Failure Loop)
     │                                 │
     ▼                                 │
[Task Coordinator] ──► [Specialized Execution Agents]
                             ├── Document Agent (docx, xlsx, pptx, py)
                             ├── Desktop Agent (create, copy, move, rename, delete)
                             ├── Browser Agent (web search, open_url)
                             └── Vision Agent (screenshot verification)
                                       │
                                       ▼
                             [Validation Agent] ──(Physical Disk Inspection)
                                       │
                                       ├──[Pass]──► [Memory Write] ──► [Completed]
                                       └──[Fail]──► Trigger Replanning Loop
```

### 3.1 Implemented Components Audit
1. **Model Router (`agents.model_router`):** Real-time connectivity health check for Groq cloud API and local Ollama daemon; dynamic fallback routing.
2. **Supervisor (`agents.supervisor`):** Intent classification routing user requests into `document_generation`, `desktop_automation`, `browser_automation`, or `general_query`.
3. **Requirement Analyzer (`agents.requirement_analyzer`):** Evaluates requirement completeness; prompts exactly one targeted clarifying question if essential parameters are absent.
4. **Planning Agent (`agents.planning_agent`):** Emits ordered JSON execution plans assigning atomic steps exclusively to execution agents. Supports failure diagnostic replanning.
5. **Task Coordinator (`agents.task_coordinator`):** Step dispatcher coordinating sequential execution and tracking current step index.
6. **Document Agent (`agents.document_agent`):** Dispatches to `tools.documents` (`generate_word_doc`, `generate_excel_sheet`, `generate_powerpoint`, `generate_code_file`).
7. **Desktop Agent (`agents.desktop_agent`):** Dispatches to `tools.files` (`op_create_file`, `op_create_folder`, `op_copy`, `op_move`, `op_rename`, `op_delete`), `tools.screenshot`, and `tools.notebook`.
8. **Browser Agent (`agents.browser_agent`):** Multi-provider web search hierarchy (DuckDuckGo, Yahoo, Qwant) with automated bot challenge/CAPTCHA filtering.
9. **Validation Agent (`agents.validation_agent`):** Programmatic verification opening files on disk, counting paragraphs/tables in docx, inspecting worksheets/rows in xlsx, slides in pptx, and syntax compiling `.py` files. Triggers replanning if validation fails.
10. **Memory & State (`memory.database`, `state.state`):** SQLite session persistence and message history tracking.

---

## 4. Benchmark Dataset Composition

The benchmark suite (`research_experiment/benchmark/benchmark_tasks.json`) consists of **exactly 50 tasks** balanced across 5 domain categories and 3 difficulty tiers:

| Category | Easy | Medium | Hard | Total | Benchmark Task IDs |
|:---|:---:|:---:|:---:|:---:|:---|
| **Documents** | 3 | 4 | 3 | **10** | DT001 – DT010 |
| **Spreadsheets** | 4 | 4 | 2 | **10** | DT011 – DT020 |
| **Presentations** | 4 | 4 | 2 | **10** | DT021 – DT030 |
| **File Operations** | 4 | 4 | 2 | **10** | DT031 – DT040 |
| **Workflows** | 0 | 4 | 6 | **10** | DT041 – DT050 |
| **Total** | **15** | **20** | **15** | **50** | **DT001 – DT050** |

- **Ambiguous Tasks:** Exactly 5 tasks (DT005, DT015, DT025, DT035, DT045) intentionally omit critical scope to evaluate Requirement Analyzer clarification.
- **Granular Requirements:** 217 atomic, measurable requirements defined across the 50 tasks (mean = 4.34 requirements per task).

---

## 5. Experimental Conditions

The benchmark was structured to evaluate five conditions:

- **Condition A (Direct LLM Baseline):** Zero-tool direct prompt baseline evaluated on N = 5 representative tasks (DT001, DT011, DT021, DT031, DT041). The LLM returned text/markdown in all 5 tasks, but physical files created on disk = 0 (0.0% physical TSR).
- **Condition B (Requirement Analysis OFF):** Requirement Analyzer bypassed on all 5 ambiguous tasks (DT005, DT015, DT025, DT035, DT045). Measured whether the system satisfied requirements without clarification (0.0% success rate without clarification).
- **Condition C (Validation OFF):** Ablation removing internal artifact verification. *Marked NOT MEASURED due to external provider daily token quota limit.*
- **Condition D (Replanning OFF):** Ablation disabling replanning loop (`MAX_REPLAN_ATTEMPTS = 0`). *Marked NOT MEASURED due to external provider daily token quota limit.*
- **Condition E (Full DesktopPilot):** Complete system with all agents, tools, validation, and replanning evaluated across all N = 50 benchmark tasks.

---

## 6. Formal Metrics Definitions

1. **Task Success Rate (TSR %):**
   $$\text{TSR} = \frac{N_{\text{success}}}{N_{\text{total}}} \times 100$$
   A task is classified as `success` strictly if 100% of its atomic requirements are satisfied and all physical disk artifacts pass programmatic inspection.
2. **Requirement Satisfaction Rate (RSR %):**
   $$\text{RSR} = \frac{\sum \text{Satisfied Requirements}}{\sum \text{Total Requirements}} \times 100$$
3. **Tool Selection Accuracy (TSA %):**
   $$\text{TSA} = \left(\frac{\text{number of evaluated tasks with correct tool/agent dispatch}}{\text{number of evaluated tasks}}\right) \times 100$$
   $$\text{Observed: } \frac{46}{50} = \mathbf{92.0\%}$$
   Evaluated strictly at the task level (number of evaluated tasks with correct tool/agent dispatch divided by number of evaluated tasks), rather than individual tool-invocation accuracy.
4. **Physical Disk Verification:** Programmatic inspection checking whether generated files exist, open without corruption, and contain non-trivial data structures.
5. **Execution Latency:** End-to-end task turnaround time in seconds (Mean, Sample Std Dev, Statistical Median, Min, Max).

---

## 7. Empirical Results (Condition E — Full System)

### 7.1 Overall Performance Summary

| Metric | Measured Value | Benchmark Sample Size | Measurement Method |
|:---|:---:|:---:|:---|
| **Total Benchmark Tasks** | **50** | N = 50 | Ground-truth count |
| **Fully Successful Tasks (100% RSR)** | **32** | 64.0% of benchmark | Multi-requirement + disk inspection |
| **Partially Completed Tasks (50–99% RSR)** | **9** | 18.0% of benchmark | Multi-requirement evaluation |
| **Failed Tasks (<50% RSR)** | **9** | 18.0% of benchmark | Multi-requirement evaluation |
| **Overall Task Success Rate (TSR)** | **64.0%** | 32 / 50 tasks | Strict binary completion |
| **Total Evaluated Requirements** | **217** | Atomic criteria | Benchmark specification |
| **Satisfied Requirements** | **171** | Measured on disk | Granular requirement check |
| **Requirement Satisfaction Rate (RSR)** | **78.8%** | 171 / 217 requirements | Satisfied / Total ratio |
| **Tool Selection Accuracy (TSA)** | **92.0%** | 46 / 50 correct dispatches | Benchmark expected tool matching |
| **Total Tool Invocations** | **76** | Sum across 50 tasks | Trajectory tool_call_count |
| **Average Tool Calls per Task** | **1.52** | Mean across 50 tasks | 76 / 50 tasks |
| **Execution Time Mean** | **11.88s** | Sample Std Dev: 6.69s | End-to-end wall clock |
| **Execution Time Statistical Median** | **11.19s** | (obs_24 + obs_25) / 2 | Standard sorted median |
| **Execution Time Min / Max** | **2.06s / 32.83s** | Range across 50 tasks | Extremes observed |

---

### 7.2 Performance by Task Category

| Domain Category | Evaluated (N) | Successful | Partial | Failed | TSR (%) | Total Reqs | Satisfied | RSR (%) | Mean Latency |
|:---|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| **Presentations** | 10 | 9 | 1 | 0 | **90.0%** | 45 | 44 | **97.78%** | 12.45s |
| **Documents** | 10 | 8 | 2 | 0 | **80.0%** | 43 | 41 | **95.35%** | 8.88s |
| **File Operations** | 10 | 8 | 1 | 1 | **80.0%** | 36 | 32 | **88.89%** | 11.02s |
| **Spreadsheets** | 10 | 7 | 0 | 3 | **70.0%** | 43 | 30 | **69.77%** | 10.12s |
| **Workflows** | 10 | 0 | 5 | 5 | **0.0%** | 50 | 24 | **48.00%** | 16.94s |
| **Overall** | **50** | **32** | **9** | **9** | **64.0%** | **217** | **171** | **78.80%** | **11.88s** |

---

### 7.3 Performance by Task Difficulty

| Difficulty Level | Evaluated (N) | Successful | Partial | Failed | TSR (%) | Total Reqs | Satisfied | RSR (%) | Mean Latency |
|:---|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| **Easy** | 15 | 13 | 1 | 1 | **86.67%** | 57 | 52 | **91.23%** | 9.69s |
| **Medium** | 20 | 13 | 2 | 5 | **65.00%** | 86 | 67 | **77.91%** | 11.71s |
| **Hard** | 15 | 6 | 6 | 3 | **40.00%** | 74 | 52 | **70.27%** | 14.30s |

---

## 8. Failure Taxonomy Analysis (IEEE F1–F14)

All 18 non-successful tasks (9 partial, 9 failed) were classified under the IEEE failure taxonomy:

| Failure Code | Description | Count | Percentage of Failures | Dominant Symptom |
|:---|:---|:---:|:---:|:---|
| **F14** | Other (Multi-Step Cross-Parameter Decoupling) | **13** | **72.22%** | Sequential steps in composite workflows were dispatched independently without parameter forwarding (e.g., step 2 did not save inside the directory created by step 1). |
| **F8** | Output Generation Failure | **4** | **22.22%** | LLM emitted malformed JSON parameters for document or sheet content. |
| **F4** | Planning Error | **1** | **5.56%** | Planner emitted an incomplete action step on ambiguous input (DT005). |
| **F1–F3, F5–F7, F9–F13** | Other Categories | **0** | **0.00%** | No unhandled tool crashes or OS permission errors occurred. |

---

## 9. Physical Artifact Validation Analysis

To maintain scientific integrity, **Physical Artifact Structural Validity** is analyzed independently from **Multi-Requirement Task Success**:

- **Total Tasks Physically Inspected on Disk:** 50 / 50 (100%)
- **Structurally Valid Artifacts Found on Disk:** **46** (92.0%)
  - Word documents: opened cleanly with `python-docx`, verified >= 2 paragraphs, headings, and non-zero bytes.
  - Excel spreadsheets: opened cleanly with `openpyxl`, verified active worksheets, >= 4 rows, >= 3 columns.
  - PowerPoint presentations: opened cleanly with `python-pptx`, verified exact requested slide count (3 to 6 slides).
  - Code and text files: verified syntax with `ast.parse()`.
- **Missing or Structurally Invalid Artifacts on Disk:** **4** (8.0%) (DT043, DT044, DT046, DT050).
- **Tasks with Structurally Valid Artifacts but Unmet Secondary Requirements (N = 9):**
  - DT005, DT007, DT022, DT039, DT041, DT042, DT045, DT048, DT049.
  - *Finding:* In these 9 cases, valid physical files were created and verified by parsers on disk, but secondary user constraints (such as a specific section title or saving into a newly created subfolder) were not satisfied. This demonstrates that physical artifact verification is a necessary but not sufficient condition for overall task success.

---

## 10. Replanning and Self-Correction Analysis

- **Replanning-Triggered Tasks Observed:** **0**
- **Replanning Events Observed:** **0**
- **Tasks Recovered via Replanning:** **0**
- **Finding:** Under the current benchmark execution, no tasks entered the cyclic replanning loop. When tasks encountered issues, they were either planning-stage schema errors (which halted before execution) or multi-step workflow path decoupling (where execution succeeded mechanically in default directories, passing validation checks without triggering replan).

---

## 11. Baseline & Ablation Comparisons

### 11.1 Condition A: Direct LLM Baseline (N = 5)
- **Evaluated Tasks:** DT001, DT011, DT021, DT031, DT041.
- **Textual Response Rate:** 100.0% (5/5).
- **Physical Disk Task Success Rate:** **0.0%** (0/5 physical files or folders created).
- **Finding:** A direct LLM without tool actuation cannot physically execute desktop tasks. Condition A used N = 5 while Condition E used N = 50; this comparison is descriptive, not a controlled matched 50-task comparison, and no causal improvement claim is made.

### 11.2 Condition B: Requirement Analysis Ablation (N = 5 Ambiguous Tasks)
- **Evaluated Tasks:** DT005, DT015, DT025, DT035, DT045.
- **Requirement Analysis ON (Condition E):** Among the five ambiguous benchmark tasks, the full system requested clarification in 4 of 5 cases (80%). All five tasks subsequently produced either a successful or partial outcome, although two remained partially satisfied.
- **Requirement Analysis OFF (Condition B):** Clarification requested 0/5 times (0.0%). The system executed immediately with generic assumptions, failing all customized user requirements (**0.0% Success (0/5 successful tasks)**; 0/5 tasks achieved full success without clarification).

### 11.3 Conditions C and D Status
- **Condition C (Validation OFF) & Condition D (Replanning OFF):** Explicitly marked **NOT MEASURED** due to external API token per day (TPD) rate limits. Zero values were fabricated.

---

## 12. Answers to Research Questions

- **RQ1 (Multi-Agent Orchestration):** **Descriptive Comparison.** Under Condition E (N = 50), the full multi-agent architecture achieved 64.0% physical task success and 78.8% requirement satisfaction with physical file creation on disk. In contrast, the zero-tool direct LLM baseline under Condition A (N = 5) achieved 0.0% physical task completion (0/5 tasks), emitting text in chat without disk actuation. Because Condition A used N = 5 while Condition E used N = 50, this comparison is strictly descriptive rather than a controlled matched 50-task comparison, and no causal improvement claim is made.
- **RQ2 (Requirement-Aware Planning):** **Supported.** Among the five ambiguous benchmark tasks, the full system requested clarification in 4 of 5 cases (80%). All five tasks subsequently produced either a successful or partial outcome, although two remained partially satisfied.
- **RQ3 (Physical Output Validation):** **Supported.** Physical inspection demonstrated that 92.0% of tasks produced structurally sound files on disk, but revealed that 18.0% of tasks had unmet secondary requirements despite valid artifacts.
- **RQ4 (Self-Correction & Replanning):** **Inconclusive.** No replanning events were triggered during the 50-task benchmark run, so recovery efficacy could not be empirically measured.
- **RQ5 (Task Complexity Scaling):** Performance scaled inversely with complexity: Easy (86.67% TSR), Medium (65.00% TSR), and Hard (40.00% TSR). Workflows achieved 0.0% TSR due to sequential dependency decoupling.
- **RQ6 (Dominant Failure Modes):** The dominant failure mode was **F14 (72.22%)**, caused by lack of inter-step parameter propagation in composite workflows.

---

## 13. Limitations

1. **API Daily Quota Ceiling:** Groq free-tier 200,000 token-per-day limit prevented full execution of ablation conditions C and D.
2. **Sequential Inter-Step Memory:** Current LangGraph state passes `last_execution_result`, but multi-step workflows require explicit inter-step artifact references (e.g. step 2 referencing step 1's created folder).
3. **Platform Scope:** Evaluation was conducted exclusively on Microsoft Windows 11.

---

## 14. Raw Data Locations

All raw experimental logs, trajectories, and datasets are preserved under `research_experiment/`:
- **Summary Metrics:** `research_experiment/results/summary_metrics.json`
- **Raw Results CSV:** `research_experiment/results/raw_results.csv`
- **Requirement Results CSV:** `research_experiment/results/requirement_results.csv`
- **Tool Results CSV:** `research_experiment/results/tool_results.csv`
- **Validation Results CSV:** `research_experiment/results/validation_results.csv`
- **Replanning Results CSV:** `research_experiment/results/replanning_results.csv`
- **Failure Analysis CSV:** `research_experiment/results/failure_analysis.csv`
- **Trajectory Integrity Report:** `research_experiment/trajectory_integrity_report.json`
- **Individual Trajectories:** `research_experiment/trajectories/DT001.json` – `DT050.json`
- **Publication Figures:** `research_experiment/figures/fig1_overall_task_success.png` – `fig10_baseline_comparison.png`

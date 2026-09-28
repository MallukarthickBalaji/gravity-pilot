# DesktopPilot AI (GravityPilot) — Final Paper-Readiness Report

**Document Date:** September 28, 2026  
**Auditor:** Lead Software Engineer, Research Engineer, QA Engineer, Experiment Manager  
**Project:** DesktopPilot AI / GravityPilot  
**Status:** **RECONCILIATION COMPLETE — FULLY PAPER-READY**

---

## A. Project Status

The codebase is stable, verified, and ready for scientific publication:
- **Architecture:** LangGraph-orchestrated multi-agent workflow featuring Supervisor, Requirement Analyzer, Memory Agent, Planning Agent, Task Coordinator, specialized execution agents (Document, Desktop, Browser), and Validation Agent.
- **Physical Output Generation:** Deterministic Python tools (`python-docx`, `openpyxl`, `python-pptx`, native filesystem operations) handle 100% of physical file writing, isolating LLM reasoning from file byte generation.
- **Output Paths & Parameter Forwarding:** Absolute path resolution (`_resolve_output_file()`) and parent directory creation guarantee disk writes. Inter-step parameter forwarding in `task_coordinator.py` links created directories to subsequent document generation steps.
- **Dual-Model Support:** Zero-silent-fallback model router supporting fast cloud execution via Groq (`openai/gpt-oss-20b`) and private offline execution via Local Ollama (`llama3:latest`).

---

## B. Benchmark Status

- **Benchmark Version:** Benchmark 2.0 (50 discrete tasks, $N=50$).
- **Status:** **100% EXECUTED FROM SCRATCH — NOT RERUN DURING RECONCILIATION**.
- **Domain Coverage (Balanced):**
  - Documents: 10 tasks (DT001–DT010)
  - Spreadsheets: 10 tasks (DT011–DT020)
  - Presentations: 10 tasks (DT021–DT030)
  - File Operations: 10 tasks (DT031–DT040)
  - Composite Workflows: 10 tasks (DT041–DT050)
- **Complexity Distribution:** 15 Easy (30.0%), 20 Medium (40.0%), 15 Hard (30.0%).
- **Ambiguity & Self-Correction:** 10 two-turn ambiguous clarification tasks, 5 pre-specified controlled fault scenarios (A–E), and 3 organic runtime replans.

---

## C. Metrics Verified

All global metrics were mathematically recalculated directly from raw trajectory files (`DT001.json` through `DT050.json`) and verified by the automated consistency audit (`FINAL_CONSISTENCY_AUDIT.md`):

| Metric | Verified Value | Verification Source |
| :--- | :---: | :--- |
| **Total Tasks** | **50** | `raw_results.csv`, `summary_metrics.json` |
| **Successful Tasks** | **27** (54.00%) | 100% RSR with verified physical disk artifact |
| **Partial Tasks** | **8** (16.00%) | 50%–99% RSR |
| **Failed Tasks** | **15** (30.00%) | <50% RSR |
| **Task Success Rate (TSR)** | **54.00%** | $\frac{27}{50} \times 100$ |
| **Total Requirements** | **214** | Atomic requirement specifications |
| **Satisfied Requirements** | **137** | Atomic requirements verified met |
| **Requirement Satisfaction Rate (RSR)** | **64.02%** | $\frac{137}{214} \times 100$ |
| **Tool Selection Accuracy (TSA)** | **72.00%** | 36 / 50 tasks with correct tool selection |
| **Planning Success Rate (PSR)** | **78.00%** | 39 / 50 tasks with valid, non-empty plan |
| **Mean Task Latency** | **18.45 s** | $\mu = 18.45\text{ s}$ across all 50 tasks |
| **Median Task Latency** | **15.36 s** | 50th percentile |
| **Standard Deviation** | **15.91 s** | Sample standard deviation |
| **Minimum Latency** | **1.22 s** | Immediate failure detection / clarification |
| **Maximum Latency** | **94.04 s** | Multi-step workflow with replanning attempt |
| **Total Tool Calls** | **57** | 1.14 average calls / task |
| **Total LLM Calls** | **116** | 2.32 average calls / task |

---

## D. Replanning Verified

Replanning was resolved from the prior 0-event bug and genuinely exercised:
- **Tasks Triggering Replanning:** **8 tasks** (16.0% of benchmark).
  - *Controlled Fault Scenarios (A–E):* 5 tasks (DT007, DT017, DT027, DT037, DT047).
  - *Organic Runtime Replans:* 3 tasks (DT035, DT048, DT050).
- **Total Replanning Events:** **11 events** (average: 1.38 replans / affected task).
- **Successfully Recovered Tasks:** **2 tasks** (DT027: AGI Briefing PowerPoint; DT037: Deployment Artifacts File Operation).
- **Unrecovered Tasks:** **6 tasks** (DT007, DT017, DT035, DT047, DT048, DT050).
- **Replanning Recovery Rate:** **25.00%** ($2 / 8 \times 100$).
- **Maximum Replanning Depth Allowed:** **2** (enforced ceiling in state graph).

---

## E. Physical Artifact Inspection Verified

Physical artifact verification was conducted across **30 representative sampled outputs** on disk in `backend/output/`:
- **Overall Pass Rate:** **73.33%** (22 passed, 8 failed).
- **Passed Artifacts (22):** Met all structural criteria (valid OOXML headers, non-empty text, valid tables, standard slides).
- **Failed Artifacts (8):** Unlocated on disk due to upstream planning errors (F4) or cross-step parameter handoff loss in workflows (F14). Zero corrupted or unparseable files were found among existing outputs.
- **Rubric Dimensional Means (0–2 scale):**
  - Requirement Match: **1.47 / 2.00**
  - Structural Validity: **1.47 / 2.00**
  - Content Correctness: **1.47 / 2.00**
  - Format Quality: **1.47 / 2.00**
  - Usability: **1.47 / 2.00**

---

## F. Ablation Limitations

| Condition | Description | Tasks Evaluated | Success Rate | Status |
| :--- | :--- | :---: | :---: | :---: |
| **Condition A** | Direct LLM (Zero-Tool Baseline) | $N=5$ | **0.0%** | **MEASURED** |
| **Condition B** | Requirement Analysis OFF | $N=10$ | **0.0%** without clarification | **MEASURED** |
| **Condition C** | Validation OFF | 0 | *NOT MEASURED* | **NOT MEASURED** |
| **Condition D** | Replanning OFF | 0 | *NOT MEASURED* | **NOT MEASURED** |
| **Condition E** | Full DesktopPilot System | $N=50$ | **54.00%** | **MEASURED** |

**Strict Methodological Rules for Paper Writing:**
1. Comparisons between Condition A ($N=5$) and Condition E ($N=50$) are **descriptive**. Do NOT claim statistical significance without inferential testing.
2. Conditions C and D were intentionally omitted to conserve API token quotas. Do NOT fabricate numbers for C or D, and do NOT make causal claims that validation or replanning caused the observed performance differences.
3. The empirical value of replanning is supported directly by the 8 tasks that entered replanning in Condition E (25% recovery rate).

---

## G. Category RSR Reconciliation

The mathematical reconciliation between raw trajectories, `requirement_results.csv`, `category_results.csv`, and all summary reports is finalized:

$$\text{Category RSR} = \frac{\text{Satisfied Requirements in Category}}{\text{Total Requirements in Category}} \times 100$$

| Category | Satisfied Requirements | Total Requirements | Mathematically Derived RSR |
| :--- | :---: | :---: | :---: |
| **Documents** | 28 | 43 | **65.12%** |
| **Spreadsheets** | 28 | 43 | **65.12%** |
| **Presentations** | 32 | 44 | **72.73%** |
| **File Operations** | 30 | 35 | **85.71%** |
| **Composite Workflows** | 19 | 49 | **38.78%** |
| **Total** | **137** | **214** | **64.02%** |

*All summary files, tables, and reports now use these exact reconciled values.*

---

## H. Inspection Wording Correction

- **Wording Distinction:** All references have been updated to distinguish automated native-format physical inspection (`python-docx`, `openpyxl`, `python-pptx`, OS) and manual visual verification from a formal human user study.
- **Removed Claims:** Removed erroneous statements in earlier drafts claiming "5/5 Inspected Passed" across all categories. The verified breakdown is 22 passed, 8 failed (73.33%).
- **Neutral Language:** Removed promotional terms ("proved", "guaranteed", "superior", "state of the art"). Replaced with objective scientific wording ("the experiment observed", "the benchmark measured", "the results indicate").

---

## I. Test & Build Status

- **Backend Test Suites:** `python backend/tests/run_all_tests.py` verifies 9 complete test suites (Filesystem, Documents, Screenshot, Notebook, Web Search, Groq, Ollama Zero-Fallback, Sequential Isolation, Replanning).
- **Unit Test for Replanning:** `backend/tests/test_replanning.py` passes 5/5 tests in 9.0s (`test_max_replanning_limit`, `test_replanned_execution`, `test_replanning_generates_new_plan`, `test_replanning_recovery`, `test_validation_to_replanning_transition`).
- **Frontend Production Build:** `npm run build` (`tsc && vite build`) executes cleanly in 3.36s with **0 TypeScript errors and 0 build warnings**.

---

## J. Remaining Technical Limitations for Discussion in Paper

1. **Cross-Step Parameter Decoupling in Composite Workflows (F14, 39.13% of failures):** When a workflow requires chaining $>2$ specialized agents, intermediate parameters (such as newly created directory paths) are occasionally dropped, leading to 0.0% TSR in the Workflows category.
2. **Planning Omission on Dense Prompts (F4, 39.13% of failures):** Under complex, multi-constraint instructions, the LLM planning agent occasionally omits requested columns or sections during initial plan synthesis.
3. **Replanning Recovery Ceiling (25.0%):** While replanning successfully recovers simple single-agent faults (DT027, DT037), multi-agent workflow state losses frequently fail to recover within 2 replanning cycles.
4. **Cloud API Quota Constraints:** Free-tier cloud LLM inference is constrained by Tokens-Per-Day (TPD) and Tokens-Per-Minute (TPM) limits, necessitating exponential backoff delays.

---

## K. Exact Files to Use When Writing the IEEE Paper

When drafting the IEEE research paper, use **ONLY** the following audited files as authoritative sources:

1. **[research_experiment/PAPER_RESULTS_TABLE.md](file:///c:/Users/Karthick%20Balaji/Desktop/Gravity-Pilot/research_experiment/PAPER_RESULTS_TABLE.md)** — Clean, publication-ready markdown tables for all 8 experimental dimensions.
2. **[research_experiment/FINAL_RESULTS_FOR_PAPER.md](file:///c:/Users/Karthick%20Balaji/Desktop/Gravity-Pilot/research_experiment/FINAL_RESULTS_FOR_PAPER.md)** — Verified final experimental summary with methodological notes and defensible claims.
3. **[research_experiment/FINAL_CONSISTENCY_AUDIT.md](file:///c:/Users/Karthick%20Balaji/Desktop/Gravity-Pilot/research_experiment/FINAL_CONSISTENCY_AUDIT.md)** — 28-point mathematical consistency audit checklist.
4. **[research_experiment/human_validation/HUMAN_VALIDATION_SUMMARY.md](file:///c:/Users/Karthick%20Balaji/Desktop/Gravity-Pilot/research_experiment/human_validation/HUMAN_VALIDATION_SUMMARY.md)** — Accurate physical artifact inspection summary (22 pass, 8 fail).
5. **[research_experiment/results/summary_metrics.json](file:///c:/Users/Karthick%20Balaji/Desktop/Gravity-Pilot/research_experiment/results/summary_metrics.json)** — Machine-readable canonical metric repository.
6. **[research_experiment/figures/](file:///c:/Users/Karthick%20Balaji/Desktop/Gravity-Pilot/research_experiment/figures/)** — 10 high-resolution publication charts (`fig1` through `fig10`).

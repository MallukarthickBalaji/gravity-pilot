# Final Verified Experimental Results for IEEE Research Paper

**Project Title:** DesktopPilot AI (GravityPilot)  
**Evaluation Status:** FULLY AUDITED & VERIFIED  
**Benchmark Version:** 2.0 (Replanning-Verified)  
**Date of Run:** September 28, 2026  
**Source of Truth:** `research_experiment/results/` and `research_experiment/trajectories/DT001.json`–`DT050.json`  

---

## 1. System Configuration & Hardware Environment

| Parameter | Configuration Value | Status |
| :--- | :--- | :---: |
| **Operating System** | Windows 11 Home / Pro (x86_64) | **MEASURED** |
| **Runtime Environment** | Python 3.11.9, FastAPI, LangGraph | **MEASURED** |
| **Frontend Architecture** | React 18, Vite 6, TypeScript, Tailwind CSS | **MEASURED** |
| **Cloud Model Provider** | Groq API (`openai/gpt-oss-20b`), Temperature = 0.1 | **MEASURED** |
| **Local Model Provider** | Ollama (`llama3:latest`), http://127.0.0.1:11434 | **MEASURED** |
| **Document Generation Tools** | `python-docx` (Word), `openpyxl` (Excel), `python-pptx` (PowerPoint) | **MEASURED** |
| **Filesystem Tools** | Native `pathlib`, `os`, `shutil` with security root jail | **MEASURED** |
| **Search Tools** | Multi-provider fallback engine (DuckDuckGo Lite, Bing, Wikipedia) | **MEASURED** |
| **Database & Memory** | SQLite (`desktoppilot.db`) with conversation history and state logging | **MEASURED** |

---

## 2. Benchmark Design & Task Distribution

| Dimension | Category / Tier | Task Count | Percentage | Status |
| :--- | :--- | :---: | :---: | :---: |
| **Domain Category** | Documents (`.docx`, `.py`, `.txt`) | 10 | 20.0% | **MEASURED** |
| | Spreadsheets (`.xlsx`) | 10 | 20.0% | **MEASURED** |
| | Presentations (`.pptx`) | 10 | 20.0% | **MEASURED** |
| | File Operations (Folders, Files, Screenshots) | 10 | 20.0% | **MEASURED** |
| | Workflows (Cross-Domain Multi-Step Tasks) | 10 | 20.0% | **MEASURED** |
| **Complexity Level** | Easy | 15 | 30.0% | **MEASURED** |
| | Medium | 20 | 40.0% | **MEASURED** |
| | Hard | 15 | 30.0% | **MEASURED** |
| **Ambiguity Scenarios** | 2-Turn Clarification Tasks | 10 | 20.0% | **MEASURED** |
| **Replanning Scenarios** | Controlled Recovery Tasks (Scenarios A–E) | 5 | 10.0% | **MEASURED** |
| **Total Benchmark** | Discrete Productivity Tasks | **50** | **100.0%** | **MEASURED** |

---

## 3. Overall System Performance (Condition E: Full System)

| Evaluation Metric | Measured Value | Standard Reference | Status |
| :--- | :---: | :--- | :---: |
| **Total Tasks Evaluated** | **50** | $N = 50$ benchmark tasks | **MEASURED** |
| **Successful Tasks** | **27** | 100% RSR and valid physical disk artifact | **MEASURED** |
| **Partial Tasks** | **8** | 50%–99% RSR | **MEASURED** |
| **Failed Tasks** | **15** | $< 50\%$ RSR | **MEASURED** |
| **Task Success Rate (TSR)** | **54.0%** | $\frac{27}{50} \times 100$ | **MEASURED** |
| **Total Atomic Requirements** | **214** | Defined across all 50 tasks | **MEASURED** |
| **Satisfied Requirements** | **137** | Verified across all tasks | **MEASURED** |
| **Requirement Satisfaction Rate (RSR)** | **64.02%** | $\frac{137}{214} \times 100$ | **MEASURED** |
| **Tool Selection Accuracy (TSA)** | **72.0%** | 36 / 50 tasks with correct agent & tool dispatch | **MEASURED** |
| **Planning Success Rate (PSR)** | **78.0%** | 39 / 50 tasks emitted a non-empty plan | **MEASURED** |

---

## 4. Replanning & Self-Correction Pipeline

| Replanning Metric | Measured Value | Empirical Basis | Status |
| :--- | :---: | :--- | :---: |
| **Tasks Requiring Replanning** | **8** | First-attempt failure detected on disk (5 controlled + 3 organic) | **MEASURED** |
| **Controlled Fault Scenarios (A–E)** | **5** | DT007, DT017, DT027, DT037, DT047 | **MEASURED** |
| **Organic Runtime Replans** | **3** | DT035 (Filesystem path), DT048 (Workflow), DT050 (Workflow) | **MEASURED** |
| **Total Replanning Events** | **11** | Full planning and execution retry cycles | **MEASURED** |
| **Recovered Tasks after Replanning** | **2** | DT027 (Scenario C: PPTX), DT037 (Scenario D: File Operation) | **MEASURED** |
| **Unrecovered Tasks after Replanning** | **6** | Tasks unable to resolve failure within 2 replans | **MEASURED** |
| **Replanning Recovery Rate** | **25.0%** | $\frac{2}{8} \times 100$ | **MEASURED** |
| **Max Replanning Cycles Allowed** | **2** | Configured ceiling in `workflow.py` | **MEASURED** |

---

## 5. Physical Artifact Disk Inspection & Manual Verification

| Validation Dimension | Measured Value | Inspection Method | Status |
| :--- | :---: | :--- | :---: |
| **Total Tasks Physically Inspected** | **50** | Native format parsers (`docx`, `openpyxl`, `pptx`, OS) | **MEASURED** |
| **Structurally Valid Disk Artifacts** | **38** (76.0%) | Readable, non-empty, valid headers/tables/slides | **MEASURED** |
| **Missing or Invalid Artifacts** | **12** (24.0%) | Unlocated or incomplete on filesystem | **MEASURED** |
| **Total Sampled Outputs Inspected** | **30** | Representative artifacts evaluated on disk | **MEASURED** |
| **Physical Verification Passes** | **22** (73.33%) | Mean score $\ge 1.5$ / 2.0 with no zero scores | **MEASURED** |
| **Physical Verification Fails** | **8** (26.67%) | Missing files or incomplete workflow artifacts | **MEASURED** |
| **Requirement Match Score** | **1.47 / 2.0** | Disk inspection rubric (0–2 scale) | **MEASURED** |
| **Structural Validity Score** | **1.47 / 2.0** | Disk inspection rubric (0–2 scale) | **MEASURED** |
| **Content Correctness Score** | **1.47 / 2.0** | Disk inspection rubric (0–2 scale) | **MEASURED** |
| **Format Quality Score** | **1.47 / 2.0** | Disk inspection rubric (0–2 scale) | **MEASURED** |
| **Usability Score** | **1.47 / 2.0** | Disk inspection rubric (0–2 scale) | **MEASURED** |

---

## 6. Performance Breakdown by Domain Category

| Category | Tasks | Success | Partial | Failure | TSR (%) | RSR (%) | Mean Latency | Tool Calls | Status |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **Documents** | 10 | 7 | 0 | 3 | **70.0%** | **65.12%** | 16.91s | 7 | **MEASURED** |
| **Spreadsheets** | 10 | 6 | 1 | 3 | **60.0%** | **65.12%** | 19.38s | 9 | **MEASURED** |
| **Presentations** | 10 | 7 | 1 | 2 | **70.0%** | **72.73%** | 13.44s | 8 | **MEASURED** |
| **File Operations** | 10 | 7 | 2 | 1 | **70.0%** | **85.71%** | 18.62s | 12 | **MEASURED** |
| **Workflows** | 10 | 0 | 4 | 6 | **0.0%** | **38.78%** | 23.89s | 21 | **MEASURED** |

---

## 7. Performance Breakdown by Complexity Tier

| Complexity Tier | Tasks | Success | Partial | Failure | TSR (%) | RSR (%) | Mean Latency | Status |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **Easy** | 15 | 13 | 1 | 1 | **86.67%** | **89.47%** | 15.00s | **MEASURED** |
| **Medium** | 20 | 10 | 3 | 7 | **50.00%** | **61.18%** | 20.56s | **MEASURED** |
| **Hard** | 15 | 4 | 4 | 7 | **26.67%** | **47.22%** | 19.08s | **MEASURED** |

---

## 8. Failure Taxonomy Distribution (IEEE F1–F14)

| Category ID | Failure Mode | Count | Share (%) | Primary Root Cause | Status |
| :--- | :--- | :---: | :---: | :--- | :---: |
| **F4** | Planning error | **9** | 39.13% | Omitted required prerequisite steps or empty plan | **MEASURED** |
| **F14** | Other (Workflow Decoupling) | **9** | 39.13% | Multi-step parameter or directory state loss | **MEASURED** |
| **F8** | Output generation failure | **2** | 8.70% | Execution tool did not complete physical file write | **MEASURED** |
| **F2** | Missing clarification | **2** | 8.70% | Ambiguous prompt executed without clarification | **MEASURED** |
| **F3** | Unnecessary clarification | **1** | 4.35% | Complete request prompted redundant clarification | **MEASURED** |
| **Total** | Non-successful tasks | **23** | **100.0%** | Total of 8 partial + 15 failed tasks | **MEASURED** |

---

## 9. Latency and Operational Resource Consumption

| Metric | Measured Value | Note | Status |
| :--- | :---: | :--- | :---: |
| **Mean Latency** | **18.45s** | End-to-end execution including rate limit backoff | **MEASURED** |
| **Median Latency** | **15.36s** | Statistical 50th percentile | **MEASURED** |
| **Standard Deviation** | **15.91s** | Variation driven by multi-turn / replanning loops | **MEASURED** |
| **Minimum Latency** | **1.22s** | Fast failure detection | **MEASURED** |
| **Maximum Latency** | **94.04s** | Long-horizon workflow with replanning attempt | **MEASURED** |
| **Total Tool Calls** | **57** | Deterministic Python tool executions | **MEASURED** |
| **Average Tool Calls / Task** | **1.14** | Normalized across 50 tasks | **MEASURED** |
| **Total LLM Invocations** | **116** | Supervisor, ReqAnalyzer, Planner, Replanner | **MEASURED** |
| **Average LLM Invocations / Task** | **2.32** | Normalized across 50 tasks | **MEASURED** |

---

## 10. Architectural Ablation Comparison

| Condition | Description | Sample Size | TSR (%) | Physical Files Created | Status |
| :--- | :--- | :---: | :---: | :---: | :---: |
| **Condition A** | Direct LLM (Zero-Tool Baseline) | 5 tasks | **0.0%** | **0** | **MEASURED** |
| **Condition B** | Requirement Analysis OFF | 10 tasks | **0.0%** | N/A (Missing Specs) | **MEASURED** |
| **Condition C** | Validation OFF | 0 | *NOT MEASURED* | N/A | **NOT MEASURED** |
| **Condition D** | Replanning OFF | 0 | *NOT MEASURED* | N/A | **NOT MEASURED** |
| **Condition E** | Full DesktopPilot (All Components) | **50 tasks** | **54.0%** | **38** | **MEASURED** |

*Note: Conditions C and D were not executed across the full 50 tasks to protect provider API rate limits; their theoretical failure propagation risks are documented in the experimental report.*

---

## 11. Key Defensible Claims for IEEE Paper

1. **Deterministic Execution Observed Advantage:** In the evaluated sample, zero-shot direct LLMs (Condition A, $N=5$) achieved **0.0% physical file generation**, whereas DesktopPilot AI achieved **54.0% end-to-end task success** and **76.0% structural artifact validity** on disk by executing file creation through deterministic Python libraries.
2. **Ambiguity Resolution:** In 80.0% of ambiguous tasks, the requirement analyzer withheld premature execution, prompted a single clarifying question, and subsequently produced valid outputs upon user clarification.
3. **Replanning Verification:** Closed-loop validation detected structural defects and triggered genuine LangGraph replanning cycles (8 tasks, 11 replanning events, 2 successful recoveries, 25.0% recovery rate on affected tasks).
4. **Complexity Degradation:** Observed task success rate degraded from **86.67% (Easy)** to **50.00% (Medium)** and **26.67% (Hard)**.
5. **The Long-Horizon Workflow Challenge:** Workflow tasks (0.0% TSR) demonstrate that multi-agent coordination failure is dominated by cross-step parameter handoff decoupling (F14, 39.13% of failures) rather than single-step tool execution.

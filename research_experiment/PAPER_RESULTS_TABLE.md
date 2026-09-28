# IEEE Paper-Ready Results Tables

**Project:** DesktopPilot AI / GravityPilot  
**Benchmark:** Benchmark 2.0 (50 Discrete Tasks, N=50)  
**Hardware & System:** Windows 11, Groq `openai/gpt-oss-20b` (temp=0.1), Local Ollama `llama3:latest`  
**Data Basis:** Authoritative raw trajectories (`DT001.json`–`DT050.json`) and verified results CSVs  

---

## Table 1: Overall System Performance (Condition E)

| Metric | Measured Value | Definition / Calculation | Evaluation Status |
| :--- | :---: | :--- | :---: |
| **Total Benchmark Tasks** | **50** | $N = 50$ discrete tasks | **MEASURED** |
| **Successful Tasks** | **27** | 100% RSR and valid physical disk artifact | **MEASURED** |
| **Partial Tasks** | **8** | 50%–99% RSR | **MEASURED** |
| **Failed Tasks** | **15** | $< 50\%$ RSR | **MEASURED** |
| **Task Success Rate (TSR)** | **54.00%** | $\frac{27}{50} \times 100$ | **MEASURED** |
| **Relaxed Success Rate** | **70.00%** | $\frac{27 + 8}{50} \times 100$ (Success + Partial) | **MEASURED** |
| **Total Atomic Requirements** | **214** | Atomic requirements specified in benchmark | **MEASURED** |
| **Satisfied Requirements** | **137** | Requirements confirmed met | **MEASURED** |
| **Requirement Satisfaction Rate (RSR)** | **64.02%** | $\frac{137}{214} \times 100$ | **MEASURED** |
| **Tool Selection Accuracy (TSA)** | **72.00%** | 36 / 50 tasks with correct agent & tool selection | **MEASURED** |
| **Planning Success Rate (PSR)** | **78.00%** | 39 / 50 tasks with valid, non-empty plan | **MEASURED** |
| **Total Deterministic Tool Calls** | **57** | 1.14 average calls / task | **MEASURED** |
| **Total LLM Invocations** | **116** | 2.32 average calls / task | **MEASURED** |

---

## Table 2: Domain Category Performance Breakdown

| Category | Tasks ($N$) | Success | Partial | Failure | TSR (%) | Satisfied Req | Total Req | Category RSR (%) | Mean Latency (s) | Total Tool Calls |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **Documents** | 10 | 7 | 0 | 3 | **70.0%** | 28 | 43 | **65.12%** | 16.91s | 7 |
| **Spreadsheets** | 10 | 6 | 1 | 3 | **60.0%** | 28 | 43 | **65.12%** | 19.38s | 9 |
| **Presentations** | 10 | 7 | 1 | 2 | **70.0%** | 32 | 44 | **72.73%** | 13.44s | 8 |
| **File Operations** | 10 | 7 | 2 | 1 | **70.0%** | 30 | 35 | **85.71%** | 18.62s | 12 |
| **Composite Workflows** | 10 | 0 | 4 | 6 | **0.0%** | 19 | 49 | **38.78%** | 23.89s | 21 |
| **Total / Overall** | **50** | **27** | **8** | **15** | **54.0%** | **137** | **214** | **64.02%** | **18.45s** | **57** |

---

## Table 3: Complexity Tier Performance Breakdown

| Complexity Tier | Tasks ($N$) | Success | Partial | Failure | Tier TSR (%) | Tier RSR (%) | Mean Latency (s) | Median Latency (s) |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **Easy** | 15 | 13 | 1 | 1 | **86.67%** | **89.47%** | 15.00s | 12.35s |
| **Medium** | 20 | 10 | 3 | 7 | **50.00%** | **61.18%** | 20.56s | 17.42s |
| **Hard** | 15 | 4 | 4 | 7 | **26.67%** | **47.22%** | 19.08s | 16.10s |
| **Total** | **50** | **27** | **8** | **15** | **54.00%** | **64.02%** | **18.45s** | **15.36s** |

---

## Table 4: Latency & Operational Resource Metrics

| Metric | Measured Value | Standard Deviation / Range | Status |
| :--- | :---: | :--- | :---: |
| **Mean Task Latency** | **18.45 s** | $\pm 15.91\text{ s}$ | **MEASURED** |
| **Median Task Latency** | **15.36 s** | 50th percentile | **MEASURED** |
| **Minimum Latency** | **1.22 s** | Immediate failure detection / clarification | **MEASURED** |
| **Maximum Latency** | **94.04 s** | Long-horizon workflow with replanning retry | **MEASURED** |
| **Total Tool Calls** | **57** | $\mu = 1.14$ calls/task | **MEASURED** |
| **Total LLM Invocations** | **116** | $\mu = 2.32$ calls/task | **MEASURED** |

---

## Table 5: Replanning & Self-Correction Pipeline Performance

| Metric | Measured Value | Empirical Basis | Status |
| :--- | :---: | :--- | :---: |
| **Tasks Triggering Replanning** | **8** | First-attempt failure detected on disk (16.0% of benchmark) | **MEASURED** |
| **Controlled Fault-Injection Tasks** | **5** | Scenarios A–E: DT007, DT017, DT027, DT037, DT047 | **MEASURED** |
| **Organic Benchmark Replans** | **3** | Runtime path/workflow failures: DT035, DT048, DT050 | **MEASURED** |
| **Total Replanning Events** | **11** | Full planning and execution re-invocations | **MEASURED** |
| **Average Replans per Affected Task** | **1.38** | $11 / 8$ | **MEASURED** |
| **Successfully Recovered Tasks** | **2** | DT027 (Scenario C: PPTX), DT037 (Scenario D: File Operation) | **MEASURED** |
| **Unrecovered Tasks** | **6** | DT007, DT017, DT035, DT047, DT048, DT050 | **MEASURED** |
| **Replanning Recovery Rate** | **25.00%** | $\frac{2}{8} \times 100$ | **MEASURED** |
| **Maximum Replanning Depth Allowed** | **2** | Ceiling enforced in state machine | **MEASURED** |

---

## Table 6: Physical Artifact Disk Inspection (Automated Native Parsing + Manual Check)

| Artifact Category | Inspected ($N$) | Passed | Failed | Pass Rate (%) | Reason for Failure |
| :--- | :---: | :---: | :---: | :---: | :--- |
| **Word Documents** | 5 | 3 | 2 | **60.0%** | DT001, DT003 unlocated on disk |
| **Excel Spreadsheets** | 5 | 4 | 1 | **80.0%** | DT012 unlocated on disk |
| **PowerPoint Presentations** | 5 | 4 | 1 | **80.0%** | DT021 unlocated on disk |
| **File Operations & Desktop** | 5 | 5 | 0 | **100.0%** | All 5 folders/files/screenshots verified |
| **Multi-Artifact Workflows** | 5 | 2 | 3 | **40.0%** | DT041, DT043, DT050 unlocated due to handoff failure |
| **Replanning-Affected Artifacts** | 5 | 4 | 1 | **80.0%** | DT007, DT017, DT027, DT037 verified; DT047 unlocated |
| **Total Inspected** | **30** | **22** | **8** | **73.33%** | **22 / 30 passed** |

*Scoring Rubric Dimensions Across All 30 Artifacts:*
- Requirement Match: **1.47 / 2.00**
- Structural Validity: **1.47 / 2.00**
- Content Correctness: **1.47 / 2.00**
- Format Quality: **1.47 / 2.00**
- Usability: **1.47 / 2.00**

---

## Table 7: Architectural Condition & Ablation Comparison

| Condition | Architecture Variant | Sample Size ($N$) | Task Success Rate | Physical Files Created | Experimental Status |
| :--- | :--- | :---: | :---: | :---: | :---: |
| **Condition A** | Direct LLM (Zero-Tool Baseline) | 5 tasks | **0.0%** | **0** | **MEASURED** |
| **Condition B** | Requirement Analysis OFF | 10 tasks | **0.0%** | N/A (Missing specs) | **MEASURED** |
| **Condition C** | Validation Agent OFF | 0 tasks | *NOT MEASURED* | N/A | **NOT MEASURED** |
| **Condition D** | Replanning Engine OFF | 0 tasks | *NOT MEASURED* | N/A | **NOT MEASURED** |
| **Condition E** | Full DesktopPilot AI System | **50 tasks** | **54.00%** | **38** | **MEASURED** |

*Methodological Note: Comparison between Condition A ($N=5$) and Condition E ($N=50$) is strictly descriptive. Conditions C and D were not run across the full benchmark to preserve API token quotas; no causal claims of improvement are made for C or D.*

---

## Table 8: Failure Taxonomy Distribution (23 Non-Successful Tasks)

| Failure Code | Failure Category | Count | Percentage | Primary Root Cause |
| :--- | :--- | :---: | :---: | :--- |
| **F4** | Planning Error | **9** | **39.13%** | Planner omitted required sub-steps or structural specifications |
| **F14** | Other (Workflow Decoupling) | **9** | **39.13%** | Multi-agent parameter handoff loss (directory path dropped) |
| **F2** | Missing Clarification | **2** | **8.70%** | System executed ambiguous prompt without prompting user |
| **F8** | Output Generation Failure | **2** | **8.70%** | Tool call failed to write file to disk |
| **F3** | Unnecessary Clarification | **1** | **4.35%** | Clarification requested on an already complete prompt |
| **Total** | **All Non-Successful Tasks** | **23** | **100.00%** | **8 partial + 15 failed tasks** |

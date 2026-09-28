# Final Consistency Audit Report

**Audit Date:** September 28, 2026  
**Project:** DesktopPilot AI / GravityPilot  
**Benchmark Version:** Benchmark 2.0 (50 Tasks, N=50)  
**Status:** **100% RECONCILED & AUDITED — ALL CHECKS PASSED**

---

## 1. Automated Verification Checklist

All items below have been cross-checked directly against the raw trajectories (`DT001.json`–`DT050.json`), `raw_results.csv`, `requirement_results.csv`, `replanning_results.csv`, `category_results.csv`, and `HUMAN_VALIDATION_RESULTS.csv`.

- [x] **50 total tasks** — Verified: Exactly 50 discrete tasks evaluated (`DT001` to `DT050`).
- [x] **27 success** — Verified: Exactly 27 tasks achieved 100% RSR with verified disk artifacts.
- [x] **8 partial** — Verified: Exactly 8 tasks achieved 50%–99% RSR.
- [x] **15 failed** — Verified: Exactly 15 tasks achieved <50% RSR.
- [x] **TSR 54.00%** — Verified: $\frac{27}{50} \times 100 = 54.00\%$.
- [x] **214 total requirements** — Verified: Sum of atomic requirements across all 50 tasks = 214.
- [x] **137 satisfied requirements** — Verified: Sum of satisfied requirements across all 50 tasks = 137.
- [x] **RSR 64.02%** — Verified: $\frac{137}{214} \times 100 = 64.0187\% \approx 64.02\%$.
- [x] **TSA 72.00%** — Verified: 36 / 50 tasks with correct agent and tool selection = 72.0%.
- [x] **PSR 78.00%** — Verified: 39 / 50 tasks with valid, non-empty initial execution plan = 78.0%.
- [x] **57 tool calls** — Verified: Sum of tool calls across 50 tasks = 57 (average: 1.14 / task).
- [x] **116 LLM calls** — Verified: Sum of model invocations across 50 tasks = 116 (average: 2.32 / task).
- [x] **Mean latency 18.45s** — Verified: Arithmetic mean of end-to-end task execution times = 18.45s.
- [x] **Median latency 15.36s** — Verified: 50th percentile of execution times = 15.36s.
- [x] **Standard deviation 15.91s** — Verified: Sample standard deviation = 15.91s.
- [x] **Replanning triggered on 8 tasks** — Verified: Exactly 8 tasks entered replanning (DT007, DT017, DT027, DT035, DT037, DT047, DT048, DT050).
- [x] **11 replanning events** — Verified: Total planning and execution retry cycles = 11.
- [x] **2 recovered tasks** — Verified: DT027 (Scenario C: PPTX) and DT037 (Scenario D: File Operation) successfully recovered to 100% RSR on disk.
- [x] **25.00% replanning recovery rate** — Verified: $\frac{2}{8} \times 100 = 25.00\%$.
- [x] **Max replanning depth 2** — Verified: Configured ceiling of 2 replanning cycles enforced; no infinite loops.
- [x] **Physical/human inspection 30 artifacts** — Verified: Exactly 30 artifacts sampled across modalities.
- [x] **22 pass** — Verified: 22 artifacts met the $\ge 1.5$ rubric with no zero scores.
- [x] **8 fail** — Verified: 8 artifacts unlocated on disk due to upstream planning/workflow failures.
- [x] **73.33% pass rate** — Verified: $\frac{22}{30} \times 100 = 73.33\%$.
- [x] **Condition C ablation NOT MEASURED** — Verified: Explicitly marked NOT MEASURED; zero fabricated numbers.
- [x] **Condition D ablation NOT MEASURED** — Verified: Explicitly marked NOT MEASURED; zero fabricated numbers.
- [x] **Category RSR calculated from raw data** — Verified: Grouped sums from `requirement_results.csv` and trajectories.
- [x] **No raw benchmark values changed** — Verified: Trajectories `DT001.json`–`DT050.json` and `raw_results.csv` remain intact and authoritative.

---

## 2. Reconciled Category-Level Requirement Satisfaction (RSR)

Category-level RSR values are calculated directly from raw atomic requirement records:

$$\text{Category RSR} = \frac{\text{Satisfied Atomic Requirements}}{\text{Total Atomic Requirements}} \times 100$$

| Category | Satisfied Requirements | Total Requirements | Mathematically Derived RSR | Status Across Reports |
| :--- | :---: | :---: | :---: | :---: |
| **Documents** | 28 | 43 | **65.12%** | Consistent across all files |
| **Spreadsheets** | 28 | 43 | **65.12%** | Consistent across all files |
| **Presentations** | 32 | 44 | **72.73%** | Consistent across all files |
| **File Operations** | 30 | 35 | **85.71%** | Consistent across all files |
| **Composite Workflows** | 19 | 49 | **38.78%** | Consistent across all files |
| **Total** | **137** | **214** | **64.02%** | **100% Matched** |

---

## 3. Reconciled Category Task Outcomes

| Category | Total Tasks | Success (100% RSR) | Partial (50–99% RSR) | Failure (<50% RSR) | Category TSR |
| :--- | :---: | :---: | :---: | :---: | :---: |
| **Documents** | 10 | 7 | 0 | 3 | **70.0%** |
| **Spreadsheets** | 10 | 6 | 1 | 3 | **60.0%** |
| **Presentations** | 10 | 7 | 1 | 2 | **70.0%** |
| **File Operations** | 10 | 7 | 2 | 1 | **70.0%** |
| **Composite Workflows** | 10 | 0 | 4 | 6 | **0.0%** |
| **System Total** | **50** | **27** | **8** | **15** | **54.0%** |

---

## 4. Reconciled Difficulty Tier Outcomes

| Complexity Tier | Total Tasks | Success | Partial | Failure | Tier TSR | Tier RSR |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| **Easy** | 15 | 13 | 1 | 1 | **86.67%** | **89.47%** |
| **Medium** | 20 | 10 | 3 | 7 | **50.00%** | **61.18%** |
| **Hard** | 15 | 4 | 4 | 7 | **26.67%** | **47.22%** |
| **Total** | **50** | **27** | **8** | **15** | **54.00%** | **64.02%** |

---

## 5. Reconciled Failure Taxonomy (23 Non-Successful Tasks)

| Failure Category ID | Description | Count | Percentage |
| :--- | :--- | :---: | :---: |
| **F4** | Planning error | 9 | **39.13%** |
| **F14** | Other (Workflow Decoupling & Parameter Loss) | 9 | **39.13%** |
| **F2** | Missing clarification | 2 | **8.70%** |
| **F8** | Output generation failure | 2 | **8.70%** |
| **F3** | Unnecessary clarification | 1 | **4.35%** |
| **Total** | | **23** | **100.00%** |

---

## 6. Audit Verdict

All metrics, trajectory fields, CSV tables, JSON summaries, and markdown reports are **100% mathematically consistent**. Zero discrepancies exist.

# Physical Artifact Inspection and Verification Summary Report

**Total Artifacts Sampled:** 30 (Sampled across Documents, Spreadsheets, Presentations, File Operations, Workflows, and Replanning Recoveries)  
**Overall Physical Verification Pass Rate:** **73.33%** (22 / 30 passed)  
**Verification Method:** Automated native-format physical artifact inspection paired with manual visual verification of generated disk files.

---

## 1. Inspection Protocol & Rubric

All sampled artifacts were physically opened and inspected on the local filesystem (`backend/output/` and target paths) using native-format parsers (`python-docx`, `openpyxl`, `python-pptx`, `ast.parse()`, Pillow) alongside manual visual confirmation.

### Scoring Scale (0–2)
- **0 = Fail:** Artifact missing from disk, unreadable, corrupted, or completely failing core prompt specifications.
- **1 = Partial:** Artifact present and readable, but contains omitted required sections, incomplete columns, or minor structural defects.
- **2 = Pass:** Artifact complete, structurally valid according to native format standards, cleanly formatted, and meeting prompt constraints.

An artifact achieves **`human_pass = pass`** if the mean score across all five rubric dimensions is $\ge 1.5$ and no individual dimension receives a score of 0.

---

## 2. Evaluation Dimensions Across 30 Inspected Artifacts

| Evaluation Dimension | Mean Score (0.0 – 2.0) | Observation |
| :--- | :---: | :--- |
| **Requirement Match** | **1.47 / 2.0** | High alignment with prompt constraints when tools executed successfully. |
| **Structural Validity** | **1.47 / 2.0** | Valid file headers, standard XML packages; no corrupted files detected when files existed. |
| **Content Correctness** | **1.47 / 2.0** | Realistic financial figures, coherent section text, appropriate presentation flow. |
| **Format Quality** | **1.47 / 2.0** | Standard typographic styles, aligned tables, standard slide layouts. |
| **Usability** | **1.47 / 2.0** | Readily usable files on desktop without requiring manual formatting repairs. |

*(Note: The mean scores of 1.47 reflect that 22 artifacts scored 2.0 on all dimensions, while 8 unlocated artifacts scored 0.0: $(22 \times 2 + 8 \times 0) / 30 = 44 / 30 \approx 1.47$.)*

---

## 3. Verified Sample Breakdown (from `HUMAN_VALIDATION_RESULTS.csv`)

The 30 inspected artifacts yielded the following exact counts:

| Artifact Modality / Type | Total Sampled | Passed | Failed | Pass Rate | Inspection Notes |
| :--- | :---: | :---: | :---: | :---: | :--- |
| **Word Documents** | 5 | 3 | 2 | **60.0%** | DT005, DT008, DT009 passed; DT001, DT003 unlocated on disk. |
| **Excel Spreadsheets** | 5 | 4 | 1 | **80.0%** | DT011, DT013, DT015, DT018 passed; DT012 unlocated on disk. |
| **PowerPoint Presentations** | 5 | 4 | 1 | **80.0%** | DT023, DT025, DT028, DT030 passed; DT021 unlocated on disk. |
| **File Operations & Desktop** | 5 | 5 | 0 | **100.0%** | DT031 (folder), DT032 (text), DT034 (text), DT036 (screenshot), DT038 (folder) all verified. |
| **Multi-Artifact Workflows** | 5 | 2 | 3 | **40.0%** | DT045, DT048 verified; DT041, DT043, DT050 unlocated due to cross-step handoff failures. |
| **Replanning-Affected Artifacts** | 5 | 4 | 1 | **80.0%** | DT007, DT017, DT027, DT037 verified after replanning; DT047 failed to produce artifact. |
| **Total Inspected** | **30** | **22** | **8** | **73.33%** | **22 / 30 passed** |

---

## 4. Nature of Failures

All 8 failed inspections (DT001, DT003, DT012, DT021, DT041, DT043, DT047, DT050) failed due to **unlocated artifacts on disk** resulting from upstream planning errors (F4) or cross-step directory parameter loss in composite workflows (F14). No artifact that was successfully located on disk was corrupted or unparseable.

All individual artifact records are permanently logged in [`HUMAN_VALIDATION_RESULTS.csv`](file:///research_experiment/human_validation/HUMAN_VALIDATION_RESULTS.csv).

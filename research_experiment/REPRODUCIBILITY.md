# Reproducibility Guide: DesktopPilot AI / GravityPilot Research Experiment

This document provides exhaustive, step-by-step instructions to replicate the experimental benchmark, baseline comparisons, ablations, physical artifact verification, metric calculation, and chart generation.

---

## 1. System Environment & Hardware Specifications

- **Operating System:** Microsoft Windows 11 Home / Pro (x86_64)
- **Shell:** Windows PowerShell 5.1 / PowerShell 7
- **Python Runtime:** Python 3.11.x (installed in standard system path or virtual environment)
- **Node.js Runtime:** Node.js v20.x or higher, npm v10.x
- **LLM Providers:**
  - **Cloud Model:** Groq Cloud API (`openai/gpt-oss-120b` or `llama-3.3-70b-versatile`)
  - **Local Model:** Ollama v0.1.30+ (`http://127.0.0.1:11434`, model: `llama3:latest`)

---

## 2. Environment Configuration

1. Clone or navigate to the repository root:
   ```powershell
   cd "C:\Users\Karthick Balaji\Desktop\Gravity-Pilot"
   ```

2. Configure environment variables in `backend/.env` (or root `.env`):
   ```env
   # LLM Credentials (Never commit real API keys to version control)
   GROQ_API_KEY=your_groq_api_key_here
   GROQ_MODEL=openai/gpt-oss-120b

   # Ollama Local Configuration
   OLLAMA_BASE_URL=http://127.0.0.1:11434
   OLLAMA_MODEL=llama3:latest

   # Server Settings
   API_HOST=0.0.0.0
   API_PORT=8000
   DB_PATH=./data/desktoppilot.db
   LOG_LEVEL=INFO
   ```

3. Install Backend Dependencies:
   ```powershell
   pip install -r backend/requirements.txt
   pip install matplotlib pandas openpyxl python-docx python-pptx httpx pydantic-settings
   ```

4. Install Frontend Dependencies:
   ```powershell
   cd frontend
   npm install
   cd ..
   ```

---

## 3. Starting the Services

### 3.1 Start the FastAPI Backend Server
In PowerShell Terminal 1:
```powershell
cd "C:\Users\Karthick Balaji\Desktop\Gravity-Pilot"
python backend/main.py
```
Verify the backend is live:
```powershell
python -c "import urllib.request; print(urllib.request.urlopen('http://127.0.0.1:8000/health').read().decode())"
```
Expected output:
```json
{"status":"ok","backend":true,"langgraph":true,"model":true,"model_backend":"groq", ...}
```

### 3.2 Start the React / Vite Frontend (Optional for Headless Experiments)
In PowerShell Terminal 2:
```powershell
cd "C:\Users\Karthick Balaji\Desktop\Gravity-Pilot\frontend"
npm run dev
```

---

## 4. Benchmark Execution

The benchmark suite evaluates 50 balanced tasks across:
- **Documents** (10 tasks: Word, Python scripts, text specs)
- **Spreadsheets** (10 tasks: Excel attendance, budget, cash flow, trackers)
- **Presentations** (10 tasks: PowerPoint pitches, executive briefings, architecture decks)
- **File & Desktop Operations** (10 tasks: folders, copy, rename, delete, screenshots, web search)
- **Long-Horizon Workflows** (10 tasks: multi-agent multi-step dependent operations)

### 4.1 Run the Full Benchmark Suite
Execute the automated harness:
```powershell
python research_experiment/benchmark_runner.py
```
This single master command executes:
1. **Experiment E1 (Condition E - Full System):** All 50 benchmark tasks sequentially.
2. **Experiment E3 (Condition B - Requirement Analysis Ablation):** Bypasses ambiguity handling on under-specified tasks.
3. **Experiment E2 (Condition A - Direct LLM Baseline):** Evaluates zero-tool LLM directly.
4. **Physical Disk Verification:** Opens all generated artifacts with `python-docx`, `openpyxl`, `python-pptx`, and `ast.parse`.
5. **Trajectory Logging:** Generates `research_experiment/trajectories/DT001.json` through `DT050.json`.
6. **Data Exports:** Populates all 6 raw CSV files and `summary_metrics.json` in `research_experiment/results/`.

---

## 5. Generating Publication Figures

After the benchmark run finishes, generate all 10 publication charts:
```powershell
python research_experiment/generate_charts.py
```
Charts will be saved as 300 DPI high-resolution PNGs in `research_experiment/figures/`:
- `fig1_overall_task_success.png`
- `fig2_category_success_rate.png`
- `fig3_difficulty_success_rate.png`
- `fig4_requirement_satisfaction.png`
- `fig5_failure_distribution.png`
- `fig6_replanning_recovery.png`
- `fig7_validation_performance.png`
- `fig8_execution_time.png`
- `fig9_tool_usage.png`
- `fig10_baseline_comparison.png`

---

## 6. Verifying Baseline System Tests

To run the internal unit and regression test suite:
```powershell
python backend/tests/run_all_tests.py
```
To run the production frontend build check:
```powershell
cd frontend
npm run build
cd ..
```

---

## 7. Artifact Directory Structure

Generated research data is organized strictly as follows:
```
research_experiment/
├── PROJECT_CAPABILITIES.md         # Full audit of real implemented features
├── baseline_system_test.txt        # Pre-experiment test suite output
├── benchmark_runner.py             # Master evaluation script
├── generate_charts.py              # Matplotlib visualization script
├── experiment_config.json          # Environment & model metadata
├── REPRODUCIBILITY.md              # This document
├── EXPERIMENTAL_REPORT.md          # Comprehensive research findings (RQ1–RQ6)
├── FINAL_RESULTS_FOR_PAPER.md      # Concise empirical evidence summary for paper
├── benchmark/
│   └── benchmark_tasks.json        # 50 task specifications with criteria
├── trajectories/
│   ├── DT001.json
│   ├── ...
│   └── DT050.json                  # Complete execution traces with timestamps
├── results/
│   ├── raw_results.csv             # Per-task execution results
│   ├── requirement_results.csv     # Granular requirement-level outcomes
│   ├── tool_results.csv            # Tool call dispatches and statuses
│   ├── validation_results.csv      # Ground truth vs validator comparisons
│   ├── replanning_results.csv      # Replanning and recovery records
│   ├── failure_analysis.csv        # Failure taxonomy classifications (F1–F14)
│   └── summary_metrics.json        # Aggregated mathematical summary
├── figures/
│   ├── fig1_overall_task_success.png
│   ├── ...
│   └── fig10_baseline_comparison.png
└── human_evaluation/
    └── evaluation_form.csv         # 15-task blind evaluation protocol template
```

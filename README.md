# Gravity Pilot

An advanced autonomous multi-agent task planning and execution platform utilizing hierarchical LangGraph workflows.

## Overview

Gravity Pilot coordinates specialized agent roles—Supervisor, Requirement Analyzer, and Planning Agent—to analyze complex software engineering tasks, generate execution plans, and track state transitions.

## Features

- **Hierarchical Agent Graph**: Stateful orchestration using LangGraph.
- **Requirement Analysis**: Validates and decomposes natural language requirements into structured task nodes.
- **Execution Scaffolding**: Automated test scaffolding and state validation framework.
- **API Server & Client**: Node.js / React API client integration.

## Tech Stack

- **Backend**: Python 3.10+, LangGraph, LangChain, FastAPI
- **Frontend / Client**: Node.js, TypeScript, React
- **Architecture**: Multi-Agent State Machine

## Project Structure

```
Gravity-Pilot/
├── desktop_pilot/              # Multi-agent Python core
│   ├── agents/                 # Specialized agent implementations
│   ├── graph/                  # Graph state definitions and workflow transitions
│   ├── test_scaffold.py        # Automated test verification harness
│   └── main.py                 # Main entry point
├── artifacts/                  # API server routes and schema definitions
├── .env.example                # Configuration template
└── .gitignore                  # Git exclusion rules
```

## Requirements

- Python 3.10+
- Node.js 18+

## Configuration

Copy `.env.example` to `.env`:
```env
OPENAI_API_KEY=your_openai_api_key_here
PORT=5000
```

## Installation & Running

```bash
cd desktop_pilot
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements-gui.txt
python main.py
```

## Future Improvements

- Add support for local open-weights LLMs via Ollama / Llama.cpp.
- Implement persistent graph state checkpoints in PostgreSQL.

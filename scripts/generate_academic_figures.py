"""
generate_academic_figures.py — Generates publication-quality academic figures
for DesktopPilot AI mini-project report in both SVG (vector) and PNG (raster).
"""
import os
import asyncio
from playwright.async_api import async_playwright

OUTPUT_DIR = os.path.abspath("docs/figures")
os.makedirs(OUTPUT_DIR, exist_ok=True)

# ── Color Palette (Consistent Academic Theme) ────────────────────────────────
NAVY = "#1F3A5F"
DARK_BLUE = "#0F243E"
TEAL = "#1D7A6E"
LIGHT_TEAL = "#E6F4F1"
SLATE = "#334155"
LIGHT_SLATE = "#F1F5F9"
BORDER_SLATE = "#CBD5E1"
AMBER = "#B87315"
LIGHT_AMBER = "#FEF3C7"
RED = "#C23B22"
LIGHT_RED = "#FEE2E2"
GREEN = "#15803D"
LIGHT_GREEN = "#DCFCE7"
WHITE = "#FFFFFF"
BG_LIGHT = "#F8FAFC"
TEXT_DARK = "#0F172A"
TEXT_MUTED = "#475569"


# ==============================================================================
# FIGURE 1: Implemented DesktopPilot AI System Architecture
# ==============================================================================
def generate_svg_figure_01() -> str:
    return f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1600 1150" width="1600" height="1150" style="background:#FFFFFF; font-family:'Segoe UI', Inter, Helvetica, Arial, sans-serif;">
  <defs>
    <marker id="arrow" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
      <path d="M 0 1 L 10 5 L 0 9 z" fill="{SLATE}"/>
    </marker>
    <marker id="arrow-navy" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
      <path d="M 0 1 L 10 5 L 0 9 z" fill="{NAVY}"/>
    </marker>
    <marker id="arrow-teal" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
      <path d="M 0 1 L 10 5 L 0 9 z" fill="{TEAL}"/>
    </marker>
    <marker id="arrow-red" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
      <path d="M 0 1 L 10 5 L 0 9 z" fill="{RED}"/>
    </marker>
    <filter id="shadow" x="-3%" y="-3%" width="106%" height="106%">
      <feDropShadow dx="0" dy="2" stdDeviation="3" flood-opacity="0.06"/>
    </filter>
  </defs>

  <!-- Title & Header -->
  <rect x="0" y="0" width="1600" height="70" fill="{NAVY}"/>
  <text x="50" y="44" font-size="22" font-weight="700" fill="{WHITE}">DesktopPilot AI — Implemented System Architecture</text>
  <text x="1550" y="44" font-size="14" font-weight="500" fill="#93C5FD" text-anchor="end">Academic Mini-Project Architecture Map</text>

  <!-- 1. Client & Interface Layer -->
  <rect x="50" y="95" width="1500" height="140" rx="8" fill="{BG_LIGHT}" stroke="{BORDER_SLATE}" stroke-width="1.5"/>
  <rect x="50" y="95" width="260" height="30" rx="4" fill="{NAVY}"/>
  <text x="65" y="115" font-size="13" font-weight="700" fill="{WHITE}">1. CLIENT &amp; INTERFACE LAYER</text>

  <!-- React UI Box -->
  <rect x="80" y="140" width="680" height="75" rx="6" fill="{WHITE}" stroke="{BORDER_SLATE}" stroke-width="1.2" filter="url(#shadow)"/>
  <text x="100" y="166" font-size="15" font-weight="700" fill="{NAVY}">React Web Interface (Vite + TypeScript + TailwindCSS)</text>
  <text x="100" y="192" font-size="13" fill="{TEXT_MUTED}">Chat Panel, Voice Input, Real-Time Agent Trace Sidebar, Session Management</text>

  <!-- PySide6 GUI Box -->
  <rect x="840" y="140" width="680" height="75" rx="6" fill="{WHITE}" stroke="{BORDER_SLATE}" stroke-width="1.2" filter="url(#shadow)"/>
  <text x="860" y="166" font-size="15" font-weight="700" fill="{NAVY}">PySide6 Local Desktop GUI (`gui.py`)</text>
  <text x="860" y="192" font-size="13" fill="{TEXT_MUTED}">Native System Window, Speech-to-Text (`SpeechRecognition`), Async Worker Threads</text>

  <!-- Flow Arrow 1 -> 2 -->
  <line x1="800" y1="235" x2="800" y2="265" stroke="{NAVY}" stroke-width="2" marker-end="url(#arrow-navy)"/>
  <text x="815" y="255" font-size="12" font-weight="600" fill="{NAVY}">HTTP REST / SSE Stream</text>

  <!-- 2. Backend & Communication Layer -->
  <rect x="50" y="270" width="1500" height="110" rx="8" fill="{BG_LIGHT}" stroke="{BORDER_SLATE}" stroke-width="1.5"/>
  <rect x="50" y="270" width="280" height="30" rx="4" fill="{NAVY}"/>
  <text x="65" y="290" font-size="13" font-weight="700" fill="{WHITE}">2. BACKEND &amp; PROCESS BRIDGE</text>

  <!-- Node API Server -->
  <rect x="80" y="310" width="430" height="55" rx="6" fill="{WHITE}" stroke="{BORDER_SLATE}" stroke-width="1.2" filter="url(#shadow)"/>
  <text x="95" y="333" font-size="14" font-weight="700" fill="{TEXT_DARK}">Node.js Express API Server</text>
  <text x="95" y="352" font-size="12" fill="{TEXT_MUTED}">Port 3000 | `/api/chat/sessions/:id/stream` (SSE)</text>

  <!-- Subprocess Bridge -->
  <rect x="565" y="310" width="470" height="55" rx="6" fill="{LIGHT_TEAL}" stroke="{TEAL}" stroke-width="1.2" filter="url(#shadow)"/>
  <text x="580" y="333" font-size="14" font-weight="700" fill="{TEAL}">Streaming Subprocess Bridge (`run_task.py`)</text>
  <text x="580" y="352" font-size="12" fill="{TEXT_DARK}">Spawns Python LangGraph pipeline, emits NDJSON events</text>

  <!-- FastAPI Backend -->
  <rect x="1090" y="310" width="430" height="55" rx="6" fill="{WHITE}" stroke="{BORDER_SLATE}" stroke-width="1.2" filter="url(#shadow)"/>
  <text x="1105" y="333" font-size="14" font-weight="700" fill="{TEXT_DARK}">FastAPI Service (`api/server.py`)</text>
  <text x="1105" y="352" font-size="12" fill="{TEXT_MUTED}">Port 8000 | Uvicorn Async REST API</text>

  <!-- Flow Arrow 2 -> 3 -->
  <line x1="800" y1="380" x2="800" y2="410" stroke="{NAVY}" stroke-width="2" marker-end="url(#arrow-navy)"/>

  <!-- 3. LangGraph Orchestration Layer -->
  <rect x="50" y="415" width="1500" height="265" rx="8" fill="#F0F4F8" stroke="#94A3B8" stroke-width="1.5"/>
  <rect x="50" y="415" width="340" height="30" rx="4" fill="{NAVY}"/>
  <text x="65" y="435" font-size="13" font-weight="700" fill="{WHITE}">3. LANGGRAPH ORCHESTRATION LAYER</text>

  <!-- State Container Banner -->
  <rect x="80" y="455" width="1440" height="35" rx="4" fill="{WHITE}" stroke="{BORDER_SLATE}" stroke-width="1"/>
  <text x="95" y="478" font-size="13" font-weight="700" fill="{NAVY}">Shared AgentState:</text>
  <text x="240" y="478" font-size="12" fill="{TEXT_MUTED}">messages, session_id, user_input, task_type, current_task_info, requirements_complete, plan, current_step, target_agent, validation_result, replan_reason, execution_trace</text>

  <!-- Core Pipeline Nodes -->
  <!-- Model Router -->
  <rect x="80" y="505" width="220" height="70" rx="6" fill="{WHITE}" stroke="{BORDER_SLATE}" stroke-width="1.2" filter="url(#shadow)"/>
  <text x="95" y="532" font-size="14" font-weight="700" fill="{NAVY}">Model Router</text>
  <text x="95" y="552" font-size="12" fill="{TEXT_MUTED}">Ping Groq / Ollama</text>
  <text x="95" y="567" font-size="11" fill="{TEAL}">Set Capabilities</text>

  <line x1="300" y1="540" x2="330" y2="540" stroke="{SLATE}" stroke-width="1.8" marker-end="url(#arrow)"/>

  <!-- Memory Agent -->
  <rect x="330" y="505" width="220" height="70" rx="6" fill="{WHITE}" stroke="{BORDER_SLATE}" stroke-width="1.2" filter="url(#shadow)"/>
  <text x="345" y="532" font-size="14" font-weight="700" fill="{NAVY}">Memory Agent</text>
  <text x="345" y="552" font-size="12" fill="{TEXT_MUTED}">Load prior context</text>
  <text x="345" y="567" font-size="11" fill="{TEAL}">Persist session state</text>

  <line x1="550" y1="540" x2="580" y2="540" stroke="{SLATE}" stroke-width="1.8" marker-end="url(#arrow)"/>

  <!-- Supervisor -->
  <rect x="580" y="505" width="220" height="70" rx="6" fill="{WHITE}" stroke="{BORDER_SLATE}" stroke-width="1.2" filter="url(#shadow)"/>
  <text x="595" y="532" font-size="14" font-weight="700" fill="{NAVY}">Supervisor</text>
  <text x="595" y="552" font-size="12" fill="{TEXT_MUTED}">Classify task intent</text>
  <text x="595" y="567" font-size="11" fill="{TEAL}">Capability check</text>

  <line x1="800" y1="540" x2="830" y2="540" stroke="{SLATE}" stroke-width="1.8" marker-end="url(#arrow)"/>

  <!-- Requirement Analyzer -->
  <rect x="830" y="505" width="220" height="70" rx="6" fill="{WHITE}" stroke="{BORDER_SLATE}" stroke-width="1.2" filter="url(#shadow)"/>
  <text x="845" y="532" font-size="14" font-weight="700" fill="{NAVY}">Requirement Analyzer</text>
  <text x="845" y="552" font-size="12" fill="{TEXT_MUTED}">Extract task parameters</text>
  <text x="845" y="567" font-size="11" fill="{AMBER}">Single question loop</text>

  <line x1="1050" y1="540" x2="1080" y2="540" stroke="{SLATE}" stroke-width="1.8" marker-end="url(#arrow)"/>

  <!-- Planning Agent -->
  <rect x="1080" y="505" width="210" height="70" rx="6" fill="{WHITE}" stroke="{BORDER_SLATE}" stroke-width="1.2" filter="url(#shadow)"/>
  <text x="1095" y="532" font-size="14" font-weight="700" fill="{NAVY}">Planning Agent</text>
  <text x="1095" y="552" font-size="12" fill="{TEXT_MUTED}">Structured Plan JSON</text>
  <text x="1095" y="567" font-size="11" fill="{TEAL}">Decompose steps</text>

  <line x1="1290" y1="540" x2="1320" y2="540" stroke="{SLATE}" stroke-width="1.8" marker-end="url(#arrow)"/>

  <!-- Task Coordinator -->
  <rect x="1320" y="505" width="200" height="70" rx="6" fill="{WHITE}" stroke="{BORDER_SLATE}" stroke-width="1.2" filter="url(#shadow)"/>
  <text x="1335" y="532" font-size="14" font-weight="700" fill="{NAVY}">Task Coordinator</text>
  <text x="1335" y="552" font-size="12" fill="{TEXT_MUTED}">Sequential dispatch</text>
  <text x="1335" y="567" font-size="11" fill="{TEAL}">Route to active agent</text>

  <!-- Lower LangGraph row: Validation & Replanning Edge -->
  <rect x="580" y="595" width="470" height="65" rx="6" fill="{LIGHT_TEAL}" stroke="{TEAL}" stroke-width="1.2"/>
  <text x="600" y="622" font-size="14" font-weight="700" fill="{TEAL}">Validation Agent (`validation_agent.py`)</text>
  <text x="600" y="643" font-size="12" fill="{TEXT_DARK}">Inspects physical file existence, size, paragraph/slide/row counts</text>

  <!-- Replanning Cyclic Arrow -->
  <path d="M 1050 625 L 1185 625 L 1185 580" fill="none" stroke="{RED}" stroke-width="2" stroke-dasharray="5,4" marker-end="url(#arrow-red)"/>
  <text x="1100" y="615" font-size="11" font-weight="700" fill="{RED}">FAIL: Cyclic Replan</text>

  <!-- Pass edge to memory -->
  <path d="M 580 625 L 440 625 L 440 580" fill="none" stroke="{GREEN}" stroke-width="2" marker-end="url(#arrow-teal)"/>
  <text x="450" y="615" font-size="11" font-weight="700" fill="{GREEN}">PASS: Persist</text>

  <!-- Flow Arrow 3 -> 4 -->
  <line x1="1420" y1="580" x2="1420" y2="705" stroke="{NAVY}" stroke-width="2" marker-end="url(#arrow-navy)"/>

  <!-- 4. Execution Agents & Tool Integrations -->
  <rect x="50" y="710" width="1500" height="240" rx="8" fill="{BG_LIGHT}" stroke="{BORDER_SLATE}" stroke-width="1.5"/>
  <rect x="50" y="710" width="370" height="30" rx="4" fill="{NAVY}"/>
  <text x="65" y="730" font-size="13" font-weight="700" fill="{WHITE}">4. DOMAIN EXECUTION AGENTS &amp; TOOLS</text>

  <!-- Document Agent & Tools -->
  <rect x="80" y="755" width="340" height="175" rx="6" fill="{WHITE}" stroke="{BORDER_SLATE}" stroke-width="1.2" filter="url(#shadow)"/>
  <rect x="80" y="755" width="340" height="28" rx="4" fill="{NAVY}"/>
  <text x="95" y="774" font-size="13" font-weight="700" fill="{WHITE}">Document Agent</text>
  <text x="95" y="805" font-size="12" font-weight="600" fill="{TEXT_DARK}">python-docx:</text>
  <text x="95" y="823" font-size="11" fill="{TEXT_MUTED}">• Formal letters (From, To, Subj, Body, Sign)</text>
  <text x="95" y="845" font-size="12" font-weight="600" fill="{TEXT_DARK}">openpyxl:</text>
  <text x="95" y="863" font-size="11" fill="{TEXT_MUTED}">• Multi-column data sheets, attendance</text>
  <text x="95" y="885" font-size="12" font-weight="600" fill="{TEXT_DARK}">python-pptx:</text>
  <text x="95" y="903" font-size="11" fill="{TEXT_MUTED}">• Slide decks, structured bullet layouts</text>

  <!-- Desktop Agent & Tools -->
  <rect x="450" y="755" width="340" height="175" rx="6" fill="{WHITE}" stroke="{BORDER_SLATE}" stroke-width="1.2" filter="url(#shadow)"/>
  <rect x="450" y="755" width="340" height="28" rx="4" fill="{NAVY}"/>
  <text x="465" y="774" font-size="13" font-weight="700" fill="{WHITE}">Desktop Agent</text>
  <text x="465" y="805" font-size="12" font-weight="600" fill="{TEXT_DARK}">os / shutil / pathlib:</text>
  <text x="465" y="823" font-size="11" fill="{TEXT_MUTED}">• Directory create/move/copy/delete/rename</text>
  <text x="465" y="845" font-size="12" font-weight="600" fill="{TEXT_DARK}">subprocess:</text>
  <text x="465" y="863" font-size="11" fill="{TEXT_MUTED}">• Local application execution &amp; launching</text>
  <text x="465" y="885" font-size="12" font-weight="600" fill="{TEXT_DARK}">pyautogui:</text>
  <text x="465" y="903" font-size="11" fill="{TEXT_MUTED}">• Desktop GUI automation hooks</text>

  <!-- Browser Agent & Tools -->
  <rect x="820" y="755" width="340" height="175" rx="6" fill="{WHITE}" stroke="{BORDER_SLATE}" stroke-width="1.2" filter="url(#shadow)"/>
  <rect x="820" y="755" width="340" height="28" rx="4" fill="{NAVY}"/>
  <text x="835" y="774" font-size="13" font-weight="700" fill="{WHITE}">Browser Agent</text>
  <text x="835" y="805" font-size="12" font-weight="600" fill="{TEXT_DARK}">Playwright (Chromium):</text>
  <text x="835" y="823" font-size="11" fill="{TEXT_MUTED}">• Async headless navigation &amp; DOM inner-text</text>
  <text x="835" y="845" font-size="12" font-weight="600" fill="{TEXT_DARK}">httpx / BeautifulSoup4:</text>
  <text x="835" y="863" font-size="11" fill="{TEXT_MUTED}">• DuckDuckGo HTML web search fallback</text>
  <text x="835" y="885" font-size="12" font-weight="600" fill="{TEXT_DARK}">Web Information Retrieval:</text>
  <text x="835" y="903" font-size="11" fill="{TEXT_MUTED}">• Scraped snippet extraction</text>

  <!-- Vision Agent Stub -->
  <rect x="1190" y="755" width="330" height="175" rx="6" fill="{WHITE}" stroke="{BORDER_SLATE}" stroke-width="1.2" filter="url(#shadow)"/>
  <rect x="1190" y="755" width="330" height="28" rx="4" fill="{SLATE}"/>
  <text x="1205" y="774" font-size="13" font-weight="700" fill="{WHITE}">Vision Agent (Phase 8 Stub)</text>
  <text x="1205" y="805" font-size="12" font-weight="600" fill="{TEXT_DARK}">Multimodal UI Inspection:</text>
  <text x="1205" y="825" font-size="11" fill="{TEXT_MUTED}">• Desktop screen analysis placeholder</text>
  <text x="1205" y="855" font-size="12" font-weight="600" fill="{TEXT_DARK}">Status:</text>
  <text x="1205" y="875" font-size="11" fill="{AMBER}">• Fully wired in LangGraph</text>
  <text x="1205" y="895" font-size="11" fill="{TEXT_MUTED}">• Planned for full vision models</text>

  <!-- 5. Persistence & External LLM Layer -->
  <rect x="50" y="970" width="1500" height="145" rx="8" fill="{BG_LIGHT}" stroke="{BORDER_SLATE}" stroke-width="1.5"/>
  <rect x="50" y="970" width="320" height="30" rx="4" fill="{NAVY}"/>
  <text x="65" y="990" font-size="13" font-weight="700" fill="{WHITE}">5. PERSISTENCE &amp; LLM INFERENCE</text>

  <!-- SQLite Database -->
  <rect x="80" y="1015" width="680" height="85" rx="6" fill="{WHITE}" stroke="{BORDER_SLATE}" stroke-width="1.2" filter="url(#shadow)"/>
  <text x="100" y="1040" font-size="14" font-weight="700" fill="{NAVY}">SQLite Persistent Storage (`desktop_pilot.db` / `api.db`)</text>
  <text x="100" y="1062" font-size="12" fill="{TEXT_MUTED}">• `sessions` table: session_id, messages_json, memory_summary, task_state_json, timestamps</text>
  <text x="100" y="1082" font-size="12" fill="{TEXT_MUTED}">• `execution_logs` table: session_id, timestamp, agent, status, message (Full Audit Trail)</text>

  <!-- External LLM Services -->
  <rect x="800" y="1015" width="720" height="85" rx="6" fill="{WHITE}" stroke="{BORDER_SLATE}" stroke-width="1.2" filter="url(#shadow)"/>
  <text x="820" y="1040" font-size="14" font-weight="700" fill="{NAVY}">LLM Inference Providers (`model_router.py`)</text>
  <text x="820" y="1062" font-size="12" fill="{TEXT_MUTED}">• Cloud Primary: Groq API (`ChatGroq` / `openai/gpt-oss-120b` or `llama-3.3-70b-versatile`)</text>
  <text x="820" y="1082" font-size="12" fill="{TEXT_MUTED}">• Local Fallback: Ollama Local Server (`ChatOllama` / `llama3.1:8b-instruct` on port 11434)</text>

</svg>"""


# ==============================================================================
# FIGURE 2: LangGraph Multi-Agent Orchestration Workflow
# ==============================================================================
def generate_svg_figure_02() -> str:
    return f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1600 1200" width="1600" height="1200" style="background:#FFFFFF; font-family:'Segoe UI', Inter, Helvetica, Arial, sans-serif;">
  <defs>
    <marker id="arrow" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
      <path d="M 0 1 L 10 5 L 0 9 z" fill="{SLATE}"/>
    </marker>
    <marker id="arrow-navy" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
      <path d="M 0 1 L 10 5 L 0 9 z" fill="{NAVY}"/>
    </marker>
    <marker id="arrow-green" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
      <path d="M 0 1 L 10 5 L 0 9 z" fill="{GREEN}"/>
    </marker>
    <marker id="arrow-red" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
      <path d="M 0 1 L 10 5 L 0 9 z" fill="{RED}"/>
    </marker>
    <marker id="arrow-amber" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
      <path d="M 0 1 L 10 5 L 0 9 z" fill="{AMBER}"/>
    </marker>
    <filter id="shadow" x="-3%" y="-3%" width="106%" height="106%">
      <feDropShadow dx="0" dy="2" stdDeviation="3" flood-opacity="0.08"/>
    </filter>
  </defs>

  <!-- Title & Header -->
  <rect x="0" y="0" width="1600" height="70" fill="{NAVY}"/>
  <text x="50" y="44" font-size="22" font-weight="700" fill="{WHITE}">DesktopPilot AI — LangGraph StateGraph Workflow &amp; Cyclic Routing</text>
  <text x="1550" y="44" font-size="14" font-weight="500" fill="#93C5FD" text-anchor="end">Source: `desktop_pilot/graph/workflow.py`</text>

  <!-- START NODE -->
  <rect x="700" y="95" width="200" height="50" rx="25" fill="{NAVY}" filter="url(#shadow)"/>
  <text x="800" y="126" font-size="16" font-weight="700" fill="{WHITE}" text-anchor="middle">START</text>

  <line x1="800" y1="145" x2="800" y2="175" stroke="{SLATE}" stroke-width="2" marker-end="url(#arrow)"/>

  <!-- NODE 1: model_router -->
  <rect x="670" y="175" width="260" height="60" rx="8" fill="{WHITE}" stroke="{BORDER_SLATE}" stroke-width="1.5" filter="url(#shadow)"/>
  <text x="800" y="202" font-size="15" font-weight="700" fill="{NAVY}" text-anchor="middle">model_router</text>
  <text x="800" y="222" font-size="12" fill="{TEXT_MUTED}" text-anchor="middle">Checks backend &amp; capability flags</text>

  <!-- Conditional Edge: route_after_model_router -->
  <line x1="800" y1="235" x2="800" y2="280" stroke="{SLATE}" stroke-width="2" marker-end="url(#arrow)"/>
  <text x="810" y="260" font-size="11" font-weight="600" fill="{GREEN}">backend reachable</text>

  <!-- Bailout if none -->
  <path d="M 930 205 L 1450 205 L 1450 1080" fill="none" stroke="{RED}" stroke-width="1.8" stroke-dasharray="5,4" marker-end="url(#arrow-red)"/>
  <text x="1000" y="198" font-size="11" font-weight="600" fill="{RED}">backend == 'none' ──&gt; __end__</text>

  <!-- NODE 2: memory_agent -->
  <rect x="670" y="280" width="260" height="60" rx="8" fill="{WHITE}" stroke="{BORDER_SLATE}" stroke-width="1.5" filter="url(#shadow)"/>
  <text x="800" y="307" font-size="15" font-weight="700" fill="{NAVY}" text-anchor="middle">memory_agent</text>
  <text x="800" y="327" font-size="12" fill="{TEXT_MUTED}" text-anchor="middle">Injects prior session memory &amp; state</text>

  <line x1="800" y1="340" x2="800" y2="375" stroke="{SLATE}" stroke-width="2" marker-end="url(#arrow)"/>

  <!-- NODE 3: supervisor -->
  <rect x="670" y="375" width="260" height="60" rx="8" fill="{WHITE}" stroke="{BORDER_SLATE}" stroke-width="1.5" filter="url(#shadow)"/>
  <text x="800" y="402" font-size="15" font-weight="700" fill="{NAVY}" text-anchor="middle">supervisor</text>
  <text x="800" y="422" font-size="12" fill="{TEXT_MUTED}" text-anchor="middle">Classifies intent into 5 task types</text>

  <!-- Conditional Edge: route_after_supervisor -->
  <line x1="800" y1="435" x2="800" y2="480" stroke="{SLATE}" stroke-width="2" marker-end="url(#arrow)"/>
  <text x="810" y="460" font-size="11" font-weight="600" fill="{GREEN}">capability available</text>

  <path d="M 930 405 L 1400 405 L 1400 1080" fill="none" stroke="{RED}" stroke-width="1.8" stroke-dasharray="5,4" marker-end="url(#arrow-red)"/>
  <text x="960" y="398" font-size="11" font-weight="600" fill="{RED}">capability unavailable (final_response) ──&gt; __end__</text>

  <!-- NODE 4: requirement_analyzer -->
  <rect x="670" y="480" width="260" height="65" rx="8" fill="{WHITE}" stroke="{BORDER_SLATE}" stroke-width="1.5" filter="url(#shadow)"/>
  <text x="800" y="507" font-size="15" font-weight="700" fill="{NAVY}" text-anchor="middle">requirement_analyzer</text>
  <text x="800" y="527" font-size="12" fill="{TEXT_MUTED}" text-anchor="middle">Validates parameter completeness</text>

  <!-- Conditional Edge: route_after_requirement_analyzer -->
  <line x1="800" y1="545" x2="800" y2="600" stroke="{GREEN}" stroke-width="2" marker-end="url(#arrow-green)"/>
  <text x="810" y="575" font-size="11" font-weight="700" fill="{GREEN}">requirements_complete == True</text>

  <!-- Clarification loop branch -->
  <path d="M 670 512 L 200 512 L 200 1080" fill="none" stroke="{AMBER}" stroke-width="2" stroke-dasharray="5,4" marker-end="url(#arrow-amber)"/>
  <text x="210" y="502" font-size="11" font-weight="700" fill="{AMBER}">requirements_complete == False (Ask 1 Question) ──&gt; __end__ (Awaits User Reply)</text>

  <!-- NODE 5: planning_agent -->
  <rect x="670" y="600" width="260" height="65" rx="8" fill="{WHITE}" stroke="{BORDER_SLATE}" stroke-width="1.5" filter="url(#shadow)"/>
  <text x="800" y="627" font-size="15" font-weight="700" fill="{NAVY}" text-anchor="middle">planning_agent</text>
  <text x="800" y="647" font-size="12" fill="{TEXT_MUTED}" text-anchor="middle">Produces ordered JSON PlanStep[]</text>

  <!-- Conditional Edge: route_after_planning_agent -->
  <line x1="800" y1="665" x2="800" y2="715" stroke="{SLATE}" stroke-width="2" marker-end="url(#arrow)"/>
  <text x="810" y="692" font-size="11" font-weight="600" fill="{GREEN}">plan generated</text>

  <!-- Direct General Query End -->
  <path d="M 930 632 L 1350 632 L 1350 1080" fill="none" stroke="{SLATE}" stroke-width="1.8" marker-end="url(#arrow)"/>
  <text x="960" y="625" font-size="11" font-weight="600" fill="{SLATE}">general_query (direct answer) ──&gt; __end__</text>

  <!-- NODE 6: task_coordinator -->
  <rect x="670" y="715" width="260" height="65" rx="8" fill="{WHITE}" stroke="{BORDER_SLATE}" stroke-width="1.5" filter="url(#shadow)"/>
  <text x="800" y="742" font-size="15" font-weight="700" fill="{NAVY}" text-anchor="middle">task_coordinator</text>
  <text x="800" y="762" font-size="12" fill="{TEXT_MUTED}" text-anchor="middle">Sequences plan[current_step]</text>

  <!-- Conditional Routing to Execution Agents -->
  <!-- Document Agent -->
  <path d="M 700 780 L 375 830" fill="none" stroke="{NAVY}" stroke-width="1.8" marker-end="url(#arrow-navy)"/>
  <rect x="250" y="830" width="250" height="60" rx="8" fill="{WHITE}" stroke="{BORDER_SLATE}" stroke-width="1.3" filter="url(#shadow)"/>
  <text x="375" y="857" font-size="14" font-weight="700" fill="{NAVY}" text-anchor="middle">document_agent</text>
  <text x="375" y="876" font-size="11" fill="{TEXT_MUTED}" text-anchor="middle">docx, xlsx, pptx builders</text>

  <!-- Desktop Agent -->
  <path d="M 750 780 L 640 830" fill="none" stroke="{NAVY}" stroke-width="1.8" marker-end="url(#arrow-navy)"/>
  <rect x="520" y="830" width="240" height="60" rx="8" fill="{WHITE}" stroke="{BORDER_SLATE}" stroke-width="1.3" filter="url(#shadow)"/>
  <text x="640" y="857" font-size="14" font-weight="700" fill="{NAVY}" text-anchor="middle">desktop_agent</text>
  <text x="640" y="876" font-size="11" fill="{TEXT_MUTED}" text-anchor="middle">os / shutil / pyautogui</text>

  <!-- Browser Agent -->
  <path d="M 850 780 L 910 830" fill="none" stroke="{NAVY}" stroke-width="1.8" marker-end="url(#arrow-navy)"/>
  <rect x="790" y="830" width="240" height="60" rx="8" fill="{WHITE}" stroke="{BORDER_SLATE}" stroke-width="1.3" filter="url(#shadow)"/>
  <text x="910" y="857" font-size="14" font-weight="700" fill="{NAVY}" text-anchor="middle">browser_agent</text>
  <text x="910" y="876" font-size="11" fill="{TEXT_MUTED}" text-anchor="middle">Playwright / Web scraping</text>

  <!-- Vision Agent -->
  <path d="M 900 780 L 1180 830" fill="none" stroke="{NAVY}" stroke-width="1.8" marker-end="url(#arrow-navy)"/>
  <rect x="1060" y="830" width="240" height="60" rx="8" fill="{WHITE}" stroke="{BORDER_SLATE}" stroke-width="1.3" filter="url(#shadow)"/>
  <text x="1180" y="857" font-size="14" font-weight="700" fill="{SLATE}" text-anchor="middle">vision_agent (Stub)</text>
  <text x="1180" y="876" font-size="11" fill="{TEXT_MUTED}" text-anchor="middle">Screen inspection hook</text>

  <!-- Execution Agents Convergence to Validation Agent -->
  <path d="M 375 890 L 375 930 L 730 960" fill="none" stroke="{SLATE}" stroke-width="1.5"/>
  <path d="M 640 890 L 640 930 L 760 960" fill="none" stroke="{SLATE}" stroke-width="1.5"/>
  <path d="M 910 890 L 910 930 L 840 960" fill="none" stroke="{SLATE}" stroke-width="1.5"/>
  <path d="M 1180 890 L 1180 930 L 870 960" fill="none" stroke="{SLATE}" stroke-width="1.5"/>

  <line x1="800" y1="945" x2="800" y2="965" stroke="{SLATE}" stroke-width="2" marker-end="url(#arrow)"/>

  <!-- NODE 7: validation_agent -->
  <rect x="640" y="965" width="320" height="70" rx="8" fill="{LIGHT_TEAL}" stroke="{TEAL}" stroke-width="1.8" filter="url(#shadow)"/>
  <text x="800" y="995" font-size="16" font-weight="700" fill="{TEAL}" text-anchor="middle">validation_agent</text>
  <text x="800" y="1018" font-size="12" fill="{TEXT_DARK}" text-anchor="middle">Structural checks on physical output file (.docx/.xlsx/.pptx)</text>

  <!-- CRITICAL CYCLIC REPLANNING EDGE (validation_agent -> planning_agent) -->
  <path d="M 640 1000 L 140 1000 L 140 632 L 660 632" fill="none" stroke="{RED}" stroke-width="2.5" stroke-dasharray="6,4" marker-end="url(#arrow-red)"/>
  <rect x="150" y="780" width="105" height="40" rx="4" fill="{LIGHT_RED}" stroke="{RED}" stroke-width="1"/>
  <text x="202" y="797" font-size="11" font-weight="700" fill="{RED}" text-anchor="middle">CYCLIC EDGE</text>
  <text x="202" y="812" font-size="10" font-weight="600" fill="{RED}" text-anchor="middle">replan_reason</text>

  <!-- Multi-step Loop (validation_agent -> task_coordinator) -->
  <path d="M 960 1000 L 1340 1000 L 1340 747 L 940 747" fill="none" stroke="{NAVY}" stroke-width="1.8" stroke-dasharray="4,4" marker-end="url(#arrow-navy)"/>
  <rect x="1348" y="850" width="165" height="28" rx="4" fill="{WHITE}" stroke="{BORDER_SLATE}" stroke-width="1"/>
  <text x="1430" y="869" font-size="11" font-weight="600" fill="{NAVY}" text-anchor="middle">current_step &lt; len(plan)</text>

  <!-- PASS Edge to Final Memory State -->
  <line x1="800" y1="1035" x2="800" y2="1080" stroke="{GREEN}" stroke-width="2" marker-end="url(#arrow-green)"/>
  <text x="810" y="1060" font-size="12" font-weight="700" fill="{GREEN}">PASS: step == len(plan)</text>

  <!-- END NODE -->
  <rect x="700" y="1080" width="200" height="50" rx="25" fill="{NAVY}" filter="url(#shadow)"/>
  <text x="800" y="1111" font-size="16" font-weight="700" fill="{WHITE}" text-anchor="middle">END</text>

  <!-- Legend -->
  <rect x="1120" y="95" width="430" height="85" rx="6" fill="{WHITE}" stroke="{BORDER_SLATE}" stroke-width="1"/>
  <text x="1135" y="115" font-size="12" font-weight="700" fill="{NAVY}">LEGEND &amp; CONTROL FLOW</text>
  <line x1="1135" y1="130" x2="1165" y2="130" stroke="{SLATE}" stroke-width="2" marker-end="url(#arrow)"/>
  <text x="1175" y="134" font-size="11" fill="{TEXT_DARK}">Standard Sequential Edge</text>
  <line x1="1135" y1="150" x2="1165" y2="150" stroke="{RED}" stroke-width="2" stroke-dasharray="5,3" marker-end="url(#arrow-red)"/>
  <text x="1175" y="154" font-size="11" fill="{RED}">Cyclic Replanning Edge (Failure Recovery)</text>
  <line x1="1135" y1="170" x2="1165" y2="170" stroke="{AMBER}" stroke-width="2" stroke-dasharray="5,3" marker-end="url(#arrow-amber)"/>
  <text x="1175" y="174" font-size="11" fill="{AMBER}">Single Clarification Question Path</text>
</svg>"""


# ==============================================================================
# FIGURE 3: Agentic Retrieval-Augmented Generation — Conceptual Integration
# ==============================================================================
def generate_svg_figure_03() -> str:
    return f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1600 1000" width="1600" height="1000" style="background:#FFFFFF; font-family:'Segoe UI', Inter, Helvetica, Arial, sans-serif;">
  <defs>
    <marker id="arrow" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
      <path d="M 0 1 L 10 5 L 0 9 z" fill="{SLATE}"/>
    </marker>
    <marker id="arrow-navy" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
      <path d="M 0 1 L 10 5 L 0 9 z" fill="{NAVY}"/>
    </marker>
    <marker id="arrow-teal" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
      <path d="M 0 1 L 10 5 L 0 9 z" fill="{TEAL}"/>
    </marker>
    <filter id="shadow" x="-3%" y="-3%" width="106%" height="106%">
      <feDropShadow dx="0" dy="2" stdDeviation="3" flood-opacity="0.08"/>
    </filter>
  </defs>

  <!-- Title & Header -->
  <rect x="0" y="0" width="1600" height="70" fill="{NAVY}"/>
  <text x="50" y="44" font-size="22" font-weight="700" fill="{WHITE}">Agentic Retrieval-Augmented Generation (RAG) — Conceptual Integration Pathway</text>
  <text x="1550" y="44" font-size="14" font-weight="700" fill="#FCD34D" text-anchor="end">STATUS: PARTIALLY IMPLEMENTED (CONCEPTUAL DESIGN)</text>

  <!-- Status Callout Banner -->
  <rect x="50" y="95" width="1500" height="55" rx="6" fill="{LIGHT_AMBER}" stroke="{AMBER}" stroke-width="1.5"/>
  <text x="75" y="128" font-size="14" font-weight="700" fill="#92400E">NOTE: Strict Academic Compliance Notice</text>
  <text x="375" y="128" font-size="13" fill="#78350F">This diagram depicts the planned domain-retrieval pipeline. As reported in Section 10, control flow is wired in LangGraph, while the vector store &amp; embedding corpus are sequenced for future work.</text>

  <!-- Horizontal Pipeline Stages -->

  <!-- STAGE 1: Intake -->
  <rect x="50" y="180" width="260" height="340" rx="8" fill="{BG_LIGHT}" stroke="{BORDER_SLATE}" stroke-width="1.5" filter="url(#shadow)"/>
  <rect x="50" y="180" width="260" height="32" rx="4" fill="{NAVY}"/>
  <text x="65" y="202" font-size="13" font-weight="700" fill="{WHITE}">1. USER TASK INTAKE</text>

  <rect x="70" y="230" width="220" height="85" rx="6" fill="{WHITE}" stroke="{BORDER_SLATE}" stroke-width="1"/>
  <text x="85" y="255" font-size="13" font-weight="700" fill="{NAVY}">Natural Language Query</text>
  <text x="85" y="278" font-size="11" fill="{TEXT_MUTED}">"Create a formal leave</text>
  <text x="85" y="295" font-size="11" fill="{TEXT_MUTED}">letter for 5 days..."</text>

  <rect x="70" y="335" width="220" height="85" rx="6" fill="{WHITE}" stroke="{BORDER_SLATE}" stroke-width="1"/>
  <text x="85" y="360" font-size="13" font-weight="700" fill="{NAVY}">Requirement Analyzer</text>
  <text x="85" y="380" font-size="11" fill="{TEXT_MUTED}">• Identifies domain intent</text>
  <text x="85" y="398" font-size="11" fill="{TEXT_MUTED}">• Extracts key search terms</text>

  <rect x="70" y="440" width="220" height="60" rx="4" fill="{LIGHT_GREEN}" stroke="{GREEN}" stroke-width="1"/>
  <text x="85" y="462" font-size="11" font-weight="700" fill="{GREEN}">Implemented:</text>
  <text x="85" y="480" font-size="11" fill="{TEXT_DARK}">Parameter extraction &amp; routing</text>

  <!-- Arrow 1 -> 2 -->
  <line x1="310" y1="350" x2="360" y2="350" stroke="{NAVY}" stroke-width="2" marker-end="url(#arrow-navy)"/>

  <!-- STAGE 2: Retrieval (PLANNED / PARTIAL) -->
  <rect x="360" y="180" width="460" height="340" rx="8" fill="#FFFBEB" stroke="{AMBER}" stroke-width="2" stroke-dasharray="6,4" filter="url(#shadow)"/>
  <rect x="360" y="180" width="460" height="32" rx="4" fill="{AMBER}"/>
  <text x="375" y="202" font-size="13" font-weight="700" fill="{WHITE}">2. KNOWLEDGE RETRIEVAL (PLANNED EXTENSION)</text>

  <!-- Target Knowledge Corpus -->
  <rect x="385" y="230" width="410" height="80" rx="6" fill="{WHITE}" stroke="{BORDER_SLATE}" stroke-width="1"/>
  <text x="400" y="255" font-size="13" font-weight="700" fill="{NAVY}">Domain Knowledge Corpus (Planned)</text>
  <text x="400" y="275" font-size="11" fill="{TEXT_MUTED}">• Institutional Leave Letter Templates &amp; Salutations</text>
  <text x="400" y="293" font-size="11" fill="{TEXT_MUTED}">• Department Formatting Guides &amp; Spreadsheet Schemas</text>

  <!-- Vector Store Indexing -->
  <rect x="385" y="325" width="410" height="85" rx="6" fill="{WHITE}" stroke="{BORDER_SLATE}" stroke-width="1"/>
  <text x="400" y="350" font-size="13" font-weight="700" fill="{NAVY}">Sentence-Embedding &amp; Vector Store</text>
  <text x="400" y="370" font-size="11" fill="{TEXT_MUTED}">• Dense Embeddings (e.g. `all-MiniLM-L6-v2`)</text>
  <text x="400" y="388" font-size="11" fill="{TEXT_MUTED}">• Top-K Similarity Search for exact section guidelines</text>

  <rect x="385" y="425" width="410" height="75" rx="4" fill="{LIGHT_AMBER}" stroke="{AMBER}" stroke-width="1"/>
  <text x="400" y="447" font-size="12" font-weight="700" fill="#92400E">Current Implementation Status:</text>
  <text x="400" y="467" font-size="11" fill="#78350F">Placeholder retrieval step wired in graph state; full vector index,</text>
  <text x="400" y="485" font-size="11" fill="#78350F">embeddings, and Precision@K evaluation sequenced for Phase 2.</text>

  <!-- Arrow 2 -> 3 -->
  <line x1="820" y1="350" x2="870" y2="350" stroke="{NAVY}" stroke-width="2" marker-end="url(#arrow-navy)"/>

  <!-- STAGE 3: Context Augmentation & Reasoning -->
  <rect x="870" y="180" width="340" height="340" rx="8" fill="{BG_LIGHT}" stroke="{BORDER_SLATE}" stroke-width="1.5" filter="url(#shadow)"/>
  <rect x="870" y="180" width="340" height="32" rx="4" fill="{NAVY}"/>
  <text x="885" y="202" font-size="13" font-weight="700" fill="{WHITE}">3. CONTEXT-AUGMENTED REASONING</text>

  <rect x="895" y="230" width="290" height="80" rx="6" fill="{WHITE}" stroke="{BORDER_SLATE}" stroke-width="1"/>
  <text x="910" y="255" font-size="13" font-weight="700" fill="{NAVY}">State Context Injection</text>
  <text x="910" y="275" font-size="11" fill="{TEXT_MUTED}">• Augments `AgentState.memory_context`</text>
  <text x="910" y="293" font-size="11" fill="{TEXT_MUTED}">• Combines User Goal + Retrieved Guidelines</text>

  <rect x="895" y="325" width="290" height="85" rx="6" fill="{WHITE}" stroke="{BORDER_SLATE}" stroke-width="1"/>
  <text x="910" y="350" font-size="13" font-weight="700" fill="{NAVY}">Planning Agent Decomposition</text>
  <text x="910" y="370" font-size="11" fill="{TEXT_MUTED}">• Emits JSON PlanStep[] conforming to</text>
  <text x="910" y="388" font-size="11" fill="{TEXT_MUTED}">  retrieved domain template structure</text>

  <rect x="895" y="440" width="290" height="60" rx="4" fill="{LIGHT_GREEN}" stroke="{GREEN}" stroke-width="1"/>
  <text x="910" y="462" font-size="11" font-weight="700" fill="{GREEN}">Implemented:</text>
  <text x="910" y="480" font-size="11" fill="{TEXT_DARK}">LLM prompt augmentation &amp; plan generation</text>

  <!-- Arrow 3 -> 4 -->
  <line x1="1210" y1="350" x2="1260" y2="350" stroke="{NAVY}" stroke-width="2" marker-end="url(#arrow-navy)"/>

  <!-- STAGE 4: Tool Execution & Verification -->
  <rect x="1260" y="180" width="290" height="340" rx="8" fill="{BG_LIGHT}" stroke="{BORDER_SLATE}" stroke-width="1.5" filter="url(#shadow)"/>
  <rect x="1260" y="180" width="290" height="32" rx="4" fill="{NAVY}"/>
  <text x="1275" y="202" font-size="13" font-weight="700" fill="{WHITE}">4. EXECUTION &amp; VALIDATION</text>

  <rect x="1285" y="230" width="240" height="80" rx="6" fill="{WHITE}" stroke="{BORDER_SLATE}" stroke-width="1"/>
  <text x="1300" y="255" font-size="13" font-weight="700" fill="{NAVY}">Document / Execution Tool</text>
  <text x="1300" y="275" font-size="11" fill="{TEXT_MUTED}">• python-docx / openpyxl</text>
  <text x="1300" y="293" font-size="11" fill="{TEXT_MUTED}">• Generates target file on disk</text>

  <rect x="1285" y="325" width="240" height="85" rx="6" fill="{LIGHT_TEAL}" stroke="{TEAL}" stroke-width="1"/>
  <text x="1300" y="350" font-size="13" font-weight="700" fill="{TEAL}">Validation Agent</text>
  <text x="1300" y="370" font-size="11" fill="{TEXT_DARK}">• Programmatic structural verification</text>
  <text x="1300" y="388" font-size="11" fill="{TEXT_DARK}">• Confirms required sections exist</text>

  <rect x="1285" y="440" width="240" height="60" rx="4" fill="{LIGHT_GREEN}" stroke="{GREEN}" stroke-width="1"/>
  <text x="1300" y="462" font-size="11" font-weight="700" fill="{GREEN}">Implemented:</text>
  <text x="1300" y="480" font-size="11" fill="{TEXT_DARK}">Deterministic file generation &amp; validation</text>

  <!-- Lower Container: Planned Sequencing Details -->
  <rect x="50" y="560" width="1500" height="390" rx="8" fill="{WHITE}" stroke="{BORDER_SLATE}" stroke-width="1.5" filter="url(#shadow)"/>
  <rect x="50" y="560" width="380" height="32" rx="4" fill="{NAVY}"/>
  <text x="65" y="582" font-size="13" font-weight="700" fill="{WHITE}">PLANNED RAG RETRIEVAL STACK ROADMAP (SECTION 10.4)</text>

  <!-- Roadmap Steps -->
  <rect x="80" y="620" width="320" height="290" rx="6" fill="{BG_LIGHT}" stroke="{BORDER_SLATE}" stroke-width="1"/>
  <rect x="80" y="620" width="320" height="28" rx="4" fill="{SLATE}"/>
  <text x="95" y="639" font-size="12" font-weight="700" fill="{WHITE}">Phase A: Corpus Curation</text>
  <text x="95" y="670" font-size="12" font-weight="600" fill="{NAVY}">Target Domain Assets:</text>
  <text x="95" y="692" font-size="11" fill="{TEXT_MUTED}">• Academic leave formats (Medical, Casual)</text>
  <text x="95" y="712" font-size="11" fill="{TEXT_MUTED}">• TC &amp; Bonafide requisition templates</text>
  <text x="95" y="732" font-size="11" fill="{TEXT_MUTED}">• Attendance record schemas &amp; formulas</text>
  <text x="95" y="752" font-size="11" fill="{TEXT_MUTED}">• 5-slide academic seminar deck guidelines</text>
  <text x="95" y="785" font-size="11" font-weight="600" fill="{TEXT_DARK}">Deliverable: Curated JSON/Markdown files</text>

  <rect x="430" y="620" width="320" height="290" rx="6" fill="{BG_LIGHT}" stroke="{BORDER_SLATE}" stroke-width="1"/>
  <rect x="430" y="620" width="320" height="28" rx="4" fill="{SLATE}"/>
  <text x="445" y="639" font-size="12" font-weight="700" fill="{WHITE}">Phase B: Embedding &amp; Index</text>
  <text x="445" y="670" font-size="12" font-weight="600" fill="{NAVY}">Vector Storage Layer:</text>
  <text x="445" y="692" font-size="11" fill="{TEXT_MUTED}">• Sentence-Transformers embeddings</text>
  <text x="445" y="712" font-size="11" fill="{TEXT_MUTED}">• Local ChromaDB / FAISS vector index</text>
  <text x="445" y="732" font-size="11" fill="{TEXT_MUTED}">• Chunking strategy: Section-level chunks</text>
  <text x="445" y="752" font-size="11" fill="{TEXT_MUTED}">• Metadata tagging by document category</text>
  <text x="445" y="785" font-size="11" font-weight="600" fill="{TEXT_DARK}">Deliverable: Queryable local vector index</text>

  <rect x="780" y="620" width="320" height="290" rx="6" fill="{BG_LIGHT}" stroke="{BORDER_SLATE}" stroke-width="1"/>
  <rect x="780" y="620" width="320" height="28" rx="4" fill="{SLATE}"/>
  <text x="795" y="639" font-size="12" font-weight="700" fill="{WHITE}">Phase C: LangGraph Wiring</text>
  <text x="795" y="670" font-size="12" font-weight="600" fill="{NAVY}">Graph Node Integration:</text>
  <text x="795" y="692" font-size="11" fill="{TEXT_MUTED}">• Replace placeholder retrieval stub</text>
  <text x="795" y="712" font-size="11" fill="{TEXT_MUTED}">• Top-K similarity lookup node</text>
  <text x="795" y="732" font-size="11" fill="{TEXT_MUTED}">• Context pruning &amp; prompt construction</text>
  <text x="795" y="752" font-size="11" fill="{TEXT_MUTED}">• Feed directly into `planning_agent` state</text>
  <text x="795" y="785" font-size="11" font-weight="600" fill="{TEXT_DARK}">Deliverable: End-to-end retrieved prompt</text>

  <rect x="1130" y="620" width="380" height="290" rx="6" fill="{BG_LIGHT}" stroke="{BORDER_SLATE}" stroke-width="1"/>
  <rect x="1130" y="620" width="380" height="28" rx="4" fill="{SLATE}"/>
  <text x="1145" y="639" font-size="12" font-weight="700" fill="{WHITE}">Phase D: Empirical RAG Evaluation</text>
  <text x="1145" y="670" font-size="12" font-weight="600" fill="{NAVY}">Quantitative Quality Metrics:</text>
  <text x="1145" y="692" font-size="11" fill="{TEXT_MUTED}">• Precision@K and Recall@K against benchmark tasks</text>
  <text x="1145" y="712" font-size="11" fill="{TEXT_MUTED}">• Context relevance &amp; faithfulness scores</text>
  <text x="1145" y="732" font-size="11" fill="{TEXT_MUTED}">• Retrieval-to-generation latency overhead</text>
  <text x="1145" y="752" font-size="11" fill="{TEXT_MUTED}">• Cross-task isolation check with multiple users</text>
  <text x="1145" y="785" font-size="11" font-weight="600" fill="{TEXT_DARK}">Deliverable: Rigorous quantitative evaluation table</text>
</svg>"""


# ==============================================================================
# FIGURE 6: Tool and External Service Integration
# ==============================================================================
def generate_svg_figure_06() -> str:
    return f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1600 1100" width="1600" height="1100" style="background:#FFFFFF; font-family:'Segoe UI', Inter, Helvetica, Arial, sans-serif;">
  <defs>
    <marker id="arrow" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
      <path d="M 0 1 L 10 5 L 0 9 z" fill="{SLATE}"/>
    </marker>
    <filter id="shadow" x="-3%" y="-3%" width="106%" height="106%">
      <feDropShadow dx="0" dy="2" stdDeviation="3" flood-opacity="0.08"/>
    </filter>
  </defs>

  <!-- Title & Header -->
  <rect x="0" y="0" width="1600" height="70" fill="{NAVY}"/>
  <text x="50" y="44" font-size="22" font-weight="700" fill="{WHITE}">DesktopPilot AI — Tool &amp; External Service Integration Matrix</text>
  <text x="1550" y="44" font-size="14" font-weight="500" fill="#93C5FD" text-anchor="end">Source: `desktop_pilot/agents/*.py`</text>

  <!-- Column Headers -->
  <rect x="50" y="95" width="450" height="40" rx="4" fill="{NAVY}"/>
  <text x="275" y="121" font-size="15" font-weight="700" fill="{WHITE}" text-anchor="middle">1. AGENT CALLER LAYER</text>

  <rect x="550" y="95" width="500" height="40" rx="4" fill="{TEAL}"/>
  <text x="800" y="121" font-size="15" font-weight="700" fill="{WHITE}" text-anchor="middle">2. IMPLEMENTED TOOL INTERFACE</text>

  <rect x="1100" y="95" width="450" height="40" rx="4" fill="{SLATE}"/>
  <text x="1325" y="121" font-size="15" font-weight="700" fill="{WHITE}" text-anchor="middle">3. UNDERLYING SYSTEM / SERVICE</text>

  <!-- ROW 1: Document Agent -->
  <rect x="50" y="155" width="450" height="180" rx="6" fill="{BG_LIGHT}" stroke="{BORDER_SLATE}" stroke-width="1.2" filter="url(#shadow)"/>
  <text x="75" y="190" font-size="16" font-weight="700" fill="{NAVY}">Document Agent</text>
  <text x="75" y="215" font-size="12" fill="{TEXT_MUTED}">• Invoked by task_coordinator</text>
  <text x="75" y="235" font-size="12" fill="{TEXT_MUTED}">• Receives structured content payload</text>
  <text x="75" y="255" font-size="12" fill="{TEXT_MUTED}">• Emits binary output file path</text>
  <text x="75" y="295" font-size="11" font-weight="600" fill="{TEAL}">File: desktop_pilot/agents/document_agent.py</text>

  <line x1="500" y1="245" x2="550" y2="245" stroke="{NAVY}" stroke-width="2" marker-end="url(#arrow)"/>

  <rect x="550" y="155" width="500" height="180" rx="6" fill="{WHITE}" stroke="{BORDER_SLATE}" stroke-width="1.2" filter="url(#shadow)"/>
  <text x="575" y="185" font-size="14" font-weight="700" fill="{TEXT_DARK}">generate_word_document()</text>
  <text x="575" y="205" font-size="12" fill="{TEXT_MUTED}">Formal letter paragraphs, headings, bullet runs</text>
  <text x="575" y="230" font-size="14" font-weight="700" fill="{TEXT_DARK}">generate_excel_document()</text>
  <text x="575" y="250" font-size="12" fill="{TEXT_MUTED}">Worksheet initialization, headers, row append</text>
  <text x="575" y="275" font-size="14" font-weight="700" fill="{TEXT_DARK}">generate_powerpoint_document()</text>
  <text x="575" y="295" font-size="12" fill="{TEXT_MUTED}">Slide layout selection, title &amp; body placeholders</text>

  <line x1="1050" y1="245" x2="1100" y2="245" stroke="{NAVY}" stroke-width="2" marker-end="url(#arrow)"/>

  <rect x="1100" y="155" width="450" height="180" rx="6" fill="{BG_LIGHT}" stroke="{BORDER_SLATE}" stroke-width="1.2" filter="url(#shadow)"/>
  <text x="1125" y="185" font-size="14" font-weight="700" fill="{NAVY}">python-docx (v1.1+)</text>
  <text x="1125" y="205" font-size="12" fill="{TEXT_MUTED}">Native OpenXML Word Document (.docx)</text>
  <text x="1125" y="230" font-size="14" font-weight="700" fill="{NAVY}">openpyxl (v3.1+)</text>
  <text x="1125" y="250" font-size="12" fill="{TEXT_MUTED}">Native OpenXML Excel Spreadsheet (.xlsx)</text>
  <text x="1125" y="275" font-size="14" font-weight="700" fill="{NAVY}">python-pptx (v1.0+)</text>
  <text x="1125" y="295" font-size="12" fill="{TEXT_MUTED}">Native OpenXML PowerPoint Deck (.pptx)</text>

  <!-- ROW 2: Desktop Agent -->
  <rect x="50" y="355" width="450" height="160" rx="6" fill="{BG_LIGHT}" stroke="{BORDER_SLATE}" stroke-width="1.2" filter="url(#shadow)"/>
  <text x="75" y="390" font-size="16" font-weight="700" fill="{NAVY}">Desktop Agent</text>
  <text x="75" y="415" font-size="12" fill="{TEXT_MUTED}">• Handles file system operations</text>
  <text x="75" y="435" font-size="12" fill="{TEXT_MUTED}">• Launches local desktop applications</text>
  <text x="75" y="475" font-size="11" font-weight="600" fill="{TEAL}">File: desktop_pilot/agents/desktop_agent.py</text>

  <line x1="500" y1="435" x2="550" y2="435" stroke="{NAVY}" stroke-width="2" marker-end="url(#arrow)"/>

  <rect x="550" y="355" width="500" height="160" rx="6" fill="{WHITE}" stroke="{BORDER_SLATE}" stroke-width="1.2" filter="url(#shadow)"/>
  <text x="575" y="385" font-size="14" font-weight="700" fill="{TEXT_DARK}">os.makedirs(), os.remove(), shutil.move()</text>
  <text x="575" y="405" font-size="12" fill="{TEXT_MUTED}">Directory creation, recursive copy, delete, rename</text>
  <text x="575" y="430" font-size="14" font-weight="700" fill="{TEXT_DARK}">subprocess.Popen()</text>
  <text x="575" y="450" font-size="12" fill="{TEXT_MUTED}">Asynchronous application launcher</text>
  <text x="575" y="475" font-size="14" font-weight="700" fill="{TEXT_DARK}">pyautogui (optional binding)</text>
  <text x="575" y="495" font-size="12" fill="{TEXT_MUTED}">Local mouse/keyboard GUI automation hooks</text>

  <line x1="1050" y1="435" x2="1100" y2="435" stroke="{NAVY}" stroke-width="2" marker-end="url(#arrow)"/>

  <rect x="1100" y="355" width="450" height="160" rx="6" fill="{BG_LIGHT}" stroke="{BORDER_SLATE}" stroke-width="1.2" filter="url(#shadow)"/>
  <text x="1125" y="390" font-size="14" font-weight="700" fill="{NAVY}">Operating System Virtual Filesystem</text>
  <text x="1125" y="415" font-size="12" fill="{TEXT_MUTED}">Local Windows / POSIX file I/O</text>
  <text x="1125" y="445" font-size="14" font-weight="700" fill="{NAVY}">OS Process Subsystem</text>
  <text x="1125" y="470" font-size="12" fill="{TEXT_MUTED}">Process tree &amp; desktop session context</text>

  <!-- ROW 3: Browser Agent -->
  <rect x="50" y="535" width="450" height="160" rx="6" fill="{BG_LIGHT}" stroke="{BORDER_SLATE}" stroke-width="1.2" filter="url(#shadow)"/>
  <text x="75" y="570" font-size="16" font-weight="700" fill="{NAVY}">Browser Agent</text>
  <text x="75" y="595" font-size="12" fill="{TEXT_MUTED}">• Web search &amp; live URL content retrieval</text>
  <text x="75" y="615" font-size="12" fill="{TEXT_MUTED}">• Headless DOM inspection</text>
  <text x="75" y="655" font-size="11" font-weight="600" fill="{TEAL}">File: desktop_pilot/agents/browser_agent.py</text>

  <line x1="500" y1="615" x2="550" y2="615" stroke="{NAVY}" stroke-width="2" marker-end="url(#arrow)"/>

  <rect x="550" y="535" width="500" height="160" rx="6" fill="{WHITE}" stroke="{BORDER_SLATE}" stroke-width="1.2" filter="url(#shadow)"/>
  <text x="575" y="565" font-size="14" font-weight="700" fill="{TEXT_DARK}">async_playwright.chromium.launch()</text>
  <text x="575" y="585" font-size="12" fill="{TEXT_MUTED}">Headless browser instance, page.goto(), text extract</text>
  <text x="575" y="610" font-size="14" font-weight="700" fill="{TEXT_DARK}">_perform_web_search()</text>
  <text x="575" y="630" font-size="12" fill="{TEXT_MUTED}">DuckDuckGo HTML query with BeautifulSoup snippet parse</text>
  <text x="575" y="655" font-size="14" font-weight="700" fill="{TEXT_DARK}">httpx.AsyncClient()</text>
  <text x="575" y="675" font-size="12" fill="{TEXT_MUTED}">Asynchronous HTTP fetch fallback</text>

  <line x1="1050" y1="615" x2="1100" y2="615" stroke="{NAVY}" stroke-width="2" marker-end="url(#arrow)"/>

  <rect x="1100" y="535" width="450" height="160" rx="6" fill="{BG_LIGHT}" stroke="{BORDER_SLATE}" stroke-width="1.2" filter="url(#shadow)"/>
  <text x="1125" y="570" font-size="14" font-weight="700" fill="{NAVY}">Chromium Browser Binary</text>
  <text x="1125" y="595" font-size="12" fill="{TEXT_MUTED}">Playwright automated browser engine</text>
  <text x="1125" y="625" font-size="14" font-weight="700" fill="{NAVY}">DuckDuckGo Search Gateway</text>
  <text x="1125" y="650" font-size="12" fill="{TEXT_MUTED}">Public HTML web search endpoint</text>

  <!-- ROW 4: Memory Agent & Persistence -->
  <rect x="50" y="715" width="450" height="160" rx="6" fill="{BG_LIGHT}" stroke="{BORDER_SLATE}" stroke-width="1.2" filter="url(#shadow)"/>
  <text x="75" y="750" font-size="16" font-weight="700" fill="{NAVY}">Memory Agent</text>
  <text x="75" y="775" font-size="12" fill="{TEXT_MUTED}">• Persists conversation turns &amp; summaries</text>
  <text x="75" y="795" font-size="12" fill="{TEXT_MUTED}">• Maintains execution audit logs</text>
  <text x="75" y="835" font-size="11" font-weight="600" fill="{TEAL}">File: desktop_pilot/agents/memory_agent.py</text>

  <line x1="500" y1="795" x2="550" y2="795" stroke="{NAVY}" stroke-width="2" marker-end="url(#arrow)"/>

  <rect x="550" y="715" width="500" height="160" rx="6" fill="{WHITE}" stroke="{BORDER_SLATE}" stroke-width="1.2" filter="url(#shadow)"/>
  <text x="575" y="745" font-size="14" font-weight="700" fill="{TEXT_DARK}">save_session_state(), get_session_memory()</text>
  <text x="575" y="765" font-size="12" fill="{TEXT_MUTED}">Async SQLAlchemy ORM session commit &amp; query</text>
  <text x="575" y="790" font-size="14" font-weight="700" fill="{TEXT_DARK}">log_execution()</text>
  <text x="575" y="810" font-size="12" fill="{TEXT_MUTED}">Append-only trace log entries per node transition</text>
  <text x="575" y="835" font-size="14" font-weight="700" fill="{TEXT_DARK}">save_task_state(), clear_task_state()</text>
  <text x="575" y="855" font-size="12" fill="{TEXT_MUTED}">Ephemeral task state sync &amp; clearing</text>

  <line x1="1050" y1="795" x2="1100" y2="795" stroke="{NAVY}" stroke-width="2" marker-end="url(#arrow)"/>

  <rect x="1100" y="715" width="450" height="160" rx="6" fill="{BG_LIGHT}" stroke="{BORDER_SLATE}" stroke-width="1.2" filter="url(#shadow)"/>
  <text x="1125" y="750" font-size="14" font-weight="700" fill="{NAVY}">SQLite 3 Database Engine</text>
  <text x="1125" y="775" font-size="12" fill="{TEXT_MUTED}">aiosqlite async connection pool</text>
  <text x="1125" y="805" font-size="14" font-weight="700" fill="{NAVY}">Relational Tables (desktop_pilot.db)</text>
  <text x="1125" y="830" font-size="12" fill="{TEXT_MUTED}">• sessions (id, session_id, messages_json, ...)</text>
  <text x="1125" y="850" font-size="12" fill="{TEXT_MUTED}">• execution_logs (id, timestamp, agent, status)</text>

  <!-- ROW 5: Model Router & LLM Service -->
  <rect x="50" y="895" width="450" height="160" rx="6" fill="{BG_LIGHT}" stroke="{BORDER_SLATE}" stroke-width="1.2" filter="url(#shadow)"/>
  <text x="75" y="930" font-size="16" font-weight="700" fill="{NAVY}">Model Router / LLM Factory</text>
  <text x="75" y="955" font-size="12" fill="{TEXT_MUTED}">• Selects active LLM backend</text>
  <text x="75" y="975" font-size="12" fill="{TEXT_MUTED}">• Configures temperature and model ID</text>
  <text x="75" y="1015" font-size="11" font-weight="600" fill="{TEAL}">File: desktop_pilot/agents/model_router.py</text>

  <line x1="500" y1="975" x2="550" y2="975" stroke="{NAVY}" stroke-width="2" marker-end="url(#arrow)"/>

  <rect x="550" y="895" width="500" height="160" rx="6" fill="{WHITE}" stroke="{BORDER_SLATE}" stroke-width="1.2" filter="url(#shadow)"/>
  <text x="575" y="925" font-size="14" font-weight="700" fill="{TEXT_DARK}">ChatGroq(model=..., api_key=...)</text>
  <text x="575" y="945" font-size="12" fill="{TEXT_MUTED}">Low-latency cloud LLM invocation (temperature=0)</text>
  <text x="575" y="970" font-size="14" font-weight="700" fill="{TEXT_DARK}">ChatOllama(model=..., base_url=...)</text>
  <text x="575" y="990" font-size="12" fill="{TEXT_MUTED}">Local self-hosted offline inference fallback</text>
  <text x="575" y="1015" font-size="14" font-weight="700" fill="{TEXT_DARK}">_check_groq(), _check_ollama()</text>
  <text x="575" y="1035" font-size="12" fill="{TEXT_MUTED}">Dynamic HTTP health ping with configurable timeout</text>

  <line x1="1050" y1="975" x2="1100" y2="975" stroke="{NAVY}" stroke-width="2" marker-end="url(#arrow)"/>

  <rect x="1100" y="895" width="450" height="160" rx="6" fill="{BG_LIGHT}" stroke="{BORDER_SLATE}" stroke-width="1.2" filter="url(#shadow)"/>
  <text x="1125" y="930" font-size="14" font-weight="700" fill="{NAVY}">Groq Cloud LPU Inference API</text>
  <text x="1125" y="955" font-size="12" fill="{TEXT_MUTED}">openai/gpt-oss-120b / llama-3.3-70b-versatile</text>
  <text x="1125" y="985" font-size="14" font-weight="700" fill="{NAVY}">Ollama Local Daemon</text>
  <text x="1125" y="1010" font-size="12" fill="{TEXT_MUTED}">llama3.1:8b-instruct on localhost:11434</text>
</svg>"""


# ==============================================================================
# FIGURE 7: Session and Task State Management
# ==============================================================================
def generate_svg_figure_07() -> str:
    return f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1600 1100" width="1600" height="1100" style="background:#FFFFFF; font-family:'Segoe UI', Inter, Helvetica, Arial, sans-serif;">
  <defs>
    <marker id="arrow" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
      <path d="M 0 1 L 10 5 L 0 9 z" fill="{SLATE}"/>
    </marker>
    <marker id="arrow-green" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
      <path d="M 0 1 L 10 5 L 0 9 z" fill="{GREEN}"/>
    </marker>
    <marker id="arrow-red" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
      <path d="M 0 1 L 10 5 L 0 9 z" fill="{RED}"/>
    </marker>
    <filter id="shadow" x="-3%" y="-3%" width="106%" height="106%">
      <feDropShadow dx="0" dy="2" stdDeviation="3" flood-opacity="0.08"/>
    </filter>
  </defs>

  <!-- Title & Header -->
  <rect x="0" y="0" width="1600" height="70" fill="{NAVY}"/>
  <text x="50" y="44" font-size="22" font-weight="700" fill="{WHITE}">DesktopPilot AI — Two-Layer Session &amp; Task State Management Architecture</text>
  <text x="1550" y="44" font-size="14" font-weight="500" fill="#93C5FD" text-anchor="end">Source: `state.py` &amp; `memory/db.py`</text>

  <!-- Side-by-Side Dual-Layer Memory Architecture -->

  <!-- LAYER 1: Persistent Session Memory (SQLite) -->
  <rect x="50" y="95" width="720" height="600" rx="8" fill="{BG_LIGHT}" stroke="{BORDER_SLATE}" stroke-width="1.5" filter="url(#shadow)"/>
  <rect x="50" y="95" width="720" height="38" rx="4" fill="{NAVY}"/>
  <text x="75" y="120" font-size="15" font-weight="700" fill="{WHITE}">1. PERSISTENT SESSION MEMORY (SQLite Database)</text>

  <!-- Table 1: sessions -->
  <rect x="80" y="155" width="660" height="235" rx="6" fill="{WHITE}" stroke="{BORDER_SLATE}" stroke-width="1.2"/>
  <rect x="80" y="155" width="660" height="28" rx="4" fill="{SLATE}"/>
  <text x="95" y="174" font-size="13" font-weight="700" fill="{WHITE}">Table: sessions (SQLAlchemy: SessionRecord)</text>

  <text x="100" y="210" font-size="13" font-weight="700" fill="{NAVY}">session_id</text>
  <text x="290" y="210" font-size="12" fill="{TEXT_MUTED}">String(64), Primary Key, Indexed (UUID)</text>

  <text x="100" y="240" font-size="13" font-weight="700" fill="{NAVY}">messages_json</text>
  <text x="290" y="240" font-size="12" fill="{TEXT_MUTED}">Text: Full accumulated chat history across all turns</text>

  <text x="100" y="270" font-size="13" font-weight="700" fill="{NAVY}">memory_summary</text>
  <text x="290" y="270" font-size="12" fill="{TEXT_MUTED}">Text: Cross-task user preferences and durable context</text>

  <text x="100" y="300" font-size="13" font-weight="700" fill="{NAVY}">task_state_json</text>
  <text x="290" y="300" font-size="12" fill="{TEXT_MUTED}">Text: Intermediate checkpointed active task dictionary</text>

  <text x="100" y="330" font-size="13" font-weight="700" fill="{NAVY}">created_at / updated_at</text>
  <text x="290" y="330" font-size="12" fill="{TEXT_MUTED}">DateTime: Timestamps of creation and last update</text>

  <rect x="100" y="350" width="620" height="28" rx="4" fill="{LIGHT_TEAL}"/>
  <text x="110" y="369" font-size="11" font-weight="600" fill="{TEAL}">• Persists across multiple tasks, clarifications, and server restarts</text>

  <!-- Table 2: execution_logs -->
  <rect x="80" y="410" width="660" height="260" rx="6" fill="{WHITE}" stroke="{BORDER_SLATE}" stroke-width="1.2"/>
  <rect x="80" y="410" width="660" height="28" rx="4" fill="{SLATE}"/>
  <text x="95" y="429" font-size="13" font-weight="700" fill="{WHITE}">Table: execution_logs (SQLAlchemy: ExecutionLogRecord)</text>

  <text x="100" y="465" font-size="13" font-weight="700" fill="{NAVY}">id</text>
  <text x="290" y="465" font-size="12" fill="{TEXT_MUTED}">Integer, Autoincrement Primary Key</text>

  <text x="100" y="495" font-size="13" font-weight="700" fill="{NAVY}">session_id</text>
  <text x="290" y="495" font-size="12" fill="{TEXT_MUTED}">String(64), Indexed Foreign Key to sessions</text>

  <text x="100" y="525" font-size="13" font-weight="700" fill="{NAVY}">timestamp</text>
  <text x="290" y="525" font-size="12" fill="{TEXT_MUTED}">DateTime: UTC timestamp of node execution</text>

  <text x="100" y="555" font-size="13" font-weight="700" fill="{NAVY}">agent</text>
  <text x="290" y="555" font-size="12" fill="{TEXT_MUTED}">String(64): Name of the agent node (e.g. supervisor)</text>

  <text x="100" y="585" font-size="13" font-weight="700" fill="{NAVY}">status</text>
  <text x="290" y="585" font-size="12" fill="{TEXT_MUTED}">String(32): Status string ('success', 'error', 'pending')</text>

  <text x="100" y="615" font-size="13" font-weight="700" fill="{NAVY}">message</text>
  <text x="290" y="615" font-size="12" fill="{TEXT_MUTED}">Text: Full trace message and action description</text>

  <rect x="100" y="635" width="620" height="25" rx="4" fill="{LIGHT_TEAL}"/>
  <text x="110" y="652" font-size="11" font-weight="600" fill="{TEAL}">• Provides complete, immutable audit trail for every agent transition</text>


  <!-- LAYER 2: Ephemeral Current Task State (LangGraph TypedDict) -->
  <rect x="830" y="95" width="720" height="600" rx="8" fill="{BG_LIGHT}" stroke="{BORDER_SLATE}" stroke-width="1.5" filter="url(#shadow)"/>
  <rect x="830" y="95" width="720" height="38" rx="4" fill="{TEAL}"/>
  <text x="855" y="120" font-size="15" font-weight="700" fill="{WHITE}">2. EPHEMERAL CURRENT TASK STATE (AgentState TypedDict)</text>

  <rect x="860" y="155" width="660" height="515" rx="6" fill="{WHITE}" stroke="{BORDER_SLATE}" stroke-width="1.2"/>

  <!-- Field groups -->
  <text x="885" y="185" font-size="13" font-weight="700" fill="{NAVY}">A. Task Intake &amp; Classification Fields (Live)</text>
  <text x="905" y="210" font-size="12" font-weight="600" fill="{TEXT_DARK}">• user_input:</text>
  <text x="1010" y="210" font-size="12" fill="{TEXT_MUTED}">Raw user prompt string for current turn</text>
  <text x="905" y="230" font-size="12" font-weight="600" fill="{TEXT_DARK}">• task_type:</text>
  <text x="1010" y="230" font-size="12" fill="{TEXT_MUTED}">document_generation | desktop_automation | browser_automation</text>
  <text x="905" y="250" font-size="12" font-weight="600" fill="{TEXT_DARK}">• current_task_info:</text>
  <text x="1045" y="250" font-size="12" fill="{TEXT_MUTED}">Dict of extracted parameters across clarification turns</text>
  <text x="905" y="270" font-size="12" font-weight="600" fill="{TEXT_DARK}">• status:</text>
  <text x="1010" y="270" font-size="12" fill="{TEXT_MUTED}">waiting_for_user | executing | completed</text>

  <line x1="885" y1="290" x2="1500" y2="290" stroke="{BORDER_SLATE}" stroke-width="1"/>

  <text x="885" y="315" font-size="13" font-weight="700" fill="{NAVY}">B. Planning &amp; Step Execution Fields (Ephemeral)</text>
  <text x="905" y="340" font-size="12" font-weight="600" fill="{TEXT_DARK}">• requirements_complete:</text>
  <text x="1075" y="340" font-size="12" fill="{TEXT_MUTED}">Boolean flag controlling branch to planning</text>
  <text x="905" y="360" font-size="12" font-weight="600" fill="{TEXT_DARK}">• clarifying_question:</text>
  <text x="1060" y="360" font-size="12" fill="{TEXT_MUTED}">Single question string when info is missing</text>
  <text x="905" y="380" font-size="12" font-weight="600" fill="{TEXT_DARK}">• plan:</text>
  <text x="955" y="380" font-size="12" fill="{TEXT_MUTED}">Ordered list of PlanStep (step_id, agent, action, params)</text>
  <text x="905" y="400" font-size="12" font-weight="600" fill="{TEXT_DARK}">• current_step:</text>
  <text x="1005" y="400" font-size="12" fill="{TEXT_MUTED}">Integer index tracking active plan execution step</text>
  <text x="905" y="420" font-size="12" font-weight="600" fill="{TEXT_DARK}">• target_agent:</text>
  <text x="1010" y="420" font-size="12" fill="{TEXT_MUTED}">Active execution agent targeted by coordinator</text>

  <line x1="885" y1="440" x2="1500" y2="440" stroke="{BORDER_SLATE}" stroke-width="1"/>

  <text x="885" y="465" font-size="13" font-weight="700" fill="{NAVY}">C. Validation &amp; Replanning Feedback (Ephemeral)</text>
  <text x="905" y="490" font-size="12" font-weight="600" fill="{TEXT_DARK}">• last_execution_result:</text>
  <text x="1065" y="490" font-size="12" fill="{TEXT_MUTED}">Dict containing success flag, output_file, error</text>
  <text x="905" y="510" font-size="12" font-weight="600" fill="{TEXT_DARK}">• validation_result:</text>
  <text x="1040" y="510" font-size="12" fill="{TEXT_MUTED}">Dict containing valid: bool, reason: str</text>
  <text x="905" y="530" font-size="12" font-weight="600" fill="{TEXT_DARK}">• replan_reason:</text>
  <text x="1015" y="530" font-size="12" fill="{RED}">Diagnostic string injected into planner on failure</text>

  <rect x="885" y="560" width="610" height="90" rx="4" fill="{LIGHT_AMBER}" stroke="{AMBER}" stroke-width="1"/>
  <text x="900" y="582" font-size="12" font-weight="700" fill="#92400E">State Reset &amp; Context Isolation Guarantee:</text>
  <text x="900" y="605" font-size="11" fill="#78350F">Upon validation PASS on final step (validation_agent.py:113):</text>
  <text x="900" y="625" font-size="11" font-weight="700" fill="{NAVY}">plan = [], current_step = 0, current_task_info = &#123;&#125;, task_type = 'unknown'</text>
  <text x="900" y="642" font-size="11" fill="#78350F">Prevents parameter contamination when a new, unrelated task is submitted.</text>


  <!-- LOWER CONTAINER: State Lifecycle & Isolation Workflow -->
  <rect x="50" y="725" width="1500" height="340" rx="8" fill="{WHITE}" stroke="{BORDER_SLATE}" stroke-width="1.5" filter="url(#shadow)"/>
  <rect x="50" y="725" width="480" height="32" rx="4" fill="{NAVY}"/>
  <text x="65" y="747" font-size="13" font-weight="700" fill="{WHITE}">STATE LIFECYCLE &amp; CROSS-TASK ISOLATION MECHANISM</text>

  <!-- Step A: Task Intake -->
  <rect x="80" y="780" width="310" height="255" rx="6" fill="{BG_LIGHT}" stroke="{BORDER_SLATE}" stroke-width="1.2"/>
  <text x="95" y="805" font-size="13" font-weight="700" fill="{NAVY}">Step 1: Task Intake &amp; Memory Injection</text>
  <text x="95" y="830" font-size="12" fill="{TEXT_MUTED}">1. User message received.</text>
  <text x="95" y="850" font-size="12" fill="{TEXT_MUTED}">2. memory_agent retrieves memory_summary</text>
  <text x="95" y="870" font-size="12" fill="{TEXT_MUTED}">   from SQLite for current session_id.</text>
  <text x="95" y="890" font-size="12" fill="{TEXT_MUTED}">3. Injects prior context into memory_context.</text>
  <text x="95" y="910" font-size="12" fill="{TEXT_MUTED}">4. Appends user message to messages_json.</text>
  <rect x="95" y="940" width="280" height="80" rx="4" fill="{WHITE}" stroke="{BORDER_SLATE}" stroke-width="1"/>
  <text x="105" y="960" font-size="11" font-weight="600" fill="{NAVY}">Initial AgentState:</text>
  <text x="105" y="980" font-size="11" fill="{TEXT_DARK}">messages: [user message]</text>
  <text x="105" y="1000" font-size="11" fill="{TEXT_DARK}">status: 'executing'</text>

  <!-- Arrow A -> B -->
  <line x1="390" y1="900" x2="430" y2="900" stroke="{NAVY}" stroke-width="2" marker-end="url(#arrow)"/>

  <!-- Step B: Execution & Verification -->
  <rect x="430" y="780" width="330" height="255" rx="6" fill="{BG_LIGHT}" stroke="{BORDER_SLATE}" stroke-width="1.2"/>
  <text x="445" y="805" font-size="13" font-weight="700" fill="{NAVY}">Step 2: Step Execution &amp; Checkpointing</text>
  <text x="445" y="830" font-size="12" fill="{TEXT_MUTED}">1. planning_agent sets plan JSON array.</text>
  <text x="445" y="850" font-size="12" fill="{TEXT_MUTED}">2. task_coordinator selects current_step.</text>
  <text x="445" y="870" font-size="12" fill="{TEXT_MUTED}">3. Execution agent outputs artifact.</text>
  <text x="445" y="890" font-size="12" fill="{TEXT_MUTED}">4. Intermediate state checkpointed to</text>
  <text x="445" y="910" font-size="12" fill="{TEXT_MUTED}">   task_state_json in SQLite.</text>
  <rect x="445" y="940" width="300" height="80" rx="4" fill="{WHITE}" stroke="{BORDER_SLATE}" stroke-width="1"/>
  <text x="455" y="960" font-size="11" font-weight="600" fill="{NAVY}">Executing AgentState:</text>
  <text x="455" y="980" font-size="11" fill="{TEXT_DARK}">plan: [Step 1: DocumentAgent...]</text>
  <text x="455" y="1000" font-size="11" fill="{TEXT_DARK}">current_step: 0 -&gt; 1</text>

  <!-- Arrow B -> C -->
  <line x1="760" y1="900" x2="800" y2="900" stroke="{NAVY}" stroke-width="2" marker-end="url(#arrow)"/>

  <!-- Step C: Validation Pass & Clearing -->
  <rect x="800" y="780" width="340" height="255" rx="6" fill="{LIGHT_GREEN}" stroke="{GREEN}" stroke-width="1.2"/>
  <text x="815" y="805" font-size="13" font-weight="700" fill="{GREEN}">Step 3: Validation PASS &amp; State Cleanup</text>
  <text x="815" y="830" font-size="12" fill="{TEXT_DARK}">1. validation_agent checks physical file.</text>
  <text x="815" y="850" font-size="12" fill="{TEXT_DARK}">2. validation_result.valid = True.</text>
  <text x="815" y="870" font-size="12" font-weight="700" fill="{GREEN}">3. Current Task State CLEARED:</text>
  <text x="830" y="890" font-size="11" fill="{TEXT_DARK}">• plan = []</text>
  <text x="830" y="908" font-size="11" fill="{TEXT_DARK}">• current_task_info = &#123;&#125;</text>
  <text x="830" y="926" font-size="11" fill="{TEXT_DARK}">• task_type = 'unknown'</text>
  <text x="815" y="955" font-size="12" fill="{TEXT_DARK}">4. task_state_json cleared in SQLite.</text>
  <text x="815" y="975" font-size="12" fill="{TEXT_DARK}">5. Final file path returned in final_response.</text>
  <text x="815" y="995" font-size="12" fill="{TEXT_DARK}">6. Execution trace logged to execution_logs.</text>

  <!-- Arrow C -> D -->
  <line x1="1140" y1="900" x2="1180" y2="900" stroke="{NAVY}" stroke-width="2" marker-end="url(#arrow)"/>

  <!-- Step D: Unrelated New Task -->
  <rect x="1180" y="780" width="340" height="255" rx="6" fill="{BG_LIGHT}" stroke="{BORDER_SLATE}" stroke-width="1.2"/>
  <text x="1195" y="805" font-size="13" font-weight="700" fill="{NAVY}">Step 4: Subsequent Unrelated Task</text>
  <text x="1195" y="830" font-size="12" fill="{TEXT_MUTED}">1. User issues new task: "Create PPTX".</text>
  <text x="1195" y="850" font-size="12" fill="{TEXT_MUTED}">2. supervisor sees empty current_task_info.</text>
  <text x="1195" y="870" font-size="12" font-weight="700" fill="{GREEN}">3. NO Context Contamination:</text>
  <text x="1210" y="890" font-size="11" fill="{TEXT_MUTED}">• No stale leave letter parameters</text>
  <text x="1210" y="908" font-size="11" fill="{TEXT_MUTED}">• No lingering step indices</text>
  <text x="1195" y="935" font-size="12" fill="{TEXT_MUTED}">4. Session conversation history remains intact</text>
  <text x="1195" y="955" font-size="12" fill="{TEXT_MUTED}">   in SQLite messages_json for reference.</text>
  <rect x="1195" y="975" width="310" height="45" rx="4" fill="{WHITE}" stroke="{BORDER_SLATE}" stroke-width="1"/>
  <text x="1205" y="995" font-size="11" font-weight="600" fill="{GREEN}">Result: Session continuity preserved;</text>
  <text x="1205" y="1010" font-size="11" fill="{TEXT_DARK}">Task contamination completely eliminated.</text>
</svg>"""


# ==============================================================================
# FIGURE 8: Closed-Loop Reasoning and Self-Correction
# ==============================================================================
def generate_svg_figure_08() -> str:
    return f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1600 1000" width="1600" height="1000" style="background:#FFFFFF; font-family:'Segoe UI', Inter, Helvetica, Arial, sans-serif;">
  <defs>
    <marker id="arrow" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
      <path d="M 0 1 L 10 5 L 0 9 z" fill="{SLATE}"/>
    </marker>
    <marker id="arrow-green" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
      <path d="M 0 1 L 10 5 L 0 9 z" fill="{GREEN}"/>
    </marker>
    <marker id="arrow-red" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
      <path d="M 0 1 L 10 5 L 0 9 z" fill="{RED}"/>
    </marker>
    <filter id="shadow" x="-3%" y="-3%" width="106%" height="106%">
      <feDropShadow dx="0" dy="2" stdDeviation="3" flood-opacity="0.08"/>
    </filter>
  </defs>

  <!-- Title & Header -->
  <rect x="0" y="0" width="1600" height="70" fill="{NAVY}"/>
  <text x="50" y="44" font-size="22" font-weight="700" fill="{WHITE}">DesktopPilot AI — Closed-Loop Reasoning &amp; Self-Correction Architecture</text>
  <text x="1550" y="44" font-size="14" font-weight="500" fill="#93C5FD" text-anchor="end">Failure Detection &amp; Autonomous Replanning Cycle</text>

  <!-- TOP FORWARD PIPELINE (Left to Right) -->
  <rect x="70" y="100" width="1480" height="230" rx="8" fill="{BG_LIGHT}" stroke="{BORDER_SLATE}" stroke-width="1.5" filter="url(#shadow)"/>
  <rect x="70" y="100" width="360" height="30" rx="4" fill="{NAVY}"/>
  <text x="85" y="120" font-size="13" font-weight="700" fill="{WHITE}">FORWARD EXECUTION PIPELINE</text>

  <!-- Node 1: User Request -->
  <rect x="95" y="150" width="220" height="150" rx="6" fill="{WHITE}" stroke="{BORDER_SLATE}" stroke-width="1.2"/>
  <rect x="95" y="150" width="220" height="26" rx="4" fill="{SLATE}"/>
  <text x="110" y="168" font-size="12" font-weight="700" fill="{WHITE}">1. Task Intake</text>
  <text x="110" y="198" font-size="13" font-weight="700" fill="{NAVY}">User Request</text>
  <text x="110" y="220" font-size="11" fill="{TEXT_MUTED}">• Natural-language goal</text>
  <text x="110" y="240" font-size="11" fill="{TEXT_MUTED}">• Supervisor classification</text>
  <text x="110" y="260" font-size="11" fill="{TEXT_MUTED}">• Requirement analysis</text>

  <line x1="315" y1="225" x2="365" y2="225" stroke="{NAVY}" stroke-width="2" marker-end="url(#arrow)"/>

  <!-- Node 2: Planning Agent -->
  <rect x="365" y="150" width="265" height="150" rx="6" fill="{WHITE}" stroke="{BORDER_SLATE}" stroke-width="1.2"/>
  <rect x="365" y="150" width="265" height="26" rx="4" fill="{NAVY}"/>
  <text x="380" y="168" font-size="12" font-weight="700" fill="{WHITE}">2. Goal Decomposition</text>
  <text x="380" y="198" font-size="13" font-weight="700" fill="{NAVY}">Planning Agent</text>
  <text x="380" y="220" font-size="11" fill="{TEXT_MUTED}">• Emits JSON PlanStep[]</text>
  <text x="380" y="240" font-size="11" fill="{TEXT_MUTED}">• Selects agent &amp; parameters</text>
  <text x="380" y="260" font-size="11" fill="{TEXT_MUTED}">• Reads replan_reason if active</text>

  <line x1="630" y1="225" x2="680" y2="225" stroke="{NAVY}" stroke-width="2" marker-end="url(#arrow)"/>

  <!-- Node 3: Task Coordinator -->
  <rect x="680" y="150" width="240" height="150" rx="6" fill="{WHITE}" stroke="{BORDER_SLATE}" stroke-width="1.2"/>
  <rect x="680" y="150" width="240" height="26" rx="4" fill="{SLATE}"/>
  <text x="695" y="168" font-size="12" font-weight="700" fill="{WHITE}">3. Dispatch</text>
  <text x="695" y="198" font-size="13" font-weight="700" fill="{NAVY}">Task Coordinator</text>
  <text x="695" y="220" font-size="11" fill="{TEXT_MUTED}">• Sequences plan steps</text>
  <text x="695" y="240" font-size="11" fill="{TEXT_MUTED}">• Routes to active agent</text>
  <text x="695" y="260" font-size="11" fill="{TEXT_MUTED}">• Sets target_agent</text>

  <line x1="920" y1="225" x2="970" y2="225" stroke="{NAVY}" stroke-width="2" marker-end="url(#arrow)"/>

  <!-- Node 4: Execution Agent & Tool -->
  <rect x="970" y="150" width="260" height="150" rx="6" fill="{WHITE}" stroke="{BORDER_SLATE}" stroke-width="1.2"/>
  <rect x="970" y="150" width="260" height="26" rx="4" fill="{NAVY}"/>
  <text x="985" y="168" font-size="12" font-weight="700" fill="{WHITE}">4. Tool Execution</text>
  <text x="985" y="198" font-size="13" font-weight="700" fill="{NAVY}">Execution Agent</text>
  <text x="985" y="220" font-size="11" fill="{TEXT_MUTED}">• Document / Desktop / Browser</text>
  <text x="985" y="240" font-size="11" fill="{TEXT_MUTED}">• Invokes native python tools</text>
  <text x="985" y="260" font-size="11" fill="{TEXT_MUTED}">• Emits output file on disk</text>

  <line x1="1230" y1="225" x2="1280" y2="225" stroke="{NAVY}" stroke-width="2" marker-end="url(#arrow)"/>

  <!-- Node 5: Physical Output Artifact -->
  <rect x="1280" y="150" width="250" height="150" rx="6" fill="{LIGHT_TEAL}" stroke="{TEAL}" stroke-width="1.2"/>
  <rect x="1280" y="150" width="250" height="26" rx="4" fill="{TEAL}"/>
  <text x="1295" y="168" font-size="12" font-weight="700" fill="{WHITE}">5. Generated Output</text>
  <text x="1295" y="198" font-size="13" font-weight="700" fill="{TEAL}">Physical File Artifact</text>
  <text x="1295" y="220" font-size="11" fill="{TEXT_DARK}">• .docx, .xlsx, .pptx</text>
  <text x="1295" y="240" font-size="11" fill="{TEXT_DARK}">• Stored in workspace directory</text>
  <text x="1295" y="260" font-size="11" fill="{TEXT_DARK}">• Target for inspection</text>

  <!-- Flow Down to Validation -->
  <line x1="1405" y1="300" x2="1405" y2="380" stroke="{NAVY}" stroke-width="2" marker-end="url(#arrow)"/>

  <!-- CENTRAL VALIDATION & DECISION NODE -->
  <rect x="70" y="380" width="1480" height="200" rx="8" fill="{WHITE}" stroke="{BORDER_SLATE}" stroke-width="1.5" filter="url(#shadow)"/>
  <rect x="70" y="380" width="400" height="30" rx="4" fill="{TEAL}"/>
  <text x="85" y="400" font-size="13" font-weight="700" fill="{WHITE}">6. INDEPENDENT PHYSICAL ARTIFACT VALIDATION</text>

  <rect x="95" y="425" width="600" height="135" rx="6" fill="{BG_LIGHT}" stroke="{BORDER_SLATE}" stroke-width="1.2"/>
  <text x="115" y="450" font-size="14" font-weight="700" fill="{TEAL}">Validation Agent (validation_agent.py)</text>
  <text x="115" y="475" font-size="12" fill="{TEXT_DARK}">• Does NOT rely on execution exit code — inspects actual file contents</text>
  <text x="115" y="495" font-size="12" fill="{TEXT_MUTED}">• Checks file existence &amp; non-zero file size (os.path.getsize(path) &gt; 0)</text>
  <text x="115" y="515" font-size="12" fill="{TEXT_MUTED}">• DOCX: Checks len(doc.paragraphs) &gt; 1 &amp; non-empty body text</text>
  <text x="115" y="535" font-size="12" fill="{TEXT_MUTED}">• XLSX: Checks ws.max_row &gt; 1 (headers + data rows present)</text>
  <text x="115" y="555" font-size="12" fill="{TEXT_MUTED}">• PPTX: Checks len(prs.slides) &gt; 0 &amp; shapes contain non-placeholder text</text>

  <!-- Decision Fork -->
  <!-- PASS BRANCH -->
  <rect x="735" y="425" width="370" height="135" rx="6" fill="{LIGHT_GREEN}" stroke="{GREEN}" stroke-width="1.5"/>
  <text x="755" y="452" font-size="15" font-weight="700" fill="{GREEN}">DECISION: VALIDATION PASS</text>
  <text x="755" y="478" font-size="12" fill="{TEXT_DARK}">• validation_result = &#123;"valid": True&#125;</text>
  <text x="755" y="498" font-size="12" fill="{TEXT_DARK}">• Increments current_step</text>
  <text x="755" y="518" font-size="12" fill="{TEXT_DARK}">• Clears ephemeral task state on final step</text>
  <text x="755" y="538" font-size="12" fill="{TEXT_DARK}">• Emits final file path &amp; completion message</text>

  <line x1="1105" y1="492" x2="1175" y2="492" stroke="{GREEN}" stroke-width="2.5" marker-end="url(#arrow-green)"/>

  <!-- Success Terminal Box -->
  <rect x="1175" y="425" width="355" height="135" rx="6" fill="{WHITE}" stroke="{GREEN}" stroke-width="1.5"/>
  <text x="1195" y="452" font-size="14" font-weight="700" fill="{NAVY}">Session Memory &amp; Delivery</text>
  <text x="1195" y="478" font-size="12" fill="{TEXT_MUTED}">• Persist turn to SQLite sessions</text>
  <text x="1195" y="498" font-size="12" fill="{TEXT_MUTED}">• Write audit log to execution_logs</text>
  <text x="1195" y="518" font-size="12" fill="{GREEN}">• Deliver validated file to User</text>
  <text x="1195" y="538" font-size="11" font-weight="700" fill="{GREEN}">STATUS: COMPLETED (Success)</text>


  <!-- BOTTOM REPLANNING LOOP (Right to Left Feedback) -->
  <rect x="70" y="610" width="1480" height="360" rx="8" fill="#FFF5F5" stroke="{RED}" stroke-width="1.8" filter="url(#shadow)"/>
  <rect x="70" y="610" width="450" height="30" rx="4" fill="{RED}"/>
  <text x="85" y="630" font-size="13" font-weight="700" fill="{WHITE}">SELF-CORRECTION &amp; CYCLIC REPLANNING FEEDBACK LOOP</text>

  <!-- Step F1: Failure Diagnosis -->
  <rect x="1115" y="660" width="415" height="280" rx="6" fill="{WHITE}" stroke="{RED}" stroke-width="1.2"/>
  <rect x="1115" y="660" width="415" height="26" rx="4" fill="{RED}"/>
  <text x="1130" y="678" font-size="12" font-weight="700" fill="{WHITE}">F1. Failure Diagnosis &amp; State Annotation</text>
  <text x="1130" y="708" font-size="13" font-weight="700" fill="{RED}">Validation Fails:</text>
  <text x="1130" y="730" font-size="12" fill="{TEXT_DARK}">• Example: Word doc contains only title</text>
  <text x="1130" y="750" font-size="12" fill="{TEXT_DARK}">• Example: Excel has header but 0 data rows</text>
  <text x="1130" y="770" font-size="12" fill="{TEXT_DARK}">• Example: PowerPoint has 0 slides</text>
  <text x="1130" y="805" font-size="13" font-weight="700" fill="{NAVY}">Generated Failure Message:</text>
  <text x="1130" y="828" font-size="11" fill="{RED}">failure_msg = "Word doc generated successfully</text>
  <text x="1130" y="846" font-size="11" fill="{RED}">but contains no meaningful text content..."</text>
  <text x="1130" y="878" font-size="12" font-weight="700" fill="{NAVY}">Populates in AgentState:</text>
  <text x="1130" y="900" font-size="11" fill="{TEXT_DARK}">replan_reason = failure_msg</text>
  <text x="1130" y="920" font-size="11" fill="{TEXT_DARK}">execution_trace.append(&#123;"status": "error"&#125;)</text>

  <!-- Arrow F1 -> F2 -->
  <line x1="1115" y1="800" x2="1055" y2="800" stroke="{RED}" stroke-width="2.5" marker-end="url(#arrow-red)"/>

  <!-- Step F2: LangGraph Cyclic Edge -->
  <rect x="675" y="660" width="380" height="280" rx="6" fill="{WHITE}" stroke="{RED}" stroke-width="1.2"/>
  <rect x="675" y="660" width="380" height="26" rx="4" fill="{RED}"/>
  <text x="690" y="678" font-size="12" font-weight="700" fill="{WHITE}">F2. LangGraph Cyclic Routing (workflow.py)</text>
  <text x="690" y="708" font-size="13" font-weight="700" fill="{NAVY}">route_after_validation() Logic:</text>
  <rect x="690" y="725" width="350" height="75" rx="4" fill="{LIGHT_RED}"/>
  <text x="700" y="745" font-size="11" font-family="monospace" fill="{RED}">if state.get("replan_reason"):</text>
  <text x="720" y="765" font-size="11" font-family="monospace" fill="{RED}">return "planning_agent"</text>
  <text x="700" y="785" font-size="11" font-family="monospace" fill="{TEXT_DARK}"># Bypasses Requirement Analyzer</text>

  <text x="690" y="825" font-size="12" font-weight="700" fill="{NAVY}">Key Architectural Advantage:</text>
  <text x="690" y="845" font-size="11" fill="{TEXT_MUTED}">• Only downstream planning and execution are redone</text>
  <text x="690" y="865" font-size="11" fill="{TEXT_MUTED}">• Does not restart entire conversational intake</text>
  <text x="690" y="885" font-size="11" fill="{TEXT_MUTED}">• Keeps replanning loop fast and computationally cheap</text>
  <text x="690" y="915" font-size="11" font-weight="700" fill="{RED}">Bounded Retries: Terminates after max attempts</text>

  <!-- Arrow F2 -> F3 -->
  <line x1="675" y1="800" x2="615" y2="800" stroke="{RED}" stroke-width="2.5" marker-end="url(#arrow-red)"/>

  <!-- Step F3: Corrective Prompting & Re-Execution -->
  <rect x="215" y="660" width="400" height="280" rx="6" fill="{WHITE}" stroke="{RED}" stroke-width="1.2"/>
  <rect x="215" y="660" width="400" height="26" rx="4" fill="{NAVY}"/>
  <text x="230" y="678" font-size="12" font-weight="700" fill="{WHITE}">F3. Corrective Replanning &amp; Re-Execution</text>
  <text x="230" y="708" font-size="13" font-weight="700" fill="{NAVY}">Planner Prompt Ingestion (planning_agent.py):</text>
  <rect x="230" y="725" width="370" height="75" rx="4" fill="{BG_LIGHT}" stroke="{BORDER_SLATE}" stroke-width="1"/>
  <text x="240" y="745" font-size="11" font-family="monospace" fill="{NAVY}">user_msg += (</text>
  <text x="255" y="765" font-size="11" font-family="monospace" fill="{RED}">  "\\nCRITICAL REPLAN REASON:\\n"</text>
  <text x="255" y="785" font-size="11" font-family="monospace" fill="{RED}">  + replan_reason)</text>

  <text x="230" y="825" font-size="12" font-weight="700" fill="{NAVY}">Corrective Action:</text>
  <text x="230" y="845" font-size="11" fill="{TEXT_MUTED}">• LLM generates new plan specifically addressing failure</text>
  <text x="230" y="865" font-size="11" fill="{TEXT_MUTED}">• Document Agent regenerates file with complete content</text>
  <text x="230" y="885" font-size="11" fill="{TEXT_MUTED}">• Re-enters Validation Agent for second verification</text>
  <text x="230" y="915" font-size="11" font-weight="700" fill="{GREEN}">Outcome: Closed-loop self-healing verified</text>

  <!-- Complete cyclic loop line back to Top Planning Node around left margin -->
  <path d="M 215 800 L 35 800 L 35 225 L 355 225" fill="none" stroke="{RED}" stroke-width="2.5" stroke-dasharray="6,4" marker-end="url(#arrow-red)"/>
  <rect x="15" y="470" width="40" height="150" rx="4" fill="{LIGHT_RED}" stroke="{RED}" stroke-width="1"/>
  <text x="38" y="545" font-size="10" font-weight="700" fill="{RED}" text-anchor="middle" transform="rotate(-90 38 545)">CYCLIC REPLAN</text>
</svg>"""


# ==============================================================================
# FIGURE 9: Output Validation and Replanning Loop
# ==============================================================================
def generate_svg_figure_09() -> str:
    return f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1600 1100" width="1600" height="1100" style="background:#FFFFFF; font-family:'Segoe UI', Inter, Helvetica, Arial, sans-serif;">
  <defs>
    <marker id="arrow" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
      <path d="M 0 1 L 10 5 L 0 9 z" fill="{SLATE}"/>
    </marker>
    <marker id="arrow-green" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
      <path d="M 0 1 L 10 5 L 0 9 z" fill="{GREEN}"/>
    </marker>
    <marker id="arrow-red" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
      <path d="M 0 1 L 10 5 L 0 9 z" fill="{RED}"/>
    </marker>
    <filter id="shadow" x="-3%" y="-3%" width="106%" height="106%">
      <feDropShadow dx="0" dy="2" stdDeviation="3" flood-opacity="0.08"/>
    </filter>
  </defs>

  <!-- Title & Header -->
  <rect x="0" y="0" width="1600" height="70" fill="{NAVY}"/>
  <text x="50" y="44" font-size="22" font-weight="700" fill="{WHITE}">DesktopPilot AI — Output Validation &amp; Replanning Loop Specification</text>
  <text x="1550" y="44" font-size="14" font-weight="500" fill="#93C5FD" text-anchor="end">Source: `desktop_pilot/agents/validation_agent.py`</text>

  <!-- 3 Main Columns: Artifact Types & Their Exact Implemented Structural Rules -->

  <!-- Column 1: Word (.docx) Validation -->
  <rect x="50" y="95" width="480" height="520" rx="8" fill="{BG_LIGHT}" stroke="{BORDER_SLATE}" stroke-width="1.5" filter="url(#shadow)"/>
  <rect x="50" y="95" width="480" height="38" rx="4" fill="{NAVY}"/>
  <text x="70" y="120" font-size="15" font-weight="700" fill="{WHITE}">WORD (.docx) STRUCTURAL VALIDATION</text>

  <rect x="70" y="150" width="440" height="150" rx="6" fill="{WHITE}" stroke="{BORDER_SLATE}" stroke-width="1.2"/>
  <text x="85" y="175" font-size="13" font-weight="700" fill="{NAVY}">Inspector: docx.Document(filepath)</text>
  <text x="85" y="200" font-size="12" fill="{TEXT_DARK}">Check 1: File Existence &amp; Non-Zero Size</text>
  <text x="85" y="220" font-size="11" fill="{TEXT_MUTED}">• os.path.exists() &amp; os.path.getsize() &gt; 0</text>
  <text x="85" y="245" font-size="12" fill="{TEXT_DARK}">Check 2: Minimum Paragraph Count</text>
  <text x="85" y="265" font-size="11" fill="{TEXT_MUTED}">• Rejects if len(doc.paragraphs) &lt;= 1</text>
  <text x="85" y="285" font-size="11" fill="{RED}">  Error: "Word document contains insufficient text (only 0 or 1 paragraph)."</text>

  <rect x="70" y="315" width="440" height="150" rx="6" fill="{WHITE}" stroke="{BORDER_SLATE}" stroke-width="1.2"/>
  <text x="85" y="340" font-size="13" font-weight="700" fill="{NAVY}">Check 3: Meaningful Content &amp; Formatting</text>
  <text x="85" y="365" font-size="12" fill="{TEXT_DARK}">• Filters whitespace: [p.text.strip() for p in doc.paragraphs]</text>
  <text x="85" y="385" font-size="12" fill="{TEXT_DARK}">• Rejects trivial placeholder text (e.g. only "Document Title")</text>
  <text x="85" y="405" font-size="11" fill="{RED}">  Error: "Word document has no meaningful text content (only title/empty)."</text>
  <text x="85" y="430" font-size="12" fill="{TEXT_DARK}">• Verifies structured formal letter components:</text>
  <text x="85" y="450" font-size="11" fill="{TEAL}">  From, To, Date, Subject, Salutation, Body paragraphs, Closing, Sign</text>

  <rect x="70" y="480" width="440" height="115" rx="6" fill="{WHITE}" stroke="{BORDER_SLATE}" stroke-width="1.2"/>
  <text x="85" y="505" font-size="13" font-weight="700" fill="{GREEN}">Outcome on Pass:</text>
  <text x="85" y="525" font-size="11" fill="{TEXT_DARK}">• validation_result.valid = True</text>
  <text x="85" y="545" font-size="11" fill="{TEXT_DARK}">• Log: "Validated execution of Word Document successfully."</text>
  <text x="85" y="565" font-size="11" fill="{TEXT_DARK}">• Returns verified .docx file path to User</text>


  <!-- Column 2: Excel (.xlsx) Validation -->
  <rect x="560" y="95" width="480" height="520" rx="8" fill="{BG_LIGHT}" stroke="{BORDER_SLATE}" stroke-width="1.5" filter="url(#shadow)"/>
  <rect x="560" y="95" width="480" height="38" rx="4" fill="{NAVY}"/>
  <text x="580" y="120" font-size="15" font-weight="700" fill="{WHITE}">EXCEL (.xlsx) STRUCTURAL VALIDATION</text>

  <rect x="580" y="150" width="440" height="150" rx="6" fill="{WHITE}" stroke="{BORDER_SLATE}" stroke-width="1.2"/>
  <text x="595" y="175" font-size="13" font-weight="700" fill="{NAVY}">Inspector: openpyxl.load_workbook(filepath)</text>
  <text x="595" y="200" font-size="12" fill="{TEXT_DARK}">Check 1: File Existence &amp; Non-Zero Size</text>
  <text x="595" y="220" font-size="11" fill="{TEXT_MUTED}">• os.path.exists() &amp; os.path.getsize() &gt; 0</text>
  <text x="595" y="245" font-size="12" fill="{TEXT_DARK}">Check 2: Active Worksheet Detection</text>
  <text x="595" y="265" font-size="11" fill="{TEXT_MUTED}">• Loads active sheet (ws = wb.active)</text>
  <text x="595" y="285" font-size="11" fill="{TEXT_MUTED}">• Verifies valid title &amp; column dimension</text>

  <rect x="580" y="315" width="440" height="150" rx="6" fill="{WHITE}" stroke="{BORDER_SLATE}" stroke-width="1.2"/>
  <text x="595" y="340" font-size="13" font-weight="700" fill="{NAVY}">Check 3: Row &amp; Cell Completeness</text>
  <text x="595" y="365" font-size="12" fill="{TEXT_DARK}">• Rejects empty workbooks (ws.max_row &lt;= 1 &amp;&amp; ws.max_column &lt;= 1)</text>
  <text x="595" y="385" font-size="11" fill="{RED}">  Error: "Excel file generated successfully but contains no data rows/columns."</text>
  <text x="595" y="410" font-size="12" fill="{TEXT_DARK}">• Rejects header-only sheets with 0 data rows (ws.max_row &lt;= 1)</text>
  <text x="595" y="430" font-size="11" fill="{RED}">  Error: "Excel file generated successfully but contains only headers (no data rows)."</text>
  <text x="595" y="450" font-size="12" fill="{TEAL}">• Confirms non-empty values across populated columns</text>

  <rect x="580" y="480" width="440" height="115" rx="6" fill="{WHITE}" stroke="{BORDER_SLATE}" stroke-width="1.2"/>
  <text x="595" y="505" font-size="13" font-weight="700" fill="{GREEN}">Outcome on Pass:</text>
  <text x="595" y="525" font-size="11" fill="{TEXT_DARK}">• validation_result.valid = True</text>
  <text x="595" y="545" font-size="11" fill="{TEXT_DARK}">• Log: "Validated execution of Excel Spreadsheet successfully."</text>
  <text x="595" y="565" font-size="11" fill="{TEXT_DARK}">• Returns verified .xlsx file path to User</text>


  <!-- Column 3: PowerPoint (.pptx) Validation -->
  <rect x="1070" y="95" width="480" height="520" rx="8" fill="{BG_LIGHT}" stroke="{BORDER_SLATE}" stroke-width="1.5" filter="url(#shadow)"/>
  <rect x="1070" y="95" width="480" height="38" rx="4" fill="{NAVY}"/>
  <text x="1090" y="120" font-size="15" font-weight="700" fill="{WHITE}">POWERPOINT (.pptx) STRUCTURAL VALIDATION</text>

  <rect x="1090" y="150" width="440" height="150" rx="6" fill="{WHITE}" stroke="{BORDER_SLATE}" stroke-width="1.2"/>
  <text x="1105" y="175" font-size="13" font-weight="700" fill="{NAVY}">Inspector: pptx.Presentation(filepath)</text>
  <text x="1105" y="200" font-size="12" fill="{TEXT_DARK}">Check 1: File Existence &amp; Non-Zero Size</text>
  <text x="1105" y="220" font-size="11" fill="{TEXT_MUTED}">• os.path.exists() &amp; os.path.getsize() &gt; 0</text>
  <text x="1105" y="245" font-size="12" fill="{TEXT_DARK}">Check 2: Minimum Slide Count</text>
  <text x="1105" y="265" font-size="11" fill="{TEXT_MUTED}">• Rejects if len(prs.slides) == 0</text>
  <text x="1105" y="285" font-size="11" fill="{RED}">  Error: "PowerPoint generated successfully but contains no slides."</text>

  <rect x="1090" y="315" width="440" height="150" rx="6" fill="{WHITE}" stroke="{BORDER_SLATE}" stroke-width="1.2"/>
  <text x="1105" y="340" font-size="13" font-weight="700" fill="{NAVY}">Check 3: Non-Placeholder Content Validation</text>
  <text x="1105" y="365" font-size="12" fill="{TEXT_DARK}">• Iterates all slide.shapes across all slides</text>
  <text x="1105" y="385" font-size="12" fill="{TEXT_DARK}">• Extracts shape.text and verifies non-empty strings</text>
  <text x="1105" y="405" font-size="12" fill="{TEXT_DARK}">• Rejects decks with only default generic text</text>
  <text x="1105" y="425" font-size="11" fill="{RED}">  Error: "PowerPoint contains only empty slides or generic placeholder text."</text>
  <text x="1105" y="450" font-size="12" fill="{TEAL}">• Confirms structured bullets across slide placeholders</text>

  <rect x="1090" y="480" width="440" height="115" rx="6" fill="{WHITE}" stroke="{BORDER_SLATE}" stroke-width="1.2"/>
  <text x="1105" y="505" font-size="13" font-weight="700" fill="{GREEN}">Outcome on Pass:</text>
  <text x="1105" y="525" font-size="11" fill="{TEXT_DARK}">• validation_result.valid = True</text>
  <text x="1105" y="545" font-size="11" fill="{TEXT_DARK}">• Log: "Validated execution of PowerPoint Deck successfully."</text>
  <text x="1105" y="565" font-size="11" fill="{TEXT_DARK}">• Returns verified .pptx file path to User</text>


  <!-- LOWER CONTAINER: Replanning Feedback Flow -->
  <rect x="50" y="640" width="1500" height="430" rx="8" fill="{WHITE}" stroke="{BORDER_SLATE}" stroke-width="1.5" filter="url(#shadow)"/>
  <rect x="50" y="640" width="560" height="32" rx="4" fill="{NAVY}"/>
  <text x="65" y="662" font-size="13" font-weight="700" fill="{WHITE}">VALIDATION FAILURE REPLANNING &amp; RE-EXECUTION PIPELINE</text>

  <!-- Flow Boxes -->
  <!-- Box 1: File Output Inspection -->
  <rect x="80" y="700" width="310" height="345" rx="6" fill="{BG_LIGHT}" stroke="{BORDER_SLATE}" stroke-width="1.2"/>
  <rect x="80" y="700" width="310" height="26" rx="4" fill="{SLATE}"/>
  <text x="95" y="718" font-size="12" font-weight="700" fill="{WHITE}">Phase 1: Deep File Parsing</text>
  <text x="95" y="750" font-size="13" font-weight="700" fill="{NAVY}">Inspect Physical File:</text>
  <text x="95" y="775" font-size="12" fill="{TEXT_MUTED}">• Target: last_execution_result["output_file"]</text>
  <text x="95" y="795" font-size="12" fill="{TEXT_MUTED}">• Reads real binary structure via native Python</text>
  <text x="95" y="825" font-size="13" font-weight="700" fill="{NAVY}">Key Design Principle:</text>
  <text x="95" y="850" font-size="12" fill="{TEXT_DARK}">A successful code run != correct result.</text>
  <text x="95" y="875" font-size="11" fill="{TEXT_MUTED}">Validation checks the physical file itself</text>
  <text x="95" y="893" font-size="11" fill="{TEXT_MUTED}">rather than merely catching runtime exceptions.</text>

  <line x1="390" y1="870" x2="440" y2="870" stroke="{NAVY}" stroke-width="2" marker-end="url(#arrow)"/>

  <!-- Box 2: Failure Detection -->
  <rect x="440" y="700" width="330" height="345" rx="6" fill="{LIGHT_RED}" stroke="{RED}" stroke-width="1.2"/>
  <rect x="440" y="700" width="330" height="26" rx="4" fill="{RED}"/>
  <text x="455" y="718" font-size="12" font-weight="700" fill="{WHITE}">Phase 2: Error Diagnosis</text>
  <text x="455" y="750" font-size="13" font-weight="700" fill="{RED}">Structural Check Fails:</text>
  <text x="455" y="775" font-size="12" fill="{TEXT_DARK}">• failure_msg generated with exact reason</text>
  <text x="455" y="805" font-size="13" font-weight="700" fill="{NAVY}">State Updates in validation_agent:</text>
  <rect x="455" y="825" width="300" height="90" rx="4" fill="{WHITE}" stroke="{RED}" stroke-width="1"/>
  <text x="465" y="845" font-size="11" font-family="monospace" fill="{RED}">"validation_result": &#123;</text>
  <text x="480" y="865" font-size="11" font-family="monospace" fill="{RED}">  "valid": False,</text>
  <text x="480" y="885" font-size="11" font-family="monospace" fill="{RED}">  "reason": failure_msg</text>
  <text x="465" y="905" font-size="11" font-family="monospace" fill="{RED}">&#125;</text>
  <text x="455" y="935" font-size="11" font-family="monospace" fill="{RED}">"replan_reason": failure_msg</text>
  <text x="455" y="955" font-size="11" fill="{TEXT_DARK}">• Appends status: "error" to trace</text>

  <line x1="770" y1="870" x2="820" y2="870" stroke="{RED}" stroke-width="2" marker-end="url(#arrow-red)"/>

  <!-- Box 3: LangGraph Routing -->
  <rect x="820" y="700" width="330" height="345" rx="6" fill="{WHITE}" stroke="{BORDER_SLATE}" stroke-width="1.2"/>
  <rect x="820" y="700" width="330" height="26" rx="4" fill="{NAVY}"/>
  <text x="835" y="718" font-size="12" font-weight="700" fill="{WHITE}">Phase 3: Cyclic Edge Routing</text>
  <text x="835" y="750" font-size="13" font-weight="700" fill="{NAVY}">route_after_validation():</text>
  <text x="835" y="775" font-size="12" fill="{TEXT_MUTED}">• Detects non-None replan_reason</text>
  <text x="835" y="795" font-size="12" fill="{RED}">• Routes graph directly to planning_agent</text>
  <text x="835" y="825" font-size="13" font-weight="700" fill="{NAVY}">Bounded Retries Mechanism:</text>
  <text x="835" y="850" font-size="12" fill="{TEXT_MUTED}">• Prevents infinite loops under unsatisfiable requests</text>
  <text x="835" y="875" font-size="12" fill="{TEXT_MUTED}">• Terminates gracefully if threshold exceeded</text>

  <line x1="1150" y1="870" x2="1200" y2="870" stroke="{NAVY}" stroke-width="2" marker-end="url(#arrow)"/>

  <!-- Box 4: Correction & Regeneration -->
  <rect x="1200" y="700" width="320" height="345" rx="6" fill="{LIGHT_GREEN}" stroke="{GREEN}" stroke-width="1.2"/>
  <rect x="1200" y="700" width="320" height="26" rx="4" fill="{GREEN}"/>
  <text x="1215" y="718" font-size="12" font-weight="700" fill="{WHITE}">Phase 4: Corrected Re-Execution</text>
  <text x="1215" y="750" font-size="13" font-weight="700" fill="{NAVY}">Planner Prompts with Context:</text>
  <text x="1215" y="775" font-size="11" fill="{TEXT_DARK}">• System prompt instructs LLM to fix errors described in replan_reason</text>
  <text x="1215" y="805" font-size="13" font-weight="700" fill="{NAVY}">Regeneration &amp; Re-Check:</text>
  <text x="1215" y="830" font-size="11" fill="{TEXT_DARK}">1. Planner outputs revised structured content</text>
  <text x="1215" y="850" font-size="11" fill="{TEXT_DARK}">2. Document Agent regenerates file</text>
  <text x="1215" y="870" font-size="11" fill="{TEXT_DARK}">3. Validation Agent performs structural re-test</text>
  <text x="1215" y="890" font-size="11" font-weight="700" fill="{GREEN}">4. PASS achieved on second pass</text>
  <text x="1215" y="920" font-size="11" fill="{TEXT_DARK}">Verified empirically in Test Case 7.</text>
</svg>"""


# ==============================================================================
# FIGURE 10: Preliminary Evaluation and Baseline Comparison
# ==============================================================================
def generate_svg_figure_10() -> str:
    return f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1600 1100" width="1600" height="1100" style="background:#FFFFFF; font-family:'Segoe UI', Inter, Helvetica, Arial, sans-serif;">
  <defs>
    <filter id="shadow" x="-3%" y="-3%" width="106%" height="106%">
      <feDropShadow dx="0" dy="2" stdDeviation="3" flood-opacity="0.08"/>
    </filter>
  </defs>

  <!-- Title & Header -->
  <rect x="0" y="0" width="1600" height="70" fill="{NAVY}"/>
  <text x="50" y="44" font-size="22" font-weight="700" fill="{WHITE}">DesktopPilot AI — Preliminary Evaluation &amp; Baseline Comparison Matrix</text>
  <text x="1550" y="44" font-size="14" font-weight="500" fill="#93C5FD" text-anchor="end">Source: Report Sections 12 &amp; 13 (Tables 4 &amp; 5)</text>

  <!-- Side-by-Side Dual-Panel Evaluation Visualization -->

  <!-- PANEL A: 7 Preliminary Structural Test Cases -->
  <rect x="50" y="95" width="750" height="950" rx="8" fill="{BG_LIGHT}" stroke="{BORDER_SLATE}" stroke-width="1.5" filter="url(#shadow)"/>
  <rect x="50" y="95" width="750" height="38" rx="4" fill="{NAVY}"/>
  <text x="70" y="120" font-size="15" font-weight="700" fill="{WHITE}">PANEL A: PRELIMINARY TEST RESULTS (7/7 PASSED)</text>

  <rect x="70" y="150" width="710" height="50" rx="4" fill="{LIGHT_GREEN}" stroke="{GREEN}" stroke-width="1.2"/>
  <text x="90" y="180" font-size="14" font-weight="700" fill="{GREEN}">Overall Empirical Result: 7 of 7 Structural Test Cases PASSED (100% Structural Success)</text>

  <!-- Table Header -->
  <rect x="70" y="215" width="710" height="32" rx="4" fill="{SLATE}"/>
  <text x="90" y="236" font-size="12" font-weight="700" fill="{WHITE}">Test Case</text>
  <text x="320" y="236" font-size="12" font-weight="700" fill="{WHITE}">Expected Structural Result</text>
  <text x="690" y="236" font-size="12" font-weight="700" fill="{WHITE}">Status</text>

  <!-- Row 1: Formal Leave Letter -->
  <rect x="70" y="255" width="710" height="90" rx="4" fill="{WHITE}" stroke="{BORDER_SLATE}" stroke-width="1"/>
  <text x="90" y="280" font-size="13" font-weight="700" fill="{NAVY}">1. Formal Leave Letter</text>
  <text x="90" y="300" font-size="11" fill="{TEXT_MUTED}">Domain: Word Document (`.docx`)</text>
  <text x="90" y="320" font-size="11" fill="{TEXT_MUTED}">Trigger: Persona "Anita" leave request</text>
  <text x="320" y="280" font-size="12" fill="{TEXT_DARK}">Valid DOCX with standard layout (From, To,</text>
  <text x="320" y="300" font-size="12" fill="{TEXT_DARK}">Subject, Salutation, Body, Closing, Signature)</text>
  <rect x="670" y="275" width="80" height="30" rx="4" fill="{LIGHT_GREEN}" stroke="{GREEN}" stroke-width="1"/>
  <text x="710" y="295" font-size="12" font-weight="700" fill="{GREEN}" text-anchor="middle">PASS</text>

  <!-- Row 2: TC Request Letter -->
  <rect x="70" y="355" width="710" height="90" rx="4" fill="{WHITE}" stroke="{BORDER_SLATE}" stroke-width="1"/>
  <text x="90" y="380" font-size="13" font-weight="700" fill="{NAVY}">2. TC Request Letter</text>
  <text x="90" y="400" font-size="11" fill="{TEXT_MUTED}">Domain: Word Document (`.docx`)</text>
  <text x="90" y="420" font-size="11" fill="{TEXT_MUTED}">Trigger: Transfer certificate application</text>
  <text x="320" y="380" font-size="12" fill="{TEXT_DARK}">Structured DOCX with multi-field verification,</text>
  <text x="320" y="400" font-size="12" fill="{TEXT_DARK}">formal institutional tone, and validated paragraphs</text>
  <rect x="670" y="375" width="80" height="30" rx="4" fill="{LIGHT_GREEN}" stroke="{GREEN}" stroke-width="1"/>
  <text x="710" y="395" font-size="12" font-weight="700" fill="{GREEN}" text-anchor="middle">PASS</text>

  <!-- Row 3: Attendance Report -->
  <rect x="70" y="455" width="710" height="90" rx="4" fill="{WHITE}" stroke="{BORDER_SLATE}" stroke-width="1"/>
  <text x="90" y="480" font-size="13" font-weight="700" fill="{NAVY}">3. Attendance Report</text>
  <text x="90" y="500" font-size="11" fill="{TEXT_MUTED}">Domain: Excel Spreadsheet (`.xlsx`)</text>
  <text x="90" y="520" font-size="11" fill="{TEXT_MUTED}">Trigger: Persona "Ramesh" staff report</text>
  <text x="320" y="480" font-size="12" fill="{TEXT_DARK}">Header row present with alignment + complete</text>
  <text x="320" y="500" font-size="12" fill="{TEXT_DARK}">data rows across 10 students (no blank cells)</text>
  <rect x="670" y="475" width="80" height="30" rx="4" fill="{LIGHT_GREEN}" stroke="{GREEN}" stroke-width="1"/>
  <text x="710" y="495" font-size="12" font-weight="700" fill="{GREEN}" text-anchor="middle">PASS</text>

  <!-- Row 4: 5-Slide Presentation -->
  <rect x="70" y="555" width="710" height="90" rx="4" fill="{WHITE}" stroke="{BORDER_SLATE}" stroke-width="1"/>
  <text x="90" y="580" font-size="13" font-weight="700" fill="{NAVY}">4. 5-Slide Presentation</text>
  <text x="90" y="600" font-size="11" fill="{TEXT_MUTED}">Domain: PowerPoint Deck (`.pptx`)</text>
  <text x="90" y="620" font-size="11" fill="{TEXT_MUTED}">Trigger: Persona "Priya" seminar topic</text>
  <text x="320" y="580" font-size="12" fill="{TEXT_DARK}">Meaningful slide deck with exact slide count,</text>
  <text x="320" y="600" font-size="12" fill="{TEXT_DARK}">title &amp; body bullets, non-placeholder content</text>
  <rect x="670" y="575" width="80" height="30" rx="4" fill="{LIGHT_GREEN}" stroke="{GREEN}" stroke-width="1"/>
  <text x="710" y="595" font-size="12" font-weight="700" fill="{GREEN}" text-anchor="middle">PASS</text>

  <!-- Row 5: New-Topic Document -->
  <rect x="70" y="655" width="710" height="90" rx="4" fill="{WHITE}" stroke="{BORDER_SLATE}" stroke-width="1"/>
  <text x="90" y="680" font-size="13" font-weight="700" fill="{NAVY}">5. New-Topic Document</text>
  <text x="90" y="700" font-size="11" fill="{TEXT_MUTED}">Domain: Context Isolation Check</text>
  <text x="90" y="720" font-size="11" fill="{TEXT_MUTED}">Trigger: Back-to-back unrelated prompt</text>
  <text x="320" y="680" font-size="12" fill="{TEXT_DARK}">No leakage of previous task's parameters or plan;</text>
  <text x="320" y="700" font-size="12" fill="{TEXT_DARK}">starts with clean ephemeral `current_task_info`</text>
  <rect x="670" y="675" width="80" height="30" rx="4" fill="{LIGHT_GREEN}" stroke="{GREEN}" stroke-width="1"/>
  <text x="710" y="695" font-size="12" font-weight="700" fill="{GREEN}" text-anchor="middle">PASS</text>

  <!-- Row 6: New-Topic Presentation -->
  <rect x="70" y="755" width="710" height="90" rx="4" fill="{WHITE}" stroke="{BORDER_SLATE}" stroke-width="1"/>
  <text x="90" y="780" font-size="13" font-weight="700" fill="{NAVY}">6. New-Topic Presentation</text>
  <text x="90" y="800" font-size="11" fill="{TEXT_MUTED}">Domain: Independent Deck Generation</text>
  <text x="90" y="820" font-size="11" fill="{TEXT_MUTED}">Trigger: Fresh topic deck request</text>
  <text x="320" y="780" font-size="12" fill="{TEXT_DARK}">Independent content and structure created</text>
  <text x="320" y="800" font-size="12" fill="{TEXT_DARK}">specifically for the requested technical domain</text>
  <rect x="670" y="775" width="80" height="30" rx="4" fill="{LIGHT_GREEN}" stroke="{GREEN}" stroke-width="1"/>
  <text x="710" y="795" font-size="12" font-weight="700" fill="{GREEN}" text-anchor="middle">PASS</text>

  <!-- Row 7: Deliberate Validation Failure -->
  <rect x="70" y="855" width="710" height="95" rx="4" fill="{WHITE}" stroke="{BORDER_SLATE}" stroke-width="1"/>
  <text x="90" y="880" font-size="13" font-weight="700" fill="{RED}">7. Deliberate Validation Failure</text>
  <text x="90" y="900" font-size="11" fill="{TEXT_MUTED}">Domain: Self-Correction &amp; Replanning</text>
  <text x="90" y="920" font-size="11" fill="{TEXT_MUTED}">Trigger: Malformed artifact injection</text>
  <text x="320" y="880" font-size="12" fill="{TEXT_DARK}">Validation fails on first pass; failure reason</text>
  <text x="320" y="900" font-size="12" fill="{TEXT_DARK}">routed to planner; successful replanned re-execution</text>
  <rect x="670" y="875" width="80" height="30" rx="4" fill="{LIGHT_GREEN}" stroke="{GREEN}" stroke-width="1"/>
  <text x="710" y="895" font-size="12" font-weight="700" fill="{GREEN}" text-anchor="middle">PASS</text>

  <rect x="70" y="960" width="710" height="70" rx="4" fill="{WHITE}" stroke="{BORDER_SLATE}" stroke-width="1"/>
  <text x="90" y="985" font-size="12" font-weight="700" fill="{NAVY}">Methodology Note (Section 12.1):</text>
  <text x="90" y="1005" font-size="11" fill="{TEXT_MUTED}">Evaluation is strictly qualitative &amp; structural against physical file checks.</text>
  <text x="90" y="1020" font-size="11" fill="{TEXT_MUTED}">No fabricated F1/accuracy scores or artificial benchmarking metrics are asserted.</text>


  <!-- PANEL B: Architectural Capability Comparison Matrix -->
  <rect x="830" y="95" width="720" height="950" rx="8" fill="{BG_LIGHT}" stroke="{BORDER_SLATE}" stroke-width="1.5" filter="url(#shadow)"/>
  <rect x="830" y="95" width="720" height="38" rx="4" fill="{NAVY}"/>
  <text x="850" y="120" font-size="15" font-weight="700" fill="{WHITE}">PANEL B: BASELINE CAPABILITY COMPARISON (TABLE 5)</text>

  <!-- Table Header -->
  <rect x="850" y="150" width="680" height="35" rx="4" fill="{SLATE}"/>
  <text x="870" y="173" font-size="13" font-weight="700" fill="{WHITE}">Capability Dimension</text>
  <text x="1100" y="173" font-size="13" font-weight="700" fill="{WHITE}">Traditional LLM Chatbot</text>
  <text x="1350" y="173" font-size="13" font-weight="700" fill="{WHITE}">DesktopPilot AI</text>

  <!-- Dim 1: Planning / Strategy -->
  <rect x="850" y="195" width="680" height="85" rx="4" fill="{WHITE}" stroke="{BORDER_SLATE}" stroke-width="1"/>
  <text x="870" y="225" font-size="13" font-weight="700" fill="{NAVY}">1. Planning / Strategy</text>
  <text x="870" y="248" font-size="11" fill="{TEXT_MUTED}">Step decomposition &amp; routing</text>
  <text x="1100" y="225" font-size="13" font-weight="600" fill="{AMBER}">Limited</text>
  <text x="1100" y="248" font-size="11" fill="{TEXT_MUTED}">Single-shot prompt only</text>
  <rect x="1340" y="215" width="130" height="28" rx="4" fill="{LIGHT_GREEN}" stroke="{GREEN}" stroke-width="1"/>
  <text x="1405" y="234" font-size="11" font-weight="700" fill="{GREEN}" text-anchor="middle">Implemented</text>
  <text x="1350" y="260" font-size="11" fill="{TEXT_DARK}">Multi-step JSON planner</text>

  <!-- Dim 2: Tool Execution (OS / GUI) -->
  <rect x="850" y="290" width="680" height="85" rx="4" fill="{WHITE}" stroke="{BORDER_SLATE}" stroke-width="1"/>
  <text x="870" y="320" font-size="13" font-weight="700" fill="{NAVY}">2. Tool Execution (OS/GUI)</text>
  <text x="870" y="343" font-size="11" fill="{TEXT_MUTED}">Desktop &amp; browser automation</text>
  <text x="1100" y="320" font-size="13" font-weight="600" fill="{AMBER}">Limited</text>
  <text x="1100" y="343" font-size="11" fill="{TEXT_MUTED}">Text explanation only</text>
  <rect x="1340" y="310" width="130" height="28" rx="4" fill="{LIGHT_GREEN}" stroke="{GREEN}" stroke-width="1"/>
  <text x="1405" y="329" font-size="11" font-weight="700" fill="{GREEN}" text-anchor="middle">Implemented</text>
  <text x="1350" y="355" font-size="11" fill="{TEXT_DARK}">Playwright / OS utilities</text>

  <!-- Dim 3: Multi-Agent Coordination -->
  <rect x="850" y="385" width="680" height="85" rx="4" fill="{WHITE}" stroke="{BORDER_SLATE}" stroke-width="1"/>
  <text x="870" y="415" font-size="13" font-weight="700" fill="{NAVY}">3. Multi-Agent Coordination</text>
  <text x="870" y="438" font-size="11" fill="{TEXT_MUTED}">Specialized roles &amp; dispatch</text>
  <text x="1100" y="415" font-size="13" font-weight="600" fill="{RED}">Absent</text>
  <text x="1100" y="438" font-size="11" fill="{TEXT_MUTED}">Monolithic single LLM</text>
  <rect x="1340" y="405" width="130" height="28" rx="4" fill="{LIGHT_GREEN}" stroke="{GREEN}" stroke-width="1"/>
  <text x="1405" y="424" font-size="11" font-weight="700" fill="{GREEN}" text-anchor="middle">Implemented</text>
  <text x="1350" y="450" font-size="11" fill="{TEXT_DARK}">LangGraph StateGraph</text>

  <!-- Dim 4: File / Asset Generation -->
  <rect x="850" y="480" width="680" height="85" rx="4" fill="{WHITE}" stroke="{BORDER_SLATE}" stroke-width="1"/>
  <text x="870" y="510" font-size="13" font-weight="700" fill="{NAVY}">4. File / Asset Generation</text>
  <text x="870" y="533" font-size="11" fill="{TEXT_MUTED}">Binary Office artifact creation</text>
  <text x="1100" y="510" font-size="13" font-weight="600" fill="{AMBER}">Limited</text>
  <text x="1100" y="533" font-size="11" fill="{TEXT_MUTED}">Markdown / raw text</text>
  <rect x="1340" y="500" width="130" height="28" rx="4" fill="{LIGHT_GREEN}" stroke="{GREEN}" stroke-width="1"/>
  <text x="1405" y="519" font-size="11" font-weight="700" fill="{GREEN}" text-anchor="middle">Implemented</text>
  <text x="1350" y="545" font-size="11" fill="{TEXT_DARK}">Native DOCX / XLSX / PPTX</text>

  <!-- Dim 5: Automated Validation -->
  <rect x="850" y="575" width="680" height="85" rx="4" fill="{WHITE}" stroke="{BORDER_SLATE}" stroke-width="1"/>
  <text x="870" y="605" font-size="13" font-weight="700" fill="{NAVY}">5. Automated Validation</text>
  <text x="870" y="628" font-size="11" fill="{TEXT_MUTED}">Physical file structural check</text>
  <text x="1100" y="605" font-size="13" font-weight="600" fill="{RED}">Absent</text>
  <text x="1100" y="628" font-size="11" fill="{TEXT_MUTED}">No verification of output</text>
  <rect x="1340" y="595" width="130" height="28" rx="4" fill="{LIGHT_GREEN}" stroke="{GREEN}" stroke-width="1"/>
  <text x="1405" y="614" font-size="11" font-weight="700" fill="{GREEN}" text-anchor="middle">Implemented</text>
  <text x="1350" y="640" font-size="11" fill="{TEXT_DARK}">Deep structural inspector</text>

  <!-- Dim 6: Memory / Persistent State -->
  <rect x="850" y="670" width="680" height="85" rx="4" fill="{WHITE}" stroke="{BORDER_SLATE}" stroke-width="1"/>
  <text x="870" y="700" font-size="13" font-weight="700" fill="{NAVY}">6. Memory / Persistent State</text>
  <text x="870" y="723" font-size="11" fill="{TEXT_MUTED}">Two-layer session persistence</text>
  <text x="1100" y="700" font-size="13" font-weight="600" fill="{AMBER}">Basic</text>
  <text x="1100" y="723" font-size="11" fill="{TEXT_MUTED}">Context window overflow risk</text>
  <rect x="1340" y="690" width="130" height="28" rx="4" fill="{LIGHT_GREEN}" stroke="{GREEN}" stroke-width="1"/>
  <text x="1405" y="709" font-size="11" font-weight="700" fill="{GREEN}" text-anchor="middle">Implemented</text>
  <text x="1350" y="735" font-size="11" fill="{TEXT_DARK}">SQLite + Ephemeral cleanup</text>

  <!-- Dim 7: Exception Replanning -->
  <rect x="850" y="765" width="680" height="85" rx="4" fill="{WHITE}" stroke="{BORDER_SLATE}" stroke-width="1"/>
  <text x="870" y="795" font-size="13" font-weight="700" fill="{NAVY}">7. Exception Replanning</text>
  <text x="870" y="818" font-size="11" fill="{TEXT_MUTED}">Autonomous error recovery</text>
  <text x="1100" y="795" font-size="13" font-weight="600" fill="{AMBER}">Limited</text>
  <text x="1100" y="818" font-size="11" fill="{TEXT_MUTED}">User must notice and re-prompt</text>
  <rect x="1340" y="785" width="130" height="28" rx="4" fill="{LIGHT_GREEN}" stroke="{GREEN}" stroke-width="1"/>
  <text x="1405" y="804" font-size="11" font-weight="700" fill="{GREEN}" text-anchor="middle">Implemented</text>
  <text x="1350" y="830" font-size="11" fill="{TEXT_DARK}">Cyclic LangGraph replan edge</text>

  <!-- Summary Callout -->
  <rect x="850" y="865" width="680" height="165" rx="6" fill="{WHITE}" stroke="{BORDER_SLATE}" stroke-width="1"/>
  <text x="870" y="895" font-size="13" font-weight="700" fill="{NAVY}">Summary of Architectural Advancements:</text>
  <text x="870" y="920" font-size="12" fill="{TEXT_DARK}">• While a standard LLM terminates its responsibility at generating conversational text,</text>
  <text x="870" y="940" font-size="12" fill="{NAVY}">  DesktopPilot AI treats user requests as obligations to produce verified filesystem artifacts.</text>
  <text x="870" y="965" font-size="12" fill="{TEXT_DARK}">• Structural validation ensures that format omissions, empty rows, or corrupt layouts are</text>
  <text x="870" y="985" font-size="12" fill="{TEXT_DARK}">  detected programmatically and corrected autonomously before delivery.</text>
  <text x="870" y="1010" font-size="11" font-weight="600" fill="{TEAL}">• All 7 capability dimensions reflect implemented modules in `desktop_pilot/` codebase.</text>
</svg>"""


# ==============================================================================
# MAIN EXPORT RUNNER (SVG + PNG RENDERING VIA PLAYWRIGHT)
# ==============================================================================
async def main():
    figures = [
        ("figure_01_system_architecture", generate_svg_figure_01(), 1600, 1150),
        ("figure_02_langgraph_workflow", generate_svg_figure_02(), 1600, 1200),
        ("figure_03_agentic_rag_concept", generate_svg_figure_03(), 1600, 1000),
        ("figure_06_tool_integration", generate_svg_figure_06(), 1600, 1100),
        ("figure_07_memory_state", generate_svg_figure_07(), 1600, 1100),
        ("figure_08_closed_loop_reasoning", generate_svg_figure_08(), 1600, 1000),
        ("figure_09_validation_replanning", generate_svg_figure_09(), 1600, 1100),
        ("figure_10_evaluation_comparison", generate_svg_figure_10(), 1600, 1100),
    ]

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        
        for name, svg_content, width, height in figures:
            svg_path = os.path.join(OUTPUT_DIR, f"{name}.svg")
            png_path = os.path.join(OUTPUT_DIR, f"{name}.png")

            # Write SVG
            with open(svg_path, "w", encoding="utf-8") as f:
                f.write(svg_content)
            print(f"Generated SVG: {svg_path}")

            # Render high-res PNG (2x scale for 300 DPI publication crispness)
            page = await browser.new_page(viewport={"width": width, "height": height}, device_scale_factor=2)
            await page.set_content(f"<!DOCTYPE html><html><body style='margin:0;padding:0;background:#fff;'>{svg_content}</body></html>")
            await page.screenshot(path=png_path)
            await page.close()
            print(f"Generated PNG: {png_path} ({width*2}x{height*2} px)")

        await browser.close()

    print("\nAll vector & raster diagram figures generated successfully!")

if __name__ == "__main__":
    asyncio.run(main())

@echo off
setlocal enabledelayedexpansion

title GravityPilot AI Launcher
cd /d "%~dp0"

echo ========================================================
echo                 GRAVITYPILOT AI STARTUP
echo ========================================================
echo.

:: 1. Check Python installation
echo [1/6] Checking Python...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo.
    echo [ERROR] Python was not found!
    echo Please install Python 3.10+ from https://www.python.org/
    echo and ensure "Add Python to PATH" is checked during installation.
    echo.
    pause
    exit /b 1
)

:: 2. Check Node.js and npm
echo [2/6] Checking Node.js and npm...
node --version >nul 2>&1
if %errorlevel% neq 0 (
    echo.
    echo [ERROR] Node.js was not found!
    echo Please install Node.js LTS from https://nodejs.org/
    echo.
    pause
    exit /b 1
)

npm --version >nul 2>&1
if %errorlevel% neq 0 (
    echo.
    echo [ERROR] npm was not found!
    echo Please install Node.js with npm included.
    echo.
    pause
    exit /b 1
)

:: 3. Check / Create .env configuration
echo [3/6] Checking configuration...
if not exist ".env" (
    if exist ".env.example" (
        copy ".env.example" ".env" >nul
        echo [INFO] Created .env template from .env.example.
    )
)

set "HAS_GROQ=0"
if exist ".env" (
    for /f "usebackq tokens=1,2 delims==" %%A in (".env") do (
        if /i "%%A"=="GROQ_API_KEY" (
            if not "%%B"=="" (
                set "HAS_GROQ=1"
            )
        )
    )
)

if "%HAS_GROQ%"=="0" (
    echo.
    echo [NOTICE] GROQ_API_KEY is not configured in .env.
    echo To enable online AI capabilities (Qwen / Llama), add your key to:
    echo   %~dp0.env
    echo Get a free key at: https://console.groq.com
    echo.
)

:: 4. Clean existing stale processes on ports 8000 and 5173
echo [4/6] Checking port availability...
for /f "tokens=5" %%a in ('netstat -aon ^| findstr ":8000" ^| findstr "LISTENING"') do (
    echo [INFO] Freeing port 8000 - PID %%a
    taskkill /F /PID %%a >nul 2>&1
)
for /f "tokens=5" %%a in ('netstat -aon ^| findstr ":5173" ^| findstr "LISTENING"') do (
    echo [INFO] Freeing port 5173 - PID %%a
    taskkill /F /PID %%a >nul 2>&1
)

:: 5. Ensure dependencies are present
echo [5/6] Verifying dependencies...
python -c "import fastapi, langgraph, docx, openpyxl, pptx, aiosqlite" >nul 2>&1
if %errorlevel% neq 0 (
    echo [INFO] Installing missing Python backend dependencies...
    python -m pip install -r backend\requirements.txt
)

if not exist "frontend\node_modules" (
    echo [INFO] Installing frontend packages...
    cd frontend && call npm install && cd ..
)

:: 6. Start Services
echo [6/6] Launching GravityPilot Services...
echo [INFO] Starting FastAPI Backend on http://localhost:8000 ...
start "GravityPilot Backend" /B python backend\main.py

echo [INFO] Starting Vite Frontend on http://localhost:5173 ...
cd frontend
start "GravityPilot Frontend" /B npm run dev
cd ..

echo.
echo [INFO] Waiting for GravityPilot Web UI to become ready...

:: Poll until http://localhost:5173 responds, then open browser
powershell -NoProfile -Command "$ready = $false; for ($i=0; $i -lt 30; $i++) { try { $res = Invoke-WebRequest -Uri 'http://localhost:5173' -UseBasicParsing -TimeoutSec 1; if ($res.StatusCode -eq 200) { $ready = $true; break } } catch {}; Start-Sleep -Milliseconds 600 }; if ($ready) { Write-Host '[SUCCESS] GravityPilot Web UI is live!' -ForegroundColor Green } else { Write-Host '[INFO] Opening browser...' }; Start-Process 'http://localhost:5173'"

echo.
echo ========================================================
echo   GravityPilot AI is running!
echo   Web UI:    http://localhost:5173
echo   API Docs:  http://localhost:8000/docs
echo   Health:    http://localhost:8000/health
echo.
echo   To stop the application, run STOP.bat or close this window.
echo ========================================================
echo.

powershell -NoProfile -Command "while ($true) { Start-Sleep -Seconds 3600 }"

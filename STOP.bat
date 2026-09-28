@echo off
setlocal enabledelayedexpansion

echo ========================================================
echo   Stopping GravityPilot Services...
echo ========================================================

set KILLED=0

:: Terminate process on Port 8000 (FastAPI Backend)
for /f "tokens=5" %%a in ('netstat -aon ^| findstr ":8000" ^| findstr "LISTENING"') do (
    echo [INFO] Stopping Backend process on port 8000 - PID %%a
    taskkill /F /PID %%a >nul 2>&1
    set KILLED=1
)

:: Terminate process on Port 5173 (Vite Frontend)
for /f "tokens=5" %%a in ('netstat -aon ^| findstr ":5173" ^| findstr "LISTENING"') do (
    echo [INFO] Stopping Frontend process on port 5173 - PID %%a
    taskkill /F /PID %%a >nul 2>&1
    set KILLED=1
)

if "%KILLED%"=="1" (
    echo [SUCCESS] GravityPilot services stopped cleanly.
) else (
    echo [INFO] No active GravityPilot services were found on ports 8000 or 5173.
)

echo ========================================================
exit /b 0

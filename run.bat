@echo off
REM ════════════════════════════════════════════════════════════════
REM  VendorGuard AI — Run Frontend + Backend Together
REM ════════════════════════════════════════════════════════════════
REM  This batch file:
REM    1. Installs required Python packages (flask, flask-cors, etc.)
REM    2. Loads environment variables from .env (if present)
REM    3. Starts the Flask API server (backend + frontend)
REM    4. Opens the dashboard in your default browser
REM ════════════════════════════════════════════════════════════════

title VendorGuard AI — Starting...

cd /d "%~dp0"

echo.
echo  ╔══════════════════════════════════════════════════════════╗
echo  ║           VendorGuard AI — Startup Script               ║
echo  ║                                                         ║
echo  ║   Backend  : Flask API Server (port 5000)               ║
echo  ║   Frontend : Executive Dashboard (served by Flask)      ║
echo  ║   Pipeline : 4-Agent AI Procurement System              ║
echo  ╚══════════════════════════════════════════════════════════╝
echo.

REM ── Step 1: Install dependencies ──────────────────────────────
echo [1/4] Installing Python dependencies...
pip install flask flask-cors streamlit plotly openai >nul 2>&1
if %errorlevel% neq 0 (
    echo    WARNING: Some packages may have failed to install.
    echo    Trying with --user flag...
    pip install --user flask flask-cors streamlit plotly openai >nul 2>&1
)
echo    Done.
echo.

REM ── Step 2: Load .env if present ──────────────────────────────
if exist ".env" (
    echo [2/4] Loading environment variables from .env ...
    for /f "usebackq tokens=1,* delims==" %%a in (".env") do (
        set "line=%%a"
        if not "!line:~0,1!"=="#" (
            set "%%a=%%b"
        )
    )
    echo    Done.
) else if exist "env.example" (
    echo [2/4] No .env found. Copying env.example to .env ...
    copy env.example .env >nul 2>&1
    echo    Created .env from env.example. Edit it with your real API key.
) else (
    echo [2/4] No .env file found. LLM explanations will be skipped.
)
echo.

REM ── Step 3: Start the Flask API Server ────────────────────────
echo [3/4] Starting VendorGuard AI API Server...
echo    API  : http://localhost:5000/api/pipeline
echo    Web  : http://localhost:5000
echo.

REM ── Step 4: Open browser after a short delay ──────────────────
echo [4/4] Opening dashboard in browser...
start "" "http://localhost:5000"

echo.
echo ═══════════════════════════════════════════════════════════════
echo   Server is running! Press Ctrl+C to stop.
echo ═══════════════════════════════════════════════════════════════
echo.

python api_server.py

pause

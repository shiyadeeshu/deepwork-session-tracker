@echo off
REM Starts backend and frontend in separate windows.
REM (Running `python main.py` directly would block, so the frontend would never start.)
cd /d "%~dp0"

if not exist env\Scripts\activate.bat (
    echo [ERROR] Virtual environment missing. Run setupdev.bat first.
    exit /b 1
)

echo Starting backend...
start "DeepWork Backend" cmd /k "call env\Scripts\activate && python main.py"

echo Starting frontend...
if exist frontend\package.json (
    start "DeepWork Frontend" cmd /k "cd frontend && npm start"
) else (
    echo [WARN] frontend not set up yet - only the backend was started.
)

echo.
echo Backend:  http://localhost:8000      (Swagger UI: http://localhost:8000/docs)
echo Frontend: http://localhost:3000

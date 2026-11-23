@echo off
REM One-time development setup: Python venv + deps, DB migrations, frontend deps.
cd /d "%~dp0"

echo Setting up backend...
if not exist env (
    python -m venv env || goto :error
)
call env\Scripts\activate || goto :error
python -m pip install --upgrade pip >nul
pip install -r requirements.txt || goto :error
alembic upgrade head || goto :error

echo Setting up frontend...
if exist frontend\package.json (
    where npm >nul 2>nul || (echo [ERROR] npm not found. Install Node.js LTS from https://nodejs.org & goto :error)
    cd frontend
    call npm install || (cd .. & goto :error)
    cd ..
) else (
    echo [WARN] frontend\package.json not found - skipping frontend setup.
)

echo.
echo Setup complete.
echo   Optional sample data:  env\Scripts\python seed.py
echo   Start the app:         runapplication.bat
exit /b 0

:error
echo.
echo [ERROR] Setup failed. See the messages above.
exit /b 1

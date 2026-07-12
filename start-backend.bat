@echo off
setlocal

cd /d "%~dp0backend"

if not exist ".venv\Scripts\python.exe" (
    echo Backend virtual environment was not found.
    echo Run .\run.bat from the project root.
    exit /b 1
)

call ".venv\Scripts\python.exe" -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload

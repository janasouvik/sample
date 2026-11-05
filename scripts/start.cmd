@echo off
cd /d "%~dp0.."
if not exist ".venv\Scripts\python.exe" (
  echo Create .venv and install requirements first. See README.md.
  exit /b 1
)
if not exist ".env" (
  echo Copy .env.example to .env and edit your database credentials first.
  exit /b 1
)
".venv\Scripts\python.exe" -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload

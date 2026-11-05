$ErrorActionPreference = 'Stop'
Set-Location -LiteralPath (Split-Path $PSScriptRoot -Parent)
if (-not (Test-Path -LiteralPath '.venv\Scripts\python.exe')) { throw 'Create .venv and install requirements first. See README.md.' }
if (-not (Test-Path -LiteralPath '.env')) { throw 'Copy .env.example to .env and edit database credentials first.' }
& '.\.venv\Scripts\python.exe' -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
exit $LASTEXITCODE

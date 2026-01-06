@echo off
setlocal

set "ROOT=%~dp0"
set "VENV_PY=%ROOT%venv\Scripts\python.exe"

if not exist "%VENV_PY%" (
  echo Could not find venv Python at "%VENV_PY%".
  echo Create the virtual environment first.
  exit /b 1
)

start "Transcriber Backend" cmd /k "cd /d ""%ROOT%backend"" && ""%VENV_PY%"" main.py"
start "Transcriber Frontend" cmd /k "cd /d ""%ROOT%frontend"" && npm run dev -- --host"

echo Servers starting...
echo Backend: http://localhost:8000
echo Frontend: http://localhost:5173

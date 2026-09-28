@echo off
setlocal
cd /d "%~dp0"
set "WEEK1_PY=%~dp0.venv\Scripts\python.exe"
if not exist "%WEEK1_PY%" set "WEEK1_PY=%~dp0..\..\.venv\Scripts\python.exe"
if not exist "%WEEK1_PY%" (
  echo Python environment was not found. See README.md for setup.
  pause
  exit /b 1
)
"%WEEK1_PY%" -B run_assignment.py
if errorlevel 1 echo Evaluation failed. Please copy the error shown above.
pause

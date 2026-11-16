@echo off
rem Coulomb Excitation Lab - Windows launcher.
rem
rem Double-click this file in File Explorer, or run start_windows.bat in a terminal.
rem First start: creates a private Python environment (.venv) and installs the pinned packages (internet needed).
rem Later starts: run offline and open the app at http://localhost:8501. Stop with Ctrl+C.
rem Extra arguments are passed to run.py, for example:  start_windows.bat --test   or   --verify --full

setlocal
cd /d "%~dp0"

set "PYTHON="
for %%V in (3.14 3.13 3.12) do (
    if not defined PYTHON (
        py -%%V -c "import sys" >nul 2>&1 && set "PYTHON=py -%%V"
    )
)
if not defined PYTHON (
    python -c "import sys; sys.exit(not (3, 12) <= sys.version_info[:2] < (3, 15))" >nul 2>&1 && set "PYTHON=python"
)
if not defined PYTHON (
    echo Python 3.12, 3.13 or 3.14 is needed but was not found.
    echo Install it from https://www.python.org/downloads/windows/ and tick "Add python.exe to PATH",
    echo then double-click this file again.
    pause
    exit /b 1
)

echo Using %PYTHON%
%PYTHON% run.py %*
set "STATUS=%ERRORLEVEL%"
if not "%STATUS%"=="0" (
    echo.
    echo The launcher stopped with an error ^(code %STATUS%^). See the messages above.
    pause
)
exit /b %STATUS%

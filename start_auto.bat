@echo off
REM Simple batch launcher for auto.py
SET SCRIPT_DIR=%~dp0
python "%SCRIPT_DIR%auto.py" %*

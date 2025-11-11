@echo off
chcp 65001 >nul
title Paraformer API Server

echo ======================================================================
echo Starting Paraformer API Server...
echo ======================================================================
echo.

:: Get script directory and navigate to it
set "SCRIPT_DIR=%~dp0"
cd /d "%SCRIPT_DIR%"

:: Find Python in parent directory's venv
set "PYTHON_EXE=%SCRIPT_DIR%..\paraformer-asr\venv\Scripts\python.exe"

if not exist "%PYTHON_EXE%" (
    echo Error: Python not found at %PYTHON_EXE%
    echo Please ensure virtual environment is created.
    pause
    exit /b 1
)

echo Using Python: %PYTHON_EXE%
echo Working directory: %CD%
echo.

"%PYTHON_EXE%" paraformer_api_server.py

echo.
echo ======================================================================
echo Service stopped
echo ======================================================================
pause

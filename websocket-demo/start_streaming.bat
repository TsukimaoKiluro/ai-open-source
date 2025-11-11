@echo off
chcp 65001 >nul
title Streaming ASR Server

echo ======================================================================
echo Starting Streaming ASR Server (Port 10096)...
echo ======================================================================
echo.

:: Get script directory
set "SCRIPT_DIR=%~dp0"
cd /d "%SCRIPT_DIR%"

:: Find Python
set "PYTHON_EXE=%SCRIPT_DIR%..\paraformer-asr\venv\Scripts\python.exe"

if not exist "%PYTHON_EXE%" (
    echo Error: Python not found
    pause
    exit /b 1
)

echo Using Python: %PYTHON_EXE%
echo Working directory: %CD%
echo.

"%PYTHON_EXE%" streaming_server.py

echo.
echo ======================================================================
echo Service stopped
echo ======================================================================
pause

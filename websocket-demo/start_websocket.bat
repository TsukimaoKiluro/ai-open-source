@echo off
chcp 65001 >nul
title WebSocket Server

echo ======================================================================
echo Starting WebSocket Server...
echo ======================================================================
echo.

:: Get script directory and navigate to it
set "SCRIPT_DIR=%~dp0"
cd /d "%SCRIPT_DIR%"

echo Working directory: %CD%
echo.

node server.js

echo.
echo ======================================================================
echo Service stopped
echo ======================================================================
pause

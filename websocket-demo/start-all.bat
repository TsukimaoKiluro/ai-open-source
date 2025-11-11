@echo off
chcp 65001 >nul
title Start All Services

echo ======================================================================
echo Starting All Services - Dialect Recognition System
echo ======================================================================
echo.

:: Get the directory where this script is located
set "SCRIPT_DIR=%~dp0"
cd /d "%SCRIPT_DIR%"

echo [1/5] Starting LLM API Server (Port 5001)...
echo.
start "LLM API" cmd /c "%SCRIPT_DIR%start_llm.bat"

:: Wait for LLM API to start
timeout /t 5 /nobreak >nul

echo.
echo [2/5] Starting Paraformer API Server (Port 5000)...
echo.
start "Paraformer API" cmd /c "%SCRIPT_DIR%start_paraformer.bat"

:: Wait for API to start
timeout /t 8 /nobreak >nul

echo.
echo [3/5] Starting WebSocket Server (Port 8080)...
echo.
start "WebSocket Server" cmd /c "%SCRIPT_DIR%start_websocket.bat"

:: Wait for WebSocket to start
timeout /t 3 /nobreak >nul

echo.
echo [4/5] Starting Streaming ASR Server (Port 10096) [Optional]...
echo.
:: Uncomment the line below to start streaming server
:: start "Streaming ASR" cmd /c "%SCRIPT_DIR%start_streaming.bat"

echo.
echo [5/5] All services started!
echo.
echo ======================================================================
echo Service Status:
echo ======================================================================
echo  LLM API Server:     http://127.0.0.1:5001
echo  Paraformer API:     http://127.0.0.1:5000
echo  WebSocket Server:   http://localhost:8080
echo  Streaming ASR:      ws://localhost:10096 (manual start)
echo  Login Page:         http://localhost:8080/login.html
echo  Controller Page:    http://localhost:8080/Controller.html
echo ======================================================================
echo.
echo Press any key to open login page in browser...
pause >nul

:: Open browser
start http://localhost:8080/login.html

echo.
echo ======================================================================
echo All services are running!
echo Keep this window open. Press Ctrl+C to view status.
echo Close the service windows to stop services.
echo ======================================================================
echo.
pause

@echo off
chcp 65001 >nul
title 一键安装并启动所有服务

echo ======================================================================
echo 方言识别系统 - 一键安装并启动
echo ======================================================================
echo.

:: Get the directory where this script is located
set "SCRIPT_DIR=%~dp0"
cd /d "%SCRIPT_DIR%"

echo [步骤 1/2] 检查并安装 LLM API 依赖...
echo ======================================================================
echo 正在安装 Flask, Flask-CORS, Requests...
pip install flask flask-cors requests --quiet
if %errorlevel% neq 0 (
    echo 依赖安装失败！请检查 Python 和 pip 是否正确安装。
    pause
    exit /b 1
)
echo 依赖安装完成！
echo.

echo [步骤 2/2] 启动所有服务...
echo ======================================================================
echo.

:: Start LLM API Server
echo [1/5] 启动 LLM API 服务器 (端口 5001)...
start "LLM API" cmd /c "%SCRIPT_DIR%start_llm.bat"
timeout /t 5 /nobreak >nul

:: Start Paraformer API Server
echo [2/5] 启动 Paraformer API 服务器 (端口 5000)...
start "Paraformer API" cmd /c "%SCRIPT_DIR%start_paraformer.bat"
timeout /t 8 /nobreak >nul

:: Start WebSocket Server
echo [3/5] 启动 WebSocket 服务器 (端口 8080)...
start "WebSocket Server" cmd /c "%SCRIPT_DIR%start_websocket.bat"
timeout /t 3 /nobreak >nul

echo [4/5] Streaming ASR 服务器 (可选，已跳过)...
echo.

echo [5/5] 所有服务已启动！
echo.
echo ======================================================================
echo 服务状态:
echo ======================================================================
echo  ✓ LLM API 服务器:       http://127.0.0.1:5001
echo  ✓ Paraformer API:       http://127.0.0.1:5000
echo  ✓ WebSocket 服务器:     http://localhost:8080
echo  - Streaming ASR:        ws://localhost:10096 (未启动)
echo.
echo  访问地址:
echo  → 登录页面:             http://localhost:8080/login.html
echo  → 主控制页面:           http://localhost:8080/Controller.html
echo ======================================================================
echo.
echo 按任意键在浏览器中打开登录页面...
pause >nul

:: Open browser
start http://localhost:8080/login.html

echo.
echo ======================================================================
echo 所有服务正在运行！
echo 保持此窗口打开。关闭服务窗口可停止服务。
echo ======================================================================
echo.
pause

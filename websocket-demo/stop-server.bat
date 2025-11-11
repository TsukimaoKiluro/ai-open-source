@echo off
REM stop-server.bat — 停止所有运行中的服务
REM 用于强制终止 websocket-demo 和 Paraformer API 服务

setlocal enableextensions enabledelayedexpansion

:: 切换控制台编码到 UTF-8
chcp 65001 >nul

cls
echo.
echo ========================================================================
echo   🛑 停止桂林理工方言识别系统服务
echo ========================================================================
echo.

:: ============ 1. 通过窗口标题终止 ============
echo [1/4] 通过窗口标题终止服务...
taskkill /FI "WINDOWTITLE eq Paraformer API Service*" /F >nul 2>&1
if %ERRORLEVEL% EQU 0 (
    echo ✅ 已终止 Paraformer API Service 窗口
) else (
    echo ℹ️  未找到 Paraformer API Service 窗口
)

:: ============ 2. 通过端口查找并终止进程 ============
echo.
echo [2/4] 检查并清理占用端口的进程...

set FOUND_5000=0
set FOUND_8080=0

:: 终止占用 5000 端口的进程
for /f "tokens=5" %%a in ('netstat -ano ^| findstr ":5000" ^| findstr "LISTENING"') do (
    echo    终止占用 5000 端口的进程 (PID: %%a^)
    taskkill /F /PID %%a >nul 2>&1
    if !ERRORLEVEL! EQU 0 (
        echo    ✅ 成功终止 PID %%a
        set FOUND_5000=1
    )
)

if %FOUND_5000% EQU 0 (
    echo ℹ️  端口 5000 未被占用
)

:: 终止占用 8080 端口的进程
for /f "tokens=5" %%a in ('netstat -ano ^| findstr ":8080" ^| findstr "LISTENING"') do (
    echo    终止占用 8080 端口的进程 (PID: %%a^)
    taskkill /F /PID %%a >nul 2>&1
    if !ERRORLEVEL! EQU 0 (
        echo    ✅ 成功终止 PID %%a
        set FOUND_8080=1
    )
)

if %FOUND_8080% EQU 0 (
    echo ℹ️  端口 8080 未被占用
)

:: ============ 3. 通过命令行参数查找进程 ============
echo.
echo [3/4] 查找并终止相关进程...

set FOUND_PYTHON=0

:: 查找运行 paraformer_api_server.py 的进程
for /f "tokens=2" %%a in ('wmic process where "commandline like '%%paraformer_api_server.py%%'" get processid 2^>nul ^| findstr /r "[0-9]"') do (
    echo    终止 Paraformer API 进程 (PID: %%a^)
    taskkill /F /PID %%a >nul 2>&1
    if !ERRORLEVEL! EQU 0 (
        echo    ✅ 成功终止 PID %%a
        set FOUND_PYTHON=1
    )
)

if %FOUND_PYTHON% EQU 0 (
    echo ℹ️  未找到 Paraformer API 进程
)

:: 查找运行 server.js 的进程
set FOUND_NODE=0
for /f "tokens=2" %%a in ('wmic process where "commandline like '%%server.js%%'" get processid 2^>nul ^| findstr /r "[0-9]"') do (
    echo    终止 Node.js 服务器进程 (PID: %%a^)
    taskkill /F /PID %%a >nul 2>&1
    if !ERRORLEVEL! EQU 0 (
        echo    ✅ 成功终止 PID %%a
        set FOUND_NODE=1
    )
)

if %FOUND_NODE% EQU 0 (
    echo ℹ️  未找到 Node.js 服务器进程
)

:: ============ 4. 验证清理结果 ============
echo.
echo [4/4] 验证清理结果...

timeout /t 2 /nobreak >nul

:: 检查端口是否已释放
netstat -ano | findstr ":5000" | findstr "LISTENING" >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo ✅ 端口 5000 已释放
) else (
    echo ⚠️  警告: 端口 5000 仍被占用
)

netstat -ano | findstr ":8080" | findstr "LISTENING" >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo ✅ 端口 8080 已释放
) else (
    echo ⚠️  警告: 端口 8080 仍被占用
)

:: ============ 完成 ============
echo.
echo ========================================================================
echo   ✅ 所有服务清理完成！
echo ========================================================================
echo.
echo 现在可以重新运行 start-server.bat 启动服务
echo.
pause

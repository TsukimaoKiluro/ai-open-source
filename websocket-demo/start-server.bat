@echo off
REM start-server.bat — 启动 websocket-demo 服务（带 AI 方言识别）
REM 将此文件放在 websocket-demo 文件夹内后双击运行，或在 PowerShell/CMD 中执行。

:: 确保无论如何退出都会暂停
setlocal enableextensions enabledelayedexpansion

:: 切换到脚本所在目录（保证相对路径正确）
pushd "%~dp0"

echo 当前工作目录: %CD%

:: 切换控制台编码到 UTF-8，避免中文在控制台与日志中出现乱码
chcp 65001 >nul

:: 设置全局变量存储进程 ID
set PYTHON_PID=
set NODE_PID=

:: 设置 Ctrl+C 处理程序
if "%1"=="CHILD" goto :start_services

:: 清屏，便于查看
cls

echo.
echo ========================================================================
echo   桂林理工 WebSocket 方言识别系统
echo ========================================================================
echo.

:: ============ 1. 检查 Node.js 环境 ============
echo [1/4] 检查 Node.js 环境...
where node >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo ❌ 未检测到 Node.js，请先安装 Node.js
    goto :cleanup_and_exit
)
echo ✅ Node.js 已安装

:: 检查 package.json 是否存在
if not exist package.json (
    echo ❌ 未找到 package.json，请确认在 websocket-demo 目录中运行此脚本
    goto :cleanup_and_exit
)

:: ============ 2. 安装 Node.js 依赖 ============
if not exist node_modules (
    echo.
    echo [2/4] 安装 Node.js 依赖...
    npm install
    if %ERRORLEVEL% NEQ 0 (
        echo ❌ npm install 失败
        goto :cleanup_and_exit
    )
    echo ✅ 依赖安装完成
) else (
    echo.
    echo [2/4] Node.js 依赖已存在
)

:: ============ 3. 检查 Python 环境和模型 ============
echo.
echo [3/4] 检查 Python 环境...

:: 定义虚拟环境路径
set VENV_PATH=F:\桂林理工智能体项目\paraformer-asr\venv
set PYTHON_EXE=%VENV_PATH%\Scripts\python.exe

if not exist "%PYTHON_EXE%" (
    echo ❌ 未找到 Python 虚拟环境
    echo    期望路径: %VENV_PATH%
    echo.
    echo    请先创建虚拟环境并安装依赖:
    echo    cd F:\桂林理工智能体项目\paraformer-asr
    echo    python -m venv venv
    echo    .\venv\Scripts\Activate.ps1
    echo    pip install flask flask-cors funasr torch torchaudio
    goto :cleanup_and_exit
)
echo ✅ Python 虚拟环境已找到

:: 检查 ffmpeg 是否安装
echo.
echo [3.5/4] 检查 ffmpeg（音频处理工具）...
where ffmpeg >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo ⚠️  警告: 未检测到 ffmpeg
    echo.
    echo    ffmpeg 用于音频格式转换，强烈建议安装以获得最佳性能
    echo.
    echo    安装方法（Windows）:
    echo    1. 使用 Chocolatey: choco install ffmpeg
    echo    2. 使用 Scoop: scoop install ffmpeg
    echo    3. 手动下载: https://www.gyan.dev/ffmpeg/builds/
    echo       下载后解压，将 bin 目录添加到系统 PATH
    echo.
    echo    安装后重新运行此脚本即可
    echo.
    echo    ℹ️  系统将使用 torchaudio 作为备用方案（功能受限）
    echo.
    timeout /t 3 >nul
) else (
    echo ✅ ffmpeg 已安装
)

:start_services
:: ============ 4. 清理旧进程 ============
echo.
echo [4/5] 清理可能存在的旧服务...

:: 查找并终止占用 5000 端口的进程
for /f "tokens=5" %%a in ('netstat -ano ^| findstr ":5000" ^| findstr "LISTENING"') do (
    echo    终止占用 5000 端口的进程 (PID: %%a^)
    taskkill /F /PID %%a >nul 2>&1
)

:: 查找并终止占用 8080 端口的进程
for /f "tokens=5" %%a in ('netstat -ano ^| findstr ":8080" ^| findstr "LISTENING"') do (
    echo    终止占用 8080 端口的进程 (PID: %%a^)
    taskkill /F /PID %%a >nul 2>&1
)

:: 终止旧的 Python API 服务窗口
taskkill /FI "WINDOWTITLE eq Paraformer API Service*" /F >nul 2>&1

echo ✅ 清理完成

:: ============ 5. 启动服务 ============
echo.
echo [5/5] 启动服务...
echo.
echo ========================================================================
echo   服务启动中...
echo ========================================================================
echo.

:: 创建临时 VBS 脚本来启动 Python 服务并获取 PID
echo Set WshShell = CreateObject("WScript.Shell") > "%TEMP%\start_python.vbs"
echo WshShell.Run "cmd /c start ""Paraformer API Service"" ""%PYTHON_EXE%"" ""%~dp0paraformer_api_server.py""", 0 >> "%TEMP%\start_python.vbs"

:: 启动 Python API 服务（后台新窗口）
echo 🐍 正在启动 Paraformer API 服务（端口 5000）...
start "Paraformer API Service" /MIN "%PYTHON_EXE%" "%~dp0paraformer_api_server.py"

:: 获取 Python 进程 PID（稍后用于清理）
timeout /t 2 /nobreak >nul
for /f "tokens=2" %%a in ('tasklist ^| findstr "python.exe"') do (
    set PYTHON_PID=%%a
    goto :found_python
)
:found_python

:: 等待 API 服务启动（给更长时间加载模型）
echo    等待 API 服务初始化（预计 15-30 秒，首次运行需下载模型）...
timeout /t 15 /nobreak >nul

:: 验证 API 服务是否启动成功
powershell -Command "try { $response = Invoke-WebRequest -Uri 'http://127.0.0.1:5000/health' -TimeoutSec 5 -UseBasicParsing; Write-Host '✅ API 服务启动成功' -ForegroundColor Green } catch { Write-Host '⚠️  API 服务可能尚未完全启动' -ForegroundColor Yellow }" 2>nul

:: 启动 Node.js WebSocket 服务（前台，显示日志）
echo.
echo 🌐 正在启动 WebSocket 服务（端口 8080）...
echo.
echo ========================================================================
echo   浏览器访问地址:
echo   http://localhost:8080
echo   http://127.0.0.1:8080
echo ========================================================================
echo.
echo 📡 Paraformer API: http://127.0.0.1:5000
echo 📊 API 健康检查: http://127.0.0.1:5000/health
echo.
echo ========================================================================
echo   实时日志输出
echo   按 Ctrl+C 停止所有服务
echo ========================================================================
echo.

echo.

:: 前台运行 Node.js 服务，捕获退出
node server.js
set NODE_EXIT_CODE=%ERRORLEVEL%

:: ============ 清理所有服务 ============
:cleanup_services
echo.
echo.
echo ========================================================================
echo   🛑 正在停止所有服务...
echo ========================================================================

:: 方法 1: 通过窗口标题终止
taskkill /FI "WINDOWTITLE eq Paraformer API Service*" /F >nul 2>&1
if %ERRORLEVEL% EQU 0 (
    echo ✅ 已通过窗口标题终止 Python API 服务
)

:: 方法 2: 通过端口查找并终止进程
echo.
echo 🔍 检查并清理占用端口的进程...

:: 终止占用 5000 端口的进程
for /f "tokens=5" %%a in ('netstat -ano ^| findstr ":5000" ^| findstr "LISTENING"') do (
    echo    终止 Python API 进程 (PID: %%a, 端口 5000^)
    taskkill /F /PID %%a >nul 2>&1
    if !ERRORLEVEL! EQU 0 (
        echo    ✅ 成功终止 PID %%a
    )
)

:: 终止占用 8080 端口的进程
for /f "tokens=5" %%a in ('netstat -ano ^| findstr ":8080" ^| findstr "LISTENING"') do (
    echo    终止 Node.js 进程 (PID: %%a, 端口 8080^)
    taskkill /F /PID %%a >nul 2>&1
    if !ERRORLEVEL! EQU 0 (
        echo    ✅ 成功终止 PID %%a
    )
)

:: 方法 3: 通过已知 PID 终止
if defined PYTHON_PID (
    echo.
    echo 🔍 终止已记录的 Python 进程 (PID: %PYTHON_PID%^)
    taskkill /F /PID %PYTHON_PID% >nul 2>&1
)

:: 方法 4: 终止所有相关的 python.exe 进程（仅限本脚本启动的）
:: 查找运行 paraformer_api_server.py 的进程
for /f "tokens=2" %%a in ('wmic process where "commandline like '%%paraformer_api_server.py%%'" get processid 2^>nul ^| findstr /r "[0-9]"') do (
    echo    终止 Paraformer API 进程 (PID: %%a^)
    taskkill /F /PID %%a >nul 2>&1
)

echo.
echo ========================================================================
echo   ✅ 所有服务已停止
echo ========================================================================

:: 跳转到清理和退出
goto :cleanup_and_exit

:: ============ 清理和退出标签 ============
:cleanup_and_exit
popd
echo.
echo ========================================================================
echo   按任意键退出...
echo ========================================================================
pause >nul
exit /b 0

@echo off
chcp 65001 >nul
title 桂林理工 AI 方言识别系统 - FunASR WSS Server 模式

echo ========================================
echo  桂林理工 AI 方言识别系统
echo  FunASR WebSocket Server (2-Pass) 模式
echo ========================================
echo.

:: 检查 Python 虚拟环境
set VENV_PATH=F:\桂林理工智能体项目\paraformer-asr\venv
set PYTHON_EXE=%VENV_PATH%\Scripts\python.exe

if not exist "%PYTHON_EXE%" (
    echo ❌ 错误: Python 虚拟环境未找到
    echo 路径: %PYTHON_EXE%
    echo.
    echo 请先创建虚拟环境:
    echo    cd F:\桂林理工智能体项目\paraformer-asr
    echo    python -m venv venv
    echo    venv\Scripts\activate
    echo    pip install flask flask-cors funasr torch torchaudio websockets
    pause
    exit /b 1
)

echo ✅ Python 虚拟环境已找到
echo    路径: %PYTHON_EXE%
echo.

:: 检查 Node.js
where node >nul 2>&1
if %ERRORLEVEL% neq 0 (
    echo ❌ 错误: Node.js 未安装或未添加到 PATH
    echo 请访问 https://nodejs.org/ 下载安装
    pause
    exit /b 1
)

echo ✅ Node.js 已安装
node --version
echo.

:: 检查 websockets 包
echo 🔍 检查 Python 依赖...
"%PYTHON_EXE%" -c "import websockets; import funasr" 2>nul
if %ERRORLEVEL% neq 0 (
    echo ❌ 缺少必需的 Python 包
    echo.
    echo 正在安装依赖...
    "%PYTHON_EXE%" -m pip install websockets funasr flask flask-cors torch torchaudio
    if %ERRORLEVEL% neq 0 (
        echo ❌ 依赖安装失败
        pause
        exit /b 1
    )
)

echo ✅ Python 依赖已安装
echo.

:: 启动 FunASR WebSocket Server (2-Pass)
echo ========================================
echo  启动 FunASR WSS Server (2-Pass)
echo ========================================
echo.
echo 📡 WebSocket 地址: ws://localhost:10095
echo 🎯 识别流程: VAD → Paraformer → 标点恢复
echo.
echo 正在启动 FunASR WSS Server...
echo 提示: 加载模型需要 30-60 秒，请耐心等待...
echo.

start "FunASR WSS Server" "%PYTHON_EXE%" "F:\桂林理工智能体项目\funasr_wss_server_2pass.py"

:: 等待服务启动
echo 等待 FunASR WSS Server 启动...
timeout /t 15 /nobreak >nul

:: 启动 WebSocket 聊天服务器
echo.
echo ========================================
echo  启动 WebSocket 聊天服务器
echo ========================================
echo.
echo 📡 服务地址: http://localhost:8080
echo.

cd /d "F:\桂林理工智能体项目\websocket-demo"
start "WebSocket 聊天服务器" cmd /k "node server.js"

timeout /t 3 /nobreak >nul

echo.
echo ========================================
echo  🎉 所有服务启动完成！
echo ========================================
echo.
echo 📋 服务列表:
echo    1. FunASR WSS Server (2-Pass) - ws://localhost:10095
echo    2. WebSocket 聊天服务器      - http://localhost:8080
echo.
echo 🌐 访问地址:
echo    登录页面: http://localhost:8080
echo    控制端:   http://localhost:8080/Controller.html
echo.
echo 👤 测试账号:
echo    用户名: admin
echo    密码:   admin123
echo.
echo ⚠️  注意:
echo    - 首次启动需要下载模型，请等待 1-2 分钟
echo    - 模型文件约 1GB，会自动下载到缓存目录
echo    - 使用 Ctrl+C 可以停止服务器
echo.
echo 💡 提示: 请保持此窗口打开，关闭将停止所有服务
echo.

pause

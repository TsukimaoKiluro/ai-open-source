@echo off
chcp 65001 >nul
title FunASR WSS Server - 快速测试

echo ========================================
echo  FunASR WSS Server 快速测试
echo ========================================
echo.

set VENV_PATH=F:\桂林理工智能体项目\paraformer-asr\venv
set PYTHON_EXE=%VENV_PATH%\Scripts\python.exe

echo 📋 测试清单:
echo    1. Python 环境检查
echo    2. 依赖包检查
echo    3. 启动 FunASR WSS Server
echo    4. 打开客户端页面
echo.

:: 1. 检查 Python
echo [1/4] 检查 Python 环境...
if not exist "%PYTHON_EXE%" (
    echo ❌ Python 虚拟环境未找到
    pause
    exit /b 1
)
echo ✅ Python 环境正常
echo.

:: 2. 检查依赖
echo [2/4] 检查依赖包...
"%PYTHON_EXE%" -c "import websockets; import funasr; print('✅ websockets 和 funasr 已安装')" 2>nul
if %ERRORLEVEL% neq 0 (
    echo ⚠️  依赖包缺失，正在安装...
    "%PYTHON_EXE%" -m pip install websockets funasr -q
)
echo.

:: 3. 启动服务器
echo [3/4] 启动 FunASR WSS Server...
echo 提示: 首次启动需要下载模型（约 1.3GB），请耐心等待...
echo.
start "FunASR WSS Server" "%PYTHON_EXE%" "F:\桂林理工智能体项目\funasr_wss_server_2pass.py"

echo ⏳ 等待服务器启动（预计 30-60 秒）...
timeout /t 20 /nobreak >nul
echo.

:: 4. 打开客户端
echo [4/4] 打开客户端页面...
start "" "F:\桂林理工智能体项目\websocket-demo\FunASR_Client.html"
timeout /t 2 /nobreak >nul
echo.

echo ========================================
echo  🎉 测试环境已启动！
echo ========================================
echo.
echo 📡 服务信息:
echo    FunASR WSS Server: ws://localhost:10095
echo    客户端页面: FunASR_Client.html (已打开)
echo.
echo 🎯 使用步骤:
echo    1. 在浏览器中点击「连接服务器」
echo    2. 点击「开始录音」
echo    3. 对着麦克风说话
echo    4. 查看实时识别结果
echo.
echo 💡 提示:
echo    - 如果连接失败，请等待 FunASR 服务器窗口显示"✅ 服务器启动成功"
echo    - 首次启动需要下载模型，可能需要 5-10 分钟
echo    - 按 Ctrl+C 可以停止服务器
echo.
echo ⚠️  请保持 FunASR 服务器窗口打开！
echo.

pause

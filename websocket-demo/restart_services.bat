@echo off
chcp 65001 >nul
echo ========================================
echo 🔄 重启所有服务
echo ========================================
echo.

echo 1️⃣ 停止现有服务...
taskkill /F /FI "WINDOWTITLE eq Paraformer*" 2>nul
taskkill /F /FI "WINDOWTITLE eq WebSocket*" 2>nul
timeout /t 2 /nobreak >nul

echo.
echo 2️⃣ 启动 Paraformer API 服务...
start "Paraformer API Server" cmd /c "cd /d F:\桂林理工智能体项目\websocket-demo && F:\桂林理工智能体项目\paraformer-asr\venv\Scripts\python.exe paraformer_api_server.py"

echo.
echo 3️⃣ 等待 API 服务初始化...
timeout /t 10 /nobreak

echo.
echo 4️⃣ 启动 WebSocket 服务器...
start "WebSocket Server" cmd /c "cd /d F:\桂林理工智能体项目\websocket-demo && node server.js"

echo.
echo ========================================
echo ✅ 服务重启完成！
echo ========================================
echo.
echo 📡 访问地址:
echo    - 登录页面: http://localhost:8080/login.html
echo    - 控制端: http://localhost:8080/Controller.html
echo.
echo 💡 如需查看日志，请查看新打开的窗口
echo.
pause

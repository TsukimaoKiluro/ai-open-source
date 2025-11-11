@echo off
chcp 65001
echo ======================================
echo 正在安装 LLM API 依赖...
echo ======================================
pip install flask flask-cors requests
echo.
echo ======================================
echo 依赖安装完成！
echo ======================================
pause

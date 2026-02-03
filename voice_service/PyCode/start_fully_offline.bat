@echo off
chcp 65001 >nul
echo ========================================
echo AI 语音助手 - 完全离线版本
echo AI Voice Assistant - Fully Offline
echo ========================================
echo.

echo [1/3] 检查 Python 环境...
python --version
if errorlevel 1 (
    echo ❌ Python 未安装或未添加到 PATH
    pause
    exit /b 1
)
echo ✓ Python 环境正常
echo.

echo [2/3] 检查依赖...
python -c "import fastapi, uvicorn, whisper, pyttsx3" 2>nul
if errorlevel 1 (
    echo ⚠️ 缺少依赖，正在安装...
    pip install -r requirements_fully_offline.txt
    if errorlevel 1 (
        echo ❌ 依赖安装失败
        pause
        exit /b 1
    )
    echo ✓ 依赖安装完成
) else (
    echo ✓ 依赖已安装
)
echo.

echo [3/3] 启动服务...
echo.
echo 服务地址: http://172.16.4.181:8001
echo 健康检查: http://172.16.4.181:8001/health
echo.
echo 按 Ctrl+C 停止服务
echo ========================================
echo.

python ai_voice_service_fully_offline.py

pause

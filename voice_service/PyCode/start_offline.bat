@echo off
chcp 65001
echo ========================================
echo   AI 语音助手 - 离线版本
echo ========================================
echo.
echo 正在启动服务...
echo Ollama: http://172.16.4.181:11434
echo 服务端口: 8001
echo.
python ai_voice_service_offline.py
pause

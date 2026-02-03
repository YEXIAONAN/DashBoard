@echo off
chcp 65001 >nul
echo ========================================
echo AI 语音服务 - Dify 工作流版本
echo ========================================
echo.
echo 正在启动服务...
echo.
echo 配置信息:
echo - LLM 服务: Dify 工作流
echo - Dify API: http://10.0.0.10:3099/v1/chat/completions
echo - 备用服务: Ollama (http://10.0.0.10:11434)
echo - 语音识别: Whisper (本地)
echo - 语音合成: pyttsx3 (本地)
echo - 服务端口: 8001
echo.
echo ========================================
echo.

cd /d "%~dp0"

python ai_voice_service_vixtts.py

pause

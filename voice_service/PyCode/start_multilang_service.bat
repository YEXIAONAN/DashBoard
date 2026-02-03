@echo off
echo ========================================
echo AI 语音助手 - 多语言支持版本
echo ========================================
echo.
echo 支持的语言:
echo - 中文 (Chinese)
echo - English
echo - Tiếng Việt (Vietnamese)
echo.
echo 启动服务中...
echo.

cd /d "%~dp0"
..\.venv\Scripts\python.exe ai_voice_service_offline.py

pause
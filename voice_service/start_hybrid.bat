@echo off
echo ========================================
echo AI Voice Service - 混合模式启动
echo 中文/英文: XTTS v2
echo 越南语: MMS-TTS
echo ========================================
echo.

cd /d "%~dp0"
call ..\.venv\Scripts\activate.bat
python ai_voice_service_hybrid.py

pause

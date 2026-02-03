@echo off
chcp 65001 >nul
echo ========================================
echo AI 语音服务 - gTTS 版本（支持越南语）
echo ========================================
echo.
echo 正在检查依赖...
echo.

cd /d "%~dp0"

REM 检查 gTTS 是否安装
python -c "import gtts" 2>nul
if errorlevel 1 (
    echo ❌ gTTS 未安装
    echo.
    echo 正在安装 gTTS...
    pip install gtts
    echo.
)

echo ✅ gTTS 已安装
echo.
echo 配置信息:
echo - LLM 服务: Dify 工作流 + Ollama
echo - Dify API: http://10.0.0.10:3099/v1/chat/completions
echo - 语音识别: Whisper (本地)
echo - 语音合成: gTTS (Google, 需要网络)
echo - 越南语支持: ✅ 完美支持
echo - 服务端口: 8001
echo.
echo ========================================
echo.
echo ⚠️ 注意: gTTS 需要网络连接！
echo.

python ai_voice_service_gtts.py

pause

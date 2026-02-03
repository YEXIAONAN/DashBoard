@echo off
chcp 65001 >nul
echo ========================================
echo AI 语音助手 - Coqui TTS 版本
echo AI Voice Assistant - Coqui TTS Edition
echo ========================================
echo.

echo [1/5] 检查 Python 环境...
python --version
if errorlevel 1 (
    echo ❌ Python 未安装或未添加到 PATH
    pause
    exit /b 1
)
echo ✓ Python 环境正常
echo.

echo [2/5] 检查基础依赖...
python -c "import fastapi, uvicorn, whisper" 2>nul
if errorlevel 1 (
    echo ⚠️ 缺少基础依赖，正在安装...
    pip install -r requirements_fully_offline.txt
    if errorlevel 1 (
        echo ❌ 依赖安装失败
        pause
        exit /b 1
    )
    echo ✓ 基础依赖安装完成
) else (
    echo ✓ 基础依赖已安装
)
echo.

echo [3/5] 检查 Coqui TTS...
python -c "from TTS.api import TTS" 2>nul
if errorlevel 1 (
    echo ⚠️ Coqui TTS 未安装或版本不兼容，正在安装...
    echo 注意：这可能需要几分钟...
    
    echo.
    echo 步骤 1: 卸载可能冲突的包...
    pip uninstall -y TTS transformers tokenizers 2>nul
    
    echo.
    echo 步骤 2: 安装兼容版本...
    pip install transformers==4.33.0 tokenizers==0.13.3
    pip install TTS==0.22.0
    
    if errorlevel 1 (
        echo ❌ Coqui TTS 安装失败
        echo 提示：可能需要安装 Microsoft C++ Build Tools
        echo 下载地址：https://visualstudio.microsoft.com/visual-cpp-build-tools/
        pause
        exit /b 1
    )
    echo ✓ Coqui TTS 安装完成
) else (
    echo ✓ Coqui TTS 已安装
    echo 检查版本兼容性...
    python -c "from transformers import BeamSearchScorer" 2>nul
    if errorlevel 1 (
        echo ⚠️ transformers 版本不兼容，正在修复...
        pip install transformers==4.33.0 tokenizers==0.13.3 --force-reinstall
        echo ✓ 版本已修复
    ) else (
        echo ✓ 版本兼容
    )
)
echo.

echo [4/5] 检查 Coqui TTS 模型...
echo 注意：首次运行会自动下载模型（约 1.8GB）
echo 这可能需要 10-30 分钟，取决于网络速度...
echo.
python -c "from TTS.api import TTS; print('正在检查/下载模型...'); tts = TTS(model_name='tts_models/multilingual/multi-dataset/xtts_v2'); print('✓ 模型准备完成')"
if errorlevel 1 (
    echo ❌ 模型下载失败
    echo 提示：请检查网络连接，或手动下载模型
    pause
    exit /b 1
)
echo.

echo [5/5] 启动服务...
echo.
echo ========================================
echo 配置信息：
echo   TTS 引擎: Coqui TTS (高质量离线)
echo   服务地址: http://172.16.4.181:8001
echo   健康检查: http://172.16.4.181:8001/health
echo   模式: 完全离线
echo ========================================
echo.
echo 提示：
echo   - 首次合成语音可能较慢（2-5秒）
echo   - 后续会更快
echo   - 如有 GPU 会自动使用加速
echo.
echo 按 Ctrl+C 停止服务
echo ========================================
echo.

python ai_voice_service_fully_offline.py

pause

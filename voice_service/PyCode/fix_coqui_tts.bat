@echo off
chcp 65001 >nul
echo ========================================
echo Coqui TTS 版本兼容性修复工具
echo Coqui TTS Compatibility Fix Tool
echo ========================================
echo.

echo 检测到的问题：
echo 1. transformers 版本不兼容
echo 2. PyTorch 2.6+ weights_only 限制
echo.
echo 解决方案：
echo - 降级 transformers 到 4.33.0
echo - 降级 PyTorch 到 2.5.x（如果需要）
echo.

echo [1/4] 检查 PyTorch 版本...
python -c "import torch; v=torch.__version__; print(f'当前版本: {v}'); exit(0 if v.startswith('2.') and int(v.split('.')[1]) < 6 else 1)" 2>nul
if errorlevel 1 (
    echo ⚠️ PyTorch 版本不兼容或未安装
    echo 正在安装兼容版本...
    pip install "torch>=2.0.0,<2.6.0" --upgrade
) else (
    echo ✓ PyTorch 版本兼容
)
echo.

echo [2/4] 卸载冲突的包...
pip uninstall -y transformers tokenizers
echo ✓ 卸载完成
echo.

echo [3/4] 安装兼容版本...
echo 正在安装 transformers==4.33.0 和 tokenizers==0.13.3...
pip install transformers==4.33.0 tokenizers==0.13.3
if errorlevel 1 (
    echo ❌ 安装失败
    pause
    exit /b 1
)
echo ✓ 安装完成
echo.

echo [4/4] 验证修复...
python -c "from TTS.api import TTS; print('✓ Coqui TTS 可以正常导入'); from transformers import BeamSearchScorer; print('✓ BeamSearchScorer 可以正常导入'); import torch; print(f'✓ PyTorch 版本: {torch.__version__}')"
if errorlevel 1 (
    echo ❌ 验证失败
    echo.
    echo 可能的原因：
    echo 1. 需要重新安装 TTS
    echo 2. 需要安装 Microsoft C++ Build Tools
    echo.
    echo 尝试运行：
    echo   pip install TTS==0.22.0 --force-reinstall
    pause
    exit /b 1
)

echo.
echo ========================================
echo ✅ 修复完成！
echo ========================================
echo.
echo 版本信息：
python -c "import torch; import transformers; import TTS; print(f'PyTorch: {torch.__version__}'); print(f'transformers: {transformers.__version__}'); print(f'TTS: {TTS.__version__}')"
echo.
echo 现在可以启动服务了：
echo   python ai_voice_service_fully_offline.py
echo.
echo 或使用启动脚本：
echo   start_coqui_tts.bat
echo.

pause

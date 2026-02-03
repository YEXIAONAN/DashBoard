@echo off
chcp 65001 >nul
echo ========================================
echo PyTorch 降级工具
echo PyTorch Downgrade Tool
echo ========================================
echo.

echo 当前版本检查...
python check_versions.py
echo.

echo ========================================
echo 开始降级 PyTorch
echo ========================================
echo.

echo [1/2] 卸载当前 PyTorch...
pip uninstall -y torch torchvision torchaudio
echo ✓ 卸载完成
echo.

echo [2/2] 安装兼容版本 (PyTorch 2.5.1)...
echo 注意：这可能需要几分钟...
pip install torch==2.5.1 torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu
if errorlevel 1 (
    echo ❌ 安装失败，尝试不指定 index-url...
    pip install torch==2.5.1 torchvision torchaudio
    if errorlevel 1 (
        echo ❌ 安装失败
        pause
        exit /b 1
    )
)
echo ✓ 安装完成
echo.

echo ========================================
echo 验证安装
echo ========================================
python -c "import torch; print(f'PyTorch 版本: {torch.__version__}'); v=torch.__version__.split('.'); exit(0 if int(v[0])==2 and int(v[1])<6 else 1)"
if errorlevel 1 (
    echo ❌ 版本验证失败
    pause
    exit /b 1
)

echo.
echo ========================================
echo ✅ PyTorch 降级完成！
echo ========================================
echo.
echo 当前版本：
python check_versions.py
echo.
echo 现在可以启动服务了：
echo   python ai_voice_service_fully_offline.py
echo.

pause

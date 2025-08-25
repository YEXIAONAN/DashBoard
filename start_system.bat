@echo off
echo ========================================
echo  启动点餐-机械臂任务控制系统
echo ========================================

:: 设置窗口标题
title 点餐-机械臂控制系统

:: 启动YOLOv5检测服务
echo 正在启动YOLOv5检测服务...
start "YOLOv5检测服务" cmd /k "cd /d %~dp0 && python yolov5_stream.py"
timeout /t 3 /nobreak > nul

:: 启动Django服务
echo 正在启动Django服务...
start "Django服务" cmd /k "cd /d %~dp0 && python manage.py runserver 0.0.0.0:8000"
timeout /t 3 /nobreak > nul

:: 启动完成
echo 系统启动完成！
echo.
echo 服务地址：
echo   - Django: http://localhost:8000
echo   - YOLOv5: http://localhost:5000
echo.

echo.
echo 按任意键关闭所有服务...
pause > nul

:: 关闭相关进程
taskkill /f /im python.exe 2>nul
taskkill /f /im cmd.exe 2>nul

echo 系统已关闭！
pause
@echo off
REM ===== 切换到脚本所在磁盘 =====
C:

REM ===== 可选：避免中文路径乱码 =====
chcp 65001 >nul

REM ===== 设置 Python 虚拟环境解释器 =====
set PYTHON_EXE=C:\Users\Administrator\Desktop\Project\Project_Web\.venv\Scripts\python.exe

REM ===== 设置语音服务脚本路径 =====
set SCRIPT_PATH=C:\Users\Administrator\Desktop\Project\Project_Web\voice_service\ai_voice_service_vixtts.py

REM ===== 切换到项目目录（非常关键） =====
cd /d C:\Users\Administrator\Desktop\Project\Project_Web

REM ===== 启动语音服务（后台运行）=====
start "" "%PYTHON_EXE%" "%SCRIPT_PATH%"

REM ===== 如果你想调试，可改成下面这一行（不后台）=====
REM "%PYTHON_EXE%" "%SCRIPT_PATH%"

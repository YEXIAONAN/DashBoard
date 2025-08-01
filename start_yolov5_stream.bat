@echo off
echo 正在启动YOLOv5视频流服务...
echo 请确保已安装所有依赖: pip install -r requirements.txt
echo.

:: 激活虚拟环境（如果存在）
if exist .venv\Scripts\activate.bat (
    call .venv\Scripts\activate.bat
    echo 已激活虚拟环境
)

:: 启动YOLOv5视频流服务
python yolov5_stream.py

pause
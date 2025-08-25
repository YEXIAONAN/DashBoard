# YOLOv5 视频流服务使用说明

## 概述
本项目在Django网站中集成YOLOv5实时检测功能，通过独立的Flask服务提供视频流，在订单状态页面显示机械臂工作区的实时画面。

## 文件结构
- `yolov5_stream.py` - YOLOv5视频流服务主程序
- `start_yolov5_stream.bat` - Windows批处理启动脚本
- `main/templates/order_status.html` - 已修改的订单状态页面，嵌入视频流

## 使用方法

### 1. 安装依赖
```bash
pip install -r requirements.txt
```

### 2. 启动YOLOv5视频流服务

#### 方法一：使用批处理脚本（推荐）
双击运行 `start_yolov5_stream.bat`

#### 方法二：命令行启动
```bash
python yolov5_stream.py
```

### 3. 访问网站
- 启动Django网站：
```bash
python manage.py runserver
```
- 访问订单状态页面：http://localhost:8000/order_status/

## 服务说明
- **YOLOv5视频流服务**：运行在 http://localhost:5000
- **检测类别**：Cucumber (黄瓜)、Shrimp (虾)
- **设备支持**：自动使用RTX 4060 GPU进行加速
- **视频源**：默认使用笔记本摄像头（索引0）

## 自定义配置
在 `yolov5_stream.py` 中可以修改以下参数：
- `WEIGHTS_PATH`: 模型权重文件路径
- `CLASS_NAMES`: 检测类别名称
- `CONF_THRESHOLD`: 置信度阈值
- `DEVICE`: GPU设备号（'0' 表示第一张GPU）
- `IMG_SIZE`: 输入图像尺寸

## 故障排除

### 摄像头无法打开
- 检查是否有其他程序占用摄像头
- 尝试修改摄像头索引：在 `yolov5_stream.py` 中修改 `detector.start_detection(0)` 的参数

### 模型加载失败
- 确保模型文件路径正确：yolov5/run/yolov5x_1024x4_gpu/weights/best.pt
- 检查模型文件是否存在

### 视频流无法显示
- 确保YOLOv5服务已启动（端口5000）
- 检查浏览器控制台是否有错误信息
- 确认防火墙允许5000端口通信

## 技术细节
- 使用Flask提供MJPEG视频流
- 视频流地址：http://localhost:5000/video_feed
- 支持30fps实时检测
- 自动处理摄像头连接失败的情况，显示备用界面
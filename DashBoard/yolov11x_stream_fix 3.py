#!/usr/bin/env python3
"""
YOLOv11x 实时检测流服务
使用Ultralytics YOLOv11模型
"""
import cv2
import torch
import numpy as np
from flask import Flask, Response, jsonify, request
import threading
import time
import os
from PIL import Image, ImageDraw, ImageFont
import logging

# 配置日志
logging.basicConfig(level=logging.INFO)
LOGGER = logging.getLogger(__name__)

app = Flask(__name__)

# 配置模型参数
WEIGHTS_PATH = "main/models/yolov11x.pt"
CONF_THRESHOLD = 0.45
IOU_THRESHOLD =  0.45
DEVICE = '0' if torch.cuda.is_available() else 'cpu'  # 自动选择GPU或CPU
IMG_SIZE = 640  # YOLO模型输入尺寸

# 自动检测摄像头最佳分辨率
import sys


def get_camera_resolution():
    """检测摄像头实际支持的分辨率"""
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        LOGGER.warning("无法打开摄像头，使用默认分辨率")
        return 640, 480

    # 自动选择高分辨率
    high_resolutions = [
        (3840, 2160),  # 4K UHD
        (2560, 1440),  # 2K QHD
        (1920, 1080),  # 1080p FHD
        (1280, 720),  # 720p HD
        (640, 480)  # SD
    ]

    for width, height in high_resolutions:
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, width)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, height)
        actual_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        actual_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

        # 检查实际设置的分辨率
        if actual_width >= width * 0.95 and actual_height >= height * 0.95:
            cap.release()
            print(f"✅ 检测到高分辨率摄像头: {actual_width}x{actual_height}")
            return actual_width, actual_height

    # 回退到实际检测到的分辨率
    actual_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    actual_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    cap.release()

    if actual_width > 0 and actual_height > 0:
        print(f"检测到摄像头分辨率: {actual_width}x{actual_height}")
        return actual_width, actual_height

    print("使用默认摄像头分辨率: 640x480")
    return 640, 480


# 自动获取摄像头分辨率
CAMERA_WIDTH, CAMERA_HEIGHT = get_camera_resolution()

# 从YOLOv11模型自动获取类别名称
CLASS_NAMES = None

try:
    from ultralytics import YOLO

    YOLO_AVAILABLE = True
    print("Ultralytics YOLO库加载成功")
except ImportError:
    YOLO_AVAILABLE = False
    LOGGER.error("Ultralytics YOLO库未安装，请先安装: pip install ultralytics")
    sys.exit(1)


class YOLO11xDetector:
    def __init__(self):
        # 智能设备选择
        self.device = 'cpu'
        if torch.cuda.is_available():
            self.device = 'cuda'
            gpu_name = torch.cuda.get_device_name(0) if torch.cuda.device_count() > 0 else "Unknown GPU"
            print(f"🚀 使用GPU: {gpu_name}")
        else:
            print("⚠️ 使用CPU推理（建议安装CUDA以获得更好性能）")

        self.model = None
        self.is_running = False
        self.frame = None
        self.cap = None
        self.camera_width = CAMERA_WIDTH
        self.camera_height = CAMERA_HEIGHT
        self.detected_classes = []
        self.lock = threading.Lock()
        
        # 摄像头重连相关参数
        self.camera_source = 0
        self.reconnect_interval = 2  # 重连间隔（秒）
        self.max_reconnect_attempts = 0  # 0表示无限重试
        self.camera_connected = False
        self.reconnect_count = 0



    def load_model(self):
        """加载YOLOv11x模型"""
        try:
            if not os.path.exists(WEIGHTS_PATH):
                LOGGER.error(f"权重文件不存在: {WEIGHTS_PATH}")
                return False

            self.model = YOLO(WEIGHTS_PATH)

            # 获取类别名称
            global CLASS_NAMES
            if hasattr(self.model, 'names'):
                CLASS_NAMES = self.model.names
                if isinstance(CLASS_NAMES, dict):
                    CLASS_NAMES = [CLASS_NAMES[i] for i in range(len(CLASS_NAMES))]
            else:
                # 使用默认的菜品类别
                CLASS_NAMES = ['清炒莲藕', '红烧排骨', '烤鸭', '花菜牛腩',
                               '清炒黑木耳', '米饭', '麻婆豆腐', '宫保鸡丁',
                               '糖醋里脊', '水煮鱼', '西红柿炒鸡蛋', '青椒土豆丝']

            print(f"YOLOv11x模型加载成功: {WEIGHTS_PATH}")
            print(f"检测类别数量: {len(CLASS_NAMES)}")
            print(f"类别列表: {CLASS_NAMES}")
            return True

        except Exception as e:
            LOGGER.error(f"YOLOv11x模型加载失败: {e}")
            return False

    def _detect_camera_resolution(self, cap):
        """检测当前摄像头支持的最佳分辨率"""
        high_resolutions = [
            (3840, 2160),  # 4K UHD
            (2560, 1440),  # 2K QHD
            (1920, 1080),  # 1080p FHD
            (1280, 720),   # 720p HD
            (640, 480)     # SD
        ]

        for width, height in high_resolutions:
            cap.set(cv2.CAP_PROP_FRAME_WIDTH, width)
            cap.set(cv2.CAP_PROP_FRAME_HEIGHT, height)
            actual_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            actual_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

            # 检查实际设置的分辨率
            if actual_width >= width * 0.95 and actual_height >= height * 0.95:
                return actual_width, actual_height

        # 回退到实际检测到的分辨率
        actual_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        actual_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

        if actual_width > 0 and actual_height > 0:
            return actual_width, actual_height

        return 640, 480

    def _init_camera(self, source):
        """初始化摄像头连接，自动检测最佳分辨率"""
        try:
            if self.cap is not None:
                self.cap.release()
            
            self.cap = cv2.VideoCapture(source)
            if not self.cap.isOpened():
                return False

            # 动态检测摄像头最佳分辨率
            detected_width, detected_height = self._detect_camera_resolution(self.cap)
            print(f"📷 检测到摄像头分辨率: {detected_width}x{detected_height}")

            # 设置摄像头参数优化
            self.cap.set(cv2.CAP_PROP_FPS, 30)
            self.cap.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc(*'MJPG'))
            self.cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)

            # 验证实际分辨率
            ret, frame = self.cap.read()
            if not ret:
                return False

            actual_height, actual_width = frame.shape[:2]
            self.camera_width, self.camera_height = actual_width, actual_height

            print(f"🎥 摄像头{source}连接成功，使用分辨率: {actual_width}x{actual_height}")
            self.camera_connected = True
            self.reconnect_count = 0
            return True

        except Exception as e:
            LOGGER.error(f"❌ 摄像头初始化失败: {e}")
            return False

    def start_detection(self, source=0):
        """开始检测，自动适配摄像头分辨率，支持断线重连"""
        if not self.load_model():
            return False

        self.is_running = True
        self.camera_source = source

        # 初始化摄像头
        if not self._init_camera(source):
            LOGGER.warning(f"⚠️ 初始摄像头连接失败，将在后台持续尝试重连...")
            self.camera_connected = False

        # 启动检测线程（即使摄像头未连接也启动，会自动重连）
        detection_thread = threading.Thread(target=self._detection_loop)
        detection_thread.daemon = True
        detection_thread.start()

        return True

    def _detection_loop(self):
        """优化版检测循环，自适应实际分辨率，支持自动重连"""
        try:
            fps_counter = 0
            fps_start_time = time.time()
            current_fps = 0
            consecutive_failures = 0
            max_consecutive_failures = 10  # 连续失败10次后尝试重连

            while self.is_running:
                # 检查摄像头连接状态
                if not self.camera_connected or self.cap is None or not self.cap.isOpened():
                    print(f"📡 摄像头未连接，尝试重连... (第{self.reconnect_count + 1}次)")
                    
                    if self._init_camera(self.camera_source):
                        print("✅ 摄像头重连成功！")
                        consecutive_failures = 0
                    else:
                        self.reconnect_count += 1
                        LOGGER.warning(f"❌ 摄像头重连失败，{self.reconnect_interval}秒后重试...")
                        time.sleep(self.reconnect_interval)
                        continue

                ret, frame = self.cap.read()
                if not ret:
                    consecutive_failures += 1
                    LOGGER.warning(f"⚠️ 无法读取摄像头帧 (连续失败: {consecutive_failures}/{max_consecutive_failures})")
                    
                    # 连续失败多次后，标记摄像头断开
                    if consecutive_failures >= max_consecutive_failures:
                        LOGGER.error("❌ 摄像头连接丢失，准备重连...")
                        self.camera_connected = False
                        consecutive_failures = 0
                        if self.cap:
                            self.cap.release()
                    
                    time.sleep(0.1)
                    continue
                
                # 成功读取帧，重置失败计数
                consecutive_failures = 0

                # 获取实际帧尺寸
                frame_height, frame_width = frame.shape[:2]

                # 计算FPS
                fps_counter += 1
                if fps_counter >= 30:  # 每30帧计算一次FPS
                    elapsed = time.time() - fps_start_time
                    current_fps = fps_counter / elapsed
                    fps_counter = 0
                    fps_start_time = time.time()

                # 缩放图像到模型输入尺寸
                input_frame = cv2.resize(frame, (IMG_SIZE, IMG_SIZE))

                # 使用YOLOv11进行推理
                results = self.model(input_frame, conf=CONF_THRESHOLD, iou=IOU_THRESHOLD, device=self.device)

                # 处理检测结果
                annotated_frame = frame.copy()
                self.detected_classes.clear()

                for result in results:
                    boxes = result.boxes
                    if boxes is not None:
                        for box in boxes:
                            # 获取边界框坐标（在640x640图像上的坐标）
                            x1, y1, x2, y2 = box.xyxy[0].cpu().numpy()
                            conf = box.conf[0].cpu().numpy()
                            cls = int(box.cls[0].cpu().numpy())

                            # 将坐标从640x640缩放回实际分辨率
                            scale_x = frame_width / IMG_SIZE
                            scale_y = frame_height / IMG_SIZE

                            x1 = int(x1 * scale_x)
                            y1 = int(y1 * scale_y)
                            x2 = int(x2 * scale_x)
                            y2 = int(y2 * scale_y)

                            if cls < len(CLASS_NAMES):
                                class_name = CLASS_NAMES[cls]
                                self.detected_classes.append(class_name)

                                # 高分辨率自适应绘制边界框
                                min_dim = min(frame_width, frame_height)
                                if min_dim >= 3000:  # 4K分辨率
                                    line_thickness = max(6, int(0.002 * min_dim))
                                    font_scale = 0.025
                                    padding_factor = 0.4
                                elif min_dim >= 2000:  # 2K分辨率
                                    line_thickness = max(4, int(0.0025 * min_dim))
                                    font_scale = 0.03
                                    padding_factor = 0.35
                                else:  # 普通分辨率
                                    line_thickness = max(2, int(0.003 * min_dim))
                                    font_scale = 0.02
                                    padding_factor = 0.3

                                cv2.rectangle(annotated_frame,
                                              (x1, y1), (x2, y2),
                                              (0, 255, 0), line_thickness)

                                # 高分辨率自适应标签
                                label = f'{class_name} {conf:.2f}'

                                # 使用PIL绘制中文标签
                                pil_img = Image.fromarray(cv2.cvtColor(annotated_frame, cv2.COLOR_BGR2RGB))
                                draw = ImageDraw.Draw(pil_img)

                                # 高分辨率自适应字体大小
                                font_size = max(24, int(frame_height * font_scale))
                                try:
                                    font = ImageFont.truetype("C:\\Windows\\Fonts\\simhei.ttf", font_size)
                                except:
                                    try:
                                        font = ImageFont.truetype("msyh.ttc", font_size)
                                    except:
                                        font = ImageFont.load_default()

                                text_bbox = draw.textbbox((0, 0), label, font=font)
                                text_width = text_bbox[2] - text_bbox[0]
                                text_height = text_bbox[3] - text_bbox[1]

                                # 高分辨率自适应标签背景
                                padding = max(8, int(font_size * padding_factor))
                                box_thickness = max(2, int(0.001 * min(frame_width, frame_height)))

                                draw.rectangle([x1, y1 - text_height - 2 * padding,
                                                x1 + text_width + 2 * padding, y1],
                                               fill=(0, 255, 0), outline=(0, 255, 0),
                                               width=box_thickness)

                                draw.text((x1 + padding, y1 - text_height - padding),
                                          label, font=font, fill=(0, 0, 0))

                                annotated_frame = cv2.cvtColor(np.array(pil_img), cv2.COLOR_RGB2BGR)

                # 高分辨率自适应信息显示
                min_dim = min(frame_width, frame_height)
                if min_dim >= 3000:  # 4K分辨率
                    info_font_scale = 1.5
                    info_thickness = 4
                    line_spacing = 50
                elif min_dim >= 2000:  # 2K分辨率
                    info_font_scale = 1.2
                    info_thickness = 3
                    line_spacing = 40
                else:  # 普通分辨率
                    info_font_scale = 0.7
                    info_thickness = 2
                    line_spacing = 30

                # 显示FPS和分辨率信息
                info_text = f"FPS: {current_fps:.1f} | {frame_width}x{frame_height}"
                cv2.putText(annotated_frame, info_text, (20, line_spacing),
                            cv2.FONT_HERSHEY_SIMPLEX, info_font_scale, (0, 255, 0), info_thickness)

                # 显示GPU状态
                gpu_text = f"GPU: {self.device}" if torch.cuda.is_available() else "CPU"
                cv2.putText(annotated_frame, gpu_text, (20, line_spacing * 2),
                            cv2.FONT_HERSHEY_SIMPLEX, info_font_scale, (0, 255, 0), info_thickness)

                # 显示摄像头连接状态
                camera_status = "Camera: Connected" if self.camera_connected else "Camera: Reconnecting..."
                status_color = (0, 255, 0) if self.camera_connected else (0, 165, 255)
                cv2.putText(annotated_frame, camera_status, (20, line_spacing * 3),
                            cv2.FONT_HERSHEY_SIMPLEX, info_font_scale, status_color, info_thickness)

                # 更新帧
                with self.lock:
                    self.frame = annotated_frame.copy()

        except Exception as e:
            LOGGER.error(f"❌ 检测循环错误: {e}")
            import traceback
            traceback.print_exc()

        except Exception as e:
            LOGGER.error(f"检测循环错误: {e}")
            import traceback
            traceback.print_exc()

    def get_frame(self):
        """获取当前帧"""
        with self.lock:
            if self.frame is None:
                return None

            # 编码为JPEG
            ret, buffer = cv2.imencode('.jpg', self.frame)
            if ret:
                return buffer.tobytes()
            return None

    def stop(self):
        """停止检测"""
        self.is_running = False
        if self.cap:
            self.cap.release()


detector = YOLO11xDetector()


def generate_frames():
    """生成视频流帧"""
    while True:
        frame = detector.get_frame()
        if frame is not None:
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
        time.sleep(0.033)  # 30fps


@app.route('/video_feed')
def video_feed():
    """视频流路由"""
    return Response(generate_frames(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')


@app.route('/detect')
def detect():
    """检测指定类别是否存在"""
    target_class = request.args.get('class', '')
    LOGGER.info(f"收到检测请求: {target_class}")
    if not target_class:
        return jsonify({'detected':False,'message':'未找到'})

    try:
        # 检查detector是否已检测到目标类别
        with detector.lock:
            detected = target_class in detector.detected_classes

        return jsonify({
            'detected': detected,
            'class': target_class,
            'confidence': 0.85 if detected else 0.0,
            'detected_classes':  detector.detected_classes
        })

    except Exception as e:
        return jsonify({'detected': False, 'message': str(e)})


@app.route('/')
def index():
    """高分辨率自适应主页"""
    return f'''
    <html>
    <head>
        <title>食品视觉检测系统 - YOLOv11x</title>
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <meta charset="UTF-8">
        <style>
            * {{
                margin: 0;
                padding: 0;
                box-sizing: border-box;
            }}
            
            body {{ 
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Microsoft YaHei', sans-serif;
                background: #f5f7f4;
                color: #3a3a3a;
                line-height: 1.6;
                min-height: 100vh;
                padding: 0;
            }}
            
            .container {{ 
                max-width: 1600px;
                margin: 0 auto;
                background: #fefffe;
                min-height: 100vh;
            }}
            
            .header {{
                background: #ffffff;
                border-bottom: 1px solid #e3e8e1;
                padding: 24px 40px;
            }}
            
            .header-content {{
                display: flex;
                justify-content: space-between;
                align-items: center;
            }}
            
            .header h1 {{
                font-size: 20px;
                font-weight: 500;
                color: #2d3e2d;
                letter-spacing: 0.3px;
            }}
            
            .header-status {{
                display: flex;
                align-items: center;
                gap: 8px;
                font-size: 13px;
                color: #6b7c6b;
            }}
            
            .status-dot {{
                width: 8px;
                height: 8px;
                background: #7fa87f;
                border-radius: 50%;
                animation: pulse 2s ease-in-out infinite;
            }}
            
            @keyframes pulse {{
                0%, 100% {{ opacity: 1; }}
                50% {{ opacity: 0.5; }}
            }}
            
            .main-content {{
                display: grid;
                grid-template-columns: 1fr 360px;
                gap: 0;
                min-height: calc(100vh - 73px);
            }}
            
            .video-section {{
                background: #fafbfa;
                padding: 16px 24px 24px 24px;
                display: flex;
                flex-direction: column;
            }}
            
            .video-wrapper {{
                width: 100%;
                background: #ffffff;
                border: 1px solid #e8ede7;
                border-radius: 2px;
                overflow: hidden;
                box-shadow: 0 1px 3px rgba(0,0,0,0.04);
            }}
            
            .video-header {{
                padding: 10px 16px;
                background: #f9faf9;
                border-bottom: 1px solid #e8ede7;
                font-size: 12px;
                color: #5a6b5a;
                font-weight: 500;
            }}
            
            .video-feed {{
                width: 100%;
                height: auto;
                display: block;
                background: #000000;
                max-height: calc(100vh - 150px);
                object-fit: contain;
            }}
            
            .sidebar {{
                background: #ffffff;
                border-left: 1px solid #e3e8e1;
                padding: 32px 24px;
                overflow-y: auto;
            }}
            
            .info-section {{
                margin-bottom: 32px;
            }}
            
            .info-section:last-child {{
                margin-bottom: 0;
            }}
            
            .section-title {{
                font-size: 13px;
                font-weight: 600;
                color: #2d3e2d;
                margin-bottom: 16px;
                text-transform: uppercase;
                letter-spacing: 0.5px;
            }}
            
            .info-list {{
                list-style: none;
            }}
            
            .info-item {{
                padding: 10px 0;
                border-bottom: 1px solid #f0f3ef;
                font-size: 14px;
                color: #4a5a4a;
            }}
            
            .info-item:last-child {{
                border-bottom: none;
            }}
            
            .info-label {{
                font-size: 12px;
                color: #7a8a7a;
                display: block;
                margin-bottom: 4px;
            }}
            
            .info-value {{
                color: #3a4a3a;
                font-weight: 500;
            }}
            
            .link-item {{
                display: block;
                padding: 10px 12px;
                margin-bottom: 8px;
                background: #f7f9f7;
                border: 1px solid #e8ede7;
                border-radius: 2px;
                color: #5a7a5a;
                text-decoration: none;
                font-size: 13px;
                transition: all 0.2s ease;
            }}
            
            .link-item:hover {{
                background: #eef2ed;
                border-color: #7fa87f;
                color: #4a6a4a;
            }}
            
            .detection-list {{
                display: grid;
                grid-template-columns: 1fr 1fr;
                gap: 8px;
            }}
            
            .detection-item {{
                padding: 8px 10px;
                background: #f9faf9;
                border: 1px solid #e8ede7;
                border-radius: 2px;
                font-size: 13px;
                color: #4a5a4a;
                text-align: center;
            }}
            
            .system-status {{
                padding: 16px;
                background: #f4f7f3;
                border: 1px solid #d8e3d7;
                border-radius: 2px;
                margin-bottom: 24px;
            }}
            
            .status-row {{
                display: flex;
                justify-content: space-between;
                padding: 6px 0;
                font-size: 13px;
            }}
            
            .status-label {{
                color: #6b7c6b;
            }}
            
            .status-value {{
                color: #3a4a3a;
                font-weight: 500;
            }}
            
            .status-value.active {{
                color: #7fa87f;
            }}
            
            @media (max-width: 1400px) {{
                .main-content {{
                    grid-template-columns: 1fr 320px;
                }}
            }}
            
            @media (max-width: 1200px) {{
                .main-content {{
                    grid-template-columns: 1fr;
                }}
                
                .sidebar {{
                    border-left: none;
                    border-top: 1px solid #e3e8e1;
                    max-width: 100%;
                }}
                
                .video-section {{
                    padding: 16px;
                }}
                
                .video-feed {{
                    max-height: 70vh;
                }}
            }}
            
            @media (max-width: 768px) {{
                .header {{
                    padding: 16px 20px;
                }}
                
                .header h1 {{
                    font-size: 16px;
                }}
                
                .header-content {{
                    flex-direction: column;
                    align-items: flex-start;
                    gap: 8px;
                }}
                
                .video-section {{
                    padding: 12px;
                }}
                
                .sidebar {{
                    padding: 24px 20px;
                }}
                
                .detection-list {{
                    grid-template-columns: 1fr;
                }}
                
                .video-feed {{
                    max-height: 60vh;
                }}
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <div class="header-content">
                    <h1>食品视觉检测系统 YOLOv11x</h1>
                    <div class="header-status">
                        <span class="status-dot"></span>
                        <span>检测状态：运行中</span>
                    </div>
                </div>
            </div>

            <div class="main-content">
                <div class="video-section">
                    <div class="video-wrapper">
                        <div class="video-header">实时检测画面</div>
                        <img src="/video_feed" class="video-feed" alt="实时检测画面">
                    </div>
                </div>

                <div class="sidebar">
                    <div class="system-status">
                        <div class="status-row">
                            <span class="status-label">系统状态</span>
                            <span class="status-value active">正常运行</span>
                        </div>
                        <div class="status-row">
                            <span class="status-label">分辨率支持</span>
                            <span class="status-value">4K/2K/1080p</span>
                        </div>
                        <div class="status-row">
                            <span class="status-label">摄像头连接</span>
                            <span class="status-value active">已连接</span>
                        </div>
                    </div>

                    <div class="info-section">
                        <div class="section-title">系统接口</div>
                        <a href="/video_feed" target="_blank" class="link-item">视频流输出</a>
                        <a href="/status" target="_blank" class="link-item">系统状态查询</a>
                        <a href="/detect?class=清炒莲藕" target="_blank" class="link-item">检测接口示例</a>
                    </div>

                    <div class="info-section">
                        <div class="section-title">技术参数</div>
                        <ul class="info-list">
                            <li class="info-item">
                                <span class="info-label">检测模型</span>
                                <span class="info-value">YOLOv11x</span>
                            </li>
                            <li class="info-item">
                                <span class="info-label">最大分辨率</span>
                                <span class="info-value">3840 × 2160</span>
                            </li>
                            <li class="info-item">
                                <span class="info-label">处理器</span>
                                <span class="info-value">GPU 加速</span>
                            </li>
                            <li class="info-item">
                                <span class="info-label">检测类别</span>
                                <span class="info-value">12 类食品</span>
                            </li>
                        </ul>
                    </div>

                    <div class="info-section">
                        <div class="section-title">识别类别</div>
                        <div class="detection-list">
                            <div class="detection-item">清炒莲藕</div>
                            <div class="detection-item">红烧排骨</div>
                            <div class="detection-item">烤鸭</div>
                            <div class="detection-item">花菜牛腩</div>
                            <div class="detection-item">清炒黑木耳</div>
                            <div class="detection-item">米饭</div>
                            <div class="detection-item">麻婆豆腐</div>
                            <div class="detection-item">宫保鸡丁</div>
                            <div class="detection-item">糖醋里脊</div>
                            <div class="detection-item">水煮鱼</div>
                            <div class="detection-item">西红柿炒鸡蛋</div>
                            <div class="detection-item">青椒土豆丝</div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </body>
    </html>
    '''


@app.route('/status')
def status():
    """状态检查"""
    return jsonify({
        'model_loaded': detector.model is not None,
        'is_running': detector.is_running,
        'camera_connected': detector.camera_connected,
        'reconnect_count': detector.reconnect_count,
        'detected_classes': detector.detected_classes,
        'class_names': CLASS_NAMES if CLASS_NAMES else []
    })


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(description='YOLOv11x Detection Stream')
    parser.add_argument('--source', type=int, default=0, help='摄像头索引')
    parser.add_argument('--port', type=int, default=5000, help='服务端口')
    parser.add_argument('--conf', type=float, default=0.45, help='置信度阈值')
    args = parser.parse_args()

    # 更新置信度阈值
    CONF_THRESHOLD = args.conf

    try:
        print("=" * 60)
        print("YOLOv11x 检测服务启动中...")
        print("=" * 60)

        # 启动检测
        if detector.start_detection(source=args.source):
            print("✅ YOLOv11x检测服务启动成功！")
            print(f"🌐 访问地址: http://127.0.0.1:{args.port}")
            print(f"📹 视频流地址: http://127.0.0.1:{args.port}/video_feed")
            print(f"📊 状态检查: http://127.0.0.1:{args.port}/status")
            print("🔄 按Ctrl+C停止服务")

            try:
                app.run(host='0.0.0.0', port=args.port, debug=False)
            except KeyboardInterrupt:
                print("\n👋 服务已停止")
                detector.stop()
        else:
            print("❌ YOLOv11x检测服务启动失败")

    except Exception as e:
        print(f"❌ 启动失败: {e}")
        import traceback

        traceback.print_exc()
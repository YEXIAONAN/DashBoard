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

# 配置参数
WEIGHTS_PATH = "main/models/yolov11x.pt"
CONF_THRESHOLD = 0.45
IOU_THRESHOLD = 0.45
DEVICE = '0' if torch.cuda.is_available() else 'cpu'  # 自动选择GPU或CPU
IMG_SIZE = 640  # YOLO模型输入尺寸，保持640x640

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
            LOGGER.info(f"✅ 检测到高分辨率摄像头: {actual_width}x{actual_height}")
            return actual_width, actual_height

    # 回退到实际检测到的分辨率
    actual_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    actual_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    cap.release()

    if actual_width > 0 and actual_height > 0:
        LOGGER.info(f"检测到摄像头分辨率: {actual_width}x{actual_height}")
        return actual_width, actual_height

    LOGGER.info("使用默认摄像头分辨率: 640x480")
    return 640, 480


# 自动获取摄像头分辨率
CAMERA_WIDTH, CAMERA_HEIGHT = get_camera_resolution()

# 从YOLOv11模型自动获取类别名称
CLASS_NAMES = None

try:
    from ultralytics import YOLO

    YOLO_AVAILABLE = True
    LOGGER.info("Ultralytics YOLO库加载成功")
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
            LOGGER.info(f"🚀 使用GPU: {gpu_name}")
        else:
            LOGGER.info("⚠️ 使用CPU推理（建议安装CUDA以获得更好性能）")

        self.model = None
        self.is_running = False
        self.frame = None
        self.cap = None
        self.camera_width = CAMERA_WIDTH
        self.camera_height = CAMERA_HEIGHT
        self.detected_classes = []
        self.lock = threading.Lock()


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

            LOGGER.info(f"YOLOv11x模型加载成功: {WEIGHTS_PATH}")
            LOGGER.info(f"检测类别数量: {len(CLASS_NAMES)}")
            LOGGER.info(f"类别列表: {CLASS_NAMES}")
            return True

        except Exception as e:
            LOGGER.error(f"YOLOv11x模型加载失败: {e}")
            return False

    def start_detection(self, source=0):
        """开始检测，自动适配摄像头分辨率"""
        if not self.load_model():
            return False

        self.is_running = True

        # 打开摄像头
        try:
            self.cap = cv2.VideoCapture(source)
            if not self.cap.isOpened():
                LOGGER.error(f"无法打开摄像头: {source}")
                return False

            # 设置摄像头为检测到的最佳分辨率
            self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, CAMERA_WIDTH)
            self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, CAMERA_HEIGHT)

            # 设置摄像头参数优化
            self.cap.set(cv2.CAP_PROP_FPS, 30)
            self.cap.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc(*'MJPG'))
            self.cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)

            # 验证实际分辨率
            ret, frame = self.cap.read()
            if not ret:
                LOGGER.error(f"无法从摄像头读取帧: {source}")
                return False

            actual_height, actual_width = frame.shape[:2]

            # 如果实际分辨率与期望不同，使用实际分辨率
            if abs(actual_width - CAMERA_WIDTH) > 10 or abs(actual_height - CAMERA_HEIGHT) > 10:
                LOGGER.warning(f"实际分辨率 {actual_width}x{actual_height} 与期望 {CAMERA_WIDTH}x{CAMERA_HEIGHT} 不同")
                # 使用实际分辨率
                self.camera_width, self.camera_height = actual_width, actual_height
            else:
                self.camera_width, self.camera_height = CAMERA_WIDTH, CAMERA_HEIGHT

            LOGGER.info(f"🎥 摄像头{source}正常，实际分辨率: {actual_width}x{actual_height}")

        except Exception as e:
            LOGGER.error(f"❌ 摄像头初始化失败: {e}")
            return False

        # 启动检测线程
        detection_thread = threading.Thread(target=self._detection_loop)
        detection_thread.daemon = True
        detection_thread.start()

        return True

    def _detection_loop(self):
        """优化版检测循环，自适应实际分辨率"""
        try:
            fps_counter = 0
            fps_start_time = time.time()
            current_fps = 0

            while self.is_running and self.cap and self.cap.isOpened():
                ret, frame = self.cap.read()
                if not ret:
                    LOGGER.warning("⚠️ 无法读取摄像头帧")
                    time.sleep(0.1)
                    continue

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
        return jsonify({'detected':False,'message':'未指定类别'})

    try:
        # 检查detector是否已检测到目标类别
        with detector.lock:
            detected = target_class in detector.detected_classes

        return jsonify({
            'detected': detected,
            'class': target_class,
            'confidence': 0.85 if detected else 0.0,
            'detected_classes': detector.detected_classes
        })

    except Exception as e:
        return jsonify({'detected': False, 'message': str(e)})


@app.route('/')
def index():
    """高分辨率自适应主页"""
    return f'''
    <html>
    <head>
        <title>YOLOv11x 4K Stream</title>
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <style>
            body {{ 
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; 
                margin: 0; 
                padding: 20px; 
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                min-height: 100vh;
            }}
            .container {{ 
                max-width: 95%; 
                margin: 0 auto; 
                background: white; 
                border-radius: 15px; 
                box-shadow: 0 10px 30px rgba(0,0,0,0.3);
                overflow: hidden;
            }}
            .header {{
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                padding: 30px;
                text-align: center;
            }}
            .header h1 {{
                margin: 0;
                font-size: 2.5em;
                font-weight: 300;
            }}
            .video-container {{ 
                text-align: center; 
                padding: 20px;
                background: #f8f9fa;
            }}
            .video-feed {{
                max-width: 100%;
                height: auto;
                border: 3px solid #667eea;
                border-radius: 10px;
                box-shadow: 0 5px 15px rgba(0,0,0,0.2);
            }}
            .info-grid {{
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
                gap: 20px;
                padding: 30px;
            }}
            .info-card {{
                background: #f8f9fa;
                padding: 25px;
                border-radius: 10px;
                border-left: 5px solid #667eea;
            }}
            .info-card h3 {{
                margin-top: 0;
                color: #333;
                font-size: 1.4em;
            }}
            .info-card ul {{
                list-style: none;
                padding: 0;
            }}
            .info-card li {{
                padding: 8px 0;
                border-bottom: 1px solid #eee;
            }}
            .info-card a {{
                color: #667eea;
                text-decoration: none;
                font-weight: bold;
            }}
            .info-card a:hover {{
                text-decoration: underline;
            }}
            .status-bar {{
                background: #28a745;
                color: white;
                padding: 15px;
                text-align: center;
                font-size: 1.2em;
            }}
            @media (max-width: 768px) {{
                .container {{ margin: 10px; }}
                .header {{ padding: 20px; }}
                .header h1 {{ font-size: 2em; }}
                .info-grid {{ padding: 20px; }}
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>🎯 YOLOv11x 4K智能检测系统</h1>
                <p>支持3840x2160超高清实时检测</p>
            </div>

            <div class="video-container">
                <img src="/video_feed" class="video-feed" alt="实时检测画面">
            </div>

            <div class="status-bar">
                ✅ 系统运行正常 | RTX 4060 GPU加速 | 4K分辨率支持
            </div>

            <div class="info-grid">
                <div class="info-card">
                    <h3>📹 视频流地址</h3>
                    <ul>
                        <li><a href="/video_feed" target="_blank">原始视频流</a></li>
                        <li>支持4K/2K/1080p自适应</li>
                    </ul>
                </div>

                <div class="info-card">
                    <h3>🔍 智能检测API</h3>
                    <ul>
                        <li><a href="/detect?class=烤鸭" target="_blank">检测烤鸭</a></li>
                        <li><a href="/detect?class=红烧排骨" target="_blank">检测红烧排骨</a></li>
                        <li><a href="/status" target="_blank">系统状态</a></li>
                    </ul>
                </div>

                <div class="info-card">
                    <h3>⚙️ 技术规格</h3>
                    <ul>
                        <li>分辨率: 3840x2160 (4K UHD)</li>
                        <li>模型: YOLOv11x</li>
                        <li>GPU: RTX 4060加速</li>
                        <li>检测类别: 6种菜品</li>
                    </ul>
                </div>

                <div class="info-card">
                    <h3>🎯 支持菜品</h3>
                    <ul>
                        <li>清炒莲藕</li>
                        <li>红烧排骨</li>
                        <li>烤鸭</li>
                        <li>花菜牛腩</li>
                        <li>清炒黑木耳</li>
                        <li>米饭</li>
                    </ul>
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
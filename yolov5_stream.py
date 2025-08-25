#!/usr/bin/env python3
import cv2
import torch
import numpy as np
from flask import Flask, Response, jsonify, request
import threading
import time
from pathlib import Path
import sys
import os
from PIL import Image, ImageDraw, ImageFont

# 添加YOLOv5路径到系统路径
YOLOV5_PATH = Path(__file__).parent / "yolov5"
sys.path.insert(0, str(YOLOV5_PATH))

from models.common import DetectMultiBackend
from utils.dataloaders import LoadStreams
from utils.general import (
    LOGGER,
    check_img_size,
    check_imshow,
    non_max_suppression,
    scale_boxes,
    cv2,
)
from utils.torch_utils import select_device

app = Flask(__name__)

# 配置参数
WEIGHTS_PATH = "main/models/best.pt"
CLASS_NAMES =  ['清炒莲藕', '红烧排骨', '烤鸭', '花菜牛腩', '清炒黑木耳', '米饭']
CONF_THRESHOLD = 0.45
IOU_THRESHOLD = 0.45
DEVICE = '0' if torch.cuda.is_available() else 'cpu'  # 自动选择GPU或CPU
IMG_SIZE = 640

class YOLODetector:
    def __init__(self):
        self.device = select_device(DEVICE)
        self.model = None
        self.stream = None
        self.is_running = False
        self.frame = None
        self.detected_classes = []  # 存储当前检测到的类别
        self.lock = threading.Lock()
        
    def load_model(self):
        """加载YOLOv5模型"""
        try:
            self.model = DetectMultiBackend(WEIGHTS_PATH, device=self.device)
            self.stride, self.names, self.pt = self.model.stride, self.model.names, self.model.pt
            self.imgsz = check_img_size(IMG_SIZE, s=self.stride)
            self.model.warmup(imgsz=(1, 3, self.imgsz, self.imgsz))
            LOGGER.info(f"模型加载成功: {WEIGHTS_PATH}")
            return True
        except Exception as e:
            LOGGER.error(f"模型加载失败: {e}")
            return False
    
    def start_detection(self, source=0):
        """开始检测"""
        if not self.load_model():
            return False
            
        self.is_running = True
        
        # 使用摄像头
        if not check_imshow():
            LOGGER.error("无法显示图像")
            return False
            
        self.stream = LoadStreams(str(source), img_size=self.imgsz, stride=self.stride, auto=self.pt)
        
        # 启动检测线程
        detection_thread = threading.Thread(target=self._detection_loop)
        detection_thread.daemon = True
        detection_thread.start()
        
        return True
    
    def _detection_loop(self):
        """检测循环"""
        try:
            for path, im, im0s, vid_cap, s in self.stream:
                if not self.is_running:
                    break
                    
                im = torch.from_numpy(im).to(self.device)
                im = im.half() if self.model.fp16 else im.float()
                im /= 255
                if len(im.shape) == 3:
                    im = im[None]
                
                # 推理
                pred = self.model(im, augment=False, visualize=False)
                pred = non_max_suppression(pred, CONF_THRESHOLD, IOU_THRESHOLD, None, False, max_det=1000)
                
                # 处理检测结果
                for i, det in enumerate(pred):
                    im0 = im0s[i].copy()
                    
                    # 清空当前检测到的类别
                    self.detected_classes.clear()
                    
                    if len(det):
                        det[:, :4] = scale_boxes(im.shape[2:], det[:, :4], im0.shape).round()
                        
                        for *xyxy, conf, cls in reversed(det):
                            class_name = CLASS_NAMES[int(cls)]
                            label = f'{class_name} {conf:.2f}'
                            self.detected_classes.append(class_name)
                            
                            # 绘制边界框
                            c1, c2 = (int(xyxy[0]), int(xyxy[1])), (int(xyxy[2]), int(xyxy[3]))
                            cv2.rectangle(im0, c1, c2, (0, 255, 0), 2)
                            
                            # 绘制标签（支持中文）
                            t_size = cv2.getTextSize(label, 0, fontScale=0.6, thickness=2)[0]
                            c2 = c1[0] + t_size[0], c1[1] - t_size[1] - 3
                            cv2.rectangle(im0, c1, c2, (0, 255, 0), -1, cv2.LINE_AA)
                            
                            # 使用PIL绘制中文
                            pil_img = Image.fromarray(cv2.cvtColor(im0, cv2.COLOR_BGR2RGB))
                            draw = ImageDraw.Draw(pil_img)
                            
                            # 尝试加载中文字体
                            try:
                                font = ImageFont.truetype("C:\Windows\Fonts\simhei.ttf", 16)
                            except:
                                try:
                                    font = ImageFont.truetype("msyh.ttc", 16)
                                except:
                                    font = ImageFont.load_default()
                            
                            draw.text((c1[0], c1[1] - 20), label, font=font, fill=(0, 0, 0))
                            im0 = cv2.cvtColor(np.array(pil_img), cv2.COLOR_RGB2BGR)
                    
                    # 更新帧
                    with self.lock:
                        self.frame = im0
                        
        except Exception as e:
            LOGGER.error(f"检测循环错误: {e}")
    
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

detector = YOLODetector()

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
    
    if not target_class:
        return jsonify({'detected': False, 'message': '未指定检测类别'})
    
    try:
        # 检查detector是否已检测到目标类别
        with detector.lock:
            detected = target_class in detector.detected_classes
            
        return jsonify({
            'detected': detected,
            'class': target_class,
            'confidence': 0.85 if detected else 0.0  # 实际置信度应从YOLO结果获取
        })
        
    except Exception as e:
        return jsonify({'detected': False, 'message': str(e)})

@app.route('/')
def index():
    """主页"""
    return '''
    <html>
    <head><title>YOLOv5 Stream</title></head>
    <body>
        <h1>YOLOv5 Detection Stream</h1>
        <img src="/video_feed" width="640" height="480">
    </body>
    </html>
    '''

if __name__ == '__main__':
    if detector.start_detection(0):  # 使用默认摄像头
        LOGGER.info("YOLOv5检测服务启动成功")
        app.run(host='0.0.0.0', port=5000, debug=False)
    else:
        LOGGER.error("YOLOv5检测服务启动失败")
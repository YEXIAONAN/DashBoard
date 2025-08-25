#!/usr/bin/env python3
"""
验证NumPy修复是否成功的脚本
"""

try:
    import numpy as np
    print(f"✅ NumPy版本: {np.__version__}")
    
    import torch
    print(f"✅ PyTorch版本: {torch.__version__}")
    
    from ultralytics import YOLO
    print("✅ Ultralytics YOLO库加载成功")
    
    import cv2
    print(f"✅ OpenCV版本: {cv2.__version__}")
    
    # 测试NumPy和PyTorch的兼容性
    arr = np.array([1, 2, 3, 4, 5])
    tensor = torch.from_numpy(arr)
    back_to_numpy = tensor.numpy()
    print("✅ NumPy <-> PyTorch 转换正常")
    
    # 测试图像处理
    test_img = np.zeros((640, 640, 3), dtype=np.uint8)
    tensor_img = torch.from_numpy(test_img)
    print("✅ 图像处理兼容性正常")
    
    print("\n🎉 所有兼容性测试通过！")
    print("现在可以安全运行YOLOv11x检测服务了")
    
except Exception as e:
    print(f"❌ 测试失败: {e}")
    import traceback
    traceback.print_exc()
    exit(1)
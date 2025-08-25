#!/usr/bin/env python3
"""
NumPy版本兼容性修复脚本
解决YOLOv11x与NumPy 2.x的兼容性问题
"""

import subprocess
import sys
import os

def run_command(cmd, description=""):
    """运行命令并显示输出"""
    print(f"正在执行: {description}")
    print(f"命令: {' '.join(cmd) if isinstance(cmd, list) else cmd}")
    
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        if result.stdout:
            print("输出:", result.stdout)
        if result.stderr:
            print("错误:", result.stderr)
        return result.returncode == 0
    except Exception as e:
        print(f"执行失败: {e}")
        return False

def main():
    """主修复流程"""
    print("=" * 60)
    print("开始修复NumPy版本兼容性问题...")
    print("=" * 60)
    
    # 1. 卸载当前NumPy
    print("\n[1/4] 卸载当前NumPy版本...")
    success = run_command([sys.executable, "-m", "pip", "uninstall", "numpy", "-y"], 
                         "卸载NumPy")
    
    if not success:
        print("警告: 卸载NumPy可能遇到问题，继续下一步...")
    
    # 2. 安装兼容版本的NumPy
    print("\n[2/4] 安装NumPy 1.26.4（兼容版本）...")
    success = run_command([sys.executable, "-m", "pip", "install", "numpy==1.26.4", "--force-reinstall"], 
                         "安装NumPy 1.26.4")
    
    if not success:
        print("尝试安装其他兼容版本...")
        success = run_command([sys.executable, "-m", "pip", "install", "numpy<2.0", "--force-reinstall"], 
                             "安装NumPy <2.0")
    
    # 3. 重新安装PyTorch相关依赖
    print("\n[3/4] 重新安装PyTorch和Ultralytics...")
    
    # 先卸载相关包
    packages_to_reinstall = ["torch", "torchvision", "ultralytics", "opencv-python"]
    
    for package in packages_to_reinstall:
        run_command([sys.executable, "-m", "pip", "uninstall", package, "-y"], 
                   f"卸载 {package}")
    
    # 重新安装
    success = run_command([sys.executable, "-m", "pip", "install", "torch", "torchvision", "ultralytics", 
                          "opencv-python", "--force-reinstall", "--no-cache-dir"], 
                         "重新安装PyTorch和Ultralytics")
    
    # 4. 验证修复结果
    print("\n[4/4] 验证修复结果...")
    
    # 创建测试脚本
    test_script = """
import numpy as np
import torch
from ultralytics import YOLO
import cv2

print("NumPy版本:", np.__version__)
print("PyTorch版本:", torch.__version__)
print("OpenCV版本:", cv2.__version__)

try:
    # 测试基本功能
    arr = np.array([1, 2, 3])
    tensor = torch.from_numpy(arr)
    print("✅ NumPy与PyTorch兼容")
    
    # 测试YOLO模型加载（不实际加载权重）
    print("✅ 所有依赖库加载成功")
    
except Exception as e:
    print("❌ 测试失败:", str(e))
    exit(1)
"""
    
    with open("test_fix.py", "w", encoding="utf-8") as f:
        f.write(test_script)
    
    success = run_command([sys.executable, "test_fix.py"], "运行兼容性测试")
    
    # 清理测试文件
    if os.path.exists("test_fix.py"):
        os.remove("test_fix.py")
    
    print("\n" + "=" * 60)
    if success:
        print("✅ 修复完成！NumPy兼容性问题已解决")
        print("\n现在可以运行YOLOv11x检测服务了:")
        print("python yolov11x_stream.py")
    else:
        print("❌ 修复遇到问题，请查看错误信息")
        print("\n备用解决方案:")
        print("1. 手动降级NumPy: pip install numpy==1.26.4")
        print("2. 创建新的虚拟环境")
        print("3. 使用requirements-yolov11x.txt重新安装")
    print("=" * 60)

if __name__ == "__main__":
    main()
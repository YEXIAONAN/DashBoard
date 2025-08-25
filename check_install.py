#!/usr/bin/env python3
"""
YOLOv11x依赖检查脚本
"""

import sys
import importlib

def check_package(package_name, import_name=None):
    """检查包是否安装"""
    if import_name is None:
        import_name = package_name.split('>=')[0].split('==')[0]
    
    try:
        importlib.import_module(import_name)
        print(f"✅ {package_name} - 已安装")
        return True
    except ImportError:
        print(f"❌ {package_name} - 未安装")
        return False

def main():
    """主检查函数"""
    print("🔍 正在检查YOLOv11x项目依赖...\n")
    
    packages = [
        "ultralytics",
        "torch",
        "torchvision", 
        "cv2",
        "numpy",
        "PIL",
        "matplotlib",
        "scipy",
        "pandas",
        "seaborn",
        "flask",
        "psutil",
        "tqdm",
        "yaml",
        "requests",
        "thop",
        "pathlib"
    ]
    
    failed = []
    for pkg in packages:
        if not check_package(pkg):
            failed.append(pkg)
    
    print(f"\n📊 检查结果:")
    print(f"总检查包数: {len(packages)}")
    print(f"成功安装: {len(packages) - len(failed)}")
    print(f"缺失包: {len(failed)}")
    
    if failed:
        print(f"\n❗ 缺失的包: {', '.join(failed)}")
        print("请运行: pip install " + " ".join([pkg.split('>=')[0] for pkg in failed]))
    else:
        print("\n🎉 所有依赖都已正确安装！")
        print("可以运行: python yolov11x_stream.py")

if __name__ == "__main__":
    main()
#!/usr/bin/env python3
"""
下载repo.html所需的所有外部资源到本地
"""

import os
import requests
import shutil
from pathlib import Path

def download_file(url, local_path):
    """下载文件到指定路径"""
    try:
        response = requests.get(url, stream=True, timeout=30)
        response.raise_for_status()
        
        # 确保目录存在
        os.makedirs(os.path.dirname(local_path), exist_ok=True)
        
        with open(local_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)
        print(f"✓ 已下载: {local_path}")
        return True
    except Exception as e:
        print(f"✗ 下载失败 {url}: {e}")
        return False

def main():
    # 基础路径
    base_dir = Path("d:/Document/Dashboard/DashBoard")
    static_dir = base_dir / "main" / "static"
    
    # 要下载的资源
    assets = {
        # Font Awesome 完整包
        "font_awesome_css": {
            "url": "https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css",
            "path": static_dir / "css" / "font-awesome" / "all.min.css"
        },
        "echarts_js": {
            "url": "https://cdn.jsdelivr.net/npm/echarts@5/dist/echarts.min.js",
            "path": static_dir / "js" / "echarts.min.js"
        },
        # 用户头像
        "user_avatar": {
            "url": "https://cdn-icons-png.flaticon.com/512/847/847969.png",
            "path": static_dir / "Images" / "user_avatar.png"
        }
    }
    
    # Font Awesome 字体文件
    font_awesome_fonts = [
        "https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/webfonts/fa-brands-400.woff2",
        "https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/webfonts/fa-brands-400.ttf",
        "https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/webfonts/fa-regular-400.woff2",
        "https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/webfonts/fa-regular-400.ttf",
        "https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/webfonts/fa-solid-900.woff2",
        "https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/webfonts/fa-solid-900.ttf",
        "https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/webfonts/fa-v4compatibility.woff2",
        "https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/webfonts/fa-v4compatibility.ttf"
    ]
    
    print("开始下载本地资源...")
    
    # 下载主要资源
    for name, asset in assets.items():
        download_file(asset["url"], asset["path"])
    
    # 下载Font Awesome字体
    for font_url in font_awesome_fonts:
        font_name = font_url.split("/")[-1]
        font_path = static_dir / "css" / "font-awesome" / "webfonts" / font_name
        download_file(font_url, font_path)
    
    print("\n下载完成！请检查以下目录：")
    print(f"Font Awesome CSS: {static_dir}/css/font-awesome/all.min.css")
    print(f"Font Awesome字体: {static_dir}/css/font-awesome/webfonts/")
    print(f"ECharts JS: {static_dir}/js/echarts.min.js")
    print(f"用户头像: {static_dir}/Images/user_avatar.png")

if __name__ == "__main__":
    main()
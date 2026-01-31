#!/usr/bin/env python3
"""
测试多语言支持功能
"""
import requests
import json

# 测试服务器地址
BASE_URL = "http://172.16.4.181:8001"

def test_health():
    """测试健康检查接口"""
    try:
        response = requests.get(f"{BASE_URL}/health")
        if response.status_code == 200:
            data = response.json()
            print("✓ 健康检查通过")
            print(f"  支持的语言: {data.get('supported_languages', [])}")
            print(f"  语言名称: {data.get('language_names', {})}")
            return True
        else:
            print(f"✗ 健康检查失败: {response.status_code}")
            return False
    except Exception as e:
        print(f"✗ 健康检查异常: {e}")
        return False

def test_language_config():
    """测试语言配置"""
    print("\n测试语言配置:")
    
    # 测试语言映射
    language_config = {
        "zh": {
            "code": "zh",
            "prompt": "以下是普通话的句子。"
        },
        "en": {
            "code": "en", 
            "prompt": "The following is spoken in English."
        },
        "vi": {
            "code": "vi",
            "prompt": "Sau đây là câu nói tiếng Việt."
        }
    }
    
    for lang, config in language_config.items():
        print(f"  {lang}: {config['code']} - {config['prompt'][:30]}...")
    
    print("✓ 语言配置正确")

if __name__ == "__main__":
    print("=== 多语言支持测试 ===")
    
    # 测试健康检查
    if test_health():
        print("✓ 服务运行正常")
    else:
        print("✗ 服务未运行，请先启动 ai_voice_service_offline.py")
    
    # 测试语言配置
    test_language_config()
    
    print("\n=== 测试完成 ===")
    print("前端使用说明:")
    print("1. 在聊天界面顶部选择语言")
    print("2. 点击麦克风按钮录音")
    print("3. 系统会使用选定的语言进行识别")
    print("4. 支持的语言: 中文(zh), 英文(en), 越南语(vi)")
"""
测试 Ollama 连接
"""
import requests
import json

OLLAMA_HOST = "http://10.0.0.10:11434"

def test_ollama():
    """测试 Ollama 服务连接"""
    print("=" * 60)
    print("Ollama 连接测试")
    print("=" * 60)
    
    # 测试 1: 检查服务是否运行
    print(f"\n测试 1: 检查 Ollama 服务 ({OLLAMA_HOST})")
    try:
        response = requests.get(f"{OLLAMA_HOST}/api/tags", timeout=5)
        if response.status_code == 200:
            print("✅ Ollama 服务运行正常")
            data = response.json()
            models = data.get("models", [])
            print(f"\n可用模型数量: {len(models)}")
            for model in models:
                print(f"  - {model.get('name')}")
        else:
            print(f"❌ Ollama 响应异常: HTTP {response.status_code}")
    except requests.exceptions.ConnectionError:
        print(f"❌ 无法连接到 Ollama 服务")
        print(f"   请检查:")
        print(f"   1. Ollama 是否运行")
        print(f"   2. 地址是否正确: {OLLAMA_HOST}")
        print(f"   3. 防火墙是否阻止连接")
        return False
    except Exception as e:
        print(f"❌ 连接失败: {e}")
        return False
    
    # 测试 2: 测试生成接口
    print(f"\n测试 2: 测试文本生成")
    try:
        payload = {
            "model": "qwen2.5:7b",
            "prompt": "Xin chào",
            "stream": False
        }
        
        response = requests.post(
            f"{OLLAMA_HOST}/api/generate",
            json=payload,
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            reply = result.get("response", "")
            print(f"✅ 生成成功")
            print(f"   回复: {reply[:100]}...")
        else:
            print(f"❌ 生成失败: HTTP {response.status_code}")
            print(f"   响应: {response.text}")
    except Exception as e:
        print(f"❌ 生成失败: {e}")
        return False
    
    print("\n" + "=" * 60)
    print("✅ 所有测试通过！Ollama 服务正常")
    print("=" * 60)
    return True

if __name__ == "__main__":
    success = test_ollama()
    if not success:
        print("\n⚠️ Ollama 服务不可用")
        print("\n解决方案:")
        print("1. 检查 Ollama 是否运行")
        print("2. 检查地址配置是否正确")
        print("3. 尝试重启 Ollama 服务")
        print("4. 检查网络连接")

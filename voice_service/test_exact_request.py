"""测试完全相同的请求"""
import httpx
import asyncio

OLLAMA_HOST = "http://172.16.4.181:11434"
OLLAMA_MODEL = "qwen2.5:7b"

async def test():
    print("测试非流式请求...")
    
    # 测试 1: 默认请求
    print("\n=== 测试 1: 默认 httpx 请求 ===")
    try:
        async with httpx.AsyncClient(timeout=120.0) as client:
            payload = {
                "model": OLLAMA_MODEL,
                "prompt": "今天是北京。",
                "stream": False
            }
            
            response = await client.post(f"{OLLAMA_HOST}/api/generate", json=payload)
            print(f"状态码: {response.status_code}")
            if response.status_code == 200:
                data = response.json()
                print(f"✅ 成功！响应: {data.get('response', '')[:100]}")
            else:
                print(f"❌ 失败！")
    except Exception as e:
        print(f"❌ 异常: {e}")
    
    # 测试 2: 添加 User-Agent
    print("\n=== 测试 2: 添加 User-Agent ===")
    try:
        headers = {
            "User-Agent": "Mozilla/5.0",
            "Accept": "application/json"
        }
        async with httpx.AsyncClient(timeout=120.0, headers=headers) as client:
            payload = {
                "model": OLLAMA_MODEL,
                "prompt": "今天是北京。",
                "stream": False
            }
            
            response = await client.post(f"{OLLAMA_HOST}/api/generate", json=payload)
            print(f"状态码: {response.status_code}")
            if response.status_code == 200:
                data = response.json()
                print(f"✅ 成功！响应: {data.get('response', '')[:100]}")
            else:
                print(f"❌ 失败！")
    except Exception as e:
        print(f"❌ 异常: {e}")
    
    # 测试 3: HTTP/1.1
    print("\n=== 测试 3: 强制 HTTP/1.1 ===")
    try:
        async with httpx.AsyncClient(timeout=120.0, http2=False) as client:
            payload = {
                "model": OLLAMA_MODEL,
                "prompt": "今天是北京。",
                "stream": False
            }
            
            response = await client.post(f"{OLLAMA_HOST}/api/generate", json=payload)
            print(f"状态码: {response.status_code}")
            if response.status_code == 200:
                data = response.json()
                print(f"✅ 成功！响应: {data.get('response', '')[:100]}")
            else:
                print(f"❌ 失败！")
    except Exception as e:
        print(f"❌ 异常: {e}")
    
    # 测试 4: 使用 requests 库（同步）
    print("\n=== 测试 4: 使用 requests 库 ===")
    try:
        import requests
        payload = {
            "model": OLLAMA_MODEL,
            "prompt": "今天是北京。",
            "stream": False
        }
        response = requests.post(f"{OLLAMA_HOST}/api/generate", json=payload, timeout=30)
        print(f"状态码: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ 成功！响应: {data.get('response', '')[:100]}")
        else:
            print(f"❌ 失败！")
    except Exception as e:
        print(f"❌ 异常: {e}")

if __name__ == "__main__":
    asyncio.run(test())

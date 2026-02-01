"""
测试 Ollama 连接和模型可用性
"""
import httpx
import json
import asyncio

OLLAMA_HOST = "http://172.16.4.181:11434"
OLLAMA_MODEL = "qwen2.5:7b"

async def test_ollama():
    """测试 Ollama 服务"""
    print("=" * 60)
    print("测试 Ollama 连接")
    print("=" * 60)
    
    # 测试 1: 检查服务是否运行
    print("\n1. 检查 Ollama 服务状态...")
    models = []
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(f"{OLLAMA_HOST}/api/tags")
            if response.status_code == 200:
                print("✅ Ollama 服务运行正常")
                data = response.json()
                models = [m['name'] for m in data.get('models', [])]
                print(f"   可用模型: {', '.join(models)}")
            else:
                print(f"❌ 服务响应异常: {response.status_code}")
                print(f"   这可能是 Ollama 服务本身的问题")
                return
    except Exception as e:
        print(f"❌ 无法连接到 Ollama 服务: {e}")
        return
    
    # 测试 2: 检查目标模型是否存在
    print(f"\n2. 检查模型 '{OLLAMA_MODEL}' 是否可用...")
    if OLLAMA_MODEL in models:
        print(f"✅ 模型 '{OLLAMA_MODEL}' 已安装")
    else:
        print(f"⚠️  模型 '{OLLAMA_MODEL}' 未找到")
        print(f"   建议使用: {models[0] if models else 'N/A'}")
    
    # 测试 3: 测试非流式生成
    print(f"\n3. 测试非流式生成...")
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            payload = {
                "model": OLLAMA_MODEL,
                "prompt": "Say hello in one sentence",
                "stream": False
            }
            response = await client.post(f"{OLLAMA_HOST}/api/generate", json=payload)
            if response.status_code == 200:
                data = response.json()
                print(f"✅ 非流式生成成功")
                print(f"   响应: {data.get('response', '')[:100]}...")
            else:
                print(f"❌ 生成失败: {response.status_code}")
    except Exception as e:
        print(f"❌ 非流式生成失败: {e}")
    
    # 测试 4: 测试流式生成
    print(f"\n4. 测试流式生成...")
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            payload = {
                "model": OLLAMA_MODEL,
                "prompt": "Count from 1 to 3",
                "stream": True
            }
            full_response = ""
            async with client.stream("POST", f"{OLLAMA_HOST}/api/generate", json=payload) as response:
                if response.status_code == 200:
                    async for line in response.aiter_lines():
                        if line:
                            try:
                                data = json.loads(line)
                                if "response" in data:
                                    full_response += data["response"]
                                if data.get("done", False):
                                    break
                            except json.JSONDecodeError:
                                continue
                    print(f"✅ 流式生成成功")
                    print(f"   响应: {full_response[:100]}...")
                else:
                    print(f"❌ 流式生成失败: {response.status_code}")
    except Exception as e:
        print(f"❌ 流式生成失败: {e}")
    
    print("\n" + "=" * 60)
    print("测试完成")
    print("=" * 60)

if __name__ == "__main__":
    asyncio.run(test_ollama())

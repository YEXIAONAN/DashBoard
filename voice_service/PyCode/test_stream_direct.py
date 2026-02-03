"""直接测试 Ollama 流式请求"""
import httpx
import json
import asyncio

async def test_stream():
    print("测试 Ollama 流式生成...")
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            payload = {
                "model": "qwen2.5:7b",
                "prompt": "Say hello",
                "stream": True
            }
            
            print(f"发送请求到: http://172.16.4.181:11434/api/generate")
            print(f"Payload: {payload}")
            
            async with client.stream("POST", "http://172.16.4.181:11434/api/generate", json=payload) as response:
                print(f"响应状态码: {response.status_code}")
                print(f"响应头: {dict(response.headers)}")
                
                if response.status_code != 200:
                    content = await response.aread()
                    print(f"错误内容: {content.decode()}")
                    return
                
                full_text = ""
                async for line in response.aiter_lines():
                    if line:
                        try:
                            data = json.loads(line)
                            if "response" in data:
                                full_text += data["response"]
                                print(data["response"], end="", flush=True)
                            if data.get("done", False):
                                print(f"\n\n✅ 流式生成成功！")
                                print(f"完整响应: {full_text}")
                                break
                        except json.JSONDecodeError as e:
                            print(f"\nJSON 解析错误: {e}, line: {line}")
                            continue
    except Exception as e:
        print(f"\n❌ 错误: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_stream())

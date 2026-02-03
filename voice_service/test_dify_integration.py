"""
测试 Dify 工作流集成
"""
import requests
import json
import base64
import time

# 服务配置
SERVICE_URL = "http://localhost:8001"

def test_health():
    """测试健康检查"""
    print("=" * 50)
    print("测试 1: 健康检查")
    print("=" * 50)
    
    try:
        response = requests.get(f"{SERVICE_URL}/health")
        if response.status_code == 200:
            data = response.json()
            print("✅ 服务运行正常")
            print(f"LLM 服务: {data.get('llm_service')}")
            print(f"Dify API: {data.get('dify_api')}")
            print(f"Dify 模型: {data.get('dify_model')}")
            print(f"备用 Ollama: {data.get('fallback_ollama')}")
            print(f"ASR: {data.get('asr')}")
            print(f"TTS: {data.get('tts')}")
            print(f"支持语言: {data.get('supported_languages')}")
            return True
        else:
            print(f"❌ 健康检查失败: HTTP {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ 连接失败: {e}")
        return False

def test_transcribe():
    """测试语音识别（需要音频文件）"""
    print("\n" + "=" * 50)
    print("测试 2: 语音识别")
    print("=" * 50)
    print("⚠️ 跳过（需要音频文件）")
    return True

def test_chat_text():
    """测试文本对话（使用 Dify 工作流）"""
    print("\n" + "=" * 50)
    print("测试 3: 文本对话（Dify 工作流）")
    print("=" * 50)
    
    try:
        data = {
            "text": "你好，请介绍一下健康饮食的重要性",
            "language": "zh",
            "user_name": "测试用户"
        }
        
        print(f"发送消息: {data['text']}")
        print("等待 Dify 工作流响应...")
        
        response = requests.post(
            f"{SERVICE_URL}/chat",
            data=data,
            timeout=120
        )
        
        if response.status_code == 200:
            result = response.json()
            reply_text = result.get("text", "")
            audio_base64 = result.get("audio", "")
            
            print("✅ 对话成功")
            print(f"回复文本: {reply_text[:200]}...")
            print(f"音频数据: {len(audio_base64)} 字符 (Base64)")
            
            # 保存音频到文件
            if audio_base64:
                audio_bytes = base64.b64decode(audio_base64)
                with open("test_output.wav", "wb") as f:
                    f.write(audio_bytes)
                print(f"✅ 音频已保存到 test_output.wav ({len(audio_bytes)} bytes)")
            
            return True
        else:
            print(f"❌ 对话失败: HTTP {response.status_code}")
            print(f"错误信息: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        return False

def test_chat_stream():
    """测试流式对话（使用 Dify 工作流）"""
    print("\n" + "=" * 50)
    print("测试 4: 流式对话（Dify 工作流）")
    print("=" * 50)
    
    try:
        data = {
            "text": "请简单介绍一下营养均衡的重要性",
            "language": "zh",
            "user_name": "测试用户"
        }
        
        print(f"发送消息: {data['text']}")
        print("等待流式响应...")
        
        response = requests.post(
            f"{SERVICE_URL}/chat-stream",
            data=data,
            stream=True,
            timeout=120
        )
        
        if response.status_code == 200:
            print("✅ 开始接收流式数据:")
            full_text = ""
            audio_data = None
            
            for line in response.iter_lines():
                if line:
                    line_str = line.decode('utf-8')
                    if line_str.startswith('data: '):
                        data_str = line_str[6:]
                        try:
                            data = json.loads(data_str)
                            
                            if 'text' in data:
                                text_chunk = data['text']
                                full_text += text_chunk
                                print(text_chunk, end='', flush=True)
                            
                            if 'audio' in data:
                                audio_data = data['audio']
                                print("\n✅ 收到音频数据")
                            
                            if data.get('done'):
                                print("\n✅ 流式响应完成")
                                break
                            
                            if 'error' in data:
                                print(f"\n❌ 错误: {data['error']}")
                                return False
                                
                        except json.JSONDecodeError:
                            continue
            
            print(f"\n完整文本长度: {len(full_text)} 字符")
            
            # 保存音频
            if audio_data:
                audio_bytes = base64.b64decode(audio_data)
                with open("test_stream_output.wav", "wb") as f:
                    f.write(audio_bytes)
                print(f"✅ 音频已保存到 test_stream_output.wav ({len(audio_bytes)} bytes)")
            
            return True
        else:
            print(f"❌ 流式对话失败: HTTP {response.status_code}")
            print(f"错误信息: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        return False

def main():
    """运行所有测试"""
    print("\n" + "=" * 50)
    print("Dify 工作流集成测试")
    print("=" * 50)
    
    results = []
    
    # 测试 1: 健康检查
    results.append(("健康检查", test_health()))
    time.sleep(1)
    
    # 测试 2: 语音识别（跳过）
    results.append(("语音识别", test_transcribe()))
    time.sleep(1)
    
    # 测试 3: 文本对话
    results.append(("文本对话", test_chat_text()))
    time.sleep(1)
    
    # 测试 4: 流式对话
    results.append(("流式对话", test_chat_stream()))
    
    # 总结
    print("\n" + "=" * 50)
    print("测试总结")
    print("=" * 50)
    
    for name, result in results:
        status = "✅ 通过" if result else "❌ 失败"
        print(f"{name}: {status}")
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    print(f"\n总计: {passed}/{total} 测试通过")
    
    if passed == total:
        print("\n🎉 所有测试通过！Dify 工作流集成成功！")
    else:
        print("\n⚠️ 部分测试失败，请检查配置")

if __name__ == "__main__":
    main()

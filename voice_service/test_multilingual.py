"""
多语言功能测试脚本
Test script for multilingual functionality
"""
import requests
import json

# 配置
BASE_URL = "http://172.16.4.181:8001"

def test_chat_stream(text, language):
    """测试流式对话接口"""
    print(f"\n{'='*60}")
    print(f"测试语言 / Testing Language: {language}")
    print(f"输入文本 / Input Text: {text}")
    print(f"{'='*60}")
    
    url = f"{BASE_URL}/chat-stream"
    data = {
        'text': text,
        'language': language
    }
    
    try:
        response = requests.post(url, data=data, stream=True, timeout=120)
        response.raise_for_status()
        
        print("\n回复 / Response:")
        full_text = ""
        
        for line in response.iter_lines():
            if line:
                line_str = line.decode('utf-8')
                if line_str.startswith('data: '):
                    try:
                        json_str = line_str[6:].strip()
                        if json_str:
                            data = json.loads(json_str)
                            
                            if 'text' in data:
                                text_chunk = data['text']
                                full_text += text_chunk
                                print(text_chunk, end='', flush=True)
                            
                            if data.get('done'):
                                print("\n\n✅ 对话完成 / Chat completed")
                                if 'audio' in data:
                                    print(f"✅ 音频已生成 / Audio generated (length: {len(data['audio'])} chars)")
                                break
                    except json.JSONDecodeError as e:
                        print(f"\n⚠️ JSON 解析错误 / JSON parse error: {e}")
        
        return True
        
    except requests.exceptions.RequestException as e:
        print(f"\n❌ 请求失败 / Request failed: {e}")
        return False

def test_health():
    """测试健康检查接口"""
    print("\n" + "="*60)
    print("健康检查 / Health Check")
    print("="*60)
    
    url = f"{BASE_URL}/health"
    
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        print("\n服务状态 / Service Status:")
        for key, value in data.items():
            print(f"  {key}: {value}")
        
        print("\n✅ 服务正常 / Service is healthy")
        return True
        
    except requests.exceptions.RequestException as e:
        print(f"\n❌ 健康检查失败 / Health check failed: {e}")
        return False

def main():
    """主测试函数"""
    print("\n" + "="*60)
    print("AI 语音助手多语言功能测试")
    print("AI Voice Assistant Multilingual Test")
    print("="*60)
    
    # 1. 健康检查
    if not test_health():
        print("\n⚠️ 服务未运行，请先启动服务 / Service not running, please start the service first")
        return
    
    # 2. 测试用例
    test_cases = [
        {
            'text': '你好，请介绍一下你自己。',
            'language': 'zh',
            'description': '中文测试 / Chinese Test'
        },
        {
            'text': 'Hello, please introduce yourself.',
            'language': 'en',
            'description': '英文测试 / English Test'
        },
        {
            'text': 'Xin chào, vui lòng giới thiệu về bản thân bạn.',
            'language': 'vi',
            'description': '越南语测试 / Vietnamese Test'
        }
    ]
    
    # 执行测试
    results = []
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n\n{'#'*60}")
        print(f"测试 {i}/3: {test_case['description']}")
        print(f"{'#'*60}")
        
        success = test_chat_stream(test_case['text'], test_case['language'])
        results.append({
            'test': test_case['description'],
            'success': success
        })
        
        # 等待一下，避免请求过快
        import time
        time.sleep(2)
    
    # 总结
    print("\n\n" + "="*60)
    print("测试总结 / Test Summary")
    print("="*60)
    
    for result in results:
        status = "✅ 通过 / PASSED" if result['success'] else "❌ 失败 / FAILED"
        print(f"{result['test']}: {status}")
    
    passed = sum(1 for r in results if r['success'])
    total = len(results)
    print(f"\n总计 / Total: {passed}/{total} 通过 / passed")
    
    if passed == total:
        print("\n🎉 所有测试通过！/ All tests passed!")
    else:
        print("\n⚠️ 部分测试失败 / Some tests failed")

if __name__ == "__main__":
    main()

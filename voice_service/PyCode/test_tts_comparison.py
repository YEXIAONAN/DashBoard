"""
TTS 引擎对比测试
比较 pyttsx3、Coqui TTS 和 Edge TTS 的效果
"""
import time
import os

def test_pyttsx3():
    """测试 pyttsx3"""
    print("\n" + "="*60)
    print("测试 pyttsx3 (完全离线)")
    print("="*60)
    
    try:
        import pyttsx3
        
        engine = pyttsx3.init()
        engine.setProperty('rate', 150)
        engine.setProperty('volume', 1.0)
        
        # 获取可用语音
        voices = engine.getProperty('voices')
        print(f"\n可用语音数量: {len(voices)}")
        
        for i, voice in enumerate(voices[:5]):  # 只显示前5个
            print(f"\n语音 {i+1}:")
            print(f"  名称: {voice.name}")
            print(f"  ID: {voice.id}")
            print(f"  语言: {voice.languages}")
        
        # 测试合成
        test_texts = {
            "中文": "你好，我是人工智能语音助手",
            "English": "Hello, I am an AI voice assistant",
            "Tiếng Việt": "Xin chào, tôi là trợ lý giọng nói AI"
        }
        
        print("\n开始语音合成测试...")
        for lang, text in test_texts.items():
            print(f"\n测试 {lang}: {text}")
            
            output_file = f"test_pyttsx3_{lang}.wav"
            
            start_time = time.time()
            engine.save_to_file(text, output_file)
            engine.runAndWait()
            elapsed = time.time() - start_time
            
            if os.path.exists(output_file):
                file_size = os.path.getsize(output_file)
                print(f"  ✓ 生成成功")
                print(f"  文件大小: {file_size} bytes")
                print(f"  耗时: {elapsed:.2f} 秒")
            else:
                print(f"  ✗ 生成失败")
        
        print("\n✅ pyttsx3 测试完成")
        return True
        
    except Exception as e:
        print(f"\n❌ pyttsx3 测试失败: {e}")
        return False

def test_coqui_tts():
    """测试 Coqui TTS"""
    print("\n" + "="*60)
    print("测试 Coqui TTS (高质量离线)")
    print("="*60)
    
    try:
        from TTS.api import TTS
        
        print("\n加载模型...")
        start_load = time.time()
        tts = TTS(model_name="tts_models/multilingual/multi-dataset/xtts_v2")
        load_time = time.time() - start_load
        print(f"✓ 模型加载完成 (耗时: {load_time:.2f} 秒)")
        
        # 测试合成
        test_cases = [
            ("中文", "你好，我是人工智能语音助手", "zh-cn"),
            ("English", "Hello, I am an AI voice assistant", "en"),
            ("Tiếng Việt", "Xin chào, tôi là trợ lý giọng nói AI", "vi")
        ]
        
        print("\n开始语音合成测试...")
        for lang_name, text, lang_code in test_cases:
            print(f"\n测试 {lang_name}: {text}")
            
            output_file = f"test_coqui_{lang_name}.wav"
            
            start_time = time.time()
            tts.tts_to_file(
                text=text,
                file_path=output_file,
                language=lang_code
            )
            elapsed = time.time() - start_time
            
            if os.path.exists(output_file):
                file_size = os.path.getsize(output_file)
                print(f"  ✓ 生成成功")
                print(f"  文件大小: {file_size} bytes")
                print(f"  耗时: {elapsed:.2f} 秒")
            else:
                print(f"  ✗ 生成失败")
        
        print("\n✅ Coqui TTS 测试完成")
        return True
        
    except Exception as e:
        print(f"\n❌ Coqui TTS 测试失败: {e}")
        print("提示: 首次运行需要下载模型（约 1.8GB）")
        return False

def test_edge_tts():
    """测试 Edge TTS"""
    print("\n" + "="*60)
    print("测试 Edge TTS (在线，需要网络)")
    print("="*60)
    
    try:
        import edge_tts
        import asyncio
        
        async def synthesize():
            test_cases = [
                ("中文", "你好，我是人工智能语音助手", "zh-CN-XiaoxiaoNeural"),
                ("English", "Hello, I am an AI voice assistant", "en-US-JennyNeural"),
                ("Tiếng Việt", "Xin chào, tôi là trợ lý giọng nói AI", "vi-VN-HoaiMyNeural")
            ]
            
            print("\n开始语音合成测试...")
            for lang_name, text, voice in test_cases:
                print(f"\n测试 {lang_name}: {text}")
                
                output_file = f"test_edge_{lang_name}.mp3"
                
                start_time = time.time()
                communicate = edge_tts.Communicate(text, voice)
                await communicate.save(output_file)
                elapsed = time.time() - start_time
                
                if os.path.exists(output_file):
                    file_size = os.path.getsize(output_file)
                    print(f"  ✓ 生成成功")
                    print(f"  文件大小: {file_size} bytes")
                    print(f"  耗时: {elapsed:.2f} 秒")
                else:
                    print(f"  ✗ 生成失败")
        
        asyncio.run(synthesize())
        
        print("\n✅ Edge TTS 测试完成")
        return True
        
    except Exception as e:
        print(f"\n❌ Edge TTS 测试失败: {e}")
        print("提示: Edge TTS 需要网络连接")
        return False

def main():
    """主测试函数"""
    print("\n" + "="*60)
    print("TTS 引擎对比测试")
    print("TTS Engine Comparison Test")
    print("="*60)
    
    results = {}
    
    # 测试 pyttsx3
    print("\n[1/3] 测试 pyttsx3...")
    results['pyttsx3'] = test_pyttsx3()
    
    # 测试 Coqui TTS
    print("\n[2/3] 测试 Coqui TTS...")
    results['coqui'] = test_coqui_tts()
    
    # 测试 Edge TTS
    print("\n[3/3] 测试 Edge TTS...")
    results['edge'] = test_edge_tts()
    
    # 总结
    print("\n\n" + "="*60)
    print("测试总结 / Test Summary")
    print("="*60)
    
    print("\n引擎状态:")
    for engine, success in results.items():
        status = "✅ 可用" if success else "❌ 不可用"
        print(f"  {engine}: {status}")
    
    print("\n推荐方案:")
    if results.get('edge'):
        print("  🥇 Edge TTS - 最佳质量（需要网络）")
    if results.get('coqui'):
        print("  🥈 Coqui TTS - 高质量离线方案")
    if results.get('pyttsx3'):
        print("  🥉 pyttsx3 - 简单快速的离线方案")
    
    print("\n生成的测试文件:")
    for file in os.listdir('.'):
        if file.startswith('test_') and (file.endswith('.wav') or file.endswith('.mp3')):
            size = os.path.getsize(file)
            print(f"  {file} ({size} bytes)")
    
    print("\n提示: 可以播放生成的音频文件来比较质量")
    print("="*60)

if __name__ == "__main__":
    main()

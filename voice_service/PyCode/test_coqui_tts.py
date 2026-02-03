"""
Coqui TTS 快速测试脚本
Quick test script for Coqui TTS
"""
import os
import time
import sys

def check_installation():
    """检查安装"""
    print("\n" + "="*60)
    print("检查 Coqui TTS 安装")
    print("Checking Coqui TTS Installation")
    print("="*60)
    
    try:
        from TTS.api import TTS
        print("✓ Coqui TTS 已安装")
        return True
    except ImportError as e:
        print("✗ Coqui TTS 未安装")
        print(f"错误: {e}")
        print("\n请运行以下命令安装:")
        print("pip install TTS==0.22.0")
        return False

def check_cuda():
    """检查 CUDA 支持"""
    print("\n" + "="*60)
    print("检查 GPU 支持")
    print("Checking GPU Support")
    print("="*60)
    
    try:
        import torch
        cuda_available = torch.cuda.is_available()
        
        if cuda_available:
            print(f"✓ CUDA 可用")
            print(f"  GPU 名称: {torch.cuda.get_device_name(0)}")
            print(f"  CUDA 版本: {torch.version.cuda}")
            print(f"  显存: {torch.cuda.get_device_properties(0).total_memory / 1024**3:.2f} GB")
        else:
            print("⚠ CUDA 不可用，将使用 CPU")
            print("  提示: 安装 CUDA 版本的 PyTorch 可以加速")
        
        return cuda_available
    except Exception as e:
        print(f"⚠ 无法检查 CUDA: {e}")
        return False

def download_model():
    """下载模型"""
    print("\n" + "="*60)
    print("下载/检查模型")
    print("Downloading/Checking Model")
    print("="*60)
    
    try:
        from TTS.api import TTS
        
        print("\n正在加载模型...")
        print("模型: tts_models/multilingual/multi-dataset/xtts_v2")
        print("大小: 约 1.8GB")
        print("首次运行会自动下载，请耐心等待...")
        print()
        
        start_time = time.time()
        tts = TTS(model_name="tts_models/multilingual/multi-dataset/xtts_v2")
        elapsed = time.time() - start_time
        
        print(f"\n✓ 模型加载完成 (耗时: {elapsed:.2f} 秒)")
        
        # 显示支持的语言
        print(f"\n支持的语言数量: {len(tts.languages)}")
        print("主要语言:", ", ".join(list(tts.languages)[:10]))
        
        return tts
    except Exception as e:
        print(f"\n✗ 模型加载失败: {e}")
        return None

def test_synthesis(tts):
    """测试语音合成"""
    print("\n" + "="*60)
    print("测试语音合成")
    print("Testing Speech Synthesis")
    print("="*60)
    
    test_cases = [
        {
            "name": "中文",
            "text": "你好，我是人工智能语音助手。这是使用 Coqui TTS 生成的高质量语音。",
            "language": "zh-cn",
            "file": "test_coqui_zh.wav"
        },
        {
            "name": "English",
            "text": "Hello, I am an AI voice assistant. This is high-quality speech generated using Coqui TTS.",
            "language": "en",
            "file": "test_coqui_en.wav"
        },
        {
            "name": "Tiếng Việt",
            "text": "Xin chào, tôi là trợ lý giọng nói AI. Đây là giọng nói chất lượng cao được tạo bằng Coqui TTS.",
            "language": "vi",
            "file": "test_coqui_vi.wav"
        }
    ]
    
    results = []
    
    for test in test_cases:
        print(f"\n测试 {test['name']}:")
        print(f"  文本: {test['text'][:50]}...")
        print(f"  语言: {test['language']}")
        
        try:
            start_time = time.time()
            
            tts.tts_to_file(
                text=test['text'],
                file_path=test['file'],
                language=test['language']
            )
            
            elapsed = time.time() - start_time
            
            if os.path.exists(test['file']):
                file_size = os.path.getsize(test['file'])
                print(f"  ✓ 生成成功")
                print(f"  文件: {test['file']}")
                print(f"  大小: {file_size:,} bytes ({file_size/1024:.2f} KB)")
                print(f"  耗时: {elapsed:.2f} 秒")
                print(f"  速度: {len(test['text'])/elapsed:.2f} 字符/秒")
                
                results.append({
                    "name": test['name'],
                    "success": True,
                    "time": elapsed,
                    "size": file_size
                })
            else:
                print(f"  ✗ 文件未生成")
                results.append({"name": test['name'], "success": False})
                
        except Exception as e:
            print(f"  ✗ 生成失败: {e}")
            results.append({"name": test['name'], "success": False})
    
    return results

def test_voice_cloning(tts):
    """测试语音克隆（可选）"""
    print("\n" + "="*60)
    print("测试语音克隆（可选）")
    print("Testing Voice Cloning (Optional)")
    print("="*60)
    
    # 检查是否有参考音频
    reference_files = [
        "reference_voice.wav",
        "voice_service/reference_voice.wav",
        "../reference_voice.wav"
    ]
    
    reference_audio = None
    for ref_file in reference_files:
        if os.path.exists(ref_file):
            reference_audio = ref_file
            break
    
    if not reference_audio:
        print("\n⚠ 未找到参考音频文件")
        print("跳过语音克隆测试")
        print("\n提示: 创建 reference_voice.wav 文件来测试语音克隆")
        return
    
    print(f"\n找到参考音频: {reference_audio}")
    print("正在克隆语音...")
    
    try:
        start_time = time.time()
        
        tts.tts_to_file(
            text="这是使用语音克隆技术生成的声音",
            file_path="test_coqui_cloned.wav",
            speaker_wav=reference_audio,
            language="zh-cn"
        )
        
        elapsed = time.time() - start_time
        
        if os.path.exists("test_coqui_cloned.wav"):
            file_size = os.path.getsize("test_coqui_cloned.wav")
            print(f"\n✓ 语音克隆成功")
            print(f"  文件: test_coqui_cloned.wav")
            print(f"  大小: {file_size:,} bytes")
            print(f"  耗时: {elapsed:.2f} 秒")
        else:
            print("\n✗ 语音克隆失败")
            
    except Exception as e:
        print(f"\n✗ 语音克隆失败: {e}")

def print_summary(results, has_cuda):
    """打印总结"""
    print("\n\n" + "="*60)
    print("测试总结")
    print("Test Summary")
    print("="*60)
    
    print("\n环境信息:")
    print(f"  GPU 加速: {'✓ 已启用' if has_cuda else '✗ 未启用 (使用 CPU)'}")
    
    print("\n合成测试结果:")
    for result in results:
        if result['success']:
            status = "✓ 通过"
            print(f"  {result['name']}: {status}")
            print(f"    耗时: {result['time']:.2f} 秒")
            print(f"    大小: {result['size']/1024:.2f} KB")
        else:
            print(f"  {result['name']}: ✗ 失败")
    
    success_count = sum(1 for r in results if r['success'])
    total_count = len(results)
    
    print(f"\n总计: {success_count}/{total_count} 通过")
    
    if success_count == total_count:
        print("\n🎉 所有测试通过！")
        print("\n生成的音频文件:")
        for result in results:
            if result['success']:
                print(f"  - test_coqui_{result['name'].lower()}.wav")
        print("\n提示: 播放这些文件来体验 Coqui TTS 的语音质量")
    else:
        print("\n⚠ 部分测试失败，请检查错误信息")
    
    print("\n性能建议:")
    if not has_cuda:
        print("  - 安装 CUDA 版本的 PyTorch 可以显著提升速度")
        print("    pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118")
    
    avg_time = sum(r.get('time', 0) for r in results if r['success']) / max(success_count, 1)
    if avg_time > 5:
        print(f"  - 当前平均合成时间: {avg_time:.2f} 秒")
        print("  - 考虑使用更小的模型或升级硬件")

def main():
    """主函数"""
    print("\n" + "="*60)
    print("Coqui TTS 测试工具")
    print("Coqui TTS Test Tool")
    print("="*60)
    
    # 1. 检查安装
    if not check_installation():
        sys.exit(1)
    
    # 2. 检查 CUDA
    has_cuda = check_cuda()
    
    # 3. 下载模型
    tts = download_model()
    if not tts:
        sys.exit(1)
    
    # 4. 测试合成
    results = test_synthesis(tts)
    
    # 5. 测试语音克隆（可选）
    test_voice_cloning(tts)
    
    # 6. 打印总结
    print_summary(results, has_cuda)
    
    print("\n" + "="*60)
    print("测试完成！")
    print("="*60)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n测试被用户中断")
    except Exception as e:
        print(f"\n\n测试失败: {e}")
        import traceback
        traceback.print_exc()

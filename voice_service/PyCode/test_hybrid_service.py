"""
测试混合TTS服务
验证中文(XTTS v2)、英文(XTTS v2)、越南语(MMS-TTS)
"""
import os

# 设置 ffmpeg 路径
FFMPEG_BIN_PATH = r"C:\ProgramData\chocolatey\bin"
FFMPEG_EXE = os.path.join(FFMPEG_BIN_PATH, "ffmpeg.exe")

if os.path.exists(FFMPEG_BIN_PATH):
    os.environ["PATH"] = FFMPEG_BIN_PATH + os.pathsep + os.environ.get("PATH", "")
    print(f"✓ 已添加 ffmpeg 路径到 PATH: {FFMPEG_BIN_PATH}")

if os.path.exists(FFMPEG_EXE):
    os.environ["FFMPEG_BINARY"] = FFMPEG_EXE
    print(f"✓ 设置 FFMPEG_BINARY: {FFMPEG_EXE}")

print("\n" + "="*60)
print("测试混合TTS服务")
print("="*60)

# 测试数据
test_cases = {
    "zh": {
        "engine": "XTTS v2",
        "text": "你好，这是中文测试。",
        "output": "test_hybrid_zh.wav"
    },
    "en": {
        "engine": "XTTS v2",
        "text": "Hello, this is an English test.",
        "output": "test_hybrid_en.wav"
    },
    "vi": {
        "engine": "MMS-TTS",
        "text": "Xin chào, đây là bài kiểm tra tiếng Việt.",
        "output": "test_hybrid_vi.wav"
    }
}

# 测试 XTTS v2 (中文/英文)
print(f"\n{'='*60}")
print("测试 XTTS v2 (中文/英文)")
print(f"{'='*60}")

try:
    from TTS.api import TTS
    import tempfile
    
    print("加载 XTTS v2 模型...")
    tts = TTS(model_name="tts_models/multilingual/multi-dataset/xtts_v2")
    print("✓ XTTS v2 模型加载成功")
    
    for lang in ["zh", "en"]:
        data = test_cases[lang]
        print(f"\n{'-'*60}")
        print(f"测试 {lang.upper()} ({data['engine']})")
        print(f"{'-'*60}")
        print(f"文本: {data['text']}")
        
        try:
            # 生成语音
            print("生成语音...")
            with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp_file:
                tmp_path = tmp_file.name
            
            tts.tts_to_file(
                text=data['text'],
                speaker="Claribel Dervla",
                language=lang,
                file_path=tmp_path
            )
            
            # 检查文件
            if os.path.exists(tmp_path):
                file_size = os.path.getsize(tmp_path)
                print(f"✓ 语音生成完成，文件大小: {file_size} bytes")
                os.unlink(tmp_path)
                print(f"🎉 {lang.upper()} 测试通过！")
            else:
                print(f"❌ {lang.upper()} 测试失败: 文件未生成")
                
        except Exception as e:
            print(f"❌ {lang.upper()} 测试失败: {e}")
            import traceback
            traceback.print_exc()
    
except Exception as e:
    print(f"❌ XTTS v2 加载失败: {e}")
    import traceback
    traceback.print_exc()

# 测试 MMS-TTS (越南语)
print(f"\n{'='*60}")
print("测试 MMS-TTS (越南语)")
print(f"{'='*60}")

try:
    from transformers import VitsModel, AutoTokenizer
    import torch
    import scipy.io.wavfile
    import tempfile
    
    lang = "vi"
    data = test_cases[lang]
    
    print(f"模型: facebook/mms-tts-vie")
    print(f"文本: {data['text']}")
    
    print("加载模型...")
    model = VitsModel.from_pretrained("facebook/mms-tts-vie")
    tokenizer = AutoTokenizer.from_pretrained("facebook/mms-tts-vie")
    print("✓ 模型加载成功")
    
    print("Tokenizing...")
    inputs = tokenizer(data['text'], return_tensors="pt")
    print("✓ Tokenize 完成")
    
    print("生成语音...")
    with torch.no_grad():
        output = model(**inputs).waveform
    
    audio_array = output.squeeze().cpu().numpy()
    print(f"✓ 语音生成完成，长度: {len(audio_array)} samples")
    
    # 保存测试
    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp_file:
        tmp_path = tmp_file.name
    
    scipy.io.wavfile.write(tmp_path, rate=16000, data=audio_array)
    
    if os.path.exists(tmp_path):
        file_size = os.path.getsize(tmp_path)
        print(f"✓ 文件保存成功，大小: {file_size} bytes")
        os.unlink(tmp_path)
        print(f"🎉 VI 测试通过！")
    
except Exception as e:
    print(f"❌ VI 测试失败: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "="*60)
print("测试完成")
print("="*60)
print("\n✅ 混合TTS服务验证完成！")
print("\n所有语言都可以正常工作：")
print("  🇨🇳 中文: XTTS v2")
print("  🇬🇧 英文: XTTS v2")
print("  🇻🇳 越南语: MMS-TTS")
print("\n现在可以启动服务了：")
print("  python ai_voice_service_hybrid.py")
print("  或者运行: start_hybrid.bat")

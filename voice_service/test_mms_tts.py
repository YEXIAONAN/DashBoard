"""
测试 Facebook MMS-TTS 模型
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

from transformers import VitsModel, AutoTokenizer
import torch
import scipy.io.wavfile

print("\n" + "="*60)
print("测试 Facebook MMS-TTS")
print("="*60)

# 测试数据
test_cases = {
    "zh": {
        "model": "facebook/mms-tts-yue",
        "text": "你好，这是中文测试。",
        "output": "test_mms_zh.wav"
    },
    "en": {
        "model": "facebook/mms-tts-eng",
        "text": "Hello, this is an English test.",
        "output": "test_mms_en.wav"
    },
    "vi": {
        "model": "facebook/mms-tts-vie",
        "text": "Xin chào, đây là bài kiểm tra tiếng Việt.",
        "output": "test_mms_vi.wav"
    }
}

for lang, data in test_cases.items():
    print(f"\n{'='*60}")
    print(f"测试 {lang.upper()}")
    print(f"{'='*60}")
    print(f"模型: {data['model']}")
    print(f"文本: {data['text']}")
    
    try:
        # 加载模型
        print("加载模型...")
        model = VitsModel.from_pretrained(data['model'])
        tokenizer = AutoTokenizer.from_pretrained(data['model'])
        print("✓ 模型加载成功")
        
        # Tokenize
        print("Tokenizing...")
        inputs = tokenizer(data['text'], return_tensors="pt")
        print("✓ Tokenize 完成")
        
        # 生成语音
        print("生成语音...")
        with torch.no_grad():
            output = model(**inputs).waveform
        
        # 转换为 numpy 数组
        audio_array = output.squeeze().cpu().numpy()
        print(f"✓ 语音生成完成，长度: {len(audio_array)} samples")
        
        # 保存为 WAV 文件
        print(f"保存到: {data['output']}")
        scipy.io.wavfile.write(data['output'], rate=16000, data=audio_array)
        print(f"✓ 文件保存成功")
        
        # 清理
        if os.path.exists(data['output']):
            file_size = os.path.getsize(data['output'])
            print(f"✓ 文件大小: {file_size} bytes")
            os.unlink(data['output'])
            print("✓ 测试文件已清理")
        
        print(f"🎉 {lang.upper()} 测试通过！")
        
    except Exception as e:
        print(f"❌ {lang.upper()} 测试失败: {e}")
        import traceback
        traceback.print_exc()

print("\n" + "="*60)
print("测试完成")
print("="*60)

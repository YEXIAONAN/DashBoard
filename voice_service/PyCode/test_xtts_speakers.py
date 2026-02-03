"""
测试 XTTS v2 说话人功能
"""
import os
import torch

# 设置 ffmpeg 路径
FFMPEG_BIN_PATH = r"C:\ProgramData\chocolatey\bin"
FFMPEG_EXE = os.path.join(FFMPEG_BIN_PATH, "ffmpeg.exe")

if os.path.exists(FFMPEG_BIN_PATH):
    os.environ["PATH"] = FFMPEG_BIN_PATH + os.pathsep + os.environ.get("PATH", "")
    print(f"✓ 已添加 ffmpeg 路径到 PATH: {FFMPEG_BIN_PATH}")

if os.path.exists(FFMPEG_EXE):
    os.environ["FFMPEG_BINARY"] = FFMPEG_EXE
    print(f"✓ 设置 FFMPEG_BINARY: {FFMPEG_EXE}")

# 添加安全全局变量
try:
    from TTS.tts.configs.xtts_config import XttsConfig
    from TTS.tts.models.xtts import XttsAudioConfig
    torch.serialization.add_safe_globals([XttsConfig, XttsAudioConfig])
    print("✓ 已添加安全全局变量")
except Exception as e:
    print(f"⚠️ 添加安全全局变量失败: {e}")

from TTS.api import TTS

print("\n" + "="*60)
print("初始化 XTTS v2 模型...")
print("="*60)

tts = TTS(model_name="tts_models/multilingual/multi-dataset/xtts_v2")

print("\n" + "="*60)
print("检查模型属性...")
print("="*60)

# 检查所有可能的属性
print(f"\n1. tts.speakers: {tts.speakers if hasattr(tts, 'speakers') else 'N/A'}")
print(f"2. tts.languages: {tts.languages if hasattr(tts, 'languages') else 'N/A'}")

if hasattr(tts, 'model'):
    print(f"\n3. tts.model 存在")
    if hasattr(tts.model, 'speaker_manager'):
        print(f"   - tts.model.speaker_manager 存在")
        sm = tts.model.speaker_manager
        if hasattr(sm, 'speaker_names'):
            print(f"   - speaker_names: {sm.speaker_names}")
        if hasattr(sm, 'speakers'):
            print(f"   - speakers: {sm.speakers}")
        if hasattr(sm, 'num_speakers'):
            print(f"   - num_speakers: {sm.num_speakers}")

if hasattr(tts, 'synthesizer'):
    print(f"\n4. tts.synthesizer 存在")
    if hasattr(tts.synthesizer, 'tts_model'):
        print(f"   - tts.synthesizer.tts_model 存在")
        model = tts.synthesizer.tts_model
        if hasattr(model, 'speaker_manager'):
            print(f"   - speaker_manager 存在")
            sm = model.speaker_manager
            if hasattr(sm, 'speaker_names'):
                print(f"   - speaker_names: {sm.speaker_names}")

print("\n" + "="*60)
print("测试语音合成...")
print("="*60)

test_texts = {
    "zh-cn": "你好，这是中文测试。",
    "en": "Hello, this is an English test.",
    "vi": "Xin chào, đây là bài kiểm tra tiếng Việt."
}

for lang, text in test_texts.items():
    print(f"\n测试语言: {lang}")
    print(f"文本: {text}")
    
    output_file = f"test_output_{lang}.wav"
    
    try:
        # 方法1: 不指定 speaker（看是否有默认值）
        print("  尝试方法1: 不指定 speaker...")
        tts.tts_to_file(
            text=text,
            file_path=output_file,
            language=lang
        )
        print(f"  ✓ 成功！文件: {output_file}")
        if os.path.exists(output_file):
            os.unlink(output_file)
        continue
    except Exception as e:
        print(f"  ✗ 失败: {e}")
    
    try:
        # 方法2: 使用 speaker="Claribel Dervla"
        print("  尝试方法2: speaker='Claribel Dervla'...")
        tts.tts_to_file(
            text=text,
            file_path=output_file,
            speaker="Claribel Dervla",
            language=lang
        )
        print(f"  ✓ 成功！文件: {output_file}")
        if os.path.exists(output_file):
            os.unlink(output_file)
        continue
    except Exception as e:
        print(f"  ✗ 失败: {e}")
    
    try:
        # 方法3: 使用 speaker_wav（需要参考音频）
        print("  尝试方法3: 使用 speaker_wav...")
        # 这需要一个参考音频文件，暂时跳过
        print("  ⊘ 跳过（需要参考音频文件）")
    except Exception as e:
        print(f"  ✗ 失败: {e}")

print("\n" + "="*60)
print("测试完成")
print("="*60)

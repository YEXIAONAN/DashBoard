"""
测试 viXTTS 模型下载
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

from huggingface_hub import hf_hub_download, list_repo_files
import torch

print("\n" + "="*60)
print("检查 viXTTS 仓库文件...")
print("="*60)

try:
    files = list_repo_files("capleaf/viXTTS")
    print(f"\n找到 {len(files)} 个文件:")
    for f in files:
        print(f"  - {f}")
except Exception as e:
    print(f"❌ 错误: {e}")

print("\n" + "="*60)
print("尝试下载模型文件...")
print("="*60)

try:
    # 添加安全全局变量
    try:
        from TTS.tts.configs.xtts_config import XttsConfig
        from TTS.tts.models.xtts import XttsAudioConfig
        torch.serialization.add_safe_globals([XttsConfig, XttsAudioConfig])
        print("✓ 已添加安全全局变量")
    except Exception as e:
        print(f"⚠️ 添加安全全局变量失败: {e}")
    
    # 下载配置文件
    print("\n下载 config.json...")
    config_path = hf_hub_download(
        repo_id="capleaf/viXTTS",
        filename="config.json"
    )
    print(f"✓ 配置文件: {config_path}")
    
    # 下载模型文件
    print("\n下载 model.pth...")
    model_path = hf_hub_download(
        repo_id="capleaf/viXTTS",
        filename="model.pth"
    )
    print(f"✓ 模型文件: {model_path}")
    
    # 下载 vocab 文件
    print("\n下载 vocab.json...")
    vocab_path = hf_hub_download(
        repo_id="capleaf/viXTTS",
        filename="vocab.json"
    )
    print(f"✓ 词汇文件: {vocab_path}")
    
    print("\n" + "="*60)
    print("尝试加载模型...")
    print("="*60)
    
    from TTS.api import TTS
    
    # 使用本地路径加载（model_path 应该是目录）
    model_dir = os.path.dirname(config_path)
    
    tts = TTS(
        model_path=model_dir,  # 使用目录而不是文件
        config_path=config_path,
        vocoder_path=None,
        vocoder_config_path=None,
        progress_bar=False,
        gpu=False
    )
    
    print("✓ 模型加载成功！")
    
    # 检查语言支持
    if hasattr(tts, 'languages'):
        print(f"\n支持的语言: {tts.languages}")
    
    # 测试越南语
    print("\n" + "="*60)
    print("测试越南语合成...")
    print("="*60)
    
    # viXTTS 需要参考音频进行语音克隆
    # 下载示例音频
    print("下载参考音频...")
    speaker_wav = hf_hub_download(
        repo_id="capleaf/viXTTS",
        filename="vi_sample.wav"
    )
    print(f"✓ 参考音频: {speaker_wav}")
    
    test_text = "Xin chào, đây là bài kiểm tra tiếng Việt."
    output_file = "test_vixtts_vi.wav"
    
    tts.tts_to_file(
        text=test_text,
        file_path=output_file,
        speaker_wav=speaker_wav,  # 使用参考音频
        language="vi"
    )
    
    print(f"✓ 越南语测试成功！文件: {output_file}")
    
    # 清理
    if os.path.exists(output_file):
        os.unlink(output_file)
    
    print("\n🎉 所有测试通过！viXTTS 可以正常使用！")
    
except Exception as e:
    print(f"\n❌ 错误: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "="*60)
print("测试完成")
print("="*60)

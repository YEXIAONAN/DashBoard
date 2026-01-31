"""
测试 Coqui TTS 可用的越南语模型
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

from TTS.api import TTS
from TTS.utils.manage import ModelManager

print("\n" + "="*60)
print("查询所有可用的 TTS 模型...")
print("="*60)

# 获取所有模型列表
manager = ModelManager()
models = manager.list_tts_models()

print(f"\n总共有 {len(models)} 个模型\n")

# 筛选越南语相关的模型
vietnamese_models = [m for m in models if 'vi' in m.lower() or 'viet' in m.lower()]

print("="*60)
print("越南语相关模型:")
print("="*60)

if vietnamese_models:
    for i, model in enumerate(vietnamese_models, 1):
        print(f"{i}. {model}")
else:
    print("❌ 没有找到越南语专用模型")

print("\n" + "="*60)
print("多语言模型（可能支持越南语）:")
print("="*60)

multilingual_models = [m for m in models if 'multilingual' in m.lower()]
for i, model in enumerate(multilingual_models[:10], 1):
    print(f"{i}. {model}")

print("\n" + "="*60)
print("检查 XTTS v2 支持的语言...")
print("="*60)

try:
    tts = TTS(model_name="tts_models/multilingual/multi-dataset/xtts_v2")
    if hasattr(tts, 'languages'):
        print(f"XTTS v2 支持的语言: {tts.languages}")
    else:
        print("无法获取语言列表")
except Exception as e:
    print(f"错误: {e}")

print("\n" + "="*60)
print("完成")
print("="*60)

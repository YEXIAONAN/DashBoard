"""
检查当前版本
"""
import sys

print("="*60)
print("当前环境版本检查")
print("="*60)

try:
    import torch
    print(f"✓ PyTorch: {torch.__version__}")
    major, minor = torch.__version__.split('.')[:2]
    if int(major) == 2 and int(minor) >= 6:
        print(f"  ⚠️ 版本过高！Coqui TTS 不兼容 PyTorch 2.6+")
        print(f"  建议降级到 2.5.x")
    else:
        print(f"  ✓ 版本兼容")
except ImportError:
    print("✗ PyTorch 未安装")

try:
    import transformers
    print(f"✓ transformers: {transformers.__version__}")
    if transformers.__version__ != "4.33.0":
        print(f"  ⚠️ 需要 4.33.0 版本")
except ImportError:
    print("✗ transformers 未安装")

try:
    import TTS
    print(f"✓ TTS: {TTS.__version__}")
except ImportError:
    print("✗ TTS 未安装")

try:
    import tokenizers
    print(f"✓ tokenizers: {tokenizers.__version__}")
except ImportError:
    print("✗ tokenizers 未安装")

print("\n" + "="*60)
print("推荐版本:")
print("="*60)
print("PyTorch:      2.0.0 - 2.5.x")
print("transformers: 4.33.0")
print("tokenizers:   0.13.3")
print("TTS:          0.22.0")

print("\n" + "="*60)
print("修复命令:")
print("="*60)
print("pip install \"torch>=2.0.0,<2.6.0\" --upgrade")
print("pip install transformers==4.33.0 tokenizers==0.13.3")
print("="*60)

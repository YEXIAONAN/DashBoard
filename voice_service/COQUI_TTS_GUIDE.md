# Coqui TTS 完整配置指南
# Complete Coqui TTS Setup Guide

## 🎯 概述 / Overview

本指南将帮助你配置和使用 Coqui TTS 作为完全离线的高质量语音合成方案。

This guide will help you configure and use Coqui TTS as a fully offline, high-quality text-to-speech solution.

## ✨ Coqui TTS 优势

- ✅ **高质量语音**：接近真人发音
- ✅ **完全离线**：无需网络连接
- ✅ **多语言支持**：100+ 语言
- ✅ **语音克隆**：可以克隆任何声音
- ✅ **开源免费**：Apache 2.0 许可证
- ✅ **GPU 加速**：支持 CUDA 加速

## 📋 系统要求

### 最低配置
- CPU: Intel i5 或同等性能
- RAM: 4GB
- 存储: 2GB 可用空间
- Python: 3.8+

### 推荐配置
- CPU: Intel i7 或更好
- RAM: 8GB+
- GPU: NVIDIA GPU (支持 CUDA)
- 存储: 5GB 可用空间
- Python: 3.9+

## 🚀 快速安装

### 方法 1: 使用启动脚本（推荐）

```bash
cd voice_service

# Windows
start_coqui_tts.bat

# 脚本会自动：
# 1. 检查 Python 环境
# 2. 安装所有依赖
# 3. 下载 Coqui TTS 模型
# 4. 启动服务
```

### 方法 2: 手动安装

```bash
cd voice_service

# 1. 安装基础依赖
pip install -r requirements_fully_offline.txt

# 2. 安装 Coqui TTS
pip install TTS==0.22.0

# 3. 下载模型（首次运行）
python -c "from TTS.api import TTS; TTS(model_name='tts_models/multilingual/multi-dataset/xtts_v2')"

# 4. 启动服务
python ai_voice_service_fully_offline.py
```

## 📦 模型下载

### 自动下载（推荐）

首次运行时会自动下载模型：

```bash
python ai_voice_service_fully_offline.py
```

下载信息：
- 模型大小：约 1.8GB
- 下载时间：10-30 分钟（取决于网络）
- 存储位置：`~/.local/share/tts/`

### 手动下载

如果自动下载失败，可以手动下载：

```bash
# 方法 1: 使用 Python
python -c "from TTS.api import TTS; TTS(model_name='tts_models/multilingual/multi-dataset/xtts_v2')"

# 方法 2: 从 GitHub 下载
# 访问：https://github.com/coqui-ai/TTS/releases
# 下载模型文件到：~/.local/share/tts/
```

### 查看已下载的模型

```bash
python -c "from TTS.api import TTS; print(TTS().list_models())"
```

## 🔧 配置选项

### 1. 选择模型

编辑 `ai_voice_service_fully_offline.py`：

```python
def load_coqui_tts():
    global coqui_tts
    if coqui_tts is None:
        from TTS.api import TTS
        
        # 多语言模型（推荐）
        coqui_tts = TTS(model_name="tts_models/multilingual/multi-dataset/xtts_v2")
        
        # 或选择其他模型：
        # 中文专用（更快）
        # coqui_tts = TTS(model_name="tts_models/zh-CN/baker/tacotron2-DDC-GST")
        
        # 英文专用（更快）
        # coqui_tts = TTS(model_name="tts_models/en/ljspeech/tacotron2-DDC")
```

### 2. GPU 加速

如果有 NVIDIA GPU：

```bash
# 安装 CUDA 版本的 PyTorch
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118

# Coqui TTS 会自动检测并使用 GPU
```

验证 GPU 使用：

```python
import torch
print(f"CUDA 可用: {torch.cuda.is_available()}")
print(f"GPU 名称: {torch.cuda.get_device_name(0) if torch.cuda.is_available() else 'N/A'}")
```

### 3. 调整语音参数

```python
async def text_to_speech_coqui(text: str, language: str = "zh") -> bytes:
    tts = load_coqui_tts()
    
    # 基础合成
    tts.tts_to_file(
        text=text,
        file_path=tmp_path,
        language=language
    )
    
    # 使用语音克隆（需要参考音频）
    tts.tts_to_file(
        text=text,
        file_path=tmp_path,
        speaker_wav="reference_voice.wav",  # 参考音频
        language=language
    )
```

## 🎨 支持的语言

### 完整支持（XTTS v2 模型）

| 语言 | 代码 | 质量 |
|------|------|------|
| 中文 | zh-cn | ⭐⭐⭐⭐⭐ |
| 英文 | en | ⭐⭐⭐⭐⭐ |
| 西班牙语 | es | ⭐⭐⭐⭐⭐ |
| 法语 | fr | ⭐⭐⭐⭐⭐ |
| 德语 | de | ⭐⭐⭐⭐⭐ |
| 意大利语 | it | ⭐⭐⭐⭐⭐ |
| 葡萄牙语 | pt | ⭐⭐⭐⭐⭐ |
| 波兰语 | pl | ⭐⭐⭐⭐⭐ |
| 土耳其语 | tr | ⭐⭐⭐⭐⭐ |
| 俄语 | ru | ⭐⭐⭐⭐⭐ |
| 荷兰语 | nl | ⭐⭐⭐⭐⭐ |
| 捷克语 | cs | ⭐⭐⭐⭐⭐ |
| 阿拉伯语 | ar | ⭐⭐⭐⭐⭐ |
| 日语 | ja | ⭐⭐⭐⭐ |
| 韩语 | ko | ⭐⭐⭐⭐ |
| 越南语 | vi | ⭐⭐⭐⭐ |

### 查看所有支持的语言

```python
from TTS.api import TTS
tts = TTS(model_name="tts_models/multilingual/multi-dataset/xtts_v2")
print(tts.languages)
```

## 🎤 语音克隆功能

Coqui TTS 支持语音克隆，可以模仿任何声音！

### 准备参考音频

1. **录制参考音频**
   - 时长：5-10 秒
   - 格式：WAV 或 MP3
   - 质量：清晰，无背景噪音
   - 内容：自然说话，不要朗读

2. **使用语音克隆**

```python
from TTS.api import TTS

tts = TTS(model_name="tts_models/multilingual/multi-dataset/xtts_v2")

# 克隆语音
tts.tts_to_file(
    text="你好，这是克隆的声音",
    file_path="output.wav",
    speaker_wav="reference_voice.wav",  # 参考音频
    language="zh-cn"
)
```

### 在服务中使用语音克隆

修改 `ai_voice_service_fully_offline.py`：

```python
async def text_to_speech_coqui(text: str, language: str = "zh") -> bytes:
    tts = load_coqui_tts()
    
    # 设置参考音频路径
    reference_audio = "voice_service/reference_voices/default.wav"
    
    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp_file:
        tmp_path = tmp_file.name
    
    try:
        if os.path.exists(reference_audio):
            # 使用语音克隆
            tts.tts_to_file(
                text=text,
                file_path=tmp_path,
                speaker_wav=reference_audio,
                language=language_map.get(language, "en")
            )
        else:
            # 使用默认语音
            tts.tts_to_file(
                text=text,
                file_path=tmp_path,
                language=language_map.get(language, "en")
            )
        
        with open(tmp_path, 'rb') as f:
            audio_data = f.read()
        
        return audio_data
    finally:
        if os.path.exists(tmp_path):
            os.unlink(tmp_path)
```

## ⚡ 性能优化

### 1. 使用 GPU 加速

```bash
# 安装 CUDA PyTorch
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118
```

性能提升：
- CPU: 6-8 秒/句
- GPU: 2-3 秒/句

### 2. 模型缓存

模型会自动缓存在内存中，后续合成会更快。

### 3. 批量合成

如果需要合成多个句子：

```python
texts = ["句子1", "句子2", "句子3"]
for i, text in enumerate(texts):
    tts.tts_to_file(
        text=text,
        file_path=f"output_{i}.wav",
        language="zh-cn"
    )
```

### 4. 降低质量换取速度

使用更小的模型：

```python
# 使用 Tacotron2（更快，质量稍低）
tts = TTS(model_name="tts_models/zh-CN/baker/tacotron2-DDC-GST")
```

## 🧪 测试和验证

### 1. 基础测试

```python
from TTS.api import TTS

# 加载模型
tts = TTS(model_name="tts_models/multilingual/multi-dataset/xtts_v2")

# 测试中文
tts.tts_to_file(
    text="你好，我是人工智能语音助手",
    file_path="test_zh.wav",
    language="zh-cn"
)

# 测试英文
tts.tts_to_file(
    text="Hello, I am an AI voice assistant",
    file_path="test_en.wav",
    language="en"
)

# 测试越南语
tts.tts_to_file(
    text="Xin chào, tôi là trợ lý giọng nói AI",
    file_path="test_vi.wav",
    language="vi"
)

print("✓ 测试完成，请播放生成的音频文件")
```

### 2. 性能测试

```python
import time
from TTS.api import TTS

tts = TTS(model_name="tts_models/multilingual/multi-dataset/xtts_v2")

text = "这是一个性能测试" * 10  # 重复10次

start = time.time()
tts.tts_to_file(text=text, file_path="perf_test.wav", language="zh-cn")
elapsed = time.time() - start

print(f"合成时间: {elapsed:.2f} 秒")
print(f"文本长度: {len(text)} 字符")
print(f"速度: {len(text)/elapsed:.2f} 字符/秒")
```

### 3. 使用测试脚本

```bash
cd voice_service
python test_tts_comparison.py
```

## 🔍 故障排除

### 问题 1: 模型下载失败

**症状：**
```
ConnectionError: Failed to download model
```

**解决方案：**
1. 检查网络连接
2. 使用代理：
   ```bash
   set HTTP_PROXY=http://proxy:port
   set HTTPS_PROXY=http://proxy:port
   python -c "from TTS.api import TTS; TTS(...)"
   ```
3. 手动下载模型文件

### 问题 2: CUDA 错误

**症状：**
```
RuntimeError: CUDA out of memory
```

**解决方案：**
1. 降低批量大小
2. 使用 CPU 模式：
   ```python
   import torch
   torch.cuda.is_available = lambda: False
   ```
3. 升级 GPU 或增加显存

### 问题 3: 合成速度慢

**症状：**
合成一句话需要 10+ 秒

**解决方案：**
1. 使用 GPU 加速
2. 使用更小的模型
3. 检查 CPU 占用率
4. 关闭其他程序

### 问题 4: 语音质量差

**症状：**
语音不自然或有杂音

**解决方案：**
1. 确保使用正确的语言代码
2. 尝试不同的模型
3. 使用语音克隆功能
4. 检查输入文本格式

### 问题 5: 安装失败

**症状：**
```
error: Microsoft Visual C++ 14.0 is required
```

**解决方案（Windows）：**
1. 下载并安装 Microsoft C++ Build Tools
2. 地址：https://visualstudio.microsoft.com/visual-cpp-build-tools/
3. 选择 "Desktop development with C++"
4. 重新安装 TTS

## 📊 与其他方案对比

| 特性 | Coqui TTS | Edge TTS | pyttsx3 |
|------|-----------|----------|---------|
| 语音质量 | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐ |
| 自然度 | 非常自然 | 非常自然 | 机器人音 |
| 离线使用 | ✅ | ❌ | ✅ |
| 多语言 | 100+ | 100+ | 有限 |
| 语音克隆 | ✅ | ❌ | ❌ |
| 安装难度 | 中等 | 简单 | 简单 |
| 资源占用 | 高 | 低 | 很低 |
| 合成速度 | 2-5秒 | 1-2秒 | <1秒 |

## 🎯 最佳实践

### 1. 生产环境配置

```python
# ai_voice_service_fully_offline.py

# 使用 XTTS v2 多语言模型
TTS_ENGINE = "coqui"

# 预加载模型
@app.on_event("startup")
async def startup_event():
    logger.info("预加载 Coqui TTS 模型...")
    load_coqui_tts()
    logger.info("模型加载完成")
```

### 2. 错误处理

```python
async def text_to_speech_coqui(text: str, language: str = "zh") -> bytes:
    try:
        tts = load_coqui_tts()
        # ... 合成逻辑
    except Exception as e:
        logger.error(f"Coqui TTS 失败: {e}")
        # 回退到简单方案
        return await text_to_speech_pyttsx3(text, language)
```

### 3. 性能监控

```python
import time

async def text_to_speech_coqui(text: str, language: str = "zh") -> bytes:
    start_time = time.time()
    
    # ... 合成逻辑
    
    elapsed = time.time() - start_time
    logger.info(f"TTS 耗时: {elapsed:.2f}秒, 文本长度: {len(text)}")
    
    return audio_data
```

## 📚 更多资源

- **官方文档**: https://docs.coqui.ai/
- **GitHub**: https://github.com/coqui-ai/TTS
- **模型列表**: https://github.com/coqui-ai/TTS#released-models
- **社区论坛**: https://github.com/coqui-ai/TTS/discussions

## 🎉 开始使用

现在你已经准备好使用 Coqui TTS 了！

```bash
# 启动服务
cd voice_service
start_coqui_tts.bat

# 或
python ai_voice_service_fully_offline.py
```

享受高质量的离线语音合成！🚀

---

**版本 / Version:** 1.0.0  
**最后更新 / Last Updated:** 2026-01-31  
**作者 / Author:** AI Voice Service Team

# 完全离线 TTS 配置指南
# Fully Offline TTS Setup Guide

## 📋 概述 / Overview

本指南将帮助你配置完全离线的语音合成（TTS）系统，无需依赖在线服务（如 Edge TTS）。

This guide will help you set up a fully offline Text-to-Speech (TTS) system without relying on online services like Edge TTS.

## 🎯 两种离线 TTS 方案

### 方案 1: pyttsx3 (推荐新手)

**优点 / Advantages:**
- ✅ 完全离线，无需网络
- ✅ 安装简单，依赖少
- ✅ 跨平台支持（Windows/macOS/Linux）
- ✅ 启动快速，资源占用低

**缺点 / Disadvantages:**
- ❌ 语音质量较低（机器人音）
- ❌ 多语言支持有限（取决于系统）
- ❌ 语音自然度不如在线服务

**适用场景:**
- 开发测试环境
- 对语音质量要求不高
- 需要快速部署
- 资源受限的环境

### 方案 2: Coqui TTS (推荐生产环境)

**优点 / Advantages:**
- ✅ 高质量语音合成
- ✅ 支持多语言（100+ 语言）
- ✅ 语音自然度高
- ✅ 可自定义语音克隆

**缺点 / Disadvantages:**
- ❌ 首次需要下载模型（约 1.8GB）
- ❌ 资源占用较高（需要较好的 CPU/GPU）
- ❌ 安装依赖较多

**适用场景:**
- 生产环境
- 对语音质量要求高
- 有足够的硬件资源
- 需要多语言支持

## 🚀 快速开始

### 步骤 1: 安装依赖

#### 方案 1: 使用 pyttsx3

```bash
cd voice_service

# 安装基础依赖
pip install -r requirements_fully_offline.txt

# Windows 额外依赖
pip install pywin32

# Linux 额外依赖（需要 espeak）
sudo apt-get install espeak espeak-data libespeak-dev
```

#### 方案 2: 使用 Coqui TTS

```bash
cd voice_service

# 安装基础依赖
pip install -r requirements_fully_offline.txt

# 安装 Coqui TTS
pip install TTS

# 首次运行会自动下载模型（约 1.8GB）
# 或者手动预下载：
python -c "from TTS.api import TTS; TTS(model_name='tts_models/multilingual/multi-dataset/xtts_v2')"
```

### 步骤 2: 配置 TTS 引擎

编辑 `ai_voice_service_fully_offline.py`，选择 TTS 引擎：

```python
# 使用 pyttsx3（默认）
TTS_ENGINE = "pyttsx3"

# 或使用 Coqui TTS（取消注释）
# TTS_ENGINE = "coqui"
```

### 步骤 3: 启动服务

```bash
# 直接运行
python ai_voice_service_fully_offline.py

# 或使用批处理文件（Windows）
start_fully_offline.bat
```

### 步骤 4: 测试

访问健康检查接口：
```bash
curl http://172.16.4.181:8001/health
```

应该看到：
```json
{
  "status": "ok",
  "tts": "pyttsx3 (fully offline)",
  "mode": "完全离线 / Fully Offline"
}
```

## 🔧 详细配置

### pyttsx3 配置

#### Windows 配置

Windows 使用 SAPI5 引擎，支持系统安装的语音包。

**查看可用语音：**
```python
import pyttsx3
engine = pyttsx3.init()
voices = engine.getProperty('voices')
for voice in voices:
    print(f"ID: {voice.id}")
    print(f"Name: {voice.name}")
    print(f"Languages: {voice.languages}")
    print("---")
```

**安装额外语音包：**
1. 打开 Windows 设置
2. 时间和语言 → 语言
3. 添加语言（如中文、越南语）
4. 下载语音包

**推荐语音包：**
- 中文：Microsoft Huihui (简体中文)
- 英文：Microsoft Zira (美式英语)
- 越南语：需要从 Microsoft Store 下载

#### Linux 配置

Linux 使用 espeak 引擎。

**安装 espeak：**
```bash
# Ubuntu/Debian
sudo apt-get install espeak espeak-data libespeak-dev

# CentOS/RHEL
sudo yum install espeak espeak-devel

# Arch Linux
sudo pacman -S espeak
```

**测试 espeak：**
```bash
espeak "Hello, this is a test"
espeak -v zh "你好，这是一个测试"
```

#### macOS 配置

macOS 使用 NSSpeechSynthesizer（内置）。

**查看可用语音：**
```bash
say -v ?
```

**测试语音：**
```bash
say "Hello, this is a test"
say -v Ting-Ting "你好，这是一个测试"
```

### Coqui TTS 配置

#### 选择模型

编辑 `ai_voice_service_fully_offline.py`：

```python
# 多语言模型（推荐）
coqui_tts = TTS(model_name="tts_models/multilingual/multi-dataset/xtts_v2")

# 或选择特定语言的高质量模型：
# 中文
# coqui_tts = TTS(model_name="tts_models/zh-CN/baker/tacotron2-DDC-GST")

# 英文
# coqui_tts = TTS(model_name="tts_models/en/ljspeech/tacotron2-DDC")
```

#### 查看所有可用模型

```python
from TTS.api import TTS
print(TTS().list_models())
```

#### GPU 加速（可选）

如果有 NVIDIA GPU：

```bash
# 安装 CUDA 版本的 PyTorch
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118

# Coqui TTS 会自动使用 GPU
```

## 📊 性能对比

| 特性 | pyttsx3 | Coqui TTS | Edge TTS (在线) |
|------|---------|-----------|-----------------|
| 语音质量 | ⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| 合成速度 | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐ |
| 资源占用 | ⭐⭐⭐⭐⭐ | ⭐⭐ | ⭐⭐⭐⭐ |
| 多语言支持 | ⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| 离线可用 | ✅ | ✅ | ❌ |
| 安装难度 | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ |

## 🎨 语音质量优化

### pyttsx3 优化技巧

```python
import pyttsx3

engine = pyttsx3.init()

# 1. 调整语速（默认 200）
engine.setProperty('rate', 150)  # 降低语速，更自然

# 2. 调整音量（0.0 - 1.0）
engine.setProperty('volume', 0.9)

# 3. 选择更好的语音
voices = engine.getProperty('voices')
# 选择女声或特定语言的语音
for voice in voices:
    if 'female' in voice.name.lower() or 'zira' in voice.name.lower():
        engine.setProperty('voice', voice.id)
        break
```

### Coqui TTS 优化技巧

```python
from TTS.api import TTS

tts = TTS(model_name="tts_models/multilingual/multi-dataset/xtts_v2")

# 1. 使用语音克隆（需要参考音频）
tts.tts_to_file(
    text="你好，这是一个测试",
    file_path="output.wav",
    speaker_wav="reference_voice.wav",  # 参考音频
    language="zh-cn"
)

# 2. 调整语速和音调（某些模型支持）
# 需要在模型配置中设置
```

## 🔍 故障排除

### 问题 1: pyttsx3 初始化失败

**Windows:**
```bash
# 重新安装 pywin32
pip uninstall pywin32
pip install pywin32==306
python -m pywin32_postinstall -install
```

**Linux:**
```bash
# 确保 espeak 已安装
sudo apt-get install --reinstall espeak espeak-data
```

### 问题 2: Coqui TTS 模型下载失败

**解决方案：**
```bash
# 手动下载模型
mkdir -p ~/.local/share/tts
cd ~/.local/share/tts

# 从 GitHub 下载模型文件
# https://github.com/coqui-ai/TTS/releases
```

### 问题 3: 语音质量差

**pyttsx3:**
- 尝试不同的系统语音
- 调整语速和音量
- 考虑升级到 Coqui TTS

**Coqui TTS:**
- 尝试不同的模型
- 使用 GPU 加速
- 提供高质量的参考音频（语音克隆）

### 问题 4: 中文语音不可用

**Windows:**
```
设置 → 时间和语言 → 语言 → 添加语言 → 中文（简体）
下载语音包：Microsoft Huihui
```

**Linux:**
```bash
# 安装中文语音
sudo apt-get install espeak-ng-data
espeak-ng -v zh "测试"
```

## 📝 使用示例

### 测试 pyttsx3

```python
import pyttsx3

engine = pyttsx3.init()
engine.setProperty('rate', 150)

# 中文
engine.say("你好，我是人工智能语音助手")
engine.runAndWait()

# 英文
engine.say("Hello, I am an AI voice assistant")
engine.runAndWait()
```

### 测试 Coqui TTS

```python
from TTS.api import TTS

tts = TTS(model_name="tts_models/multilingual/multi-dataset/xtts_v2")

# 中文
tts.tts_to_file(
    text="你好，我是人工智能语音助手",
    file_path="output_zh.wav",
    language="zh-cn"
)

# 英文
tts.tts_to_file(
    text="Hello, I am an AI voice assistant",
    file_path="output_en.wav",
    language="en"
)

# 越南语
tts.tts_to_file(
    text="Xin chào, tôi là trợ lý giọng nói AI",
    file_path="output_vi.wav",
    language="vi"
)
```

## 🔄 从 Edge TTS 迁移

### 修改前端配置

前端无需修改！完全兼容现有的 API 接口。

### 更新服务启动脚本

```bash
# 停止旧服务
# Ctrl+C 或关闭终端

# 启动新服务
python ai_voice_service_fully_offline.py
```

### 验证迁移

```bash
# 测试健康检查
curl http://172.16.4.181:8001/health

# 应该看到 "tts": "pyttsx3 (fully offline)" 或 "coqui (fully offline)"
```

## 🎯 推荐配置

### 开发环境
```python
TTS_ENGINE = "pyttsx3"
WHISPER_MODEL = "base"  # 快速测试
```

### 生产环境（有网络）
```python
# 继续使用 Edge TTS（质量最好）
# 使用 ai_voice_service_offline.py
```

### 生产环境（无网络）
```python
TTS_ENGINE = "coqui"
WHISPER_MODEL = "small"  # 平衡质量和速度
```

### 资源受限环境
```python
TTS_ENGINE = "pyttsx3"
WHISPER_MODEL = "tiny"  # 最快
```

## 📚 更多资源

- **pyttsx3 文档**: https://pyttsx3.readthedocs.io/
- **Coqui TTS 文档**: https://docs.coqui.ai/
- **Whisper 文档**: https://github.com/openai/whisper
- **espeak 文档**: http://espeak.sourceforge.net/

## 🆘 获取帮助

如果遇到问题：

1. 检查日志输出
2. 验证依赖安装
3. 测试系统语音功能
4. 查看故障排除部分

---

**版本 / Version:** 1.0.0  
**最后更新 / Last Updated:** 2026-01-31

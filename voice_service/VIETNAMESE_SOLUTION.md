# 越南语 TTS 解决方案

## 问题说明

XTTS v2 (Coqui TTS) **不支持越南语**。

支持的语言列表：
```python
['en', 'es', 'fr', 'de', 'it', 'pt', 'pl', 'tr', 'ru', 'nl', 'cs', 'ar', 'zh-cn', 'hu', 'ko', 'ja', 'hi']
```

越南语 (vi) 不在列表中。

## 🎯 解决方案对比

| 方案 | 越南语支持 | 质量 | 网络要求 | 难度 |
|------|-----------|------|---------|------|
| **Edge TTS** | ✅ 完美 | ⭐⭐⭐⭐⭐ | 需要 | 简单 |
| **gTTS** | ✅ 支持 | ⭐⭐⭐⭐ | 需要 | 简单 |
| **pyttsx3** | ⚠️ 看系统 | ⭐⭐ | 不需要 | 简单 |
| **训练模型** | ✅ 可以 | ⭐⭐⭐⭐⭐ | 不需要 | 困难 |

## 方案 1: 使用 Edge TTS（推荐）

### 优点
- ✅ 完美支持越南语
- ✅ 语音质量最高
- ✅ 支持多种越南语音（男声、女声）
- ✅ 免费使用

### 缺点
- ❌ 需要网络连接

### 实施步骤

#### 1. 安装依赖

```bash
pip install edge-tts
```

#### 2. 使用混合模式服务

创建新文件 `ai_voice_service_hybrid.py`：

```python
"""
混合模式：
- 中文、英文：使用 Coqui TTS（离线）
- 越南语：使用 Edge TTS（在线）
"""

async def text_to_speech(text: str, language: str = "zh") -> bytes:
    """根据语言选择 TTS 引擎"""
    
    if language == "vi":
        # 越南语使用 Edge TTS
        return await text_to_speech_edge(text, language)
    else:
        # 中文、英文使用 Coqui TTS
        return await text_to_speech_coqui(text, language)

async def text_to_speech_edge(text: str, language: str = "vi") -> bytes:
    """使用 Edge TTS（支持越南语）"""
    import edge_tts
    
    # 越南语语音选项
    voice_map = {
        "vi": "vi-VN-HoaiMyNeural",  # 女声
        # "vi": "vi-VN-NamMinhNeural",  # 男声
        "zh": "zh-CN-XiaoxiaoNeural",
        "en": "en-US-AriaNeural"
    }
    
    voice = voice_map.get(language, "en-US-AriaNeural")
    
    communicate = edge_tts.Communicate(text, voice)
    
    with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as tmp_file:
        tmp_path = tmp_file.name
    
    try:
        await communicate.save(tmp_path)
        
        with open(tmp_path, 'rb') as f:
            audio_data = f.read()
        
        return audio_data
    finally:
        if os.path.exists(tmp_path):
            os.unlink(tmp_path)
```

#### 3. 修改配置

```python
# 混合模式配置
TTS_MODE = "hybrid"  # "coqui", "edge", "hybrid"

# 语言到引擎的映射
TTS_ENGINE_MAP = {
    "zh": "coqui",   # 中文用 Coqui（离线）
    "en": "coqui",   # 英文用 Coqui（离线）
    "vi": "edge"     # 越南语用 Edge（在线）
}
```

## 方案 2: 使用 gTTS

### 优点
- ✅ 支持越南语
- ✅ 简单易用
- ✅ 免费

### 缺点
- ❌ 需要网络
- ❌ 质量不如 Edge TTS

### 实施步骤

```bash
pip install gTTS
```

```python
from gtts import gTTS

async def text_to_speech_gtts(text: str, language: str = "vi") -> bytes:
    """使用 gTTS"""
    
    with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as tmp_file:
        tmp_path = tmp_file.name
    
    try:
        tts = gTTS(text=text, lang=language)
        tts.save(tmp_path)
        
        with open(tmp_path, 'rb') as f:
            audio_data = f.read()
        
        return audio_data
    finally:
        if os.path.exists(tmp_path):
            os.unlink(tmp_path)
```

## 方案 3: 使用 pyttsx3（完全离线）

### 优点
- ✅ 完全离线
- ✅ 不需要额外安装

### 缺点
- ❌ 质量很差
- ❌ 需要系统安装越南语语音包
- ❌ Windows 默认没有越南语语音

### 检查系统语音

```python
import pyttsx3

engine = pyttsx3.init()
voices = engine.getProperty('voices')

for voice in voices:
    print(f"ID: {voice.id}")
    print(f"Name: {voice.name}")
    print(f"Languages: {voice.languages}")
    print("-" * 50)
```

如果没有越南语语音，需要从 Windows 设置中下载。

## 方案 4: 训练自己的模型（高级）

### 优点
- ✅ 完全离线
- ✅ 可以定制

### 缺点
- ❌ 需要大量越南语语音数据
- ❌ 需要 GPU 训练
- ❌ 技术难度高
- ❌ 时间成本高

不推荐，除非你有专业需求。

## 🎯 推荐方案

### 如果有网络连接（推荐）

使用**混合模式**：
- 中文、英文 → Coqui TTS（离线，高质量）
- 越南语 → Edge TTS（在线，高质量）

### 如果必须完全离线

1. **接受现状**：越南语用英语发音（当前方案）
2. **使用 pyttsx3**：安装越南语语音包（质量差）
3. **不支持越南语**：只提供中文和英文

## 📝 实施建议

我建议创建一个**混合模式服务**，这样可以：
- ✅ 中文和英文保持离线（Coqui TTS）
- ✅ 越南语获得最佳质量（Edge TTS）
- ✅ 灵活切换

需要我帮你实现混合模式吗？

---

**更新时间:** 2026-01-31  
**版本:** 1.0.0

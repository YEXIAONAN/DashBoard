# XTTS v2 语言支持说明

## ✅ 支持的语言

XTTS v2 模型支持以下 **17 种语言**：

| 语言 | 代码 | 状态 |
|------|------|------|
| 🇨🇳 中文 | zh-cn | ✓ 完美支持 |
| 🇺🇸 英文 | en | ✓ 完美支持 |
| 🇪🇸 西班牙语 | es | ✓ 支持 |
| 🇫🇷 法语 | fr | ✓ 支持 |
| 🇩🇪 德语 | de | ✓ 支持 |
| 🇮🇹 意大利语 | it | ✓ 支持 |
| 🇵🇹 葡萄牙语 | pt | ✓ 支持 |
| 🇵🇱 波兰语 | pl | ✓ 支持 |
| 🇹🇷 土耳其语 | tr | ✓ 支持 |
| 🇷🇺 俄语 | ru | ✓ 支持 |
| 🇳🇱 荷兰语 | nl | ✓ 支持 |
| 🇨🇿 捷克语 | cs | ✓ 支持 |
| 🇸🇦 阿拉伯语 | ar | ✓ 支持 |
| 🇭🇺 匈牙利语 | hu | ✓ 支持 |
| 🇰🇷 韩语 | ko | ✓ 支持 |
| 🇯🇵 日语 | ja | ✓ 支持 |
| 🇮🇳 印地语 | hi | ✓ 支持 |

## ❌ 不支持的语言

| 语言 | 代码 | 回退方案 |
|------|------|---------|
| 🇻🇳 越南语 | vi | 自动回退到英语 (en) |

## 🔧 技术细节

### 说话人 (Speaker)

XTTS v2 是多说话人模型，**必须**指定说话人参数。

默认使用的说话人：
- **Claribel Dervla** (已验证可用于所有支持的语言)

其他可用说话人：
- Daisy Studious
- Gracie Wise
- 等等...

### 使用示例

```python
from TTS.api import TTS

tts = TTS(model_name="tts_models/multilingual/multi-dataset/xtts_v2")

# 中文
tts.tts_to_file(
    text="你好，这是中文测试。",
    file_path="output_zh.wav",
    speaker="Claribel Dervla",
    language="zh-cn"
)

# 英文
tts.tts_to_file(
    text="Hello, this is an English test.",
    file_path="output_en.wav",
    speaker="Claribel Dervla",
    language="en"
)

# 越南语 - 不支持，会报错
# tts.tts_to_file(
#     text="Xin chào",
#     language="vi"  # ❌ 错误！
# )
```

## 🚨 常见错误

### 错误 1: 未指定说话人

```
Model is multi-speaker but no `speaker` is provided.
```

**解决方案：** 必须指定 `speaker` 参数

```python
tts.tts_to_file(
    text="你好",
    file_path="output.wav",
    speaker="Claribel Dervla",  # ✓ 必须指定
    language="zh-cn"
)
```

### 错误 2: 使用不支持的语言

```
Language vi is not supported. Supported languages are ['en', 'es', 'fr', ...]
```

**解决方案：** 使用支持的语言或回退到英语

```python
# 方案 1: 使用英语代替
language = "vi" if language != "vi" else "en"

# 方案 2: 在服务层自动处理
language_map = {
    "zh": "zh-cn",
    "en": "en",
    "vi": "en"  # 越南语回退到英语
}
```

## 📝 服务配置

在 `ai_voice_service_fully_offline.py` 中的配置：

```python
async def text_to_speech_coqui(text: str, language: str = "zh") -> bytes:
    # 语言映射
    language_map = {
        "zh": "zh-cn",
        "en": "en",
        "vi": "en"  # 越南语不支持，回退到英语
    }
    
    coqui_lang = language_map.get(language, "en")
    
    if language == "vi":
        logger.warning("⚠️ XTTS v2 不支持越南语，使用英语代替")
    
    # 使用默认说话人
    default_speaker = "Claribel Dervla"
    
    tts.tts_to_file(
        text=text,
        file_path=tmp_path,
        speaker=default_speaker,
        language=coqui_lang
    )
```

## 🎯 最佳实践

1. **始终指定说话人** - XTTS v2 要求必须指定
2. **使用支持的语言** - 检查语言代码是否在支持列表中
3. **提供回退方案** - 不支持的语言自动回退到英语
4. **记录警告日志** - 当使用回退方案时记录日志

## 🔍 验证语言支持

运行测试脚本验证：

```bash
cd voice_service
..\.venv\Scripts\python.exe test_xtts_speakers.py
```

输出示例：
```
测试语言: zh-cn
  ✓ 成功！文件: test_output_zh-cn.wav

测试语言: en
  ✓ 成功！文件: test_output_en.wav

测试语言: vi
  ✗ 失败: Language vi is not supported
```

## 📚 参考资料

- [Coqui TTS 官方文档](https://github.com/coqui-ai/TTS)
- [XTTS v2 模型说明](https://huggingface.co/coqui/XTTS-v2)
- 测试脚本: `test_xtts_speakers.py`
- 服务代码: `ai_voice_service_fully_offline.py`

---

**更新时间:** 2026-01-31  
**版本:** 1.0.0

# 🎉 viXTTS 安装指南 - 支持越南语！

## 🌟 什么是 viXTTS？

**viXTTS** 是基于 XTTS-v2 专门为越南语微调的 TTS 模型，由 FPT University HCMC 的 Thinh Le 开发。

### ✅ 支持的语言（18种）

| 语言 | 代码 | 状态 |
|------|------|------|
| 🇨🇳 中文 | zh-cn | ✅ 完美支持 |
| 🇺🇸 英文 | en | ✅ 完美支持 |
| 🇻🇳 **越南语** | vi | ✅ **完美支持** |
| 🇪🇸 西班牙语 | es | ✅ 支持 |
| 🇫🇷 法语 | fr | ✅ 支持 |
| 🇩🇪 德语 | de | ✅ 支持 |
| 🇮🇹 意大利语 | it | ✅ 支持 |
| 🇵🇹 葡萄牙语 | pt | ✅ 支持 |
| 🇵🇱 波兰语 | pl | ✅ 支持 |
| 🇹🇷 土耳其语 | tr | ✅ 支持 |
| 🇷🇺 俄语 | ru | ✅ 支持 |
| 🇳🇱 荷兰语 | nl | ✅ 支持 |
| 🇨🇿 捷克语 | cs | ✅ 支持 |
| 🇸🇦 阿拉伯语 | ar | ✅ 支持 |
| 🇭🇺 匈牙利语 | hu | ✅ 支持 |
| 🇰🇷 韩语 | ko | ✅ 支持 |
| 🇯🇵 日语 | ja | ✅ 支持 |
| 🇮🇳 印地语 | hi | ✅ 支持 |

## 🚀 快速开始

### 步骤 1: 安装依赖

viXTTS 使用与 Coqui TTS 相同的依赖：

```bash
cd voice_service

# 确保已安装基础依赖
pip install -r requirements_fully_offline.txt

# 确认版本
pip list | findstr "torch transformers TTS"
```

**要求的版本：**
- torch: 2.5.1+cpu
- transformers: 4.33.0
- tokenizers: 0.13.3
- TTS: 0.22.0

### 步骤 2: 下载 viXTTS 模型

首次运行时会自动下载模型（约 1.8GB）：

```bash
..\.venv\Scripts\python.exe -c "from TTS.api import TTS; TTS(model_name='capleaf/viXTTS')"
```

**下载位置：**
```
C:\Users\Administrator\AppData\Local\tts\capleaf--viXTTS\
```

### 步骤 3: 测试模型

创建测试脚本：

```python
from TTS.api import TTS

# 加载 viXTTS 模型
tts = TTS(model_name="capleaf/viXTTS")

# 测试中文
tts.tts_to_file(
    text="你好，这是中文测试。",
    file_path="test_zh.wav",
    speaker="Claribel Dervla",
    language="zh-cn"
)

# 测试英文
tts.tts_to_file(
    text="Hello, this is an English test.",
    file_path="test_en.wav",
    speaker="Claribel Dervla",
    language="en"
)

# 测试越南语
tts.tts_to_file(
    text="Xin chào, đây là bài kiểm tra tiếng Việt.",
    file_path="test_vi.wav",
    speaker="Claribel Dervla",
    language="vi"
)

print("✅ 所有测试完成！")
```

### 步骤 4: 启动服务

```bash
..\.venv\Scripts\python.exe ai_voice_service_vixtts.py
```

**预期输出：**
```
✓ 已添加 ffmpeg 路径到 PATH
✓ 设置 FFMPEG_BINARY
INFO: Started server process
==================================================
AI 语音助手服务启动中（viXTTS - 支持越南语）...
Ollama: http://172.16.4.181:11434
模型: qwen2.5:7b
Whisper: small
TTS 引擎: vixtts
TTS 模型: capleaf/viXTTS
==================================================
预加载 Whisper 模型...
Whisper 模型加载成功
预加载 viXTTS 模型...
初始化 viXTTS 模型
模型: capleaf/viXTTS
> Downloading model to C:\Users\Administrator\AppData\Local\tts\capleaf--viXTTS\
[或] > capleaf/viXTTS is already downloaded.
> Using model: xtts
✅ viXTTS 模型加载成功
支持语言: 中文 (zh-cn), 英文 (en), 越南语 (vi)
✅ 所有模型加载完成
INFO: Uvicorn running on http://0.0.0.0:8001
```

## 📊 与 XTTS v2 对比

| 特性 | XTTS v2 | viXTTS |
|------|---------|--------|
| 中文支持 | ✅ | ✅ |
| 英文支持 | ✅ | ✅ |
| 越南语支持 | ❌ | ✅ |
| 其他语言 | 15种 | 18种 |
| 模型大小 | 1.8GB | 1.8GB |
| 质量 | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| 速度 | 3-5秒 | 3-5秒 |
| 离线运行 | ✅ | ✅ |

## 🎯 使用场景

### 场景 1: 越南餐厅

```python
# 用户用越南语询问
用户: "Hôm nay tôi nên ăn gì?"

# ASR 识别
识别: "Hôm nay tôi nên ăn gì?"

# LLM 回复
AI: "Tôi khuyên bạn nên thử món phở bò..."

# TTS 合成
语音: 🔊 高质量越南语语音
```

### 场景 2: 多语言客服

```python
# 支持三种语言切换
- 中文客户 → 中文服务
- 英文客户 → 英文服务
- 越南客户 → 越南语服务
```

## ⚙️ 配置选项

### 基础配置

**文件:** `ai_voice_service_vixtts.py`

```python
# Ollama 配置
OLLAMA_HOST = "http://172.16.4.181:11434"
OLLAMA_MODEL = "qwen2.5:7b"

# 服务端口
SERVICE_PORT = 8001

# Whisper 模型
WHISPER_MODEL = "small"

# TTS 引擎
TTS_ENGINE = "vixtts"

# viXTTS 模型
VIXTTS_MODEL = "capleaf/viXTTS"
```

### 前端配置

**文件:** `main/templates/ai_health_advisor.html`

```html
<select id="languageSelect" class="language-select">
    <option value="zh" selected>🇨🇳 中文 (Chinese)</option>
    <option value="en">🇺🇸 English</option>
    <option value="vi">🇻🇳 Tiếng Việt (Vietnamese)</option>
</select>
```

## 🔍 故障排除

### 问题 1: 模型下载失败

**错误：**
```
ConnectionError: Failed to download model from Hugging Face
```

**解决方案：**

1. **检查网络连接**（首次下载需要网络）
2. **使用代理**：
   ```bash
   set HTTP_PROXY=http://proxy:port
   set HTTPS_PROXY=http://proxy:port
   ```
3. **手动下载**：
   - 访问：https://huggingface.co/capleaf/viXTTS
   - 下载所有文件到：`C:\Users\Administrator\AppData\Local\tts\capleaf--viXTTS\`

### 问题 2: 越南语合成失败

**错误：**
```
Language vi is not supported
```

**检查：**
```python
from TTS.api import TTS
tts = TTS(model_name="capleaf/viXTTS")
print(tts.languages)
# 应该包含 'vi'
```

**解决：**
- 确认使用的是 `capleaf/viXTTS` 而不是 `tts_models/multilingual/multi-dataset/xtts_v2`
- 重新下载模型

### 问题 3: 越南语质量差

**可能原因：**
- 输入文本太短（<10个词）
- 文本包含特殊字符

**优化：**
```python
# 确保文本长度适中
if len(text.split()) < 10:
    text = text + " Cảm ơn bạn."  # 添加填充文本
```

## 📈 性能优化

### 1. 使用 GPU 加速

```bash
# 安装 CUDA 版本的 PyTorch
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118
```

**效果：** 速度提升 3-5 倍

### 2. 调整 Whisper 模型大小

```python
# 更快但准确率略低
WHISPER_MODEL = "base"

# 更慢但准确率更高
WHISPER_MODEL = "medium"
```

### 3. 预加载模型

服务启动时预加载所有模型（已实现）。

## 🎨 越南语示例

### 常用短语

```python
greetings = {
    "你好": "Xin chào",
    "谢谢": "Cảm ơn",
    "再见": "Tạm biệt",
    "早上好": "Chào buổi sáng",
    "晚上好": "Chào buổi tối"
}

# 测试所有短语
for zh, vi in greetings.items():
    tts.tts_to_file(
        text=vi,
        file_path=f"test_{zh}.wav",
        speaker="Claribel Dervla",
        language="vi"
    )
```

### 餐厅场景

```python
restaurant_phrases = [
    "Hôm nay bạn muốn ăn gì?",  # 今天你想吃什么？
    "Món này rất ngon.",  # 这道菜很好吃
    "Bạn có dị ứng thực phẩm không?",  # 你有食物过敏吗？
    "Tôi khuyên bạn nên thử món này.",  # 我推荐你试试这道菜
]
```

## 📚 参考资料

- **viXTTS GitHub**: https://github.com/thinhlpg/vixtts-demo
- **Hugging Face**: https://huggingface.co/capleaf/viXTTS
- **Coqui TTS**: https://github.com/coqui-ai/TTS
- **viVoice Dataset**: 越南语语音数据集

## 🎉 完成清单

部署前检查：

- [ ] PyTorch 版本正确 (2.5.1)
- [ ] transformers 版本正确 (4.33.0)
- [ ] viXTTS 模型已下载
- [ ] Whisper 模型已下载
- [ ] ffmpeg 已安装
- [ ] 服务启动成功
- [ ] 中文测试通过
- [ ] 英文测试通过
- [ ] **越南语测试通过** ✨
- [ ] 前端语言选择器已更新

## 🌟 优势总结

✅ **完全离线运行**  
✅ **支持越南语**（原 XTTS v2 不支持）  
✅ **质量与 XTTS v2 相当**  
✅ **无需额外配置**  
✅ **开源免费**  

---

**更新时间:** 2026-01-31  
**版本:** 1.0.0  
**状态:** ✅ 可用

**现在你可以为越南客户提供完美的语音服务了！** 🇻🇳🎉

# 多语言功能快速开始指南
# Quick Start Guide for Multilingual Support

## 🚀 快速开始 / Quick Start

### 1. 启动服务 / Start the Service

```bash
# Windows
cd voice_service
python ai_voice_service_offline.py

# 或使用批处理文件 / Or use batch file
start_offline.bat
```

服务将在 `http://172.16.4.181:8001` 启动。

The service will start at `http://172.16.4.181:8001`.

### 2. 访问前端 / Access Frontend

打开浏览器访问 / Open browser and visit:
```
http://your-django-server:8000/ai_health_advisor/
```

### 3. 选择语言 / Select Language

在对话框顶部，您会看到一个语言选择器：

At the top of the chat interface, you'll see a language selector:

```
🌐 语言: [中文 (Chinese) ▼]
```

点击下拉菜单，选择您想要的语言：
- **中文 (Chinese)** - 默认 / Default
- **English**
- **Tiếng Việt (Vietnamese)**

### 4. 开始对话 / Start Chatting

#### 文字输入 / Text Input
1. 在输入框中输入您的消息
2. 点击发送按钮 ✈️
3. AI 将用您选择的语言回复

#### 语音输入 / Voice Input
1. 点击麦克风按钮 🎤
2. 开始说话（使用您选择的语言）
3. 再次点击停止录音
4. AI 将识别您的语音并用相同语言回复

## 📝 使用示例 / Usage Examples

### 中文示例 / Chinese Example
```
用户: 你好，今天天气怎么样？
AI: 你好！很抱歉，我无法获取实时天气信息...
```

### English Example
```
User: Hello, how are you today?
AI: Hello! I'm doing well, thank you for asking...
```

### Vietnamese Example / Ví dụ tiếng Việt
```
Người dùng: Xin chào, hôm nay thời tiết thế nào?
AI: Xin chào! Rất tiếc, tôi không thể lấy thông tin thời tiết...
```

## 🎯 功能特点 / Features

### ✅ 支持的功能 / Supported Features

| 功能 / Feature | 中文 | English | Tiếng Việt |
|---------------|------|---------|------------|
| 文字输入 / Text Input | ✅ | ✅ | ✅ |
| 语音识别 / Voice Recognition | ✅ | ✅ | ✅ |
| 语音合成 / Text-to-Speech | ✅ | ✅ | ✅ |
| 流式输出 / Streaming Output | ✅ | ✅ | ✅ |
| Markdown 渲染 / Markdown Rendering | ✅ | ✅ | ✅ |

### 🎤 语音质量 / Voice Quality

- **中文 / Chinese**: 晓晓 (Xiaoxiao) - 自然流畅的女声
- **English**: Jenny - Clear and natural female voice
- **Tiếng Việt / Vietnamese**: Hoai My - Giọng nữ tự nhiên

## 🔧 配置选项 / Configuration Options

### 修改默认语言 / Change Default Language

编辑 `main/templates/ai_health_advisor.html`:

```javascript
let currentLanguage = 'zh'; // 改为 'en' 或 'vi'
```

### 添加更多语言 / Add More Languages

1. **后端 / Backend** (`ai_voice_service_offline.py`):

```python
# 在 text_to_speech() 函数中添加
voice_map = {
    "zh": "zh-CN-XiaoxiaoNeural",
    "en": "en-US-JennyNeural",
    "vi": "vi-VN-HoaiMyNeural",
    "ja": "ja-JP-NanamiNeural",  # 日语 / Japanese
    "ko": "ko-KR-SunHiNeural"    # 韩语 / Korean
}
```

2. **前端 / Frontend** (`ai_health_advisor.html`):

```html
<select id="languageSelect" class="language-select">
    <option value="zh">中文 (Chinese)</option>
    <option value="en">English</option>
    <option value="vi">Tiếng Việt</option>
    <option value="ja">日本語 (Japanese)</option>
    <option value="ko">한국어 (Korean)</option>
</select>
```

## 🧪 测试 / Testing

### 运行测试脚本 / Run Test Script

```bash
cd voice_service
python test_multilingual.py
```

这将测试所有三种语言的功能。

This will test functionality for all three languages.

### 手动测试 / Manual Testing

1. **测试语音识别 / Test Voice Recognition**
   - 选择一种语言
   - 点击麦克风按钮
   - 用该语言说话
   - 验证识别结果是否正确

2. **测试语音合成 / Test Text-to-Speech**
   - 选择一种语言
   - 输入该语言的文字
   - 发送消息
   - 听取 AI 的语音回复

3. **测试语言切换 / Test Language Switching**
   - 在对话中切换语言
   - 验证新消息使用新语言
   - 确认历史消息保持不变

## ❓ 常见问题 / FAQ

### Q: 可以在对话中途切换语言吗？
**A:** 可以！切换语言后，新的消息将使用新语言进行识别和合成。

### Q: Can I switch languages mid-conversation?
**A:** Yes! After switching languages, new messages will use the new language for recognition and synthesis.

### Q: 语音识别支持方言吗？
**A:** Whisper 模型对标准发音效果最好，方言可能影响识别准确度。

### Q: Does voice recognition support dialects?
**A:** The Whisper model works best with standard pronunciation. Dialects may affect recognition accuracy.

### Q: 为什么语音合成需要网络？
**A:** 默认使用 Microsoft Edge TTS（在线服务）。如需离线使用，请参考 `OFFLINE_TTS_SETUP.md` 配置离线 TTS。

### Q: Why does text-to-speech require internet?
**A:** By default, we use Microsoft Edge TTS (online service). For offline use, refer to `OFFLINE_TTS_SETUP.md` to configure offline TTS.

### Q: 如何在离线环境使用？
**A:** 使用 `ai_voice_service_fully_offline.py` 替代默认服务，支持 pyttsx3 或 Coqui TTS。详见 `OFFLINE_TTS_SETUP.md`。

### Q: How to use in offline environment?
**A:** Use `ai_voice_service_fully_offline.py` instead of the default service, supporting pyttsx3 or Coqui TTS. See `OFFLINE_TTS_SETUP.md` for details.

## 📞 技术支持 / Technical Support

如果遇到问题，请检查：

If you encounter issues, please check:

1. ✅ 服务是否正常运行 / Service is running
   ```bash
   curl http://172.16.4.181:8001/health
   ```

2. ✅ 浏览器控制台是否有错误 / Browser console for errors
   - 按 F12 打开开发者工具
   - 查看 Console 标签

3. ✅ 麦克风权限是否已授予 / Microphone permission granted
   - 浏览器会提示授权请求
   - 确保允许访问麦克风

4. ✅ 网络连接是否正常 / Network connection is stable
   - TTS 需要网络连接
   - 检查防火墙设置

## 🎉 开始使用 / Get Started

现在您已经准备好使用多语言 AI 语音助手了！

You're now ready to use the multilingual AI voice assistant!

选择您的语言，开始对话吧！🚀

Choose your language and start chatting! 🚀

---

**版本 / Version:** 1.1.0  
**更新日期 / Last Updated:** 2026-01-31

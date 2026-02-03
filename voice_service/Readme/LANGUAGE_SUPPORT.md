# 多语言语音识别支持

## 概述

AI 语音助手现在支持多语言语音识别功能，用户可以在前端界面选择不同的语言进行语音输入。

## 支持的语言

| 语言代码 | 语言名称 | Whisper 代码 | 提示词 |
|---------|---------|-------------|--------|
| `zh` | 中文 (Chinese) | `zh` | "以下是普通话的句子。" |
| `en` | English | `en` | "The following is spoken in English." |
| `vi` | 越南语 (Tiếng Việt) | `vi` | "Sau đây là câu nói tiếng Việt." |

## 后端修改

### 1. 语音识别函数更新

```python
async def transcribe_audio(audio_bytes: bytes, language: str = "zh") -> str:
    # 支持语言参数，默认中文
    # 根据语言选择对应的 Whisper 配置和提示词
```

### 2. API 接口更新

- `/transcribe` - 添加 `language` 参数
- `/chat` - 添加 `language` 参数
- `/health` - 返回支持的语言列表

### 3. 语言配置

```python
language_config = {
    "zh": {
        "code": "zh",
        "prompt": "以下是普通话的句子。"
    },
    "en": {
        "code": "en", 
        "prompt": "The following is spoken in English."
    },
    "vi": {
        "code": "vi",
        "prompt": "Sau đây là câu nói tiếng Việt."
    }
}
```

## 前端修改

### 1. 语言选择器

在聊天界面头部添加了语言选择下拉菜单：

```html
<div class="language-selector">
    <label for="languageSelect">语音识别语言:</label>
    <select id="languageSelect" class="language-select">
        <option value="zh">中文 (Chinese)</option>
        <option value="en">English</option>
        <option value="vi">Tiếng Việt</option>
    </select>
</div>
```

### 2. JavaScript 更新

- 添加 `currentLanguage` 变量跟踪选中的语言
- 更新 `sendAudio` 函数，发送语言参数到后端
- 添加语言切换事件监听器
- 根据语言显示不同的状态提示信息

### 3. 响应式设计

为移动设备优化了语言选择器的显示效果。

## 使用方法

### 用户操作流程

1. 打开 AI 语音助手页面
2. 在聊天界面顶部选择想要使用的语言
3. 点击麦克风按钮开始录音
4. 说话完毕后再次点击停止录音
5. 系统会使用选定的语言进行语音识别
6. 识别结果会显示在聊天界面中

### 开发者测试

```bash
# 启动语音服务
cd voice_service
python ai_voice_service_offline.py

# 运行测试脚本
python test_language_support.py
```

## 技术细节

### Whisper 模型配置

- 使用 OpenAI Whisper 的 `small` 模型
- 支持多语言识别
- 通过 `language` 参数指定识别语言
- 使用 `initial_prompt` 提高特定语言的识别准确度

### 音频处理流程

1. 前端录制音频 (WebM/Opus 格式)
2. 使用 ffmpeg 转换为 WAV 格式 (16kHz, 单声道)
3. Whisper 模型进行语音识别
4. 返回识别结果给前端

### API 请求格式

```javascript
// 语音识别请求
const formData = new FormData();
formData.append('audio', audioBlob, 'audio.wav');
formData.append('language', currentLanguage); // 'zh', 'en', 或 'vi'
```

## 注意事项

1. **语言切换**: 语言选择只影响语音识别，不影响 AI 回复的语言
2. **识别准确度**: 不同语言的识别准确度可能有差异
3. **网络要求**: 需要连接到语音服务后端 (172.16.4.181:8001)
4. **浏览器兼容性**: 需要支持 WebRTC 的现代浏览器

## 未来扩展

可以考虑添加更多语言支持：
- 日语 (ja)
- 韩语 (ko)
- 法语 (fr)
- 德语 (de)
- 西班牙语 (es)

只需在 `language_config` 中添加对应的配置即可。
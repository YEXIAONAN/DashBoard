# 🚀 快速启动指南 - Dify 工作流版本

## 一、前置要求

### 必需组件
- ✅ Python 3.8+
- ✅ ffmpeg（用于音频处理）
- ✅ Dify 工作流服务（http://10.0.0.10:3099）

### 可选组件
- ⚠️ Ollama 服务（备用，http://10.0.0.10:11434）

## 二、安装依赖

```bash
cd voice_service
pip install -r requirements_ai_voice.txt
```

主要依赖：
- fastapi
- uvicorn
- httpx
- openai-whisper
- pyttsx3
- requests

## 三、启动服务

### 方法 1: 使用批处理脚本（推荐）

```bash
start_dify_service.bat
```

### 方法 2: 直接运行

```bash
python ai_voice_service_vixtts.py
```

服务将在 **http://localhost:8001** 启动

## 四、验证服务

### 1. 浏览器测试

打开浏览器访问：
```
http://localhost:8001/health
```

应该看到类似输出：
```json
{
  "status": "ok",
  "llm_service": "Dify Workflow",
  "dify_api": "http://10.0.0.10:3099/v1/chat/completions",
  "mode": "Dify 工作流 + 本地语音"
}
```

### 2. 使用测试脚本

```bash
python test_dify_integration.py
```

### 3. 使用测试页面

在浏览器中打开：
```
voice_service/test_voice_ui.html
```

## 五、API 使用示例

### Python 示例（中文）

```python
import requests

# 中文对话（使用 Dify 工作流）
response = requests.post(
    'http://localhost:8001/chat',
    data={
        'text': '你好，请介绍一下健康饮食',
        'language': 'zh',
        'user_name': '张三'
    }
)

result = response.json()
print(f"AI 回复: {result['text']}")
print(f"音频数据: {len(result['audio'])} 字符")
```

### Python 示例（越南语）

```python
import requests

# 越南语对话（自动使用 Ollama）
response = requests.post(
    'http://localhost:8001/chat',
    data={
        'text': 'Xin chào, hãy giới thiệu về dinh dưỡng lành mạnh',
        'language': 'vi',
        'user_name': 'Nguyen'
    }
)

result = response.json()
print(f"AI 回复: {result['text']}")
```

### JavaScript 示例

```javascript
// 文本对话
const formData = new FormData();
formData.append('text', '你好，请介绍一下健康饮食');
formData.append('language', 'zh');
formData.append('user_name', '张三');

fetch('http://localhost:8001/chat', {
    method: 'POST',
    body: formData
})
.then(response => response.json())
.then(data => {
    console.log('AI 回复:', data.text);
    // 播放音频
    const audio = new Audio(`data:audio/wav;base64,${data.audio}`);
    audio.play();
});
```

### cURL 示例

```bash
# 文本对话
curl -X POST http://localhost:8001/chat \
  -F "text=你好，请介绍一下健康饮食" \
  -F "language=zh" \
  -F "user_name=张三"

# 流式对话
curl -X POST http://localhost:8001/chat-stream \
  -F "text=请简单介绍营养均衡" \
  -F "language=zh" \
  -F "user_name=张三"
```

## 六、配置说明

### 修改 Dify 配置

编辑 `ai_voice_service_vixtts.py`：

```python
# Dify 工作流配置
DIFY_API_URL = "http://10.0.0.10:3099/v1/chat/completions"
DIFY_API_KEY = "http://10.0.0.10:180/v1|app-bzBAseue8wuzdhSCG8O05fkI|Chat"
DIFY_MODEL = "dify"
```

### 修改服务端口

```python
SERVICE_PORT = 8001  # 改为其他端口
```

### 修改 Whisper 模型大小

```python
WHISPER_MODEL = "small"  # 可选: tiny, base, small, medium, large
```

## 七、功能特性

### ✅ 已实现功能

1. **语音识别（ASR）**
   - 使用本地 Whisper 模型
   - 支持中文、英文、越南语
   - 自动音频格式转换

2. **大语言模型（LLM）- 智能语言路由**
   - **中文/英文**: Dify 工作流（主服务）
   - **越南语**: Ollama（Dify 不支持时）
   - 自动故障切换到备用服务

3. **语音合成（TTS）**
   - 使用 pyttsx3（完全离线）
   - 快速响应
   - 支持多语言

4. **流式响应**
   - 实时文本输出
   - 完成后生成音频
   - Server-Sent Events

5. **用户上下文**
   - 支持用户名传递
   - 可扩展更多上下文信息

### 🔄 智能语言路由

```
用户输入 + 语言参数
    ↓
├─ language="zh" → Dify 工作流
├─ language="en" → Dify 工作流
└─ language="vi" → Ollama（Dify 不支持越南语）
    ↓
如果主服务失败 → 自动切换到备用 Ollama
```

## 八、故障排查

### 问题 1: 服务无法启动

**症状**: 运行脚本后立即退出

**解决方案**:
1. 检查 Python 版本: `python --version`
2. 检查依赖安装: `pip list | grep fastapi`
3. 查看错误日志

### 问题 2: Dify 连接失败

**症状**: 日志显示 "Dify 工作流失败"

**解决方案**:
1. 检查 Dify 服务是否运行
2. 测试连接: `curl http://10.0.0.10:3099/v1/chat/completions`
3. 检查 API Key 是否正确
4. 服务会自动切换到备用 Ollama
5. **注意**: 越南语会直接使用 Ollama（Dify 不支持）

### 问题 3: 语音识别失败

**症状**: 音频上传后无响应

**解决方案**:
1. 检查 ffmpeg 安装: `ffmpeg -version`
2. 确认音频格式支持
3. 查看日志中的详细错误

### 问题 4: 语音合成无声音

**症状**: 返回音频但无法播放

**解决方案**:
1. Windows 需要安装中文语音包
2. 检查 pyttsx3 安装: `pip show pyttsx3`
3. 测试系统语音: 运行 `python -c "import pyttsx3; engine = pyttsx3.init(); engine.say('测试'); engine.runAndWait()"`

### 问题 5: 端口被占用

**症状**: "Address already in use"

**解决方案**:
1. 查找占用进程: `netstat -ano | findstr :8001`
2. 结束进程或修改端口配置

### 问题 6: 越南语响应质量差

**症状**: 越南语对话不准确

**解决方案**:
1. 越南语自动使用 Ollama（Dify 不支持）
2. 确认 Ollama 服务正常运行
3. 可以尝试更换支持越南语的 Ollama 模型
4. 查看日志确认路由到了 Ollama

## 九、性能优化

### 1. Whisper 模型选择

| 模型 | 大小 | 速度 | 准确度 |
|------|------|------|--------|
| tiny | 39M | 最快 | 较低 |
| base | 74M | 快 | 中等 |
| small | 244M | 中等 | 良好 |
| medium | 769M | 慢 | 很好 |
| large | 1550M | 最慢 | 最佳 |

**推荐**: 
- 开发测试: `tiny` 或 `base`
- 生产环境: `small` 或 `medium`

### 2. 并发处理

服务使用 FastAPI 的异步处理，支持多个并发请求。

### 3. 缓存优化

- Whisper 模型在启动时预加载
- 避免重复加载模型

## 十、集成到现有项目

### 在 Django 项目中调用

```python
import requests
import base64

def get_ai_voice_response(text, user_name="用户"):
    """调用语音服务获取 AI 回复"""
    try:
        response = requests.post(
            'http://localhost:8001/chat',
            data={
                'text': text,
                'language': 'zh',
                'user_name': user_name
            },
            timeout=120
        )
        
        if response.status_code == 200:
            data = response.json()
            return {
                'text': data['text'],
                'audio_base64': data['audio']
            }
    except Exception as e:
        print(f"语音服务调用失败: {e}")
        return None
```

### 在前端页面中调用

参考 `test_voice_ui.html` 中的实现。

## 十一、下一步

1. ✅ 服务已启动
2. ✅ 测试基本功能
3. 🔄 集成到您的应用
4. 🔄 根据需求调整配置
5. 🔄 监控服务运行状态

## 十二、相关文档

- 详细文档: `DIFY_INTEGRATION_README.md`
- 测试脚本: `test_dify_integration.py`
- 测试页面: `test_voice_ui.html`
- 启动脚本: `start_dify_service.bat`

## 十三、技术支持

如遇问题：
1. 查看日志输出
2. 运行测试脚本诊断
3. 检查配置文件
4. 参考详细文档

---

**祝您使用愉快！** 🎉

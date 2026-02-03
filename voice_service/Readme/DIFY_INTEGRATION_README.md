# AI 语音服务 - Dify 工作流集成说明

## 概述

本服务已成功集成 Dify 工作流，并实现了智能语言路由：

- **语音识别（ASR）**: 使用本地 Whisper 模型
- **大语言模型（LLM）**: 
  - **中文/英文** → Dify 工作流 API
  - **越南语** → Ollama（因为 Dify 不支持越南语）
- **语音合成（TTS）**: 使用本地 pyttsx3 引擎
- **智能路由**: 根据语言自动选择最佳 LLM 服务

## 语言路由策略

```
用户输入语言检测
    ↓
├─ 中文 (zh) → Dify 工作流
├─ 英文 (en) → Dify 工作流
└─ 越南语 (vi) → Ollama（Dify 不支持）
    ↓
如果 Dify 失败 → 自动切换到 Ollama
```

## 配置信息

### Dify 工作流配置

```python
DIFY_API_URL = "http://10.0.0.10:3099/v1/chat/completions"
DIFY_API_KEY = "http://10.0.0.10:180/v1|app-bzBAseue8wuzdhSCG8O05fkI|Chat"
DIFY_MODEL = "dify"
```

### 备用 Ollama 配置

```python
OLLAMA_HOST = "http://10.0.0.10:11434"
OLLAMA_MODEL = "qwen2.5:7b"
```

### 服务端口

```
SERVICE_PORT = 8001
```

## 启动服务

### 方法 1: 使用批处理脚本（推荐）

```bash
start_dify_service.bat
```

### 方法 2: 直接运行 Python

```bash
cd voice_service
python ai_voice_service_vixtts.py
```

## API 接口

### 1. 健康检查

**请求:**
```
GET http://localhost:8001/health
```

**响应:**
```json
{
  "status": "ok",
  "llm_service": "Dify Workflow (中文/英文) + Ollama (越南语)",
  "dify_api": "http://10.0.0.10:3099/v1/chat/completions",
  "dify_model": "dify",
  "dify_languages": ["zh", "en"],
  "ollama_host": "http://10.0.0.10:11434",
  "ollama_model": "qwen2.5:7b",
  "ollama_languages": ["vi", "fallback"],
  "supported_languages": ["zh-cn", "en", "vi"],
  "mode": "智能语言路由 + 本地语音",
  "routing": {
    "zh": "Dify Workflow",
    "en": "Dify Workflow",
    "vi": "Ollama (Dify 不支持越南语)"
  }
}
```

### 2. 语音识别

**请求:**
```
POST http://localhost:8001/transcribe
Content-Type: multipart/form-data

audio: <音频文件>
language: zh (可选，默认 zh)
```

**响应:**
```json
{
  "text": "识别出的文本"
}
```

### 3. 文本对话（非流式）

**请求:**
```
POST http://localhost:8001/chat
Content-Type: multipart/form-data

text: 你好，请介绍一下健康饮食
language: zh (可选，默认 zh)
user_name: 张三 (可选，默认 "用户")
audio: <音频文件> (可选，如果提供则先进行语音识别)
```

**响应:**
```json
{
  "text": "AI 回复的文本",
  "audio": "base64编码的音频数据",
  "recognized_text": "如果提供了音频，这里是识别出的文本"
}
```

### 4. 流式对话

**请求:**
```
POST http://localhost:8001/chat-stream
Content-Type: multipart/form-data

text: 请介绍一下营养均衡
language: zh (可选，默认 zh)
user_name: 张三 (可选，默认 "用户")
```

**响应（Server-Sent Events）:**
```
data: {"text": "文本片段1"}

data: {"text": "文本片段2"}

data: {"audio": "base64音频数据", "done": true}
```

## 工作流程

### 智能语言路由

```
用户输入（带语言参数）
    ↓
语言检测
    ↓
├─ 中文/英文 → Dify 工作流
└─ 越南语 → Ollama（Dify 不支持）
    ↓
如果失败 → 自动切换到备用服务
```

### 文本输入流程（中文/英文）

```
用户文本输入
    ↓
Dify 工作流处理
    ↓
返回 AI 回复
    ↓
pyttsx3 语音合成
    ↓
返回文本 + 音频
```

### 文本输入流程（越南语）

```
用户文本输入
    ↓
Ollama 处理（qwen2.5:7b）
    ↓
返回 AI 回复
    ↓
pyttsx3 语音合成
    ↓
返回文本 + 音频
```

### 语音输入流程

```
用户语音输入
    ↓
Whisper 语音识别
    ↓
Dify 工作流处理
    ↓
返回 AI 回复
    ↓
pyttsx3 语音合成
    ↓
返回识别文本 + 回复文本 + 音频
```

### 流式对话流程

```
用户文本输入
    ↓
Dify 工作流（流式）
    ↓
实时返回文本片段
    ↓
文本完成后生成语音
    ↓
返回完整音频
```

## Dify 工作流集成细节

### 请求格式

```python
payload = {
    "model": "dify",
    "messages": [
        {
            "role": "system",
            "content": f"用户名：{user_name}"
        },
        {
            "role": "user",
            "content": text
        }
    ],
    "max_tokens": 2000,
    "temperature": 0.7,
    "stream": False  # 或 True（流式）
}

headers = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {DIFY_API_KEY}"
}
```

### 响应解析

**非流式响应:**
```python
result = response.json()
reply = result.get("choices", [{}])[0].get("message", {}).get("content", "")
```

**流式响应:**
```python
for line in response.iter_lines():
    if line.startswith('data: '):
        data = json.loads(line[6:])
        content = data.get("choices", [{}])[0].get("delta", {}).get("content", "")
```

### 错误处理

- 如果 Dify 工作流不可用，自动切换到备用 Ollama 服务
- 支持最多 3 次重试，每次重试间隔递增
- 详细的日志记录，便于调试

## 测试

### 运行测试脚本

```bash
cd voice_service
python test_dify_integration.py
```

测试脚本会自动测试：
1. ✅ 健康检查
2. ⚠️ 语音识别（需要音频文件）
3. ✅ 文本对话（Dify 工作流）
4. ✅ 流式对话（Dify 工作流）

### 手动测试

#### 测试健康检查
```bash
curl http://localhost:8001/health
```

#### 测试文本对话
```bash
curl -X POST http://localhost:8001/chat \
  -F "text=你好，请介绍一下健康饮食" \
  -F "language=zh" \
  -F "user_name=测试用户"
```

#### 测试流式对话
```bash
curl -X POST http://localhost:8001/chat-stream \
  -F "text=请简单介绍营养均衡" \
  -F "language=zh" \
  -F "user_name=测试用户"
```

## 与 repo.html 的集成

在 `main/templates/repo.html` 中，AI 分析功能已经使用了相同的 Dify 工作流配置：

```javascript
const OPENAI_API_URL = 'http://10.0.0.10:3099/v1/chat/completions';
const OPENAI_API_KEY = 'http://10.0.0.10:180/v1|app-bzBAseue8wuzdhSCG8O05fkI|Chat';
```

现在语音服务也使用相同的配置，确保了一致性。

## 优势

1. **智能语言路由**: 根据语言自动选择最佳 LLM 服务
   - 中文/英文 → Dify 工作流（更强大）
   - 越南语 → Ollama（Dify 不支持时的最佳选择）
2. **高可用性**: 自动备用到 Ollama
3. **完全本地化**: 语音识别和合成都在本地运行
4. **流式支持**: 实时返回 AI 响应
5. **真正的多语言支持**: 中文、英文、越南语都有最佳方案
6. **用户上下文**: 支持传递用户名等上下文信息

## 故障排查

### Dify 连接失败

1. 检查 Dify API 地址是否正确
2. 检查 API Key 是否有效
3. 检查网络连接
4. 查看日志中的详细错误信息

### 越南语不工作

**症状**: 越南语对话没有响应或响应质量差

**解决方案**:
1. 越南语会自动使用 Ollama 服务（Dify 不支持）
2. 确认 Ollama 服务运行正常
3. 检查 Ollama 模型是否支持越南语
4. 查看日志确认路由到了 Ollama

1. 检查 Ollama 服务是否运行
2. 检查 Ollama 地址和端口
3. 确认模型已下载

### 备用 Ollama 也失败

**症状**: Dify 和 Ollama 都无法使用

1. 检查 Whisper 模型是否已下载
2. 检查 ffmpeg 是否安装
3. 确认音频格式正确

### 语音合成失败

1. 检查 pyttsx3 是否安装
2. Windows 系统需要安装中文语音包
3. 查看日志中的错误信息

## 日志

服务运行时会输出详细日志：

```
2026-02-03 10:00:00 - INFO - AI 语音助手服务启动中（Dify 工作流 + 本地语音）...
2026-02-03 10:00:00 - INFO - LLM 服务: Dify Workflow
2026-02-03 10:00:00 - INFO - Dify API: http://10.0.0.10:3099/v1/chat/completions
2026-02-03 10:00:00 - INFO - 预加载 Whisper 模型...
2026-02-03 10:00:05 - INFO - ✅ Whisper 模型加载完成
```

## 更新日志

### 2026-02-03
- ✅ 集成 Dify 工作流 API
- ✅ 添加备用 Ollama 服务
- ✅ 支持用户名上下文传递
- ✅ 优化流式响应处理
- ✅ 添加详细的错误处理和日志
- ✅ 创建测试脚本和文档

## 联系方式

如有问题，请查看日志文件或联系开发团队。

# 🌐 智能语言路由说明

## 概述

语音服务实现了智能语言路由功能，根据用户输入的语言自动选择最合适的 LLM 服务。

## 为什么需要语言路由？

**问题**: Dify 工作流主要支持中文和英文，对越南语的支持有限或不支持。

**解决方案**: 实现智能语言路由，根据语言参数自动选择最佳的 LLM 服务。

## 路由策略

### 语言 → LLM 服务映射

| 语言 | 语言代码 | 主服务 | 备用服务 | 说明 |
|------|---------|--------|---------|------|
| 中文 | `zh` | Dify 工作流 | Ollama | Dify 对中文支持优秀 |
| 英文 | `en` | Dify 工作流 | Ollama | Dify 对英文支持优秀 |
| 越南语 | `vi` | Ollama | - | Dify 不支持，直接使用 Ollama |

### 路由流程图

```
用户请求 (text + language)
    ↓
检测 language 参数
    ↓
    ├─ language = "zh" 或 "en"
    │   ↓
    │   尝试 Dify 工作流
    │   ↓
    │   ├─ 成功 → 返回结果
    │   └─ 失败 → 切换到 Ollama
    │
    └─ language = "vi"
        ↓
        直接使用 Ollama
        ↓
        返回结果
```

## 代码实现

### 核心路由逻辑

```python
async def chat_with_dify(text: str, user_name: str = "用户", language: str = "zh") -> str:
    """与 Dify 工作流对话（非流式）
    
    注意：Dify 主要支持中文和英文，越南语会自动使用 Ollama
    """
    # 越南语直接使用 Ollama（Dify 可能不支持）
    if language == "vi":
        logger.info("检测到越南语，直接使用 Ollama 服务")
        return await chat_with_ollama_fallback(text, language)
    
    # 中文/英文使用 Dify
    try:
        # ... Dify API 调用 ...
    except Exception as e:
        # 失败时切换到 Ollama
        return await chat_with_ollama_fallback(text, language)
```

### 流式对话路由

```python
@app.post("/chat-stream")
async def chat_stream(text: str, language: str, user_name: str):
    async def generate():
        # 越南语直接使用 Ollama（非流式）
        if language == "vi":
            logger.info("检测到越南语，使用 Ollama 服务（非流式）")
            reply_text = await chat_with_ollama_fallback(text, language)
            # 分块发送...
            return
        
        # 中文/英文使用 Dify（流式）
        # ... Dify 流式 API 调用 ...
```

## 使用示例

### 中文对话（使用 Dify）

```python
import requests

response = requests.post(
    'http://localhost:8001/chat',
    data={
        'text': '你好，请介绍一下健康饮食',
        'language': 'zh',  # 中文 → Dify 工作流
        'user_name': '张三'
    }
)
```

**日志输出:**
```
INFO - 收到请求 - language: zh, user: 张三
INFO - 发送到 Dify 工作流: 你好，请介绍一下健康饮食...
INFO - Dify 回复: 健康饮食是指...
```

### 英文对话（使用 Dify）

```python
response = requests.post(
    'http://localhost:8001/chat',
    data={
        'text': 'Hello, please introduce healthy eating',
        'language': 'en',  # 英文 → Dify 工作流
        'user_name': 'John'
    }
)
```

**日志输出:**
```
INFO - 收到请求 - language: en, user: John
INFO - 发送到 Dify 工作流: Hello, please introduce...
INFO - Dify 回复: Healthy eating refers to...
```

### 越南语对话（使用 Ollama）

```python
response = requests.post(
    'http://localhost:8001/chat',
    data={
        'text': 'Xin chào, hãy giới thiệu về dinh dưỡng lành mạnh',
        'language': 'vi',  # 越南语 → Ollama
        'user_name': 'Nguyen'
    }
)
```

**日志输出:**
```
INFO - 收到请求 - language: vi, user: Nguyen
INFO - 检测到越南语，直接使用 Ollama 服务
INFO - 发送到 Ollama (备用/越南语): Xin chào...
INFO - Ollama 回复: Dinh dưỡng lành mạnh...
```

## 优势

### 1. 最佳性能
- 中文/英文使用 Dify 工作流，获得更好的响应质量
- 越南语使用 Ollama，确保可用性

### 2. 高可用性
- 自动故障切换
- 即使 Dify 不可用，仍可使用 Ollama

### 3. 透明路由
- 用户无需关心底层实现
- 只需指定语言参数即可

### 4. 易于扩展
- 可以轻松添加更多语言
- 可以配置不同语言的不同服务

## 配置

### 当前配置

```python
# Dify 工作流配置（中文/英文）
DIFY_API_URL = "http://10.0.0.10:3099/v1/chat/completions"
DIFY_API_KEY = "http://10.0.0.10:180/v1|app-bzBAseue8wuzdhSCG8O05fkI|Chat"
DIFY_MODEL = "dify"

# Ollama 配置（越南语 + 备用）
OLLAMA_HOST = "http://10.0.0.10:11434"
OLLAMA_MODEL = "qwen2.5:7b"
```

### 添加新语言

如果要添加新语言（例如日语），可以修改路由逻辑：

```python
async def chat_with_dify(text: str, user_name: str = "用户", language: str = "zh") -> str:
    # 不支持的语言使用 Ollama
    if language in ["vi", "ja", "ko"]:  # 越南语、日语、韩语
        logger.info(f"检测到 {language}，使用 Ollama 服务")
        return await chat_with_ollama_fallback(text, language)
    
    # 其他语言使用 Dify
    # ...
```

## 监控和调试

### 查看路由决策

通过日志可以清楚看到路由决策：

```bash
# 中文请求
INFO - 收到请求 - language: zh
INFO - 发送到 Dify 工作流...

# 越南语请求
INFO - 收到请求 - language: vi
INFO - 检测到越南语，直接使用 Ollama 服务
INFO - 发送到 Ollama (备用/越南语)...
```

### 健康检查

```bash
curl http://localhost:8001/health
```

返回的 `routing` 字段显示路由配置：

```json
{
  "routing": {
    "zh": "Dify Workflow",
    "en": "Dify Workflow",
    "vi": "Ollama (Dify 不支持越南语)"
  }
}
```

## 性能对比

| 语言 | 服务 | 响应时间 | 质量 | 备注 |
|------|------|---------|------|------|
| 中文 | Dify | ~2-3秒 | ⭐⭐⭐⭐⭐ | 专门优化 |
| 英文 | Dify | ~2-3秒 | ⭐⭐⭐⭐⭐ | 专门优化 |
| 越南语 | Ollama | ~3-5秒 | ⭐⭐⭐⭐ | 通用模型 |

## 故障切换

### 场景 1: Dify 服务不可用

```
用户请求（中文）
    ↓
尝试 Dify 工作流
    ↓
连接失败
    ↓
自动切换到 Ollama
    ↓
返回结果
```

**日志:**
```
ERROR - Dify 工作流失败: Connection refused
INFO - 尝试使用备用 Ollama 服务...
INFO - Ollama 回复: ...
```

### 场景 2: Ollama 也不可用

```
用户请求（越南语）
    ↓
尝试 Ollama
    ↓
连接失败
    ↓
返回错误信息
```

**日志:**
```
ERROR - Ollama 备用服务也失败: Connection refused
ERROR - AI 对话失败
```

## 最佳实践

### 1. 语言参数准确性

确保传递正确的语言参数：
- `zh` - 中文
- `en` - 英文
- `vi` - 越南语

### 2. 监控服务状态

定期检查两个服务的健康状态：
```bash
# 检查 Dify
curl http://10.0.0.10:3099/v1/chat/completions

# 检查 Ollama
curl http://10.0.0.10:11434/api/tags
```

### 3. 日志分析

定期查看日志，了解路由分布：
```bash
# 统计 Dify 使用次数
grep "发送到 Dify 工作流" service.log | wc -l

# 统计 Ollama 使用次数
grep "使用 Ollama 服务" service.log | wc -l
```

## 未来扩展

### 可能的改进

1. **动态路由配置**
   - 从配置文件读取路由规则
   - 支持运行时修改

2. **负载均衡**
   - 多个 Dify 实例
   - 多个 Ollama 实例

3. **智能路由**
   - 根据响应时间自动选择
   - 根据服务负载自动切换

4. **更多语言支持**
   - 日语、韩语、泰语等
   - 为每种语言配置最佳服务

## 总结

智能语言路由确保了：
- ✅ 中文/英文获得最佳 Dify 体验
- ✅ 越南语有可靠的 Ollama 支持
- ✅ 自动故障切换保证高可用性
- ✅ 透明的路由决策，易于调试

这种设计让语音服务真正支持多语言，同时为每种语言提供最佳的 AI 服务。

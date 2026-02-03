# 修复 Ollama 连接问题

## 当前错误

```
ERROR - Ollama 备用服务也失败: All connection attempts failed
```

## 诊断步骤

### 1. 测试 Ollama 连接

```bash
# 测试远程 Ollama
curl http://10.0.0.10:11434/api/tags

# 测试本地 Ollama
curl http://localhost:11434/api/tags
```

### 2. 检查 Ollama 是否运行

```bash
# Windows
tasklist | findstr ollama

# 或者检查端口
netstat -ano | findstr :11434
```

## 解决方案

### 方案 1: Ollama 在本机运行

如果 Ollama 在你的电脑上运行，修改配置：

**编辑 `ai_voice_service_vixtts.py`，第 45 行:**

```python
# 改为本地地址
OLLAMA_HOST = "http://localhost:11434"
```

### 方案 2: Ollama 在其他机器

确认 Ollama 服务器地址和端口，然后修改配置。

### 方案 3: 启动 Ollama 服务

如果 Ollama 未运行：

```bash
# 启动 Ollama
ollama serve
```

### 方案 4: 安装 Ollama

如果未安装 Ollama：

1. 下载: https://ollama.ai/download
2. 安装后运行: `ollama serve`
3. 下载模型: `ollama pull qwen2.5:7b`

### 方案 5: 暂时禁用越南语（使用 Dify）

如果不需要越南语，或者 Dify 也支持越南语，可以让越南语也使用 Dify：

**编辑 `ai_voice_service_vixtts.py`，找到 `chat_with_dify` 函数:**

```python
async def chat_with_dify(text: str, user_name: str = "用户", language: str = "zh") -> str:
    # 注释掉这几行，让越南语也使用 Dify
    # if language == "vi":
    #     logger.info("检测到越南语，直接使用 Ollama 服务")
    #     return await chat_with_ollama_fallback(text, language)
    
    try:
        # ... 继续使用 Dify
```

## 快速测试

修改后，运行测试：

```bash
cd voice_service
python test_ollama_connection.py
```

应该看到：
```
✅ Ollama 服务运行正常
```

## 重启服务

```bash
# 停止当前服务 (Ctrl+C)
# 重新启动
python ai_voice_service_vixtts.py
```

## 验证

发送越南语请求：

```bash
curl -X POST http://localhost:8001/chat \
  -F "text=Xin chào" \
  -F "language=vi"
```

应该看到日志：
```
INFO - 发送到 Ollama: Xin chào...
INFO - Ollama 回复: ...
```

## 我的建议

**最简单的方案**: 让越南语也使用 Dify（如果 Dify 支持的话），这样就不需要 Ollama 了。

或者确认 Ollama 的正确地址并修改配置。

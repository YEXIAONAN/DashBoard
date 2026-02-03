# Ollama 502 Bad Gateway 错误修复

## 问题描述

在使用 AI 语音助手时，遇到 502 Bad Gateway 错误：
```
HTTP Request: POST http://172.16.4.181:11434/api/generate "HTTP/1.1 502 Bad Gateway"
```

## 根本原因

**Ollama 服务器的流式端点（stream=true）返回 502 错误，但非流式端点正常工作。**

测试结果：
- ✅ `/api/tags` - 正常（200）
- ✅ `/api/generate` (stream=false) - 正常（200）
- ❌ `/api/generate` (stream=true) - 失败（502）

可能原因：
1. Ollama 前面有反向代理（Nginx/HAProxy）不支持流式响应
2. 防火墙/负载均衡器阻止了长连接
3. Ollama 服务配置问题

## 解决方案（已实施）

### 方案：改用非流式模式 + 模拟流式输出

修改 `ai_voice_service_vixtts.py`：

1. **添加配置开关**：
```python
# 使用非流式模式（流式模式在某些 Ollama 配置下会返回 502）
USE_STREAMING = False
```

2. **修改 `/chat-stream` 端点**：
   - 使用 `stream=False` 调用 Ollama
   - 一次性获取完整响应
   - 在客户端分块发送，模拟流式效果
   - 保留重试机制（最多 3 次，指数退避）

3. **优势**：
   - ✅ 避免 502 错误
   - ✅ 保持客户端流式体验
   - ✅ 保留自动重试机制
   - ✅ 无需修改 Ollama 服务器配置

## 测试验证

```bash
# 测试非流式请求（应该成功）
python voice_service/test_stream_direct.py

# 重启服务
# 停止旧进程
Stop-Process -Id <PID> -Force

# 启动新服务
.\.venv\Scripts\python.exe voice_service\ai_voice_service_vixtts.py
```

## 代码改动摘要

**修改文件**：`voice_service/ai_voice_service_vixtts.py`

**主要改动**：
```python
# 原来：流式请求
payload = {"model": OLLAMA_MODEL, "prompt": text, "stream": True}
async with client.stream("POST", f"{OLLAMA_HOST}/api/generate", json=payload) as response:
    async for line in response.aiter_lines():
        # 处理流式响应

# 现在：非流式请求 + 模拟流式
payload = {"model": OLLAMA_MODEL, "prompt": text, "stream": False}
response = await client.post(f"{OLLAMA_HOST}/api/generate", json=payload)
full_text = response.json().get("response", "")

# 分块发送模拟流式效果
for i in range(0, len(full_text), chunk_size):
    chunk = full_text[i:i+chunk_size]
    yield f"data: {json.dumps({'text': chunk})}\n\n"
```

## 长期解决方案（可选）

如果需要真正的流式响应，需要在 Ollama 服务器端修复：

### 选项 1：检查反向代理配置

如果 Ollama 前面有 Nginx，添加流式支持：

```nginx
location /api/generate {
    proxy_pass http://ollama_backend;
    proxy_buffering off;  # 关键：禁用缓冲
    proxy_cache off;
    proxy_http_version 1.1;
    proxy_set_header Connection "";
    chunked_transfer_encoding on;
}
```

### 选项 2：直接访问 Ollama

如果可能，绕过反向代理直接访问 Ollama 服务。

### 选项 3：升级 Ollama

确保使用最新版本的 Ollama，可能已修复流式问题。

## 监控建议

观察日志中的请求信息：
- 成功：`收到 Ollama 响应，长度: XXX 字符`
- 失败：会自动重试，最多 3 次
- 如果频繁失败，检查 Ollama 服务器状态

## 当前状态

✅ **已修复** - 服务现在使用非流式模式，避免 502 错误
✅ **保持用户体验** - 客户端仍然看到流式输出效果
✅ **自动重试** - 遇到临时问题会自动重试

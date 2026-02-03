# AI 语音助手部署说明

## 1. 安装依赖
```bash
pip install -r requirements_ai_voice.txt
```

## 2. 启动服务

### Windows
```bash
start_ai_voice.bat
```

### Linux/Mac
```bash
python ai_voice_service.py
```

## 3. 访问前端
打开浏览器访问 Django 页面：
```
http://localhost:8000/ai_health_advisor/
```

## 4. 配置说明

### 修改服务地址（ai_voice_service.py）
```python
OLLAMA_HOST = "http://172.16.4.181:11434"  # Ollama 地址
OLLAMA_MODEL = "qwen2.5:7b"                # 模型名称
ASR_HOST = "http://127.0.0.1:9001"         # ASR 服务
TTS_HOST = "http://127.0.0.1:9002"         # TTS 服务
SERVICE_PORT = 8001                         # 本服务端口
```

### 修改前端 API 地址（ai_health_advisor.html）
```javascript
const API_URL = 'http://127.0.0.1:8001/chat';
```

## 5. ASR/TTS 服务接口规范

### ASR 接口
```
POST http://127.0.0.1:9001/transcribe
Content-Type: multipart/form-data

audio: [wav file]

Response:
{
  "text": "识别的文本"
}
```

### TTS 接口
```
POST http://127.0.0.1:9002/synthesize
Content-Type: application/json

{
  "text": "要合成的文本"
}

Response: audio/wav binary
```

## 6. 测试
```bash
curl http://127.0.0.1:8001/health
```

## 7. 故障排查
- 确保 Ollama 服务运行
- 确保 ASR/TTS 服务运行
- 检查防火墙和端口占用
- 查看浏览器控制台错误

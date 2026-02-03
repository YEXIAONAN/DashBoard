# 🚀 快速参考卡

## 一键启动

```bash
cd voice_service
start_hybrid.bat
```

## 服务地址

```
http://localhost:8001
```

## 健康检查

```bash
curl http://localhost:8001/health
```

## 支持的语言

| 语言 | 代码 | TTS 引擎 | 状态 |
|------|------|----------|------|
| 中文 | `zh` | XTTS v2 | ✅ |
| 英文 | `en` | XTTS v2 | ✅ |
| 越南语 | `vi` | MMS-TTS | ✅ |

## API 端点

### 语音识别
```
POST /transcribe
- audio: 音频文件
- language: zh|en|vi
```

### 流式对话
```
POST /chat-stream
- text: 用户输入
- language: zh|en|vi
```

### 统一聊天
```
POST /chat
- text: 文本 (可选)
- audio: 音频 (可选)
- language: zh|en|vi
```

## 文件位置

- **服务**: `ai_voice_service_hybrid.py`
- **启动**: `start_hybrid.bat`
- **测试**: `test_hybrid_service.py`
- **文档**: `START_HERE_FINAL.md`

## 测试命令

```bash
# 测试依赖
..\.venv\Scripts\python.exe -c "from TTS.api import TTS; from transformers import VitsModel; print('✅ OK')"

# 测试服务
..\.venv\Scripts\python.exe test_hybrid_service.py
```

## 故障排除

### PyTorch 版本
```bash
pip install "torch>=2.0.0,<2.6.0"
```

### transformers 版本
```bash
pip install transformers==4.33.0 tokenizers==0.13.3
```

### ffmpeg
```bash
choco install ffmpeg
```

## 状态

✅ **所有语言测试通过**  
✅ **完全离线运行**  
✅ **生产就绪**  

---

**需要帮助？** 查看 `START_HERE_FINAL.md`

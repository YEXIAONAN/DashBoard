# gTTS 解决方案 - 立即支持越南语

## 概述

由于你的系统没有安装越南语 TTS 语音包，我创建了一个使用 **gTTS (Google Text-to-Speech)** 的版本，可以**立即使用**，完美支持越南语。

## 优势

✅ **立即可用**: 无需安装 Windows 语音包
✅ **完美支持越南语**: Google 的越南语 TTS 质量很高
✅ **支持所有语言**: 中文、英文、越南语都有高质量语音
✅ **简单**: 只需安装一个 Python 包

## 劣势

⚠️ **需要网络连接**: 每次合成语音都需要访问 Google 服务器
⚠️ **稍慢**: 比本地 TTS 慢 1-2 秒
⚠️ **依赖 Google**: 如果 Google 服务不可用则无法工作

## 安装步骤

### 1. 安装 gTTS

```bash
pip install gtts
```

### 2. 启动服务

```bash
cd voice_service
start_gtts_service.bat
```

或直接运行：
```bash
python ai_voice_service_gtts.py
```

### 3. 测试

```bash
curl -X POST http://localhost:8001/chat \
  -F "text=Xin chào, bạn khỏe không?" \
  -F "language=vi" \
  -F "user_name=Nguyen"
```

## 与 pyttsx3 版本对比

| 特性 | pyttsx3 版本 | gTTS 版本 |
|------|-------------|-----------|
| 越南语支持 | ❌ 需要安装语音包 | ✅ 原生支持 |
| 网络需求 | ✅ 完全离线 | ⚠️ 需要网络 |
| 语音质量 | 中等 | 高 |
| 响应速度 | 快 (~0.5秒) | 中等 (~2秒) |
| 安装难度 | 难（需要 Windows 语音包） | 易（一行命令） |
| 稳定性 | 高 | 中（依赖 Google） |

## 使用建议

### 短期方案（立即使用）
使用 **gTTS 版本**：
- 立即可用
- 完美支持越南语
- 适合开发和测试

### 长期方案（生产环境）
安装 **Windows 越南语语音包** + 使用 pyttsx3 版本：
- 完全离线
- 更快的响应
- 更稳定

## 切换版本

### 使用 gTTS 版本
```bash
python ai_voice_service_gtts.py
```

### 使用 pyttsx3 版本（需要安装语音包）
```bash
python ai_voice_service_vixtts.py
```

## 配置

两个版本使用相同的配置：
- Dify API: `http://10.0.0.10:3099/v1/chat/completions`
- Ollama: `http://10.0.0.10:11434`
- 端口: `8001`

## 健康检查

```bash
curl http://localhost:8001/health
```

gTTS 版本返回：
```json
{
  "status": "ok",
  "tts": "gTTS (Google Text-to-Speech, 需要网络)",
  "tts_support": "完美支持中文、英文、越南语",
  "note": "gTTS 需要网络连接"
}
```

## 测试示例

### 中文
```bash
curl -X POST http://localhost:8001/chat \
  -F "text=你好，请介绍一下健康饮食" \
  -F "language=zh"
```

### 英文
```bash
curl -X POST http://localhost:8001/chat \
  -F "text=Hello, please introduce healthy eating" \
  -F "language=en"
```

### 越南语 ✅
```bash
curl -X POST http://localhost:8001/chat \
  -F "text=Xin chào, hãy giới thiệu về dinh dưỡng lành mạnh" \
  -F "language=vi"
```

## 日志示例

```
INFO - 开始合成语音 (gTTS): Xin chào..., 语言: vi
INFO - 使用 gTTS 语言: vi
INFO - gTTS 生成 MP3: /tmp/tmpxxx.mp3
INFO - ✅ 语音合成完成 (gTTS): 45678 bytes
```

## 故障排查

### 问题 1: gTTS 安装失败

```bash
pip install --upgrade pip
pip install gtts
```

### 问题 2: 网络连接失败

**症状**: `gTTS 失败: Connection error`

**解决方案**:
1. 检查网络连接
2. 检查是否需要代理
3. 尝试使用 VPN
4. 检查防火墙设置

### 问题 3: 语音生成慢

**原因**: gTTS 需要访问 Google 服务器

**优化**:
1. 使用更快的网络
2. 考虑缓存常用语音
3. 长期使用建议安装 Windows 语音包

### 问题 4: Google 服务不可用

**解决方案**:
1. 使用 VPN
2. 安装 Windows 越南语语音包
3. 使用其他 TTS 服务（Azure, AWS）

## 性能对比

### pyttsx3（本地）
- 响应时间: ~0.5秒
- 网络: 不需要
- 质量: 中等

### gTTS（在线）
- 响应时间: ~2秒
- 网络: 需要
- 质量: 高

## 推荐使用场景

### 使用 gTTS 版本
- ✅ 开发和测试
- ✅ 无法安装 Windows 语音包
- ✅ 需要高质量越南语
- ✅ 网络连接稳定

### 使用 pyttsx3 版本
- ✅ 生产环境
- ✅ 需要离线运行
- ✅ 需要快速响应
- ✅ 已安装 Windows 语音包

## 下一步

1. **立即使用**: 运行 `start_gtts_service.bat`
2. **测试越南语**: 发送越南语请求
3. **长期规划**: 考虑安装 Windows 语音包

## 总结

gTTS 版本是一个**立即可用**的解决方案，完美支持越南语。虽然需要网络连接，但对于开发和测试来说是最快的方案。

如果你需要生产环境使用，建议按照 `INSTALL_VIETNAMESE_TTS.md` 安装 Windows 越南语语音包。

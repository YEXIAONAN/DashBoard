# AI 语音助手 - 离线版本说明
# AI Voice Assistant - Offline Version Guide

## 📚 文档索引 / Documentation Index

### 核心文档 / Core Documents

1. **OFFLINE_TTS_SETUP.md** - 离线 TTS 完整配置指南
   - 详细的安装步骤
   - 两种 TTS 方案对比
   - 故障排除指南

2. **TTS_COMPARISON.md** - TTS 引擎详细对比
   - 性能测试结果
   - 使用场景推荐
   - 成本分析

3. **MULTILINGUAL_SUPPORT.md** - 多语言支持文档
   - API 接口说明
   - 技术实现细节
   - 配置说明

4. **QUICK_START_MULTILINGUAL.md** - 快速开始指南
   - 基础使用教程
   - 常见问题解答

## 🚀 快速选择方案

### 我应该使用哪个版本？

```
有网络环境？
├─ 是 → 使用 Edge TTS (ai_voice_service_offline.py)
│        ✅ 最佳质量
│        ✅ 最简单
│        ✅ 推荐！
│
└─ 否 → 需要离线
    │
    ├─ 对质量要求高？
    │  ├─ 是 → 使用 Coqui TTS (ai_voice_service_fully_offline.py)
    │  │        ✅ 高质量
    │  │        ⚠️ 需要下载 1.8GB 模型
    │  │        ⚠️ 需要较好的硬件
    │  │
    │  └─ 否 → 使用 pyttsx3 (ai_voice_service_fully_offline.py)
    │           ✅ 简单快速
    │           ✅ 低资源占用
    │           ⚠️ 质量较低
```

## 📦 可用的服务版本

### 1. ai_voice_service_offline.py (推荐)

**特点：**
- 使用 Edge TTS（在线）
- 最佳语音质量
- 支持多语言
- 需要网络连接

**启动：**
```bash
python ai_voice_service_offline.py
# 或
start_offline.bat
```

**适用场景：**
- 生产环境（有网络）
- 对质量要求高
- 快速部署

### 2. ai_voice_service_fully_offline.py (完全离线)

**特点：**
- 支持 pyttsx3 或 Coqui TTS
- 完全离线运行
- 支持多语言
- 无需网络连接

**启动：**
```bash
python ai_voice_service_fully_offline.py
# 或
start_fully_offline.bat
```

**配置 TTS 引擎：**
```python
# 编辑 ai_voice_service_fully_offline.py

# 使用 pyttsx3（默认）
TTS_ENGINE = "pyttsx3"

# 或使用 Coqui TTS
TTS_ENGINE = "coqui"
```

**适用场景：**
- 离线环境
- 内网部署
- 对隐私要求高

## 🔧 安装步骤

### 方案 1: Edge TTS (在线)

```bash
# 1. 安装依赖
pip install -r requirements_offline.txt

# 2. 启动服务
python ai_voice_service_offline.py
```

### 方案 2: pyttsx3 (离线)

```bash
# 1. 安装依赖
pip install -r requirements_fully_offline.txt

# Windows 额外依赖
pip install pywin32

# Linux 额外依赖
sudo apt-get install espeak

# 2. 配置引擎
# 编辑 ai_voice_service_fully_offline.py
TTS_ENGINE = "pyttsx3"

# 3. 启动服务
python ai_voice_service_fully_offline.py
```

### 方案 3: Coqui TTS (离线高质量)

```bash
# 1. 安装依赖
pip install -r requirements_fully_offline.txt
pip install TTS

# 2. 下载模型（首次运行自动下载）
python -c "from TTS.api import TTS; TTS(model_name='tts_models/multilingual/multi-dataset/xtts_v2')"

# 3. 配置引擎
# 编辑 ai_voice_service_fully_offline.py
TTS_ENGINE = "coqui"

# 4. 启动服务
python ai_voice_service_fully_offline.py
```

## 📊 方案对比

| 特性 | Edge TTS | Coqui TTS | pyttsx3 |
|------|----------|-----------|---------|
| 语音质量 | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐ |
| 安装难度 | ⭐ | ⭐⭐⭐ | ⭐ |
| 资源占用 | 低 | 高 | 很低 |
| 网络需求 | 需要 | 不需要 | 不需要 |
| 模型大小 | 0MB | 1.8GB | 0MB |
| 启动速度 | 快 | 慢 | 很快 |
| 合成速度 | 快 | 中等 | 很快 |

## 🧪 测试工具

### 1. 对比测试

```bash
# 测试所有 TTS 引擎
python test_tts_comparison.py
```

生成音频文件，可以直接播放对比质量。

### 2. 多语言测试

```bash
# 测试多语言功能
python test_multilingual.py
```

测试中文、英文、越南语的完整流程。

### 3. 健康检查

```bash
# 检查服务状态
curl http://172.16.4.181:8001/health
```

## 📝 配置文件说明

### requirements_offline.txt
- Edge TTS 版本的依赖
- 包含 edge-tts、whisper 等

### requirements_fully_offline.txt
- 完全离线版本的依赖
- 包含 pyttsx3、可选 Coqui TTS

### requirements_ai_voice.txt
- 原始版本（已弃用）

## 🔄 版本迁移

### 从在线版迁移到离线版

```bash
# 1. 停止当前服务
# Ctrl+C

# 2. 安装离线依赖
pip install -r requirements_fully_offline.txt

# 3. 选择 TTS 引擎
# 编辑 ai_voice_service_fully_offline.py

# 4. 启动新服务
python ai_voice_service_fully_offline.py
```

**前端无需修改！** API 接口完全兼容。

## 🎯 推荐配置

### 开发环境

```python
# ai_voice_service_fully_offline.py
TTS_ENGINE = "pyttsx3"
WHISPER_MODEL = "base"
```

**优点：** 快速启动，低资源占用

### 测试环境

```python
# ai_voice_service_offline.py
# 使用 Edge TTS（默认）
WHISPER_MODEL = "small"
```

**优点：** 接近生产环境，质量好

### 生产环境（有网络）

```python
# ai_voice_service_offline.py
# 使用 Edge TTS（默认）
WHISPER_MODEL = "small"
```

**优点：** 最佳质量，稳定可靠

### 生产环境（无网络）

```python
# ai_voice_service_fully_offline.py
TTS_ENGINE = "coqui"
WHISPER_MODEL = "small"
```

**优点：** 高质量离线方案

## 🆘 常见问题

### Q: 如何选择 TTS 引擎？

**A:** 
- 有网络 → Edge TTS
- 无网络 + 高质量 → Coqui TTS
- 无网络 + 快速 → pyttsx3

### Q: Coqui TTS 模型下载失败？

**A:** 
```bash
# 手动下载模型
mkdir -p ~/.local/share/tts
# 从 GitHub 下载模型文件
```

### Q: pyttsx3 没有中文语音？

**A:**
- Windows: 安装中文语音包（设置 → 语言）
- Linux: 安装 espeak-ng
- macOS: 系统自带中文语音

### Q: 如何提高语音质量？

**A:**
1. 使用 Edge TTS（最佳）
2. 使用 Coqui TTS + GPU
3. 调整 pyttsx3 语速和音量

## 📚 更多资源

- **详细配置：** 查看 `OFFLINE_TTS_SETUP.md`
- **性能对比：** 查看 `TTS_COMPARISON.md`
- **多语言支持：** 查看 `MULTILINGUAL_SUPPORT.md`
- **快速开始：** 查看 `QUICK_START_MULTILINGUAL.md`

## 🎉 开始使用

1. **选择方案** - 根据需求选择 TTS 引擎
2. **安装依赖** - 按照上述步骤安装
3. **启动服务** - 运行对应的 Python 文件
4. **测试功能** - 使用测试脚本验证

祝使用愉快！🚀

---

**版本 / Version:** 1.0.0  
**最后更新 / Last Updated:** 2026-01-31  
**维护者 / Maintainer:** AI Voice Service Team

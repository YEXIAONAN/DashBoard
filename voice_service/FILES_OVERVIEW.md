# 📁 Coqui TTS 文件清单
# Coqui TTS Files Overview

## 🎯 核心文件（必需）

| 文件 | 说明 | 状态 |
|------|------|------|
| `ai_voice_service_fully_offline.py` | 完全离线服务（已配置 Coqui TTS） | ✅ 已配置 |
| `requirements_fully_offline.txt` | 依赖清单（包含 TTS） | ✅ 已更新 |
| `start_coqui_tts.bat` | Windows 启动脚本 | ✅ 新建 |

## 📚 文档文件

### 快速开始

| 文件 | 说明 | 适合人群 |
|------|------|---------|
| `START_HERE.md` | 🌟 从这里开始 | 所有人 |
| `INSTALL_COQUI.md` | 快速安装指南 | 新手 |
| `README_COQUI.md` | Coqui TTS 总览 | 所有人 |

### 详细指南

| 文件 | 说明 | 适合人群 |
|------|------|---------|
| `COQUI_TTS_GUIDE.md` | 完整配置指南 | 高级用户 |
| `TTS_COMPARISON.md` | 三种方案对比 | 决策者 |
| `OFFLINE_TTS_SETUP.md` | 离线 TTS 通用指南 | 技术人员 |

### 多语言支持

| 文件 | 说明 | 适合人群 |
|------|------|---------|
| `MULTILINGUAL_SUPPORT.md` | 多语言技术文档 | 开发者 |
| `QUICK_START_MULTILINGUAL.md` | 多语言快速指南 | 用户 |

### 其他文档

| 文件 | 说明 |
|------|------|
| `README_OFFLINE.md` | 离线版本总览 |
| `FILES_OVERVIEW.md` | 本文件 |

## 🧪 测试文件

| 文件 | 说明 | 用途 |
|------|------|------|
| `test_coqui_tts.py` | Coqui TTS 专用测试 | 验证安装 |
| `test_tts_comparison.py` | 三种 TTS 对比测试 | 性能对比 |
| `test_multilingual.py` | 多语言功能测试 | 功能测试 |

## 🚀 启动脚本

| 文件 | 说明 | TTS 引擎 |
|------|------|---------|
| `start_coqui_tts.bat` | Coqui TTS 启动 | Coqui TTS |
| `start_fully_offline.bat` | 通用离线启动 | pyttsx3/Coqui |
| `start_offline.bat` | Edge TTS 启动 | Edge TTS |

## 📦 依赖文件

| 文件 | 说明 | 包含内容 |
|------|------|---------|
| `requirements_fully_offline.txt` | 完全离线依赖 | TTS, Whisper, FastAPI |
| `requirements_offline.txt` | Edge TTS 依赖 | edge-tts, Whisper |
| `requirements_ai_voice.txt` | 原始依赖（已弃用） | - |

## 🔧 服务文件

| 文件 | 说明 | 模式 |
|------|------|------|
| `ai_voice_service_fully_offline.py` | 完全离线服务 | Coqui/pyttsx3 |
| `ai_voice_service_offline.py` | Edge TTS 服务 | Edge TTS |
| `ai_voice_service.py` | 原始服务（已弃用） | - |

## 📖 阅读顺序推荐

### 新手用户

1. `START_HERE.md` - 快速开始
2. `INSTALL_COQUI.md` - 安装步骤
3. `README_COQUI.md` - 了解功能
4. 运行 `test_coqui_tts.py` - 测试

### 高级用户

1. `README_COQUI.md` - 总览
2. `COQUI_TTS_GUIDE.md` - 详细配置
3. `TTS_COMPARISON.md` - 性能对比
4. `OFFLINE_TTS_SETUP.md` - 深入了解

### 开发者

1. `ai_voice_service_fully_offline.py` - 源码
2. `COQUI_TTS_GUIDE.md` - API 文档
3. `MULTILINGUAL_SUPPORT.md` - 技术细节
4. `test_coqui_tts.py` - 测试代码

## 🎯 快速查找

### 我想...

| 需求 | 查看文件 |
|------|---------|
| 快速开始 | `START_HERE.md` |
| 安装 Coqui TTS | `INSTALL_COQUI.md` |
| 了解配置选项 | `COQUI_TTS_GUIDE.md` |
| 对比不同方案 | `TTS_COMPARISON.md` |
| 测试功能 | `test_coqui_tts.py` |
| 启动服务 | `start_coqui_tts.bat` |
| 解决问题 | `COQUI_TTS_GUIDE.md` 故障排除 |
| 语音克隆 | `COQUI_TTS_GUIDE.md` 语音克隆 |
| GPU 加速 | `COQUI_TTS_GUIDE.md` 性能优化 |
| 多语言支持 | `MULTILINGUAL_SUPPORT.md` |

## 📊 文件大小

| 类型 | 数量 | 说明 |
|------|------|------|
| 文档文件 | 12 个 | Markdown 格式 |
| Python 文件 | 4 个 | 服务和测试 |
| 批处理文件 | 3 个 | Windows 启动脚本 |
| 配置文件 | 3 个 | 依赖清单 |

## 🗂️ 文件组织

```
voice_service/
├── 📖 快速开始
│   ├── START_HERE.md ⭐
│   ├── INSTALL_COQUI.md
│   └── README_COQUI.md
│
├── 📚 详细文档
│   ├── COQUI_TTS_GUIDE.md
│   ├── TTS_COMPARISON.md
│   ├── OFFLINE_TTS_SETUP.md
│   ├── MULTILINGUAL_SUPPORT.md
│   └── QUICK_START_MULTILINGUAL.md
│
├── 🚀 启动脚本
│   ├── start_coqui_tts.bat ⭐
│   ├── start_fully_offline.bat
│   └── start_offline.bat
│
├── 🧪 测试文件
│   ├── test_coqui_tts.py ⭐
│   ├── test_tts_comparison.py
│   └── test_multilingual.py
│
├── 🔧 服务文件
│   ├── ai_voice_service_fully_offline.py ⭐
│   └── ai_voice_service_offline.py
│
└── 📦 依赖文件
    ├── requirements_fully_offline.txt ⭐
    └── requirements_offline.txt
```

## ⭐ 重点文件（标记 ⭐）

这些是使用 Coqui TTS 最重要的文件：

1. `START_HERE.md` - 从这里开始
2. `start_coqui_tts.bat` - 一键启动
3. `ai_voice_service_fully_offline.py` - 核心服务
4. `requirements_fully_offline.txt` - 依赖清单
5. `test_coqui_tts.py` - 测试脚本

## 🎉 开始使用

```bash
# 1. 阅读快速开始
cat START_HERE.md

# 2. 运行启动脚本
start_coqui_tts.bat

# 3. 测试功能
python test_coqui_tts.py
```

---

**版本:** 1.0.0  
**更新:** 2026-01-31

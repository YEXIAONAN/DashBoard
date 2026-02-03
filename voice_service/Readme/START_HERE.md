# 🎯 从这里开始 - Coqui TTS 版本
# START HERE - Coqui TTS Edition

## ⚡ 3 分钟快速开始

### 步骤 1: 打开终端

```bash
cd voice_service
```

### 步骤 2: 运行启动脚本

```bash
# Windows
start_coqui_tts.bat

# 脚本会自动：
# ✓ 检查 Python 环境
# ✓ 安装所有依赖
# ✓ 下载 Coqui TTS 模型（1.8GB）
# ✓ 启动服务
```

### 步骤 3: 等待完成

首次运行需要下载模型，请耐心等待 10-30 分钟。

看到以下信息表示成功：

```
========================================
配置信息：
  TTS 引擎: Coqui TTS (高质量离线)
  服务地址: http://172.16.4.181:8001
  健康检查: http://172.16.4.181:8001/health
  模式: 完全离线
========================================
```

## ✅ 验证安装

打开浏览器，访问你的 AI 助手页面，选择语言并测试语音功能。

或者运行测试脚本：

```bash
python test_coqui_tts.py
```

## 📚 文档导航

| 如果你想... | 查看这个文档 |
|------------|-------------|
| 快速安装 | **INSTALL_COQUI.md** ⭐ |
| 了解详细配置 | **COQUI_TTS_GUIDE.md** |
| 对比不同方案 | **TTS_COMPARISON.md** |
| 查看完整说明 | **README_COQUI.md** |
| 测试功能 | 运行 `test_coqui_tts.py` |

## 🎯 配置已完成

以下配置已经为你设置好：

✅ `ai_voice_service_fully_offline.py` - TTS_ENGINE = "coqui"  
✅ `requirements_fully_offline.txt` - 包含 TTS==0.22.0  
✅ `start_coqui_tts.bat` - 一键启动脚本  
✅ `test_coqui_tts.py` - 测试脚本  

**你只需要运行启动脚本即可！**

## ⚠️ 注意事项

### 首次运行

- 需要下载 1.8GB 模型
- 需要 10-30 分钟
- 需要稳定的网络连接

### Windows 用户

如果遇到编译错误，需要安装：
- Microsoft C++ Build Tools
- 下载：https://visualstudio.microsoft.com/visual-cpp-build-tools/

### 性能优化

如果有 NVIDIA GPU，安装 CUDA 版本的 PyTorch：

```bash
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118
```

速度提升 3-5 倍！

## 🚀 下一步

1. ✅ 运行 `start_coqui_tts.bat`
2. ✅ 等待模型下载完成
3. ✅ 测试语音功能
4. ✅ 享受高质量离线语音！

## 💡 提示

- 首次合成语音可能需要 5-8 秒
- 后续会更快（2-3 秒）
- 使用 GPU 会更快（1-2 秒）
- 完全离线，无需网络

## 🆘 遇到问题？

1. 查看 **INSTALL_COQUI.md** 的故障排除部分
2. 运行 `python test_coqui_tts.py` 诊断问题
3. 检查日志输出

## 🎉 准备好了吗？

```bash
cd voice_service
start_coqui_tts.bat
```

**就这么简单！** 🚀

---

**版本:** 1.0.0  
**更新:** 2026-01-31

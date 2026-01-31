# Coqui TTS 快速安装指南
# Quick Installation Guide for Coqui TTS

## 🚀 一键安装（推荐）

### Windows

```bash
cd voice_service
start_coqui_tts.bat
```

脚本会自动完成所有安装步骤！

## 📋 手动安装步骤

### 步骤 1: 安装基础依赖

```bash
cd voice_service
pip install -r requirements_fully_offline.txt
```

### 步骤 2: 安装 Coqui TTS

```bash
pip install TTS==0.22.0
```

**注意（Windows）：** 如果遇到编译错误，需要安装 Microsoft C++ Build Tools：
- 下载地址：https://visualstudio.microsoft.com/visual-cpp-build-tools/
- 安装时选择 "Desktop development with C++"

### 步骤 3: 下载模型

```bash
python -c "from TTS.api import TTS; TTS(model_name='tts_models/multilingual/multi-dataset/xtts_v2')"
```

**注意：**
- 模型大小约 1.8GB
- 首次下载需要 10-30 分钟
- 需要稳定的网络连接

### 步骤 4: 测试安装

```bash
python test_coqui_tts.py
```

### 步骤 5: 启动服务

```bash
python ai_voice_service_fully_offline.py
```

## ✅ 验证安装

访问健康检查接口：

```bash
curl http://172.16.4.181:8001/health
```

应该看到：

```json
{
  "status": "ok",
  "tts": "coqui (fully offline)",
  "mode": "完全离线 / Fully Offline"
}
```

## 🎯 GPU 加速（可选）

如果有 NVIDIA GPU，安装 CUDA 版本的 PyTorch：

```bash
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118
```

验证 GPU：

```python
import torch
print(f"CUDA 可用: {torch.cuda.is_available()}")
```

## 🔧 配置确认

确保 `ai_voice_service_fully_offline.py` 中的配置正确：

```python
TTS_ENGINE = "coqui"  # 确保设置为 coqui
```

## 📝 依赖清单

核心依赖：
- TTS==0.22.0
- torch>=1.13.0
- numpy>=1.24.3
- scipy>=1.11.4
- soundfile>=0.12.1

## ❓ 常见问题

### Q: 模型下载失败？
**A:** 检查网络连接，或使用代理：
```bash
set HTTP_PROXY=http://proxy:port
set HTTPS_PROXY=http://proxy:port
```

### Q: 编译错误（Windows）？
**A:** 安装 Microsoft C++ Build Tools

### Q: 内存不足？
**A:** 
- 关闭其他程序
- 使用更小的模型
- 升级内存

### Q: 合成速度慢？
**A:**
- 安装 GPU 版本的 PyTorch
- 使用更小的模型
- 升级硬件

## 📚 更多帮助

- 详细配置：查看 `COQUI_TTS_GUIDE.md`
- 故障排除：查看 `OFFLINE_TTS_SETUP.md`
- 性能对比：查看 `TTS_COMPARISON.md`

## 🎉 完成！

安装完成后，你就可以使用高质量的离线语音合成了！

```bash
# 启动服务
python ai_voice_service_fully_offline.py

# 或使用批处理文件
start_coqui_tts.bat
```

---

**版本:** 1.0.0  
**更新:** 2026-01-31

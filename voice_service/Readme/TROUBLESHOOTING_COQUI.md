# Coqui TTS 故障排除指南
# Coqui TTS Troubleshooting Guide

## 🔴 常见错误 1: BeamSearchScorer 导入失败

### 错误信息

```
ERROR - Coqui TTS 初始化失败: cannot import name 'BeamSearchScorer' from 'transformers'
```

### 原因

`transformers` 库版本太新，Coqui TTS 0.22.0 需要 `transformers==4.33.0`。

### 解决方案

#### 方法 1: 使用修复脚本（推荐）

```bash
cd voice_service
fix_coqui_tts.bat
```

#### 方法 2: 手动修复

```bash
# 1. 卸载冲突的包
pip uninstall -y transformers tokenizers

# 2. 安装兼容版本
pip install transformers==4.33.0 tokenizers==0.13.3

# 3. 验证
python -c "from TTS.api import TTS; from transformers import BeamSearchScorer; print('✓ 修复成功')"
```

#### 方法 3: 重新安装所有依赖

```bash
# 1. 卸载所有相关包
pip uninstall -y TTS transformers tokenizers

# 2. 重新安装
pip install -r requirements_fully_offline.txt
```

### 验证修复

```bash
python -c "from TTS.api import TTS; print('Coqui TTS 可以正常使用')"
```

---

## 🔴 常见错误 2: Microsoft C++ Build Tools 缺失

### 错误信息

```
error: Microsoft Visual C++ 14.0 or greater is required
```

### 解决方案

1. 下载 Microsoft C++ Build Tools
   - 地址：https://visualstudio.microsoft.com/visual-cpp-build-tools/

2. 安装时选择：
   - "Desktop development with C++"
   - 或 "C++ build tools"

3. 重启电脑

4. 重新安装 Coqui TTS：
   ```bash
   pip install TTS==0.22.0
   ```

---

## 🔴 常见错误 3: 模型下载失败

### 错误信息

```
ConnectionError: Failed to download model
```

### 解决方案

#### 方法 1: 使用代理

```bash
# Windows CMD
set HTTP_PROXY=http://proxy:port
set HTTPS_PROXY=http://proxy:port

# Windows PowerShell
$env:HTTP_PROXY="http://proxy:port"
$env:HTTPS_PROXY="http://proxy:port"

# 重新下载
python -c "from TTS.api import TTS; TTS(model_name='tts_models/multilingual/multi-dataset/xtts_v2')"
```

#### 方法 2: 手动下载

1. 访问：https://github.com/coqui-ai/TTS/releases
2. 下载模型文件
3. 放到：`C:\Users\Administrator\AppData\Local\tts\`

#### 方法 3: 使用国内镜像（如果可用）

```bash
# 设置 Hugging Face 镜像
set HF_ENDPOINT=https://hf-mirror.com

# 重新下载
python -c "from TTS.api import TTS; TTS(model_name='tts_models/multilingual/multi-dataset/xtts_v2')"
```

---

## 🔴 常见错误 4: CUDA 内存不足

### 错误信息

```
RuntimeError: CUDA out of memory
```

### 解决方案

#### 方法 1: 强制使用 CPU

编辑 `ai_voice_service_fully_offline.py`：

```python
def load_coqui_tts():
    global coqui_tts
    if coqui_tts is None:
        from TTS.api import TTS
        import torch
        
        # 强制使用 CPU
        torch.cuda.is_available = lambda: False
        
        tts = TTS(model_name="tts_models/multilingual/multi-dataset/xtts_v2")
        return tts
```

#### 方法 2: 使用更小的模型

```python
# 使用语言专用模型（更小）
tts = TTS(model_name="tts_models/zh-CN/baker/tacotron2-DDC-GST")
```

#### 方法 3: 清理 GPU 缓存

```python
import torch
torch.cuda.empty_cache()
```

---

## 🔴 常见错误 5: 服务启动后回退到 pyttsx3

### 症状

日志显示：
```
WARNING - 将回退到 pyttsx3
```

### 原因

Coqui TTS 初始化失败，自动回退到 pyttsx3。

### 解决方案

1. 查看完整错误日志
2. 根据具体错误信息修复
3. 最常见的是 transformers 版本问题，运行：
   ```bash
   fix_coqui_tts.bat
   ```

---

## 🔴 常见错误 6: 合成速度非常慢

### 症状

合成一句话需要 10+ 秒

### 解决方案

#### 方法 1: 使用 GPU 加速

```bash
# 安装 CUDA 版本的 PyTorch
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118
```

#### 方法 2: 使用更小的模型

```python
# 中文专用模型（更快）
tts = TTS(model_name="tts_models/zh-CN/baker/tacotron2-DDC-GST")
```

#### 方法 3: 检查 CPU 占用

- 关闭其他程序
- 检查后台进程
- 升级硬件

---

## 🔴 常见错误 7: 语音质量差或有杂音

### 解决方案

1. **确保使用正确的语言代码**
   ```python
   # 正确
   tts.tts_to_file(text="你好", language="zh-cn")
   
   # 错误
   tts.tts_to_file(text="你好", language="zh")  # 应该是 zh-cn
   ```

2. **尝试不同的模型**
   ```python
   # 多语言模型
   tts = TTS(model_name="tts_models/multilingual/multi-dataset/xtts_v2")
   
   # 中文专用模型
   tts = TTS(model_name="tts_models/zh-CN/baker/tacotron2-DDC-GST")
   ```

3. **使用语音克隆**
   ```python
   tts.tts_to_file(
       text="你好",
       file_path="output.wav",
       speaker_wav="reference_voice.wav",  # 提供参考音频
       language="zh-cn"
   )
   ```

---

## 🔴 常见错误 8: 首次合成非常慢

### 症状

首次合成需要 8-10 秒，后续正常

### 原因

模型需要预热（加载到内存/GPU）

### 解决方案

在服务启动时预加载：

```python
@app.on_event("startup")
async def startup_event():
    logger.info("预加载 Coqui TTS 模型...")
    tts = load_coqui_tts()
    
    # 预热模型
    tts.tts_to_file(
        text="预热",
        file_path="warmup.wav",
        language="zh-cn"
    )
    os.remove("warmup.wav")
    
    logger.info("模型预热完成")
```

---

## 🔴 常见错误 9: 依赖冲突

### 错误信息

```
ERROR: pip's dependency resolver does not currently take into account all the packages that are installed
```

### 解决方案

```bash
# 1. 创建新的虚拟环境
python -m venv .venv_coqui
.venv_coqui\Scripts\activate

# 2. 安装依赖
pip install -r requirements_fully_offline.txt

# 3. 测试
python test_coqui_tts.py
```

---

## 🔴 常见错误 10: 许可证确认

### 症状

启动时提示：
```
> You must confirm the following:
| > "I have purchased a commercial license from Coqui: licensing@coqui.ai"
| > "Otherwise, I agree to the terms of the non-commercial CPML: https://coqui.ai/cpml" - [y/n]
```

### 解决方案

1. **非商业使用**：输入 `y` 并回车
2. **商业使用**：购买商业许可证

自动接受（仅用于测试）：

```python
import os
os.environ["COQUI_TOS_AGREED"] = "1"
```

---

## 📋 完整诊断流程

### 步骤 1: 运行诊断脚本

```bash
python test_coqui_tts.py
```

### 步骤 2: 检查版本

```bash
python -c "import TTS; print(f'TTS: {TTS.__version__}')"
python -c "import transformers; print(f'transformers: {transformers.__version__}')"
python -c "import torch; print(f'PyTorch: {torch.__version__}')"
```

### 步骤 3: 检查 GPU

```bash
python -c "import torch; print(f'CUDA 可用: {torch.cuda.is_available()}')"
```

### 步骤 4: 测试导入

```bash
python -c "from TTS.api import TTS; from transformers import BeamSearchScorer; print('✓ 所有导入正常')"
```

### 步骤 5: 测试合成

```bash
python -c "from TTS.api import TTS; tts = TTS(model_name='tts_models/multilingual/multi-dataset/xtts_v2'); tts.tts_to_file(text='测试', file_path='test.wav', language='zh-cn'); print('✓ 合成成功')"
```

---

## 🆘 仍然无法解决？

### 收集信息

```bash
# 1. Python 版本
python --version

# 2. 已安装的包
pip list > installed_packages.txt

# 3. 系统信息
systeminfo > system_info.txt

# 4. 错误日志
# 复制完整的错误信息
```

### 尝试替代方案

如果 Coqui TTS 无法工作，可以：

1. **使用 pyttsx3**（已自动回退）
   - 质量较低，但稳定可靠

2. **使用 Edge TTS**（需要网络）
   ```bash
   python ai_voice_service_offline.py
   ```

3. **等待 Coqui TTS 更新**
   - 关注：https://github.com/coqui-ai/TTS

---

## 📚 相关文档

- `INSTALL_COQUI.md` - 安装指南
- `COQUI_TTS_GUIDE.md` - 详细配置
- `fix_coqui_tts.bat` - 自动修复脚本
- `test_coqui_tts.py` - 测试脚本

---

**版本:** 1.0.0  
**更新:** 2026-01-31

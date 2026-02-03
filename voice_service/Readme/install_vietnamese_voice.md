# 安装越南语语音包指南

## 问题诊断

根据日志显示：
```
INFO - 系统可用语音数量: 3
INFO -   0: Microsoft David Desktop - English (United States)
INFO -   1: Microsoft Zira Desktop - English (United States)
INFO -   2: Microsoft Huihui Desktop - Chinese (Simplified)
WARNING - ⚠️ 未找到 vi 语音，使用默认语音
```

**问题**: pyttsx3 只能访问 3 个 Desktop 版本的语音，没有越南语语音。

虽然你的 Windows 语言设置显示已安装越南语语言包，但 **语音包（Text-to-Speech）和语言包是分开的**。

## 解决方案

### 方法 1: 安装 Windows 越南语语音包（推荐）

#### 步骤 1: 打开 Windows 设置
1. 按 `Win + I` 打开设置
2. 进入 **时间和语言** → **语音**

#### 步骤 2: 添加语音
1. 点击 **添加语音**
2. 搜索 "Vietnamese" 或"越南语"
3. 选择 **Microsoft An - Vietnamese (Vietnam)**
4. 点击安装

#### 步骤 3: 下载语音包
1. 进入 **时间和语言** → **语言和区域**
2. 找到 **Vietnamese** 语言
3. 点击 **...** → **语言选项**
4. 在 **语音** 部分，点击 **下载**
5. 等待下载完成（可能需要几分钟）

#### 步骤 4: 验证安装
运行测试脚本：
```bash
cd voice_service
python test_voice_selection.py
```

应该能看到：
```
✅ 找到: Microsoft An - Vietnamese (Vietnam)
```

### 方法 2: 使用在线 TTS 服务（备选）

如果无法安装语音包，可以使用在线 TTS 服务：

#### Azure Cognitive Services TTS
- 支持高质量越南语
- 需要 API Key
- 按使用量付费

#### Google Cloud Text-to-Speech
- 支持越南语
- 需要 API Key
- 按使用量付费

### 方法 3: 使用 gTTS（Google Text-to-Speech）

安装 gTTS：
```bash
pip install gtts
```

修改代码使用 gTTS（需要网络连接）：
```python
from gtts import gTTS

def text_to_speech_gtts(text: str, language: str = "zh") -> bytes:
    """使用 gTTS 生成语音"""
    lang_map = {
        "zh": "zh-CN",
        "en": "en",
        "vi": "vi"
    }
    
    tts = gTTS(text=text, lang=lang_map.get(language, "en"))
    
    with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as tmp_file:
        tmp_path = tmp_file.name
    
    tts.save(tmp_path)
    
    with open(tmp_path, 'rb') as f:
        audio_data = f.read()
    
    os.unlink(tmp_path)
    return audio_data
```

## 检查当前语音包

### PowerShell 命令
```powershell
# 列出所有已安装的语音
Get-WmiObject -Class Win32_SpeechVoice | Select-Object Name, Language

# 或者
Add-Type -AssemblyName System.Speech
$synth = New-Object System.Speech.Synthesis.SpeechSynthesizer
$synth.GetInstalledVoices() | ForEach-Object { $_.VoiceInfo }
```

### Python 脚本
```python
import pyttsx3

engine = pyttsx3.init()
voices = engine.getProperty('voices')

print(f"已安装 {len(voices)} 个语音:")
for i, voice in enumerate(voices):
    print(f"{i}. {voice.name}")
    print(f"   ID: {voice.id}")
    print(f"   Languages: {voice.languages}")
    print()
```

## 常见问题

### Q1: 为什么语言包已安装但没有语音？

**A**: Windows 语言包和语音包是分开的：
- **语言包**: 用于界面翻译、输入法等
- **语音包**: 用于 Text-to-Speech（TTS）

你需要单独安装语音包。

### Q2: pyttsx3 只能看到 3 个语音？

**A**: pyttsx3 使用 Windows SAPI5，只能访问系统注册的 TTS 语音。可能的原因：
1. 语音包未正确安装
2. 语音包未注册到 SAPI5
3. 需要重启系统

**解决方案**:
1. 重新安装语音包
2. 重启电脑
3. 运行 `test_voice_selection.py` 验证

### Q3: 如何手动下载语音包？

**A**: 
1. 访问 Microsoft Store
2. 搜索 "Vietnamese Language Pack"
3. 安装语言包和语音包
4. 重启系统

### Q4: 可以使用第三方越南语 TTS 吗？

**A**: 可以，推荐：
- **gTTS**: 免费，需要网络
- **Azure TTS**: 高质量，付费
- **Google Cloud TTS**: 高质量，付费
- **Coqui TTS**: 开源，本地运行

## 验证步骤

### 1. 运行详细测试
```bash
python test_voice_selection.py
```

### 2. 检查日志
重启服务后，发送越南语请求，查看日志：
```
INFO - === 所有可用语音详情 ===
INFO - 语音 0:
INFO -   名称: Microsoft David Desktop - English (United States)
INFO -   ID: ...
INFO -   语言: ...
INFO - 语音 1:
INFO -   名称: Microsoft An - Vietnamese (Vietnam)  # 应该看到这个
INFO -   ID: ...
INFO -   语言: ...
```

### 3. 测试越南语
```bash
curl -X POST http://localhost:8001/chat \
  -F "text=Xin chào" \
  -F "language=vi"
```

## 临时解决方案

在安装语音包之前，代码已经添加了备选方案：

```python
# 对于越南语，如果找不到专用语音，尝试使用英文语音
if language == "vi":
    logger.warning("⚠️ 越南语语音不可用，将使用英文语音（发音可能不准确）")
    # 尝试找一个英文语音
    for voice in voices:
        if 'english' in voice.name.lower():
            engine.setProperty('voice', voice.id)
            logger.info(f"使用英文语音作为备选: {voice.name}")
            break
```

这样至少能输出声音，虽然发音不准确。

## 推荐方案

### 短期（立即可用）
使用 gTTS（需要网络）：
```bash
pip install gtts
```

### 长期（最佳方案）
1. 安装 Windows 越南语语音包
2. 重启系统
3. 验证 pyttsx3 能访问

### 企业级（高质量）
使用 Azure Cognitive Services TTS：
- 高质量越南语
- 支持多种声音
- 可调节语速、音调
- 按使用量付费

## 下一步

1. **立即**: 运行 `python test_voice_selection.py` 查看详细信息
2. **短期**: 安装 Windows 越南语语音包
3. **验证**: 重启服务并测试
4. **备选**: 如果无法安装，考虑使用 gTTS

## 联系支持

如果问题仍然存在：
1. 提供 `test_voice_selection.py` 的完整输出
2. 提供服务日志中的 "=== 所有可用语音详情 ===" 部分
3. 确认 Windows 版本和语言设置

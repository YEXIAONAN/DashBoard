# 安装越南语 TTS 语音包 - 详细步骤

## 当前状态

✅ 已安装语音:
- Microsoft David Desktop - English (United States)
- Microsoft Zira Desktop - English (United States)
- Microsoft Huihui Desktop - Chinese (Simplified)

❌ 缺少语音:
- Microsoft An - Vietnamese (Vietnam)

## 安装步骤

### 方法 1: 通过 Windows 设置安装（推荐）

#### 步骤 1: 打开语音设置
1. 按 `Win + I` 打开 Windows 设置
2. 点击 **时间和语言**
3. 点击左侧的 **语音**

#### 步骤 2: 管理语音
1. 向下滚动找到 **管理语音** 部分
2. 点击 **添加语音** 按钮

#### 步骤 3: 搜索越南语语音
1. 在搜索框输入 "Vietnamese" 或 "越南语"
2. 找到 **Microsoft An - Vietnamese (Vietnam)**
3. 点击旁边的 **下载** 或 **安装** 按钮

#### 步骤 4: 等待下载
- 下载大小约 50-100 MB
- 需要网络连接
- 可能需要 5-10 分钟

#### 步骤 5: 重启电脑
⚠️ **重要**: 必须重启电脑才能让语音包生效！

#### 步骤 6: 验证安装
重启后运行：
```powershell
Add-Type -AssemblyName System.Speech
$synth = New-Object System.Speech.Synthesis.SpeechSynthesizer
$synth.GetInstalledVoices() | ForEach-Object { $_.VoiceInfo } | Where-Object { $_.Culture -like "*vi*" }
```

应该看到：
```
Name: Microsoft An Desktop
Culture: vi-VN
```

### 方法 2: 通过语言设置安装

#### 步骤 1: 打开语言设置
1. 按 `Win + I` 打开 Windows 设置
2. 点击 **时间和语言**
3. 点击 **语言和区域**

#### 步骤 2: 找到越南语
1. 在已安装的语言列表中找到 **Vietnamese (Tiếng Việt)**
2. 点击右侧的 **...** (三个点)
3. 选择 **语言选项**

#### 步骤 3: 下载语音
1. 在 **语音** 部分，查看是否有可下载的语音
2. 如果有 **Microsoft An** 或其他越南语语音，点击 **下载**
3. 等待下载完成

#### 步骤 4: 重启电脑
⚠️ **必须重启！**

### 方法 3: 使用 PowerShell 命令（高级）

```powershell
# 列出可用的语言包
Get-WindowsCapability -Online | Where-Object { $_.Name -like "*Language.Speech*vi*" }

# 安装越南语语音包（如果找到）
Add-WindowsCapability -Online -Name "Language.Speech~~~vi-VN~0.0.1.0"
```

## 验证安装

### 使用 PowerShell
```powershell
Add-Type -AssemblyName System.Speech
$synth = New-Object System.Speech.Synthesis.SpeechSynthesizer
$synth.GetInstalledVoices() | ForEach-Object { $_.VoiceInfo }
```

应该看到 4 个语音（包括越南语）。

### 使用 Python 测试脚本
```bash
cd voice_service
python test_voice_selection.py
```

应该看到：
```
✅ 找到: Microsoft An Desktop - Vietnamese (Vietnam)
```

### 测试语音服务
```bash
python ai_voice_service_vixtts.py
```

然后发送越南语请求：
```bash
curl -X POST http://localhost:8001/chat \
  -F "text=Xin chào" \
  -F "language=vi"
```

## 常见问题

### Q: 找不到"添加语音"按钮？
**A**: 可能是 Windows 版本问题。尝试：
1. 更新 Windows 到最新版本
2. 使用方法 2（语言选项）
3. 使用方法 3（PowerShell）

### Q: 下载失败？
**A**: 
1. 检查网络连接
2. 检查 Windows Update 服务是否运行
3. 尝试使用 VPN
4. 稍后重试

### Q: 安装后仍然找不到？
**A**:
1. **必须重启电脑**
2. 检查语音是否真的安装成功
3. 运行 PowerShell 验证命令

### Q: 我的 Windows 版本太旧？
**A**: 
- Windows 10 1803 及以上支持
- Windows 11 完全支持
- 如果版本太旧，考虑使用方案 2（gTTS）

## 如果无法安装

如果无法安装 Windows 语音包，请使用 **方案 2: gTTS**（见下一个文件）

# 🔧 越南语语音输出修复说明

## 问题描述

**症状**: 
- 越南语文本输入正常，LLM 返回越南语文本
- 但语音输出是英文发音，而不是越南语

**原因**:
- 代码中的 `text_to_speech_vixtts` 函数只针对中文选择语音
- 没有根据 `language` 参数为越南语选择正确的语音包
- 系统有越南语语音包（**Microsoft An - Vietnamese (Vietnam)**），但没有被使用

## 解决方案

### 修改内容

在 `text_to_speech_vixtts` 函数中添加了智能语音选择逻辑：

```python
# 语言关键词映射
language_keywords = {
    "zh": ['chinese', 'mandarin', 'zh-cn', 'huihui', 'kangkang', 'yaoyao', 'simplified'],
    "en": ['english', 'en-us', 'david', 'zira', 'mark'],
    "vi": ['vietnamese', 'vietnam', 'vi-vn', 'an']  # Microsoft An 是越南语语音
}

# 根据语言参数查找匹配的语音
keywords = language_keywords.get(language, [])

for voice in voices:
    voice_name_lower = voice.name.lower()
    voice_id_lower = voice.id.lower()
    
    if any(keyword in voice_name_lower or keyword in voice_id_lower for keyword in keywords):
        selected_voice = voice
        logger.info(f"✓ 找到 {language} 语音: {voice.name}")
        break
```

### 语音映射

| 语言 | 语言代码 | 关键词 | Windows 语音包 |
|------|---------|--------|---------------|
| 中文 | `zh` | chinese, mandarin, huihui, yaoyao, kangkang | Microsoft Huihui, Microsoft Yaoyao, Microsoft Kangkang |
| 英文 | `en` | english, david, zira, mark | Microsoft David, Microsoft Zira, Microsoft Mark |
| 越南语 | `vi` | vietnamese, vietnam, an | **Microsoft An - Vietnamese (Vietnam)** |

## 验证修复

### 方法 1: 运行测试脚本

```bash
cd voice_service
python test_voice_selection.py
```

这个脚本会：
1. 列出所有可用语音
2. 测试每种语言的语音匹配
3. 生成测试音频文件（test_zh.wav, test_en.wav, test_vi.wav）

### 方法 2: 测试完整服务

1. 启动服务：
```bash
python ai_voice_service_vixtts.py
```

2. 测试越南语对话：
```bash
curl -X POST http://localhost:8001/chat \
  -F "text=Xin chào, hãy giới thiệu về dinh dưỡng lành mạnh" \
  -F "language=vi" \
  -F "user_name=Nguyen"
```

3. 检查日志输出：
```
INFO - 开始合成语音 (pyttsx3): Xin chào..., 语言: vi
INFO - 系统可用语音数量: 10
INFO - ✓ 找到 vi 语音: Microsoft An - Vietnamese (Vietnam)
INFO - ✅ 使用语音: Microsoft An - Vietnamese (Vietnam)
INFO - ✅ 语音合成完成 (pyttsx3): 12345 bytes
```

### 方法 3: 使用测试页面

1. 打开 `test_voice_ui.html`
2. 选择语言：越南语
3. 输入越南语文本：`Xin chào, bạn khỏe không?`
4. 点击"发送文本"
5. 听音频输出，应该是越南语发音

## 日志示例

### 修复前（错误）

```
INFO - 开始合成语音 (pyttsx3): Xin chào..., 语言: vi
INFO - 系统可用语音数量: 10
WARNING - ⚠️ 未找到中文语音，使用默认语音（可能是英文）
INFO - ✅ 语音合成完成 (pyttsx3): 12345 bytes
```
❌ 使用了默认英文语音

### 修复后（正确）

```
INFO - 开始合成语音 (pyttsx3): Xin chào..., 语言: vi
INFO - 系统可用语音数量: 10
INFO - ✓ 找到 vi 语音: Microsoft An - Vietnamese (Vietnam)
INFO - ✅ 使用语音: Microsoft An - Vietnamese (Vietnam)
INFO - ✅ 语音合成完成 (pyttsx3): 12345 bytes
```
✅ 正确使用了越南语语音

## 系统可用语音

根据你的截图，系统有以下语音：

### 英文语音
- Microsoft David - English (United States)
- Microsoft Zira - English (United States)
- Microsoft Mark - English (United States)
- Microsoft David Desktop - English (United States)
- Microsoft Zira Desktop - English (United States)

### 中文语音
- Microsoft Huihui - Chinese (Simplified, PRC)
- Microsoft Yaoyao - Chinese (Simplified, PRC)
- Microsoft Kangkang - Chinese (Simplified, PRC)
- Microsoft Huihui Desktop - Chinese (Simplified)

### 越南语语音
- **Microsoft An - Vietnamese (Vietnam)** ✅

## 语音选择优先级

代码会按以下优先级选择语音：

1. **精确匹配**: 查找包含语言关键词的语音
2. **第一个匹配**: 如果有多个匹配，使用第一个
3. **默认语音**: 如果没有匹配，使用系统默认语音（并记录警告）

### 越南语示例

```python
# 越南语关键词
keywords = ['vietnamese', 'vietnam', 'vi-vn', 'an']

# 遍历所有语音
for voice in voices:
    if 'vietnamese' in voice.name.lower():  # 匹配 "Microsoft An - Vietnamese (Vietnam)"
        selected_voice = voice
        break
```

## 语速调整

代码还针对不同语言调整了语速：

```python
# 越南语可能需要稍慢一点
rate = 180 if language == "vi" else 200
engine.setProperty('rate', rate)
```

- 中文/英文: 200 (正常速度)
- 越南语: 180 (稍慢，发音更清晰)

## 故障排查

### 问题 1: 仍然使用英文语音

**检查步骤**:
1. 运行 `test_voice_selection.py` 确认能找到越南语语音
2. 检查日志中是否有 "✓ 找到 vi 语音" 消息
3. 确认传递的 `language` 参数是 `"vi"` 而不是其他值

### 问题 2: 找不到越南语语音

**解决方案**:
1. 确认 Windows 已安装越南语语音包
2. 在 Windows 设置中检查：设置 → 时间和语言 → 语音 → 管理语音
3. 如果没有，需要安装越南语语音包

### 问题 3: 语音质量差

**优化建议**:
1. 调整语速：修改 `rate` 参数（范围 0-400）
2. 调整音量：修改 `volume` 参数（范围 0.0-1.0）
3. 考虑使用更高质量的 TTS 引擎（如 Azure TTS）

## 完整工作流程

```
用户输入越南语文本
    ↓
language="vi" 参数传递
    ↓
Ollama 处理（返回越南语文本）
    ↓
text_to_speech_vixtts(text, language="vi")
    ↓
查找越南语语音（Microsoft An）
    ↓
使用 Microsoft An 合成语音
    ↓
返回越南语音频
```

## 测试用例

### 测试 1: 中文
```bash
curl -X POST http://localhost:8001/chat \
  -F "text=你好，请介绍一下健康饮食" \
  -F "language=zh"
```
预期：使用 Microsoft Huihui/Yaoyao 中文语音

### 测试 2: 英文
```bash
curl -X POST http://localhost:8001/chat \
  -F "text=Hello, please introduce healthy eating" \
  -F "language=en"
```
预期：使用 Microsoft David/Zira 英文语音

### 测试 3: 越南语
```bash
curl -X POST http://localhost:8001/chat \
  -F "text=Xin chào, hãy giới thiệu về dinh dưỡng lành mạnh" \
  -F "language=vi"
```
预期：使用 Microsoft An 越南语语音 ✅

## 代码改进点

### 1. 智能语音选择
- 根据语言参数自动选择
- 支持多个关键词匹配
- 详细的日志输出

### 2. 语速优化
- 越南语使用稍慢的语速
- 提高发音清晰度

### 3. 错误处理
- 找不到语音时记录警告
- 提供默认语音作为备选
- 返回空音频而不是崩溃

## 总结

修复后的语音服务现在能够：
- ✅ 正确识别越南语参数
- ✅ 自动选择 Microsoft An 越南语语音
- ✅ 生成正确的越南语音频输出
- ✅ 支持中文、英文、越南语三种语言
- ✅ 详细的日志便于调试

现在越南语对话应该能够正确输出越南语语音了！

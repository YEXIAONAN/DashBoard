# 🚨 Coqui TTS 快速修复
# Quick Fix for Coqui TTS

## ⚡ 你遇到的错误

```
ERROR - Coqui TTS 初始化失败: cannot import name 'BeamSearchScorer' from 'transformers'
```

## ✅ 快速解决（3 步）

### 步骤 1: 运行修复脚本

```bash
cd voice_service
fix_coqui_tts.bat
```

### 步骤 2: 等待完成

脚本会自动：
- 卸载冲突的 transformers
- 安装兼容版本 (4.33.0)
- 验证修复

### 步骤 3: 重启服务

```bash
python ai_voice_service_fully_offline.py
```

---

## 🔧 手动修复（如果脚本失败）

```bash
# 1. 卸载
pip uninstall -y transformers tokenizers

# 2. 安装兼容版本
pip install transformers==4.33.0 tokenizers==0.13.3

# 3. 验证
python -c "from TTS.api import TTS; print('✓ 修复成功')"

# 4. 重启服务
python ai_voice_service_fully_offline.py
```

---

## 📊 版本要求

| 包 | 版本 | 说明 |
|---|------|------|
| TTS | 0.22.0 | Coqui TTS |
| transformers | 4.33.0 | ⚠️ 必须此版本 |
| tokenizers | 0.13.3 | 与 transformers 兼容 |

---

## ✅ 验证修复

运行测试：

```bash
python test_coqui_tts.py
```

应该看到：

```
✓ Coqui TTS 已安装
✓ 模型加载完成
✓ 生成成功
🎉 所有测试通过！
```

---

## 🎯 现在可以使用了

```bash
# 启动服务
python ai_voice_service_fully_offline.py

# 或使用启动脚本
start_coqui_tts.bat
```

---

## 🆘 仍然有问题？

查看详细故障排除：`TROUBLESHOOTING_COQUI.md`

---

**快速修复完成！** 🚀

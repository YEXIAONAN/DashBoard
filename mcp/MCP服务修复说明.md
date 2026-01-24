# MCP 服务修复说明

## 问题描述
MCP 服务启动时出现错误：
```
TypeError: cannot specify both default and default_factory
```

## 问题原因
`fastmcp==2.7.1` 与新版本的 `pydantic` (v2.x) 存在兼容性问题。`fastmcp` 内部的 `settings.py` 中的 `ServerSettings` 类在定义字段时同时使用了 `default` 和 `default_factory`，这在新版 pydantic 中是不允许的。

## 解决方案
升级 `fastmcp` 到兼容版本，并明确指定 `pydantic` 版本范围。

### 修改前 (requirements.txt)
```txt
fastmcp==2.7.1
python-dotenv==1.1.0
pymysql==1.1.0
uvicorn[standard]==0.23.2
```

### 修改后 (requirements.txt)
```txt
fastmcp>=2.8.0
pydantic>=2.8.0
python-dotenv==1.1.0
pymysql==1.1.0
uvicorn[standard]==0.23.2
```

## 安装步骤
```bash
cd mcp
pip install -r requirements.txt --upgrade
```

## 验证
```bash
python main.py --help
```

应该看到正常的帮助信息，而不是错误。

## 实际安装的版本
- `fastmcp==2.12.5`
- `pydantic==2.12.5`
- `mcp==1.12.4`

## 注意事项
1. 如果在 Docker 环境中运行，需要重新构建镜像
2. 确保 `.env` 文件中的数据库配置正确
3. 服务默认运行在 `0.0.0.0:8020`

## 启动服务
```bash
python main.py
# 或指定参数
python main.py --host 0.0.0.0 --port 8020 --debug
```

## 测试接口
```bash
# 测试 REST 接口
curl "http://localhost:8020/get_monthly_nutrition?user_id=default"

# 按用户名查询
curl "http://localhost:8020/nutrition_by_name?user_name=张三"
```

---
**修复时间**: 2026-01-24  
**状态**: ✅ 已解决

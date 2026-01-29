# CORS 跨域问题解决方案

## 🔴 问题描述

前端页面在访问 MCP 服务时出现两个错误：

### 错误 1：CORS 跨域错误
```
Access to fetch at 'http://172.16.4.181:8120/nutrition_by_name?user_name=User1' 
from origin 'http://127.0.0.1:8000' has been blocked by CORS policy: 
No 'Access-Control-Allow-Origin' header is present on the requested resource.
```

### 错误 2：500 内部服务器错误
```
GET http://172.16.4.181:8120/nutrition_by_name?user_name=User1 
net::ERR_FAILED 500 (Internal Server Error)
```

---

## 🔍 问题分析

### 1. CORS 跨域问题
- **前端地址：** `http://127.0.0.1:8000` (Django 服务)
- **后端地址：** `http://172.16.4.181:8120` (MCP 服务)
- **问题：** 浏览器阻止了跨域请求

### 2. 500 错误可能的原因
- 数据库连接失败
- 用户名 "User1" 不存在
- SQL 查询错误
- 其他服务器内部错误

---

## ✅ 解决方案

### 方案 1：确保 MCP 服务运行在正确的端口（推荐）

#### 步骤 1：更新 .env 文件
```env
# mcp/.env
MYSQL_HOST="172.16.4.181"
MYSQL_PORT='6666'
MYSQL_USER="root"
MYSQL_PASSWORD="BigData#123.."
MYSQL_DATABASE="SDashboard"

# MCP 服务端口（新增）
HOST="0.0.0.0"
PORT=8120
DEBUG=True
```

#### 步骤 2：重启 MCP 服务
```bash
# 停止旧容器
docker stop <container_id>
docker rm <container_id>

# 重新构建并启动
cd mcp
docker build -t mcp-server .
docker run -d -p 8120:8120 --env-file .env --name mcp-server mcp-server

# 检查日志
docker logs -f mcp-server
```

#### 步骤 3：验证服务
```bash
# 测试 API 是否可访问
curl "http://172.16.4.181:8120/nutrition_by_name?user_name=User1"
```


### 方案 2：检查并修复 500 错误

#### 步骤 1：查看 Docker 日志
```bash
docker logs mcp-server

# 查找错误信息，特别是：
# - Database error
# - Connection refused
# - SQL syntax error
```

#### 步骤 2：测试数据库连接
```bash
# 进入容器
docker exec -it mcp-server bash

# 测试 MySQL 连接
mysql -h 172.16.4.181 -P 6666 -u root -p
# 输入密码：BigData#123..

# 测试查询
USE SDashboard;
SELECT * FROM users WHERE name = 'User1';
```

#### 步骤 3：检查用户是否存在
```sql
-- 查看所有用户
SELECT user_id, name FROM users;

-- 如果 User1 不存在，创建一个
INSERT INTO users (user_id, name) VALUES (1, 'User1');
```

---

### 方案 3：修改前端代码使用代理（备选）

如果不想处理 CORS，可以让 Django 作为代理。

#### 在 Django 中添加代理视图
```python
# main/views.py
import requests
from django.http import JsonResponse

def mcp_proxy(request):
    """代理 MCP 服务请求"""
    user_name = request.GET.get('user_name', '')
    
    try:
        # 转发请求到 MCP 服务
        response = requests.get(
            f'http://172.16.4.181:8120/nutrition_by_name',
            params={'user_name': user_name},
            timeout=10
        )
        return JsonResponse(response.json(), safe=False)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
```

#### 添加路由
```python
# main/urls.py 或 DashBoard/urls.py
from django.urls import path
from main.views import mcp_proxy

urlpatterns = [
    # ... 其他路由
    path('api/mcp/nutrition_by_name', mcp_proxy, name='mcp_proxy'),
]
```

#### 修改前端代码
```javascript
// 修改前
fetch(`http://172.16.4.181:8120/nutrition_by_name?user_name=${userName}`)

// 修改后（使用代理）
fetch(`/api/mcp/nutrition_by_name?user_name=${userName}`)
```

---

## 🧪 测试步骤

### 1. 测试 MCP 服务是否运行
```bash
# 检查端口是否监听
netstat -tuln | grep 8120

# 或者
curl http://172.16.4.181:8120/get_monthly_nutrition?user_id=default
```

### 2. 测试 CORS 是否生效
```bash
# 使用 curl 测试（带 Origin 头）
curl -H "Origin: http://127.0.0.1:8000" \
     -H "Access-Control-Request-Method: GET" \
     -H "Access-Control-Request-Headers: Content-Type" \
     -X OPTIONS \
     http://172.16.4.181:8120/nutrition_by_name

# 应该返回 CORS 头：
# Access-Control-Allow-Origin: *
# Access-Control-Allow-Methods: *
# Access-Control-Allow-Headers: *
```

### 3. 测试 API 返回数据
```bash
# 测试正常请求
curl "http://172.16.4.181:8120/nutrition_by_name?user_name=User1"

# 应该返回 JSON 数据或错误信息
```

### 4. 在浏览器中测试
```javascript
// 打开浏览器控制台，运行：
fetch('http://172.16.4.181:8120/nutrition_by_name?user_name=User1')
  .then(res => res.json())
  .then(data => console.log('成功:', data))
  .catch(err => console.error('失败:', err));
```

---

## 🔧 调试技巧

### 1. 启用 DEBUG 模式
```env
# mcp/.env
DEBUG=True
```

### 2. 查看详细日志
```bash
# 实时查看日志
docker logs -f mcp-server

# 查看最后 100 行
docker logs --tail 100 mcp-server
```

### 3. 检查网络连接
```bash
# 从 Django 容器测试 MCP 服务
docker exec -it <django_container> bash
curl http://172.16.4.181:8120/nutrition_by_name?user_name=User1
```

### 4. 使用浏览器开发者工具
- 打开 Network 标签
- 查看请求详情
- 检查 Response Headers 是否有 CORS 头
- 查看 Response 内容

---

## 📋 检查清单

### MCP 服务检查
- [ ] MCP 服务是否运行？
- [ ] 端口 8120 是否正确映射？
- [ ] .env 文件配置是否正确？
- [ ] CORS 中间件是否已添加？
- [ ] 数据库连接是否正常？

### 数据库检查
- [ ] 数据库地址是否正确？
- [ ] 数据库端口是否正确？
- [ ] 用户名密码是否正确？
- [ ] 数据库名称是否正确？
- [ ] 用户 "User1" 是否存在？

### 网络检查
- [ ] 防火墙是否阻止了 8120 端口？
- [ ] Docker 网络是否正常？
- [ ] 前端能否访问后端 IP？

---

## 💡 常见问题

### Q1: CORS 配置了但还是报错？
**A:** 检查：
1. 中间件是否正确添加
2. 服务是否重启
3. 浏览器缓存是否清除

### Q2: 500 错误但日志没有信息？
**A:** 
1. 启用 DEBUG 模式
2. 检查数据库连接
3. 测试 SQL 查询

### Q3: 本地测试正常，Docker 中不行？
**A:**
1. 检查 Docker 网络配置
2. 检查端口映射
3. 检查环境变量

---

## 🎯 推荐解决顺序

1. ✅ **更新 .env 文件**（设置 PORT=8120）
2. ✅ **重启 MCP 服务**
3. ✅ **查看 Docker 日志**（找出 500 错误原因）
4. ✅ **测试 API 端点**（curl 测试）
5. ✅ **检查数据库**（User1 是否存在）
6. ✅ **浏览器测试**（确认 CORS 生效）

---

**文档创建时间：** 2026-01-28  
**状态：** 待解决

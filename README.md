# DashBoard 点餐系统

这是一个基于 Python 与前端技术的 **餐饮点餐系统**，提供完整的菜品管理、点餐操作、订单管理和数据统计功能。前端采用简洁绿白配色界面，后端支持数据持久化和接口管理，便于餐饮场景快速部署与使用。

---

## 🚀 核心功能

* **菜品管理**：增删改查菜品信息，支持分类管理
* **点餐操作**：顾客可选择菜品、修改数量、提交订单
* **订单管理**：管理员查看订单列表、修改状态、生成统计报表
* **统计分析**：支持每日/每周/每月销售数据统计
* **权限控制**：分普通用户、管理员，确保数据安全
* **可扩展**：前端模板和后端接口均可快速拓展新功能

---

## 🧱 项目结构

```text
/
├── main/                   # 主业务逻辑
│   ├── templates/          # 前端页面 HTML
│   ├── static/             # 静态资源 (CSS/JS/图片)
│   └── models/             # 数据模型、数据库文件
├── pysh/                   # Python 工具脚本
├── sql/                    # 数据库初始化/迁移脚本
├── manage.py               # Django 启动/管理脚本
├── requirements.txt        # Python 依赖
├── README.md               # 项目说明
└── LICENSE                 # 开源许可
```

---

## 📦 技术栈

| 层级    | 技术 / 工具                        |
| ----- | ------------------------------ |
| 后端    | Python, Django                 |
| 前端    | HTML, CSS, JavaScript          |
| 数据库   | SQLite / 可扩展至 MySQL/PostgreSQL |
| 容器化   | Docker (可选)                    |
| 自动化脚本 | Python / Shell                 |

---

## 🛠 安装与运行（开发环境）

### 1. 克隆项目

```bash
git clone https://github.com/YEXIAONAN/DashBoard.git
cd DashBoard
```

### 2. 安装依赖

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### 3. 数据库初始化

```bash
python manage.py migrate
```

### 4. 启动服务

```bash
python manage.py runserver
```

访问 `http://localhost:8000` 即可使用点餐系统。

---

## 🐳 Docker 部署（可选）

```bash
docker build -t dashboard-app .
docker run -p 8000:8000 dashboard-app
```

---

## 🤝 贡献指南

欢迎贡献代码和改进建议：

1. Fork 仓库
2. 新建分支 (`git checkout -b feature/YourFeature`)
3. 提交修改 (`git commit -m "Add new feature"`)
4. 推送分支 (`git push origin feature/YourFeature`)
5. 创建 Pull Request

---

## 📄 许可协议

本项目详细信息见 LICENSE 文件。


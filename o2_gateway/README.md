# O2 Gateway - 服务网关页面

现代化的服务网关展示页面，采用液态玻璃效果和黑白配色设计。

## 特性

- 🎨 液态玻璃效果（Glassmorphism）
- 🌊 流动的背景渐变动画
- 📱 完全响应式设计
- ⚡ 轻量级，基于 Nginx
- 🎯 现代化的圆角设计
- ✨ 平滑的交互动画

## 快速开始

### 使用 Docker

```bash
# 构建镜像
docker build -t o2-gateway .

# 运行容器
docker run -d -p 8080:80 --name o2-gateway o2-gateway
```

### 使用 Docker Compose

```bash
# 启动服务
docker-compose up -d

# 停止服务
docker-compose down
```

访问 http://localhost:8080 查看页面

## 文件结构

```
o2_gateway/
├── Dockerfile              # Docker 构建文件
├── docker-compose.yml      # Docker Compose 配置
├── nginx.conf             # Nginx 配置文件
├── html/
│   ├── index.html         # 主页面
│   ├── style.css          # 样式文件
│   └── script.js          # 交互脚本
└── README.md              # 说明文档
```

## 自定义

### 修改端口

编辑 `docker-compose.yml` 文件中的端口映射：

```yaml
ports:
  - "你的端口:80"
```

### 修改服务卡片

编辑 `html/index.html` 中的 `.service-card` 部分，添加或修改服务信息。

### 修改配色

编辑 `html/style.css` 中的 CSS 变量：

```css
:root {
    --glass-bg: rgba(255, 255, 255, 0.05);
    --glass-border: rgba(255, 255, 255, 0.1);
    --text-primary: #ffffff;
    --text-secondary: rgba(255, 255, 255, 0.7);
}
```

## 技术栈

- Nginx Alpine
- HTML5
- CSS3 (Glassmorphism)
- Vanilla JavaScript

## 浏览器支持

- Chrome (推荐)
- Firefox
- Safari
- Edge

## License

MIT License

# 测试快速开始指南

## 🚀 快速开始

### 1️⃣ 安装依赖
```bash
# 进入测试目录
cd tests

# 安装 npm 依赖
npm install
```

### 2️⃣ 运行测试
```bash
# 运行所有测试
npm run test:all

# 或运行单个测试
npm test                      # 属性测试
npm run test:unit             # 单元测试
npm run test:roundtrip        # 往返测试
npm run validate:lazy-loading # 懒加载验证
```

### 3️⃣ 查看结果
测试结果会直接显示在终端中，包括：
- ✅ 通过的测试数量
- ❌ 失败的测试详情
- 📊 测试覆盖率（如果配置）

## 📁 文件结构
```
tests/
├── package.json              # npm 配置和测试脚本
├── package-lock.json         # 依赖锁定文件
├── frontend/                 # 前端测试
│   ├── test_form_validation_property.js
│   ├── test_form_validation_roundtrip.js
│   ├── test_form_validation_unit.js
│   └── test_lazy_loading_integration.js
├── backend/                  # 后端测试
│   └── test_form_validation.py
└── README.md                 # 详细文档
```

## 🔧 常用命令

| 命令 | 说明 |
|------|------|
| `npm install` | 安装依赖 |
| `npm test` | 运行属性测试 |
| `npm run test:unit` | 运行单元测试 |
| `npm run test:roundtrip` | 运行往返测试 |
| `npm run test:all` | 运行所有前端测试 |
| `npm run validate:lazy-loading` | 验证懒加载 |

## 💡 提示

- **首次运行**: 必须先执行 `npm install`
- **工作目录**: 确保在 `tests/` 目录中运行命令
- **Node.js 版本**: 需要 Node.js >= 8.0.0

## 📚 更多信息

查看 [README.md](./README.md) 获取完整文档。

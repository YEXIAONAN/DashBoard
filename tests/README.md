# 测试文件组织结构

本目录包含项目的所有测试文件，按照测试类型进行组织。

## 目录结构

```
tests/
├── frontend/                           # 前端测试
│   ├── test_form_validation_property.js      # 表单验证属性测试
│   ├── test_form_validation_roundtrip.js     # 表单验证往返测试
│   ├── test_form_validation_unit.js          # 表单验证单元测试
│   ├── test_lazy_loading_integration.js      # 懒加载集成测试
│   └── test_form_validation_roundtrip_README.md  # 测试文档
├── backend/                            # 后端测试
│   └── test_form_validation.py              # Python 表单验证测试
├── test_button_keyboard_accessibility.py    # 按钮键盘可访问性测试
├── test_navbar_component.py                 # 导航栏组件测试
└── README.md                                # 本文件
```

## 测试类型说明

### 前端测试 (frontend/)
- **JavaScript 测试**: 使用 Jest 或其他 JS 测试框架
- **表单验证测试**: 测试前端表单验证逻辑
- **集成测试**: 测试前端组件的集成功能

### 后端测试 (backend/)
- **Python 测试**: 使用 Django 测试框架或 pytest
- **API 测试**: 测试后端 API 端点
- **模型测试**: 测试数据库模型

### 组件测试 (根目录)
- **可访问性测试**: 测试 UI 组件的可访问性
- **组件单元测试**: 测试独立组件功能

## 运行测试

### 前端测试
```bash
# 进入测试目录
cd tests

# 安装依赖（首次运行）
npm install

# 运行所有前端测试
npm test

# 运行特定测试
npm run test:unit              # 单元测试
npm run test:roundtrip         # 往返测试
npm run validate:lazy-loading  # 懒加载验证

# 运行所有测试
npm run test:all

# 返回项目根目录
cd ..
```

### 后端测试
```bash
# 运行所有 Django 测试
python manage.py test

# 运行特定测试文件
python manage.py test tests.backend.test_form_validation

# 使用 pytest (如果已安装)
pytest tests/backend/
```

### 组件测试
```bash
# 运行可访问性测试
python manage.py test tests.test_button_keyboard_accessibility

# 运行导航栏测试
python manage.py test tests.test_navbar_component
```

## 添加新测试

1. **前端测试**: 在 `tests/frontend/` 目录下创建新的 `.js` 文件
2. **后端测试**: 在 `tests/backend/` 目录下创建新的 `.py` 文件
3. **组件测试**: 在 `tests/` 根目录下创建测试文件

## 测试命名规范

- 测试文件名以 `test_` 开头
- 使用描述性名称，如 `test_form_validation.py`
- JavaScript 测试使用 `.test.js` 或 `test_*.js` 格式
- Python 测试使用 `test_*.py` 格式

## 注意事项

- 确保所有测试都能独立运行
- 测试应该快速且可重复
- 使用 mock 数据避免依赖外部服务
- 保持测试代码的可读性和可维护性

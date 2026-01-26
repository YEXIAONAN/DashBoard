# API 字段映射表

## 📡 数据流向图

```
数据库 (Dishes) 
    ↓
后端聚合 (views.py)
    ↓
模板变量 (today_total)
    ↓
前端渲染 (index.html)
    ↓
用户界面
```

## 🗄️ 数据库字段

### Dishes 表字段
| 字段名 | 类型 | 说明 | 单位 |
|--------|------|------|------|
| `total_calorie` | Decimal | 总热量 | kcal |
| `total_protein` | Decimal | 总蛋白质 | g |
| `total_fat` | Decimal | 总脂肪 | g |
| `total_carbohydrate` | Decimal | 总碳水化合物 | g |
| `total_fiber` | Decimal | 总膳食纤维 | g |

## 🔧 后端处理逻辑

### views.py - index 函数

```python
def index(request):
    user = getUserSession(request)
    user_id = user["user_id"]
    today = timezone.localdate()
    
    # 1. 查询今日订单
    orders = Orders.objects.filter(
        user_id=user["user_id"],
        order_time__date=today
    )
    
    # 2. 查询订单项
    order_items = OrderItems.objects.filter(order__in=orders)
    
    # 3. 聚合营养数据
    totals = (
        Dishes.objects
        .filter(orderitems__in=order_items)
        .aggregate(
            calorie=Coalesce(Sum('total_calorie'), Value(0), output_field=DecimalField()),
            protein=Coalesce(Sum('total_protein'), Value(0), output_field=DecimalField()),
            fat=Coalesce(Sum('total_fat'), Value(0), output_field=DecimalField()),
            carbohydrate=Coalesce(Sum('total_carbohydrate'), Value(0), output_field=DecimalField()),
            fiber=Coalesce(Sum('total_fiber'), Value(0), output_field=DecimalField()),
        )
    )
    
    # 4. 传递给模板
    return render(request, 'index.html', {
        'today': today,
        'today_total': totals,
    })
```

### 数据聚合说明

#### Coalesce 函数
```python
Coalesce(Sum('total_calorie'), Value(0), output_field=DecimalField())
```
- **作用**: 如果 Sum 结果为 NULL，返回 0
- **原因**: 避免前端显示 "None" 或报错
- **输出**: 始终返回 Decimal 类型

#### Sum 聚合
```python
Sum('total_calorie')
```
- **作用**: 对所有今日订单的菜品热量求和
- **SQL 等价**: `SELECT SUM(total_calorie) FROM dishes WHERE ...`

## 📤 模板变量结构

### today_total 对象
```python
{
    'calorie': Decimal('1450.00'),      # 热量
    'protein': Decimal('65.50'),        # 蛋白质
    'fat': Decimal('45.20'),            # 脂肪
    'carbohydrate': Decimal('180.30'),  # 碳水化合物
    'fiber': Decimal('18.00'),          # 膳食纤维
}
```

### today 对象
```python
datetime.date(2026, 1, 25)  # 今日日期
```

## 🎨 前端字段映射

### 1. 热量 (Calorie)

#### 后端字段
```python
totals.calorie  # Decimal 类型
```

#### 前端显示
```django
<!-- 数值显示 -->
{{ totals.calorie|floatformat:0 }}  
<!-- 输出: 1450 -->

<!-- 进度计算 -->
{% widthratio totals.calorie 10000 100 %}
<!-- 输出: 14 (表示14%) -->
```

#### 目标值
- **推荐摄入**: 10000 kcal
- **单位**: kcal
- **显示格式**: 整数（无小数）

#### UI 组件
- 环形进度图 (SVG Circle)
- 颜色: `#8B9D83`
- 动画: 1.2s 缓动

---

### 2. 蛋白质 (Protein)

#### 后端字段
```python
totals.protein  # Decimal 类型
```

#### 前端显示
```django
<!-- 数值显示 -->
{{ totals.protein|floatformat:1 }}
<!-- 输出: 65.5 -->

<!-- 进度计算 -->
{% widthratio totals.protein 750 100 %}
<!-- 输出: 8 (表示8%) -->
```

#### 目标值
- **推荐摄入**: 750 g
- **单位**: g
- **显示格式**: 1位小数

#### UI 组件
- 横向进度条
- 颜色: `linear-gradient(90deg, #8B9D83, #9CAF88)`
- 动画: 1.2s 缓动

---

### 3. 碳水化合物 (Carbohydrate)

#### 后端字段
```python
totals.carbohydrate  # Decimal 类型
```

#### 前端显示
```django
<!-- 数值显示 -->
{{ totals.carbohydrate|floatformat:1 }}
<!-- 输出: 180.3 -->

<!-- 进度计算 -->
{% widthratio totals.carbohydrate 450 100 %}
<!-- 输出: 40 (表示40%) -->
```

#### 目标值
- **推荐摄入**: 450 g
- **单位**: g
- **显示格式**: 1位小数

#### UI 组件
- 横向进度条
- 颜色: `linear-gradient(90deg, #A4AC86, #B8C5A8)`
- 动画: 1.2s 缓动

---

### 4. 脂肪 (Fat)

#### 后端字段
```python
totals.fat  # Decimal 类型
```

#### 前端显示
```django
<!-- 数值显示 -->
{{ totals.fat|floatformat:1 }}
<!-- 输出: 45.2 -->

<!-- 进度计算（带超限保护） -->
{% if totals.fat > 550 %}100{% else %}{% widthratio totals.fat 550 100 %}{% endif %}
<!-- 输出: 8 (表示8%) 或 100 (如果超过550g) -->
```

#### 目标值
- **推荐摄入**: 550 g
- **单位**: g
- **显示格式**: 1位小数
- **超限处理**: 最大显示100%

#### UI 组件
- 横向进度条
- 颜色: `linear-gradient(90deg, #9CAF88, #A4AC86)`
- 动画: 1.2s 缓动

---

### 5. 膳食纤维 (Fiber)

#### 后端字段
```python
totals.fiber  # Decimal 类型
```

#### 前端显示
```django
<!-- 数值显示 -->
{{ totals.fiber|floatformat:1 }}
<!-- 输出: 18.0 -->

<!-- 进度计算（带超限保护） -->
{% if totals.fiber > 35 %}100{% else %}{% widthratio totals.fiber 35 100 %}{% endif %}
<!-- 输出: 51 (表示51%) 或 100 (如果超过35g) -->
```

#### 目标值
- **推荐摄入**: 35 g
- **单位**: g
- **显示格式**: 1位小数
- **超限处理**: 最大显示100%

#### UI 组件
- 横向进度条
- 颜色: `linear-gradient(90deg, #8B9D83, #9CAF88)`
- 动画: 1.2s 缓动

---

## 📅 日期字段映射

### 后端字段
```python
today = timezone.localdate()  # datetime.date 对象
```

### 前端显示
```django
<!-- 完整日期格式 -->
{{ today|date:"Y年n月j日 l" }}
<!-- 输出: 2026年1月25日 星期六 -->

<!-- 时间格式 -->
{{ today|date:"H:i" }}
<!-- 输出: 12:30 -->
```

### Django 日期格式化参数
| 参数 | 说明 | 示例 |
|------|------|------|
| `Y` | 4位年份 | 2026 |
| `n` | 月份（无前导0） | 1 |
| `j` | 日期（无前导0） | 25 |
| `l` | 星期几（完整） | 星期六 |
| `H` | 小时（24小时制） | 12 |
| `i` | 分钟 | 30 |

## 🔢 进度计算公式

### widthratio 模板标签

#### 语法
```django
{% widthratio 当前值 目标值 100 %}
```

#### 示例
```django
{% widthratio 65.5 750 100 %}
<!-- 计算: (65.5 / 750) * 100 = 8.73 → 8 (取整) -->
```

#### 特点
- 自动取整（向下取整）
- 返回整数
- 安全处理除零（目标值为0时返回0）

### 超限保护

#### 脂肪和纤维的特殊处理
```django
{% if totals.fat > 550 %}
    100
{% else %}
    {% widthratio totals.fat 550 100 %}
{% endif %}
```

#### 原因
- 防止进度条超过100%
- 保持UI一致性
- 提供视觉上限

## 🎯 目标值设定依据

### 营养素推荐摄入量（RNI）

| 营养素 | 目标值 | 依据 | 备注 |
|--------|--------|------|------|
| 热量 | 10000 kcal | 成年人日均需求 | 可根据性别、年龄、活动量调整 |
| 蛋白质 | 750 g | 体重 × 1.0-1.2 g/kg | 假设体重75kg |
| 脂肪 | 550 g | 总热量的20-30% | 1g脂肪=9kcal |
| 碳水化合物 | 450 g | 总热量的50-60% | 1g碳水=4kcal |
| 膳食纤维 | 35 g | 成年人推荐量 | 25-35g/天 |

### 个性化调整建议

#### 方案1: 用户配置表
```python
# models.py
class UserNutritionTarget(models.Model):
    user = models.ForeignKey(Users, on_delete=models.CASCADE)
    target_calorie = models.DecimalField(max_digits=10, decimal_places=2, default=10000)
    target_protein = models.DecimalField(max_digits=10, decimal_places=2, default=750)
    target_fat = models.DecimalField(max_digits=10, decimal_places=2, default=550)
    target_carbohydrate = models.DecimalField(max_digits=10, decimal_places=2, default=450)
    target_fiber = models.DecimalField(max_digits=10, decimal_places=2, default=35)
```

#### 方案2: 动态计算
```python
# views.py
def calculate_targets(user):
    weight = user.weight or 75  # kg
    height = user.height or 170  # cm
    age = user.age or 30
    gender = user.gender or 'M'
    
    # 基础代谢率 (BMR)
    if gender == 'M':
        bmr = 10 * weight + 6.25 * height - 5 * age + 5
    else:
        bmr = 10 * weight + 6.25 * height - 5 * age - 161
    
    # 总能量消耗 (TDEE)
    activity_factor = 1.55  # 中等活动量
    tdee = bmr * activity_factor
    
    return {
        'calorie': tdee,
        'protein': weight * 1.2,
        'fat': tdee * 0.25 / 9,
        'carbohydrate': tdee * 0.55 / 4,
        'fiber': 35,
    }
```

## 🛡️ 数据验证和错误处理

### 后端验证

#### 1. 空值处理
```python
Coalesce(Sum('total_calorie'), Value(0))
```
- **问题**: 用户今日无订单时，Sum返回NULL
- **解决**: 使用Coalesce返回0
- **结果**: 前端始终显示有效数值

#### 2. 类型转换
```python
output_field=DecimalField()
```
- **问题**: 聚合结果可能是整数或浮点数
- **解决**: 强制转换为Decimal类型
- **结果**: 保持数据精度和一致性

### 前端验证

#### 1. 除零保护
```django
{% widthratio totals.protein 750 100 %}
```
- **问题**: 如果目标值为0会报错
- **解决**: widthratio内置除零保护
- **结果**: 返回0而不是错误

#### 2. 超限保护
```django
{% if totals.fat > 550 %}100{% else %}...{% endif %}
```
- **问题**: 进度条可能超过100%
- **解决**: 条件判断限制最大值
- **结果**: 进度条不会溢出

#### 3. 数值格式化
```django
{{ totals.calorie|floatformat:0 }}
```
- **问题**: Decimal类型显示过多小数位
- **解决**: 使用floatformat过滤器
- **结果**: 整洁的数值显示

## 📊 示例数据流

### 完整示例

#### 1. 数据库查询结果
```python
# Orders
[
    Order(order_id=1, user_id=1, order_time='2026-01-25 08:30'),
    Order(order_id=2, user_id=1, order_time='2026-01-25 12:15'),
]

# OrderItems
[
    OrderItem(order_id=1, dish_id=101),
    OrderItem(order_id=1, dish_id=102),
    OrderItem(order_id=2, dish_id=103),
]

# Dishes
[
    Dish(dish_id=101, total_calorie=500, total_protein=25, ...),
    Dish(dish_id=102, total_calorie=450, total_protein=20, ...),
    Dish(dish_id=103, total_calorie=500, total_protein=20.5, ...),
]
```

#### 2. 聚合计算
```python
totals = {
    'calorie': Decimal('1450.00'),      # 500 + 450 + 500
    'protein': Decimal('65.50'),        # 25 + 20 + 20.5
    'fat': Decimal('45.20'),            # ...
    'carbohydrate': Decimal('180.30'),  # ...
    'fiber': Decimal('18.00'),          # ...
}
```

#### 3. 模板渲染
```html
<!-- 热量 -->
<div class="calorie-value">1450</div>
<div class="calorie-target">/ 10000</div>

<!-- 蛋白质 -->
<div class="nutrient-values">65.5 / 750 g</div>
<div class="nutrient-percentage">8%</div>
<div class="nutrient-progress-bar" style="width: 8%;"></div>
```

#### 4. 用户界面
```
营养摄入分析
2026年1月25日 星期六

[环形图: 1450 / 10000 kcal]

营养素构成:
┌─────────────┬─────────────┐
│ 蛋白质      │ 碳水化合物  │
│ 65.5/750g   │ 180.3/450g  │
│ 8%          │ 40%         │
│ [████░░░░]  │ [████████░] │
├─────────────┼─────────────┤
│ 脂肪        │ 膳食纤维    │
│ 45.2/550g   │ 18.0/35g    │
│ 8%          │ 51%         │
│ [███░░░░░]  │ [█████░░░░] │
└─────────────┴─────────────┘

● 营养摄入状态: 良好
```

## 🔄 实时更新方案（可选）

### REST API 端点
```python
# urls.py
path('api/nutrition/today/', views.nutrition_today_api, name='nutrition_today_api'),

# views.py
from django.http import JsonResponse

def nutrition_today_api(request):
    user = getUserSession(request)
    today = timezone.localdate()
    
    orders = Orders.objects.filter(user_id=user["user_id"], order_time__date=today)
    order_items = OrderItems.objects.filter(order__in=orders)
    
    totals = Dishes.objects.filter(orderitems__in=order_items).aggregate(
        calorie=Coalesce(Sum('total_calorie'), Value(0)),
        protein=Coalesce(Sum('total_protein'), Value(0)),
        fat=Coalesce(Sum('total_fat'), Value(0)),
        carbohydrate=Coalesce(Sum('total_carbohydrate'), Value(0)),
        fiber=Coalesce(Sum('total_fiber'), Value(0)),
    )
    
    return JsonResponse({
        'calorie': float(totals['calorie']),
        'protein': float(totals['protein']),
        'fat': float(totals['fat']),
        'carbohydrate': float(totals['carbohydrate']),
        'fiber': float(totals['fiber']),
    })
```

### 前端轮询
```javascript
// 每分钟更新一次
setInterval(function() {
    fetch('/api/nutrition/today/')
        .then(res => res.json())
        .then(data => {
            updateNutritionData(data);
        })
        .catch(err => console.error('更新失败:', err));
}, 60000);

function updateNutritionData(data) {
    // 更新热量
    document.querySelector('.calorie-value').textContent = Math.round(data.calorie);
    
    // 更新蛋白质
    document.querySelector('.nutrient-values').textContent = 
        `${data.protein.toFixed(1)} / 750 g`;
    
    // 更新进度条
    // ...
}
```

---

**文档版本**: v1.0  
**最后更新**: 2026-01-25  
**状态**: ✅ 完整映射

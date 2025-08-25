-- 为NutritionRecord表添加数据库索引以优化查询性能

-- 1. 为created_at字段添加索引，优化日期范围查询
CREATE INDEX IF NOT EXISTS idx_nutrition_created_at ON main_userinputdishtable(created_at);

-- 2. 为created_at和calorie的组合索引，优化聚合查询
CREATE INDEX IF NOT EXISTS idx_nutrition_created_calorie ON main_userinputdishtable(created_at, calorie);

-- 3. 为各个营养素字段添加索引，优化SUM聚合查询
CREATE INDEX IF NOT EXISTS idx_nutrition_created_protein ON main_userinputdishtable(created_at, protein);
CREATE INDEX IF NOT EXISTS idx_nutrition_created_fat ON main_userinputdishtable(created_at, fat);
CREATE INDEX IF NOT EXISTS idx_nutrition_created_carbohydrate ON main_userinputdishtable(created_at, carbohydrate);
CREATE INDEX IF NOT EXISTS idx_nutrition_created_fiber ON main_userinputdishtable(created_at, fiber);
CREATE INDEX IF NOT EXISTS idx_nutrition_created_sugar_added ON main_userinputdishtable(created_at, sugar_added);
CREATE INDEX IF NOT EXISTS idx_nutrition_created_iron ON main_userinputdishtable(created_at, iron);
CREATE INDEX IF NOT EXISTS idx_nutrition_created_calcium ON main_userinputdishtable(created_at, calcium);
CREATE INDEX IF NOT EXISTS idx_nutrition_created_vitamin_c ON main_userinputdishtable(created_at, vitamin_c);

-- 4. 检查现有索引
SHOW INDEX FROM main_userinputdishtable;
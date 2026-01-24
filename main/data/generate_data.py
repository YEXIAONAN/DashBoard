import csv
import random
from datetime import datetime, timedelta

# 基础食材类型
base_materials = [
    ("鸡蛋", "鸡蛋", (1.2, 1.8), (0.04, 0.06), (0.11, 0.15), (0.09, 0.13), (0.01, 0.02)),
    ("牛奶", "牛奶", (0.35, 0.5), (0.01, 0.03), (0.02, 0.04), (0.01, 0.02), (0.04, 0.06)),
    ("花生", "花生", (5.2, 6.0), (0.02, 0.04), (0.23, 0.29), (0.45, 0.53), (0.14, 0.18)),
    ("大豆", "大豆", (4.0, 4.9), (0.01, 0.03), (0.34, 0.40), (0.18, 0.22), (0.28, 0.32)),
    ("小麦", "小麦", (3.0, 3.5), (0.01, 0.03), (0.11, 0.15), (0.01, 0.03), (0.65, 0.73))
]

# 蔬菜类
vegetables = [
    ("胡萝卜", "", (0.35, 0.45), (0.0, 0.02), (0.01, 0.02), (0.0, 0.01), (0.08, 0.12)),
    ("西红柿", "", (0.15, 0.25), (0.0, 0.01), (0.01, 0.02), (0.0, 0.01), (0.03, 0.05)),
    ("黄瓜", "", (0.12, 0.20), (0.0, 0.01), (0.01, 0.02), (0.0, 0.01), (0.03, 0.05)),
    ("白菜", "", (0.10, 0.16), (0.0, 0.01), (0.01, 0.02), (0.0, 0.01), (0.01, 0.03))
]

# 肉类
meats = [
    ("猪肉", "", (2.2, 2.6), (0.10, 0.14), (0.20, 0.24), (0.12, 0.16), (0.0, 0.01)),
    ("牛肉", "", (2.3, 2.7), (0.25, 0.29), (0.24, 0.28), (0.13, 0.17), (0.0, 0.01)),
    ("鸡肉", "", (2.2, 2.6), (0.06, 0.08), (0.25, 0.29), (0.12, 0.16), (0.0, 0.01))
]

def generate_random_value(min_val, max_val):
    return round(random.uniform(min_val, max_val), 2)

def generate_material():
    # 随机选择一个食材类型
    material_type = random.choice([base_materials, vegetables, meats])
    base = random.choice(material_type)
    
    # 生成随机变化的数值
    name = base[0]
    allergens = base[1]
    calorie = generate_random_value(*base[2])
    carbon = generate_random_value(*base[3])
    protein = generate_random_value(*base[4])
    fat = generate_random_value(*base[5])
    carb = generate_random_value(*base[6])
    
    # 添加随机变化
    calorie *= random.uniform(0.95, 1.05)
    protein *= random.uniform(0.95, 1.05)
    fat *= random.uniform(0.95, 1.05)
    carb *= random.uniform(0.95, 1.05)
    
    return [name, allergens, round(calorie, 2), round(carbon, 2), 
            round(protein, 2), round(fat, 2), round(carb, 2)]

# 生成数据
with open('raw_materials_extended.csv', 'w', newline='', encoding='utf-8') as f:
    writer = csv.writer(f)
    writer.writerow(['material_id', 'name', 'allergens', 'calorie', 
                    'carbon_emission', 'protein', 'fat', 'carbohydrate'])
    
    for i in range(1, 50001):
        row_data = [i] + generate_material()
        writer.writerow(row_data)

print("数据生成完成！")

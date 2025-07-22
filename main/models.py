# main/models.py

from django.db import models

class NutritionRecord(models.Model):
    # 映射到新数据库表 main_userinputdishtable
    id = models.IntegerField(primary_key=True)

# 对应菜品数据表
class DishOrderTable(models.Model):
    name = models.CharField(max_length=100)
    price = models.DecimalField(max_digits=20, decimal_places=2)
    description = models.TextField()
    image_url = models.URLField(max_length=500)
    allergens = models.CharField(max_length=100, blank=True)
    total_calorie = models.DecimalField(max_digits=10, decimal_places=2)
    total_carbon_emission = models.DecimalField(max_digits=10, decimal_places=2)
    total_protein = models.DecimalField(max_digits=10, decimal_places=2)
    total_fat = models.DecimalField(max_digits=10, decimal_places=2)
    total_carbohydrate = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return self.name


# 用户下单记录表
class UserInputDishTable(models.Model):
    name = models.CharField(max_length=100)
    dishname = models.CharField(max_length=100)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    calorie = models.DecimalField(max_digits=10, decimal_places=2, db_column='calorie')
    price = models.DecimalField(max_digits=20, decimal_places=2)
    calorie = models.DecimalField(max_digits=10, decimal_places=2)
    carbon_emission = models.DecimalField(max_digits=10, decimal_places=2)
    protein = models.DecimalField(max_digits=10, decimal_places=2)
    fat = models.DecimalField(max_digits=10, decimal_places=2)
    carbohydrate = models.DecimalField(max_digits=10, decimal_places=2, db_column='carbohydrate')
    created_at = models.DateTimeField(db_column='created_at')
    fiber = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    sugar_added = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    calories = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    iron = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    calcium = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    vitamin_c = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    carbohydrate = models.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        managed = False
        db_table = 'main_userinputdishtable' # 更新为新表名
    # ---------------------------------------------------
    # 核心修复：只在这里添加下单时间字段
    # auto_now_add=True 会在创建记录时自动填充当前时间
    # ---------------------------------------------------
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="下单时间")

    def __str__(self):
        return f"Record for {self.created_at.date()} - {self.calorie} kcal"
        if self.created_at:
            return f"{self.name} 在 {self.created_at.strftime('%Y-%m-%d %H:%M')} 点了 {self.dishname}"
        return self.name


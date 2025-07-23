# main/models.py

from django.db import models


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
    total_fiber = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)

    def __str__(self):
        return self.name


# 用户下单记录表
class UserInputDishTable(models.Model):
    name = models.CharField(max_length=100)
    dishname = models.CharField(max_length=100)
    price = models.DecimalField(max_digits=20, decimal_places=2)
    calorie = models.DecimalField(max_digits=10, decimal_places=2)
    carbon_emission = models.DecimalField(max_digits=10, decimal_places=2)
    protein = models.DecimalField(max_digits=10, decimal_places=2)
    fat = models.DecimalField(max_digits=10, decimal_places=2)
    carbohydrate = models.DecimalField(max_digits=10, decimal_places=2)
    fiber = models.DecimalField(max_digits=10, decimal_places=2)

    # ---------------------------------------------------
    # 核心修复：只在这里添加下单时间字段
    # auto_now_add=True 会在创建记录时自动填充当前时间
    # ---------------------------------------------------
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="下单时间")

    def save(self, *args, **kwargs):
        # 自动填充 fiber
        if not self.fiber:  # 允许手动传值，防止覆盖
            try:
                dish = DishOrderTable.objects.get(name=self.dishname)
                self.fiber = dish.total_fiber or 0  # 若 total_fiber 为 None 则默认 0
            except DishOrderTable.DoesNotExist:
                # 若菜品不存在，可设默认值或记录日志
                self.fiber = 0
        super().save(*args, **kwargs)

    def __str__(self):
        if self.created_at:
            return f"{self.name} 在 {self.created_at.strftime('%Y-%m-%d %H:%M')} 点了 {self.dishname}"
        return self.name


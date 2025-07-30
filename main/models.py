# main/models.py
from django.utils import timezone

from django.db import models

class NutritionRecord(models.Model):
    # 映射到新数据库表 main_userinputdishtable
    id = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=100)
    dishname = models.CharField(max_length=100)
    price = models.DecimalField(max_digits=20, decimal_places=2)
    calorie = models.DecimalField(max_digits=10, decimal_places=2)
    carbon_emission = models.DecimalField(max_digits=10, decimal_places=2)
    protein = models.DecimalField(max_digits=10, decimal_places=2)
    fat = models.DecimalField(max_digits=10, decimal_places=2)
    carbohydrate = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(db_column='created_at')
    fiber = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    sugar_added = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    iron = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    calcium = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    vitamin_c = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)

    class Meta:
        managed = False
        db_table = 'main_userinputdishtable'

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
    order_id = models.IntegerField(max_length=100)
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
    fiber = models.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        managed = False
        db_table = 'main_userinputdishtable' # 更新为新表名
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
        return f"Record for {self.created_at.date()} - {self.calorie} kcal"
        if self.created_at:
            return f"{self.name} 在 {self.created_at.strftime('%Y-%m-%d %H:%M')} 点了 {self.dishname}"
        return self.name

class Orders(models.Model):
    order_number = models.CharField(unique=True, max_length=20, db_comment='订单号(唯一)')
    status = models.IntegerField(blank=True, null=True, db_comment='订单状态')
    created_at = models.DateTimeField(blank=True, null=True, db_comment='创建时间',default=timezone.now())
    updated_at = models.DateTimeField(blank=True, null=True, db_comment='更新时间',default=timezone.now())
    payment_status = models.IntegerField(blank=True, null=True, db_comment='支付状态')
    paid_at = models.DateTimeField(blank=True, null=True, db_comment='支付时间',default=timezone.now())

    class Meta:
        managed = False
        db_table = 'orders'
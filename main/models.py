from django.db import models

class NutritionRecord(models.Model):
    # 映射到新数据库表 main_userinputdishtable
    id = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=100)
    dishname = models.CharField(max_length=100)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    calorie = models.DecimalField(max_digits=10, decimal_places=2, db_column='calorie')
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

    class Meta:
        managed = False
        db_table = 'main_userinputdishtable' # 更新为新表名

    def __str__(self):
        return f"Record for {self.created_at.date()} - {self.calorie} kcal"


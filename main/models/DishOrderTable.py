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

# class UserInputDishTable(models.Model):
#     name = models.CharField(max_length=100)


    def __str__(self):
        return self.name
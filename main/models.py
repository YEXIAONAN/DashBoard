# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey and OneToOneField has `on_delete` set to the desired behavior
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
from django.db import models


class Admin(models.Model):
    admin_id = models.AutoField(primary_key=True)
    username = models.CharField(unique=True, max_length=50)
    password = models.CharField(max_length=255)

    class Meta:
        managed = False
        db_table = 'admin'


class DishIngredients(models.Model):
#    pk = models.CompositePrimaryKey('dish_id', 'material_id')
    dish = models.ForeignKey('Dishes', models.DO_NOTHING)
    material = models.ForeignKey('RawMaterials', models.DO_NOTHING)
    portion = models.IntegerField()

    class Meta:
        managed = False
        db_table = 'dish_ingredients'


class Dishes(models.Model):
    dish_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.TextField(blank=True, null=True)
    image_url = models.CharField(max_length=255, blank=True, null=True)
    allergens = models.CharField(max_length=255, blank=True, null=True)
    total_calorie = models.DecimalField(max_digits=10, decimal_places=2)
    total_carbon_emission = models.DecimalField(max_digits=10, decimal_places=2)
    total_protein = models.DecimalField(max_digits=10, decimal_places=2)
    total_fat = models.DecimalField(max_digits=10, decimal_places=2)
    total_carbohydrate = models.DecimalField(max_digits=10, decimal_places=2)
    total_fiber = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    total_sugar = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    iron = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    calcium = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    vitamin_c = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'dishes'


class OrderEvaluation(models.Model):
    evaluation_id = models.AutoField(primary_key=True)
    order = models.OneToOneField('Orders', models.DO_NOTHING)
    rating = models.IntegerField()
    content = models.CharField(max_length=150, blank=True, null=True)
    evaluation_time = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'order_evaluation'


class OrderItems(models.Model):
    order_item_id = models.AutoField(primary_key=True)
    order = models.ForeignKey('Orders', models.DO_NOTHING)
    dish = models.ForeignKey(Dishes, models.DO_NOTHING)
    quantity = models.IntegerField()
    dish_price = models.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        managed = False
        db_table = 'order_items'


class Orders(models.Model):
    order_id = models.AutoField(primary_key=True)
    user = models.ForeignKey('Users', models.DO_NOTHING)
    order_time = models.DateTimeField(blank=True, null=True)
    status = models.CharField(max_length=3)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'orders'


class RawMaterials(models.Model):
    material_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100)
    allergens = models.CharField(max_length=255, blank=True, null=True)
    calorie = models.DecimalField(max_digits=10, decimal_places=2)
    carbon_emission = models.DecimalField(max_digits=10, decimal_places=2)
    protein = models.DecimalField(max_digits=10, decimal_places=2)
    fat = models.DecimalField(max_digits=10, decimal_places=2)
    carbohydrate = models.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        managed = False
        db_table = 'raw_materials'


class Users(models.Model):
    user_id = models.AutoField(primary_key=True)
    phone = models.CharField(unique=True, max_length=20)
    password = models.CharField(max_length=255)
    age = models.IntegerField(blank=True, null=True)
    height = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True)
    weight = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True)
    gender = models.CharField(max_length=2, blank=True, null=True)
    allergens = models.CharField(max_length=255, blank=True, null=True)
    chronic_diseases = models.CharField(max_length=11, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'users'


class ChatHistory(models.Model):
    chat_id = models.AutoField(primary_key=True)
    user = models.ForeignKey('Users', models.DO_NOTHING)
    message = models.TextField()
    is_user = models.BooleanField(default=True)  # True表示用户消息，False表示AI回复
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        managed = True
        db_table = 'chat_history'
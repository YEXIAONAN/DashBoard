from main.models import OrderItems, Dishes
from django.db.models import Sum, F
from main.views import getUserSession

# 检查是否有订单数据
order_count = OrderItems.objects.count()
print(f"订单项总数: {order_count}")

# 检查最近的一些订单数据
recent_orders = OrderItems.objects.select_related('dish', 'order').order_by('-order__order_time')[:5]
print("\n最近的5个订单项:")
for order in recent_orders:
    print(f"订单ID: {order.order_item_id}, 菜品: {order.dish.name}, 数量: {order.quantity}")
    print(f"  蛋白质: {order.dish.total_protein}, 铁: {order.dish.iron}")
    print(f"  订单时间: {order.order.order_time}")
    print("---")

# 检查菜品表中的营养数据
dishes_with_nutrition = Dishes.objects.filter(total_protein__isnull=False).exclude(total_protein=0).count()
print(f"\n有蛋白质数据的菜品数量: {dishes_with_nutrition}")

dishes_with_iron = Dishes.objects.filter(iron__isnull=False).exclude(iron=0).count()
print(f"有铁数据的菜品数量: {dishes_with_iron}")

# 检查聚合查询是否能获取到数据
from django.utils import timezone
from datetime import timedelta

today = timezone.now().date()
this_month_start = today.replace(day=1)

# 测试查询本月蛋白质和铁数据
protein_data = OrderItems.objects.filter(
    order__order_time__date__range=[this_month_start, today]
).aggregate(
    total_protein=Sum(F('dish__total_protein') * F('quantity')),
    total_iron=Sum(F('dish__iron') * F('quantity'))
)

print(f"\n本月聚合数据:")
print(f"总蛋白质: {protein_data['total_protein']}")
print(f"总铁: {protein_data['total_iron']}")

# 测试查询本周蛋白质和铁数据
this_week_start = today - timedelta(days=today.weekday())
protein_data_week = OrderItems.objects.filter(
    order__order_time__date__range=[this_week_start, today]
).aggregate(
    total_protein=Sum(F('dish__total_protein') * F('quantity')),
    total_iron=Sum(F('dish__iron') * F('quantity'))
)

print(f"\n本周聚合数据:")
print(f"总蛋白质: {protein_data_week['total_protein']}")
print(f"总铁: {protein_data_week['total_iron']}")
print(f"总脂肪: {protein_data_week['total_fat']}")
print(f"总碳水化合物: {protein_data_week['total_carb']}")
print(f"总纤维: {protein_data_week['total_fiber']}")
print(f"总钙: {protein_data_week['total_calcium']}")
print(f"总维生素C: {protein_data_week['total_vitamin_c']}")
print(f"总铁: {protein_data_week['total_iron']}")
print(f"总糖: {protein_data_week['total_sugar']}")
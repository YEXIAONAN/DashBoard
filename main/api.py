# main/api.py

import json
from datetime import datetime

from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt  # <--- 导入 csrf_exempt
from .models import DishOrderTable, UserInputDishTable, Orders


def generate_order_number(now):


    # 格式: YYMMDDHHmmss + 4位随机数 (例如: 2308101530451234)
    timestamp_part = now.strftime("%y%m%d%H%M%S")  # 12位时间字符串
    random_part = str(round(1000, 9999))  # 4位随机数

    return f"{timestamp_part}{random_part}"

@csrf_exempt  # <--- 在视图函数正上方添加这个装饰器
@require_POST
def submit_order(request):
    try:
        data = json.loads(request.body)
        cart_items = data.get('items', [])

        if not cart_items:
            return JsonResponse({'status': 'error', 'message': '购物车不能为空'}, status=400)
        """生成基于时间的订单号"""
        now = datetime.now()
        orders = Orders.objects.create(
            order_number = generate_order_number(now),
            status = 1,
            created_at = now,
            updated_at = now,
            payment_status = 1,
            paid_at = now
        )

        for item in cart_items:
            dish_id = item.get('id')
            if not dish_id:
                continue

            try:
                dish = DishOrderTable.objects.get(id=dish_id)

                UserInputDishTable.objects.create(
                    name="DefaultUser",  # 使用固定的默认用户名
                    order_id = orders.id,
                    dishname=dish.name,
                    price=dish.price,
                    calorie=dish.total_calorie,
                    carbon_emission=dish.total_carbon_emission,
                    protein=dish.total_protein,
                    fat=dish.total_fat,
                    carbohydrate=dish.total_carbohydrate
                )

            except DishOrderTable.DoesNotExist:
                return JsonResponse({'status': 'error', 'message': f'菜品ID {dish_id} 不存在'}, status=400)

        return JsonResponse({'status': 'success', 'order_id': orders.id})

    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)
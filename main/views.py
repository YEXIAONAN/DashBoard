
# 1. 将所有需要的模块一次性导入在文件顶部
from django.shortcuts import render
from datetime import datetime, timedelta

# 2. 定义所有页面的渲染视图
from django.utils import timezone
from django.db.models import Sum
from .models import DishOrderTable, UserInputDishTable
from collections import defaultdict


def index(request):
    # 1. 推荐菜品（最多 4 条）
    dishes = DishOrderTable.objects.all()[:4]
    dishes.getnamelen()

    # 2. 今日营养汇总
    today = timezone.localdate()
    totals = (
        UserInputDishTable.objects
        .filter(created_at__date=today)
        .aggregate(
            calorie=Sum('calorie') or 0,
            protein=Sum('protein') or 0,
            fat=Sum('fat') or 0,
            carbohydrate=Sum('carbohydrate') or 0,
        )
    )

    return render(request, 'index.html', {
        'dishes': dishes,
        'today': today,
        'today_total': totals,
    })

def orders(request):
    # 查询所有菜品，传给模板
    dishes = DishOrderTable.objects.all()

    # 叶小楠Bug记录 ： 购物车无法显示总蛋白质问题
    # print(f"--- 调试信息: 正在渲染菜品 '{dishes[0].name}'，其蛋白质为: {dishes[0].total_protein} ---")
    return render(request, 'orders.html', {'dishes': dishes})


def profile(request):
    """
    渲染个人中心页面
    """
    return render(request, 'profile.html')

def order_history(request):
    cutoff = timezone.now() - timedelta(days=3)

    # ① 最近 3 天的订单记录
    dishes = UserInputDishTable.objects.filter(created_at__gte=cutoff)

    # ② 菜品名 → 图片 URL 映射
    img_map = {d.name: d.image_url for d in DishOrderTable.objects.all()}

    # ③ 按日期+菜品名聚合
    grouped = defaultdict(lambda: defaultdict(int))
    price_map, calorie_map, protein_map = {}, {}, {}
    for d in dishes:
        day = d.created_at.date()
        grouped[day][d.dishname] += 1
        price_map[d.dishname] = float(d.price)
        calorie_map[d.dishname] = float(d.calorie)
        protein_map[d.dishname] = float(d.protein)

    # ④ 整理模板数据
    history = []
    for day in sorted(grouped.keys(), reverse=True):
        dish_list = []
        for name, cnt in grouped[day].items():
            dish_list.append({
                'dishname': name,
                'count': cnt,
                'price': price_map[name],
                'calorie': calorie_map[name],
                'protein': protein_map[name],
                'subtotal': round(price_map[name] * cnt, 2),
                'image_url': img_map.get(name, 'Images/default.jpg'),
            })
        total = round(sum(d['subtotal'] for d in dish_list), 2)
        history.append({'day': day, 'dishes': dish_list, 'total': total})

    return render(request, 'order_history.html', {'history': history})

def nutrition_recipes(request):
    dishes = DishOrderTable.objects.all()  # 或者你用过滤条件
    return render(request, 'nutrition_recipes.html', {'dishes': dishes})

def repo(request):
    """
    渲染报告页面
    """
    return render(request, 'repo.html')


def MyOrder(request):
    cutoff = timezone.now() - timedelta(days=3)
    dishes = UserInputDishTable.objects.filter(created_at__gte=cutoff)

    img_map = {d.name: d.image_url for d in DishOrderTable.objects.all()}
    grouped = defaultdict(lambda: defaultdict(int))
    price_map, calorie_map, protein_map = {}, {}, {}
    for d in dishes:
        day = d.created_at.date()
        grouped[day][d.dishname] += 1
        price_map[d.dishname] = float(d.price)
        calorie_map[d.dishname] = float(d.calorie)
        protein_map[d.dishname] = float(d.protein)

    history = []
    for day in sorted(grouped.keys(), reverse=True):
        dish_list = []
        for name, cnt in grouped[day].items():
            dish_list.append({
                'dishname': name,
                'count': cnt,
                'price': price_map[name],
                'calorie': calorie_map[name],
                'protein': protein_map[name],
                'subtotal': round(price_map[name] * cnt, 2),
                'image_url': img_map.get(name, 'Images/default.jpg'),
            })
        total = round(sum(d['subtotal'] for d in dish_list), 2)
        history.append({'day': day, 'dishes': dish_list, 'total': total})

    # 假设模板中用到order，传递history或orders，模板变量保持一致
    return render(request, 'MyOrder.html', {'history': history})

def Collection(request):
    return render(request, 'Collection.html')

def NoComment(request):
    return render(request, 'NoComment.html')

def profile_view(request):
    return render(request, 'profile.html')  # 渲染 profile.html 模板

def menu_view(request):
    dishes = DishOrderTable.objects.all()  # 查询所有菜品
    return render(request, 'main/menu.html', {'dishes': dishes})



# 放在文件最底部，不影响原有代码
import pymysql
from django.http import JsonResponse

def api_orders(request):
    """
    提供 JSON 接口，供前端 AJAX 获取订单数据
    """
    conn = pymysql.connect(
        host='172.16.7.79',
        port=3306,
        user='root',
        password='BigData#123..',
        database='ds',
        charset='utf8mb4',
        cursorclass=pymysql.cursors.DictCursor
    )
    with conn.cursor() as cursor:
        sql = """
            SELECT id, name AS username, dishname, price, calorie,
                   carbon_emission, protein, fat, carbohydrate, created_at
            FROM main_userinputdishtable
            ORDER BY created_at DESC
        """
        cursor.execute(sql)
        rows = cursor.fetchall()
    conn.close()
    return JsonResponse(rows, safe=False)

# import json
# from django.http import JsonResponse
# from django.views.decorators.csrf import csrf_exempt
# from .models import Order, OrderItem, Dish
#
# @csrf_exempt
# def submit_order(request):
#     if request.method == 'POST':
#         data = json.loads(request.body)
#         items = data.get('items', [])
#         if not items:
#             return JsonResponse({'status': 'error', 'message': '购物车为空'})
#
#         order = Order.objects.create(user=request.user if request.user.is_authenticated else None)
#         total_price = 0
#         for item in items:
#             dish = Dish.objects.filter(name=item['name']).first()
#             if not dish:
#                 return JsonResponse({'status': 'error', 'message': f'菜品不存在：{item["name"]}'})
#             OrderItem.objects.create(
#                 order=order,
#                 dish=dish,
#                 quantity=item['quantity'],
#                 price=item['price']
#             )
#             total_price += item['price'] * item['quantity']
#         order.total_price = total_price
#         order.save()
#
#         return JsonResponse({'status': 'success', 'order_id': order.id})

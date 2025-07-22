# main/views.py

# 1. 将所有需要的模块一次性导入在文件顶部
from django.shortcuts import render
from .models import DishOrderTable


# 2. 定义所有页面的渲染视图
from django.utils import timezone
from django.db.models import Sum
from .models import DishOrderTable, UserInputDishTable

def index(request):
    # 1. 推荐菜品（最多 4 条）
    dishes = DishOrderTable.objects.all()[:4]

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

# 2. 定义所有页面的渲染视图

# def index(request):
#     """
#     渲染首页
#     """
#     dishes = Dish.objects.all()
#     return render(request, 'index.html', {'dishes': dishes})


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
    return render(request, 'order_history.html')

def nutrition_recipes(request):
    return render(request, 'nutrition_recipes.html')

def repo(request):
    """
    渲染报告页面
    """
    return render(request, 'repo.html')


def MyOrder(request):
    """
    渲染“我的订单”页面
    """
    # 在未来，您可以在这里查询数据库，获取该用户的历史订单并传递给模板
    return render(request, 'MyOrder.html')

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


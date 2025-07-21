# main/views.py

# 1. 将所有需要的模块一次性导入在文件顶部
from django.shortcuts import render
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
    """
    渲染点餐页面，并从数据库获取所有菜品传递给前端
    这是正确的 orders 视图函数
    """
    return render(request, 'orders.html')


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


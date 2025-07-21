# main/views.py

# 1. 将所有需要的模块一次性导入在文件顶部
from django.shortcuts import render
from .models import DishOrderTable


# 2. 定义所有页面的渲染视图

def index(request):
    """
    渲染首页
    """
    return render(request, 'index.html')


def orders(request):
    # 查询所有菜品，传给模板
    dishes = DishOrderTable.objects.all()
    print(f"--- 调试信息: 正在渲染菜品 '{dishes[0].name}'，其蛋白质为: {dishes[0].total_protein} ---")
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


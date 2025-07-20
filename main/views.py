# main/views.py

# 1. 将所有需要的模块一次性导入在文件顶部
from django.shortcuts import render



# 2. 定义所有页面的渲染视图

def index(request):
    """
    渲染首页
    """
    return render(request, 'index.html')


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

from django.shortcuts import render

def index(request):
    return render(request, 'index.html')

def orders(request):
    return render(request,'orders.html')

def profile(request):
    return render(request,'profile.html')

def order_history(request):
    return render(request, 'order_history.html')

def nutrition_recipes(request):
    return render(request, 'nutrition_recipes.html')

def repo(request):
    return render(request,'repo.html')


from django.shortcuts import render

def index(request):
    return render(request, 'index.html')

def orders(request):
    return render(request,'orders.html')

def profile(request):
    return render(request,'profile.html')

def repo(request):
    return render(request,'repo.html')

def MyOrder(request):
    return render(request, 'MyOrder.html')

def Collection(request):
    return render(request, 'Collection.html')

def NoComment(request):
    return render(request, 'NoComment.html')

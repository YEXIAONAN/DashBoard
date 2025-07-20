from django.http import HttpResponse
from main.models import models

# 定义数据库操作
def dishdb(request):
    dishdb1 = DishOrderTable(name='MuGay')
    dishdb1.save()
    return HttpResponse("<p>数据添加成功</p>")
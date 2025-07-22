from django.views.static import serve
from django.conf import settings
from django.urls import re_path
from django.contrib import admin
from main import views,dishdb,api
# 1. 导入必要的模块
from django.conf import settings
from django.conf.urls.static import static
from django.urls import path,include

from django.urls import path

from main import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('index/', views.index,name='index'),
    path('orders/',views.orders,name='orders'),
    path('repo/', views.repo, name='repo'),
    path('dishdb/',dishdb.dishdb),
    path('submit-order/', api.submit_order, name='submit-order'),
    path('profile/',views.profile,name='profile'),
    path('order_history/', views.order_history, name='order_history'),
    path('nutrition_recipes/', views.nutrition_recipes, name='nutrition_recipes'),
    path('MyOrder/',views.MyOrder,name='MyOrder'),
    path('Collection/',views.Collection,name='Collection'),
    path('NoComment/',views.NoComment,name='NoComment'),
    path('NoComment/profile/', views.profile, name='profile'),
    path('api/orders/', views.api_orders, name='api_orders'),
]


if settings.DEBUG:

    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATICFILES_DIRS[0])

from django.views.static import serve
from django.conf import settings
import os

urlpatterns += [
    path('img/<str:dish>.jpg', serve, {
        'document_root': os.path.join(settings.BASE_DIR, 'main', 'static', 'Images'),
    }, name='dish_img'),
]
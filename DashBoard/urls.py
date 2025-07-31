# DashBoard/DashBoard/urls.py

from django.views.static import serve
from django.conf import settings
from django.urls import re_path
from django.contrib import admin
from main import views,dishdb,api
# 1. 导入必要的模块
from django.conf import settings
from django.conf.urls.static import static
from django.urls import path,include
from django.views.static import serve
from django.conf import settings
import os
from django.urls import path
from main import views  # 确保这个导入在文件顶部

urlpatterns = [
    path('admin/', admin.site.urls),
    path('index/', views.index, name='index'),
    path('orders/',views.orders,name='orders'),
    path('repo/', views.repo, name='repo'),
    path('dishdb/',dishdb.dishdb),
    path('profile/',views.profile,name='profile'),
    path('order_history/', views.order_history, name='order_history'),
    path('nutrition_recipes/', views.nutrition_recipes, name='nutrition_recipes'),
    path('MyOrder/',views.MyOrder,name='MyOrder'),
    path('Collection/',views.Collection,name='Collection'),
    path('NoComment/',views.NoComment,name='NoComment'),
    path('api/orders/', views.api_orders, name='api_orders'),
    path('calorie-data/', views.calorie_trend_data, name='calorie_data'),
    path('nutrient-comparison-data/', views.nutrient_comparison_data, name='nutrient_comparison_data'),
    path('monthly-calorie-data/', views.monthly_calorie_data, name='monthly_calorie_data'),
    path('weekly-summary-data/', views.weekly_summary_data, name='weekly_summary_data'),
    path('monthly-summary-data/', views.monthly_summary_data, name='monthly_summary_data'),
    path('weekly-nutrient-analysis-data/', views.weekly_nutrient_analysis_data, name='weekly_nutrient_analysis_data'),
    path('get_nutrient_radar_data/', views.get_nutrient_radar_data, name='get_nutrient_radar_data'),
    path('get_order_status/', views.get_order_status, name='get_order_status'),
    path('ai_health_advisor/', views.ai_health_advisor, name='ai_health_advisor'),
    path('submit-order/', api.submit_order, name='submit-order'),
    path('execute_task_one/', api.execute_task_one, name='execute_task_one'),
]
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATICFILES_DIRS[0])





from django.views.static import serve
import os
from django.conf import settings

urlpatterns += [
    re_path(r'^img/(?P<path>.*)$', serve, {
        'document_root': os.path.join(settings.BASE_DIR, 'main', 'static', 'Images'),
    }),
]
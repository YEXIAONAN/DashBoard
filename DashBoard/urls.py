# DashBoard/DashBoard/urls.py
from django.urls import re_path
from django.contrib import admin
from main import views,dishdb,api
# 1. 导入必要的模块
from django.conf import settings
from django.conf.urls.static import static
from django.urls import path
from django.views.static import serve
import os

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.index, name='home'),  # 让根路径访问 index 视图
    path('index/', views.index, name='index'),
    path('orders/',views.orders,name='orders'),
    path('repo/', views.repo, name='repo'),
    # path('dishdb/',dishdb.dishdb),
    path('profile/',views.profile,name='profile'),
    path('order_history/', views.order_history, name='order_history'),
    # path('nutrition_recipes/', views.nutrition_recipes, name='nutrition_recipes'),
    path('MyOrder/',views.MyOrder,name='MyOrder'),
    path('Collection/',views.Collection,name='Collection'),
    path('NoComment/',views.NoComment,name='NoComment'),
    # path('api/orders/', views.api_orders, name='api_orders'),
    path('calorie-data/', views.calorie_trend_data, name='calorie_data'),
    path('nutrient-comparison-data/', views.nutrient_comparison_data, name='nutrient_comparison_data'),
    path('monthly-calorie-data/', views.monthly_calorie_data, name='monthly_calorie_data'),
    path('weekly-summary-data/', views.weekly_summary_data, name='weekly_summary_data'),
    path('monthly-summary-data/', views.monthly_summary_data, name='monthly_summary_data'),
    path('weekly-nutrient-analysis-data/', views.weekly_nutrient_analysis_data, name='weekly_nutrient_analysis_data'),
    path('get_nutrient_radar_data/', views.get_nutrient_radar_data, name='get_nutrient_radar_data'),
    path('get_order_status/', views.get_order_status, name='get_order_status'),
    # path('order_status/', views.get_order_status, name='order_status'),
    path('ai_health_advisor/', views.ai_health_advisor, name='ai_health_advisor'),
    path('refresh_recommendation/', views.refresh_recommendation, name='refresh_recommendation'),
    path('login/', views.login, name='login'),
    path('register/', views.register, name='login'),
    path('get_weekly_nutrient_radar_data/', views.get_weekly_nutrient_radar_data, name='get_weekly_nutrient_radar_data'),
    ##api
    path('submit-order/', api.submit_order, name='submit-order'),
    path('execute_task_one/', api.execute_task_one, name='execute_task_one'),
    path('execute_order_tasks/', api.execute_order_tasks, name='execute_order_tasks'),
    path('api/login/', api.login_v, name='api_login'),
    path('api/logout/', api.logout, name='api_logout'),
    path('api/save_chat_message/', api.save_chat_message, name='save_chat_message'),
    path('api/get_chat_history/', api.get_chat_history, name='get_chat_history'),
    path('api/clear_chat_history/', api.clear_chat_history, name='clear_chat_history'),
    # Test routes
    path('test/form-fields/', views.test_form_fields, name='test_form_fields'),
    path('test/form-validation/', views.test_form_validation, name='test_form_validation'),
]
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATICFILES_DIRS[0])




urlpatterns += [
    re_path(r'^img/(?P<path>.*)$', serve, {
        'document_root': os.path.join(settings.BASE_DIR, 'main', 'static', 'Images'),
    }),
]
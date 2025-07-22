# DashBoard/DashBoard/urls.py

from django.contrib import admin
from django.urls import path
from main import views # 确保这个导入在文件顶部

urlpatterns = [
    path('admin/', admin.site.urls),
    path('index/', views.index, name='index'),
    path('orders/', views.orders, name='orders'),
    path('repo/', views.repo, name='repo'),
    path('profile/', views.profile, name='profile'),

    # API 路径
    path('calorie-data/', views.calorie_trend_data, name='calorie_data'),
    path('nutrient-comparison-data/', views.nutrient_comparison_data, name='nutrient_comparison_data'),
    path('monthly-calorie-data/', views.monthly_calorie_data, name='monthly_calorie_data'),
    path('weekly-summary-data/', views.weekly_summary_data, name='weekly_summary_data'),
    path('monthly-summary-data/', views.monthly_summary_data, name='monthly_summary_data'),
    path('weekly-nutrient-analysis-data/', views.weekly_nutrient_analysis_data, name='weekly_nutrient_analysis_data'),
    path('get_nutrient_radar_data/', views.get_nutrient_radar_data, name='get_nutrient_radar_data'),

]
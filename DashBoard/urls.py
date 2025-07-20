# 修正后的完整代码
from django.contrib import admin
from main import views,dishdb,api
# 1. 导入必要的模块
from django.conf import settings
from django.conf.urls.static import static
from django.urls import path,include


urlpatterns = [
    path('admin/', admin.site.urls),
    path('index/', views.index, name='index'),
    path('orders/', views.orders, name='orders'),
    path('repo/', views.repo, name='repo'),
    path('profile/', views.profile, name='profile'),
    path('MyOrder/', views.MyOrder, name='MyOrder'),
    path('dishdb/',dishdb.dishdb),
    path('submit-order/', api.submit_order, name='submit-order'),


]

# 2. 在文件末尾添加以下关键代码
if settings.DEBUG:
    # 这行代码让Django开发服务器能够找到并提供静态文件
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATICFILES_DIRS[0])
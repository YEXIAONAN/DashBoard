from django.db.models.lookups import IsNull
from django.shortcuts import render,redirect,HttpResponse
from django.utils.deprecation import MiddlewareMixin


class AuthMiddleWare(MiddlewareMixin):
    def process_request(self,request):
        #  排除不需要登录运行访问的界面
        if request.path_info in ['/login/','/api/login/','/monthly-summary-data/']:
            return
        # 1.读取当前访问的用户的session信息，如果能读到，说明已登陆过，就可以继续向后走
        info_dict = request.session.get("user")
        # 如果登录过，继续往后走
        if  info_dict is not None:
            return

        # 没登录过，返回登录界面
        return redirect('/login/')
from django.http import JsonResponse
from django.shortcuts import render
from django.views import View
from rest_framework_simplejwt.settings import api_settings
from rest_framework_simplejwt.tokens import RefreshToken

from user.models import SysUser


# Create your views here.
class TestView(View):

    def get(self,request):
        token=request.headers.get('Authorization')
        if token is not None and token !='':
            userList_obj=SysUser.objects.all()
            userList_dict=userList_obj.values()
            userList=list(userList_dict)     
            return JsonResponse({'code':200,'info':'测试！','data':userList,'token':token})
        else:
            return JsonResponse({'code':401,'info':'没有访问权限'})
        # print("token:",token,type(token))
        # userList_obj=SysUser.objects.all()
        # print(userList_obj,type(userList_obj))
        # userList_dict=userList_obj.values() # 转存字典
        # print(userList_dict, type(userList_dict))
        # userList=list(userList_dict) # 把外层的容器转存List
        # print(userList, type(userList))
        # return JsonResponse({'code':200,'info':'测试！','data':userList})


class JwtTestView(View):
    def get(self,request):
        try:
            # 通过用户名获取用户（AbstractBaseUser 的密码是加密存储的，不能直接查询）
            user = SysUser.objects.get(username='python222')
            # 验证密码（如果需要的话）
            # if not user.check_password('123456'):
            #     return JsonResponse({'code': 401, 'error': '密码错误'})
            
            # 现在 user 是 AuthUser 类型，可以用于 RefreshToken.for_user()
            refresh_token = RefreshToken.for_user(user)
            access_token = str(refresh_token.access_token)
            refresh_token=str(refresh_token)
            return JsonResponse({'code': 200, 'access_token': access_token,'refresh_token': refresh_token})
        except SysUser.DoesNotExist:
            return JsonResponse({'code': 404, 'error': '用户不存在'})
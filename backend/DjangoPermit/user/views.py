import json
from django.http import JsonResponse
from django.shortcuts import render
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from rest_framework_simplejwt.tokens import RefreshToken

from user.models import SysUser

@method_decorator(csrf_exempt, name='dispatch')
class LoginView(View):

    def post(self, request):
        # 支持多种方式获取参数：请求体（JSON/表单）和查询字符串
        username = None
        password = None
        
        # 优先级：请求体 > 查询字符串
        try:
            # 1. 优先从请求体中获取（JSON 格式）
            content_type = request.content_type or ''
            if 'application/json' in content_type:
                if request.body:
                    data = json.loads(request.body)
                    username = data.get("username")
                    password = data.get("password")
            # 2. 从请求体中获取（表单格式）
            elif request.POST:
                username = request.POST.get("username")
                password = request.POST.get("password")
        except json.JSONDecodeError as e:
            print(f"JSON 解析错误: {e}")
            return JsonResponse({'code': 400, 'info': f'JSON 格式错误: {str(e)}'})
        except Exception as e:
            print(f"参数获取错误: {e}")
        
        # 3. 如果请求体中没有，尝试从查询字符串获取（兼容 Postman 的 Params 方式）
        if not username:
            username = request.GET.get("username")
        if not password:
            password = request.GET.get("password")
        
        # 调试信息
        print(f"接收到的参数 - username: {username}, password: {'***' if password else None}")
        print(f"Content-Type: {request.content_type}")
        print(f"Request body: {request.body}")
        print(f"Query params: {request.GET}")
        
        if not username or not password:
            return JsonResponse({
                'code': 400, 
                'info': '用户名和密码不能为空',
                'debug': {
                    'username': username,
                    'password': '***' if password else None,
                    'content_type': request.content_type,
                    'has_body': bool(request.body),
                    'query_params': dict(request.GET)
                }
            })
        try:
            # 先通过用户名查找用户
            print(f"尝试查找用户: {username}")
            user = SysUser.objects.get(username=username)
            print(f"找到用户: {user.username}, ID: {user.id}")
            
            # 使用 check_password 方法验证密码（支持加密和明文密码）
            print(f"验证密码...")
            if not user.check_password(password):
                print(f"密码验证失败")
                return JsonResponse({'code': 500, 'info': '用户名或者密码错误！'})
            print(f"密码验证成功")
            
            # 使用 SimpleJWT 的 RefreshToken 生成 token
            refresh_token = RefreshToken.for_user(user)
            access_token = str(refresh_token.access_token)
            token = access_token
            print(f"Token 生成成功")
                    
        except SysUser.DoesNotExist:
            print(f"用户不存在: {username}")
            return JsonResponse({'code': 500, 'info': '用户名或者密码错误！'})
        except Exception as e:
            print(f"登录错误: {e}")
            print(f"错误类型: {type(e).__name__}")
            import traceback
            print(f"完整错误堆栈:\n{traceback.format_exc()}")
            return JsonResponse({
                'code': 500, 
                'info': '登录失败，请稍后重试！',
                'error': str(e),
                'error_type': type(e).__name__
            })
        return JsonResponse({'code': 200, 'token': token, 'info': '登录成功'})
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
    
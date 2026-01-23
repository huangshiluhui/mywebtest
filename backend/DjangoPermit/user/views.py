import json
import os
from django.http import JsonResponse
from django.shortcuts import render
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.conf import settings
from rest_framework_simplejwt.tokens import RefreshToken

from user.models import SysUser,SysUserSerializer
from role.models import SysRole, SysRoleSerializer, SysUserRole
from menu.models import SysMenu, SysMenuSerializer
from django.core.paginator import Paginator

@method_decorator(csrf_exempt, name='dispatch')
class LoginView(View):

    def buildTreeMenu(self, sysMenuList):
        resultMenuList: list[SysMenu] = list()
        for menu in sysMenuList:
            # 寻找子节点
            for e in sysMenuList:
                if e.parent_id == menu.id:
                    # 判断当前menu下面是否存在children属性
                    if not hasattr(menu, "children"):
                        menu.children = list()
                    menu.children.append(e)
            # 判断父节点，添加到集合
            if menu.parent_id == 0:
                resultMenuList.append(menu)
        return resultMenuList
    
    def printTreeMenu(self, menuList, level=0, prefix=""):
        """
        递归打印菜单树结构
        :param menuList: 菜单列表
        :param level: 当前层级（用于缩进）
        :param prefix: 前缀符号（用于显示树形结构）
        """
        for i, menu in enumerate(menuList):
            # 判断是否是最后一个节点
            is_last = (i == len(menuList) - 1)
            # 当前节点的连接符号
            current_prefix = "└── " if is_last else "├── "
            # 子节点的缩进前缀
            child_prefix = prefix + ("    " if is_last else "│   ")
            
            # 打印当前菜单信息
            menu_info = f"{prefix}{current_prefix}[ID:{menu.id}] {menu.name}"
            if menu.path:
                menu_info += f" (path: {menu.path})"
            if menu.menu_type:
                menu_info += f" [类型: {menu.menu_type}]"
            if menu.order_num is not None:
                menu_info += f" [排序: {menu.order_num}]"
            print(menu_info)
            
            # 递归打印子节点
            if hasattr(menu, "children") and menu.children:
                self.printTreeMenu(menu.children, level + 1, child_prefix)
    
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
            
            # 初始化菜单列表
            serializerMenuList = []
            
            # 查询用户的角色列表（使用参数化查询避免 SQL 注入）
            roleList = SysRole.objects.raw(                
                "SELECT id, NAME FROM sys_role WHERE id IN (SELECT role_id FROM sys_user_role WHERE user_id = %s)",
                [user.id]
            )
            print(roleList)
            # 使用 ID 集合来去重（因为 Django 模型对象不可哈希，不能直接放入 set）
            menuIdSet = set()
            for role in roleList:   
                print(role.id, role.name)
                menuList = SysMenu.objects.raw(
                    "SELECT * FROM sys_menu WHERE id IN (SELECT menu_id FROM sys_role_menu WHERE role_id = %s)",
                    [role.id]
                )
                for row2 in menuList:
                    print(row2.id, row2.name)
                    menuIdSet.add(row2.id)  # 只存储 ID（ID 是可哈希的）
            
            # 根据去重后的 ID 集合查询菜单对象
            sorted_menuList = []
            if menuIdSet:
                menuList = list(SysMenu.objects.filter(id__in=menuIdSet))
                # 根据 order_num 排序（处理 None 值，将 None 排在最后）
                sorted_menuList = sorted(menuList, key=lambda x: (x.order_num is None, x.order_num or 0))
                print(f"菜单数量: {len(sorted_menuList)}")
                print(sorted_menuList)
                for menu in sorted_menuList:
                    print(menu.id, menu.name, menu.path, menu.component, menu.menu_type, menu.perms, menu.create_time, menu.update_time, menu.remark)
            
            # 构造菜单树
            sysMenuList = self.buildTreeMenu(sorted_menuList)
            print(f"\n{'='*60}")
            print(f"菜单树根节点数量: {len(sysMenuList)}")
            print(f"{'='*60}")
            if sysMenuList:
                print("\n菜单树结构：")
                self.printTreeMenu(sysMenuList)
                print(f"\n{'='*60}\n")
            else:
                print("菜单树为空")
                print(f"{'='*60}\n")
            
            # 序列化菜单树
            serializerMenuList = list()
            for sysMenu in sysMenuList:
                print(SysMenuSerializer(sysMenu))
                print("\n")
                serializerMenuList.append(SysMenuSerializer(sysMenu).data)
            print(serializerMenuList)
                    
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
        # 准备返回数据
        response_data = {
            'code': 200,
            'token': token,
            'user': SysUserSerializer(user).data,
            'info': '登录成功',
            'menuList': serializerMenuList
        }
        
        # 如果存在菜单数据，添加到响应中
        if serializerMenuList:
            response_data['menuList'] = serializerMenuList
        
        return JsonResponse(response_data)
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


@method_decorator(csrf_exempt, name='dispatch')
class SaveView(View):

    def post(self, request):
        try:
            data = json.loads(request.body.decode("utf-8"))
            print(data)
            from datetime import datetime
            
            if data['id'] == -1:  # 添加新用户
                # 检查用户名是否已存在
                if SysUser.objects.filter(username=data['username']).exists():
                    return JsonResponse({'code': 500, 'errorInfo': '用户名已存在！'})
                
                # 创建新用户
                obj_sysUser = SysUser(
                    username=data['username'],
                    email=data.get('email', ''),
                    phonenumber=data.get('phonenumber', ''),
                    status=data.get('status', 1),
                    remark=data.get('remark', ''),
                    create_time=datetime.now().date(),
                    update_time=datetime.now().date()
                )
                # 设置密码（会自动加密）
                if 'password' in data and data['password']:
                    obj_sysUser.set_password(data['password'])
                else:
                    obj_sysUser.set_password('123456')  # 默认密码
                obj_sysUser.save()
                return JsonResponse({'code': 200, 'info': '添加成功！'})
            else:  # 修改用户
                try:
                    obj_sysUser = SysUser.objects.get(id=data['id'])
                except SysUser.DoesNotExist:
                    return JsonResponse({'code': 500, 'errorInfo': '用户不存在！'})
                
                # 检查用户名是否被其他用户使用
                if data['username'] != obj_sysUser.username:
                    if SysUser.objects.filter(username=data['username']).exclude(id=data['id']).exists():
                        return JsonResponse({'code': 500, 'errorInfo': '用户名已被其他用户使用！'})
                
                # 更新用户信息
                obj_sysUser.username = data['username']
                obj_sysUser.email = data.get('email', obj_sysUser.email)
                obj_sysUser.phonenumber = data.get('phonenumber', obj_sysUser.phonenumber)
                obj_sysUser.status = data.get('status', obj_sysUser.status)
                obj_sysUser.remark = data.get('remark', obj_sysUser.remark)
                obj_sysUser.update_time = datetime.now().date()
                
                # 如果提供了新密码，则更新密码
                if 'password' in data and data['password']:
                    obj_sysUser.set_password(data['password'])
                
                obj_sysUser.save()
                return JsonResponse({'code': 200, 'info': '修改成功！'})
        except Exception as e:
            import traceback
            print(f"保存用户错误: {e}")
            print(f"完整错误堆栈:\n{traceback.format_exc()}")
            return JsonResponse({'code': 500, 'errorInfo': f'操作失败：{str(e)}'})


@method_decorator(csrf_exempt, name='dispatch')
class PwdView(View):

    def post(self, request):
        data = json.loads(request.body.decode("utf-8"))
        id = data['id']
        oldPassword = data['oldPassword']
        newPassword = data['newPassword']
        from datetime import datetime
        
        try:
            obj_user = SysUser.objects.get(id=id)
            # 使用 check_password 方法验证旧密码（支持加密和明文密码）
            if obj_user.check_password(oldPassword):
                # 使用 set_password 方法设置新密码（会自动加密）
                obj_user.set_password(newPassword)
                obj_user.update_time = datetime.now().date()
                obj_user.save()
                return JsonResponse({'code': 200})
            else:
                return JsonResponse({'code': 500, 'errorInfo': '原密码错误！'})
        except SysUser.DoesNotExist:
            return JsonResponse({'code': 500, 'errorInfo': '用户不存在！'})
        except Exception as e:
            print(f"修改密码错误: {e}")
            import traceback
            print(f"完整错误堆栈:\n{traceback.format_exc()}")
            return JsonResponse({'code': 500, 'errorInfo': f'修改密码失败：{str(e)}'})


@method_decorator(csrf_exempt, name='dispatch')
class UploadImageView(View):
    """处理头像图片上传"""
    
    def post(self, request):
        try:
            # 获取上传的文件
            if 'avatar' not in request.FILES:
                return JsonResponse({'code': 400, 'errorInfo': '未找到上传的文件'})
            
            uploaded_file = request.FILES['avatar']
            
            # 验证文件类型
            if not uploaded_file.content_type.startswith('image/'):
                return JsonResponse({'code': 400, 'errorInfo': '文件必须是图片格式'})
            
            # 创建保存目录
            upload_dir = os.path.join(settings.MEDIA_ROOT, 'userAvatar')
            os.makedirs(upload_dir, exist_ok=True)
            
            # 生成文件名（使用时间戳避免重名）
            import time
            file_extension = os.path.splitext(uploaded_file.name)[1]  # 获取文件扩展名
            file_name = f"{int(time.time() * 1000)}{file_extension}"  # 使用时间戳作为文件名
            
            # 保存文件
            file_path = os.path.join(upload_dir, file_name)
            with open(file_path, 'wb+') as destination:
                for chunk in uploaded_file.chunks():
                    destination.write(chunk)
            
            # 返回文件名
            return JsonResponse({'code': 200, 'title': file_name})
            
        except Exception as e:
            import traceback
            print(f"上传图片错误: {e}")
            print(f"完整错误堆栈:\n{traceback.format_exc()}")
            return JsonResponse({'code': 500, 'errorInfo': f'上传图片失败：{str(e)}'})


@method_decorator(csrf_exempt, name='dispatch')
class AvatarView(View):

    def post(self, request):
        data = json.loads(request.body.decode("utf-8"))
        id = data['id']
        avatar = data['avatar']
        obj_user = SysUser.objects.get(id=id)
        obj_user.avatar = avatar
        obj_user.save()
        return JsonResponse({'code': 200})

@method_decorator(csrf_exempt, name='dispatch')
class SearchView(View):
    
    def post(self, request):
        try:
            # 检查请求体是否为空
            if not request.body:
                return JsonResponse({'code': 400, 'errorInfo': '请求体不能为空'})
            
            # 解析 JSON
            try:
                data = json.loads(request.body.decode("utf-8"))
            except json.JSONDecodeError as e:
                return JsonResponse({'code': 400, 'errorInfo': f'JSON格式错误: {str(e)}'})
            
            # 使用 get 方法安全获取参数，设置默认值
            id = data.get('id', None)
            pageNum = data.get('pageNum', 1)
            pageSize = data.get('pageSize', 10)
            query = data.get('query', '').strip()  # 去除前后空格
            
            # 构建查询，添加排序以避免分页警告
            queryset = SysUser.objects.all().order_by('id')
            
            # 如果有查询条件，进行模糊搜索
            if query:
                queryset = queryset.filter(username__icontains=query)
            
            # 如果有 id 参数，用于筛选
            if id:
                queryset = queryset.filter(id=id)
            
            # 分页
            paginator = Paginator(queryset, pageSize)
            total = paginator.count
            
            try:
                userListPage = paginator.page(pageNum)
            except Exception as e:
                # 如果页码超出范围，返回空列表
                return JsonResponse({
                    'code': 400, 
                    'errorInfo': f'页码超出范围: {str(e)}',
                    'total': total,
                    'userList': []
                })
            
            # 将 Page 对象中的模型实例转换为字典列表
            # 明确指定所有需要的字段，确保包含 email 和 phonenumber
            obj_users = userListPage.object_list.values(
                'id', 'username', 'avatar', 'email', 'phonenumber', 
                'login_date', 'status', 'create_time', 'update_time', 'remark'
            )
            users = list(obj_users)
            for user in users:
                userid = user['id']
                # 查询用户的角色列表
                sysRoleList = SysRole.objects.raw(
                    "SELECT id, NAME FROM sys_role WHERE id IN (SELECT role_id FROM sys_user_role WHERE user_id = %s)",
                    [userid]
                )
                # 将 RawQuerySet 转换为可序列化的字典列表
                user['roleList'] = [{'id': role.id, 'name': role.name} for role in sysRoleList]
            return JsonResponse({
                'code': 200, 
                'total': total,
                'userList': users,
                'pageNum': pageNum,
                'pageSize': pageSize
            })
            
        except Exception as e:
            import traceback
            print(f"搜索用户错误: {e}")
            print(f"完整错误堆栈:\n{traceback.format_exc()}")
            return JsonResponse({'code': 500, 'errorInfo': f'搜索失败：{str(e)}'})


@method_decorator(csrf_exempt, name='dispatch')
class UpdateStatusView(View):
    def post(self, request):
        data = json.loads(request.body.decode("utf-8"))
        print(data)
        id = data['id']
        status = data['status']
        obj_user = SysUser.objects.get(id=id)
        obj_user.status = status
        obj_user.save()
        return JsonResponse({'code': 200})

@method_decorator(csrf_exempt, name='dispatch')
class DeleteView(View):
    def post(self, request):
        try:
            data = json.loads(request.body.decode("utf-8"))
            print(data)
            id = data.get('id')
            
            if not id:
                return JsonResponse({'code': 400, 'errorInfo': '用户ID不能为空'})
            
            try:
                obj_user = SysUser.objects.get(id=id)
                # 防止删除超级管理员
                if obj_user.username == 'python222':
                    return JsonResponse({'code': 500, 'errorInfo': '不能删除超级管理员！'})
                
                # 先删除用户角色关联表中的记录（因为外键使用了 PROTECT）
                SysUserRole.objects.filter(user_id=id).delete()
                
                # 然后删除用户
                obj_user.delete()
                return JsonResponse({'code': 200, 'info': '删除成功！'})
            except SysUser.DoesNotExist:
                return JsonResponse({'code': 500, 'errorInfo': '用户不存在！'})
        except Exception as e:
            import traceback
            print(f"删除用户错误: {e}")
            print(f"完整错误堆栈:\n{traceback.format_exc()}")
            return JsonResponse({'code': 500, 'errorInfo': f'删除失败：{str(e)}'})

@method_decorator(csrf_exempt, name='dispatch')
class ResetPasswordView(View):
    def post(self, request):
        data = json.loads(request.body.decode("utf-8"))
        print(data)
        id = data['id']
        obj_user = SysUser.objects.get(id=id)
        obj_user.set_password('hualijun123')
        obj_user.save()
        return JsonResponse({'code': 200})
 
    
@method_decorator(csrf_exempt, name='dispatch')
class AssignRoleView(View):
    def post(self, request):
        try:
            data = json.loads(request.body.decode("utf-8"))
            user_id = data.get('userId')
            role_ids = data.get('roleIds', [])  # 角色ID列表
            
            if not user_id:
                return JsonResponse({'code': 500, 'errorInfo': '用户ID不能为空！'})
            
            # 验证用户是否存在
            try:
                obj_user = SysUser.objects.get(id=user_id)
            except SysUser.DoesNotExist:
                return JsonResponse({'code': 500, 'errorInfo': '用户不存在！'})
            
            # 先删除该用户的所有角色关联
            SysUserRole.objects.filter(user_id=user_id).delete()
            
            # 添加新的角色关联
            if role_ids and len(role_ids) > 0:
                for role_id in role_ids:
                    try:
                        role = SysRole.objects.get(id=role_id)
                        SysUserRole.objects.create(user=obj_user, role=role)
                    except SysRole.DoesNotExist:
                        print(f"角色ID {role_id} 不存在，跳过")
            
            return JsonResponse({'code': 200, 'info': '角色分配成功！'})
        except Exception as e:
            import traceback
            print(f"分配角色错误: {e}")
            print(f"完整错误堆栈:\n{traceback.format_exc()}")
            return JsonResponse({'code': 500, 'errorInfo': f'分配角色失败：{str(e)}'})
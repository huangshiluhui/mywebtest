from django.shortcuts import render
from django.views import View
from django.http import JsonResponse
from role.models import SysRole, SysRoleSerializer, SysUserRole
from menu.models import SysMenu, SysRoleMenu
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
import json
from django.core.paginator import Paginator
from datetime import datetime


@method_decorator(csrf_exempt, name='dispatch')
class SearchAllRoleView(View):
    def get(self, request):
        allRoles = SysRole.objects.all().values('id', 'name', 'code', 'create_time', 'update_time', 'remark')
        allRoleList = list(allRoles)
        return JsonResponse({'code': 200, 'allRoles': allRoleList})
    

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
            queryset = SysRole.objects.all().order_by('id')
            
            # 如果有查询条件，进行模糊搜索，按照角色名称来查询
            if query:
                queryset = queryset.filter(name__icontains=query)
            
            # 如果有 id 参数，用于筛选
            if id:
                queryset = queryset.filter(id=id)
            
            # 分页
            paginator = Paginator(queryset, pageSize)
            total = paginator.count
            
            try:
                roleListPage = paginator.page(pageNum)
            except Exception as e:
                # 如果页码超出范围，返回空列表
                return JsonResponse({
                    'code': 400, 
                    'errorInfo': f'页码超出范围: {str(e)}',
                    'total': total,
                    'roleList': []
                })
            
            # 将 Page 对象中的模型实例转换为字典列表
            # 明确指定所有需要的字段，确保包含 email 和 phonenumber
            obj_roles = roleListPage.object_list.values(
                'id', 'name', 'code', 'create_time', 'update_time', 'remark'
            )
            roles = list(obj_roles)
            return JsonResponse({
                'code': 200, 
                'total': total,
                'roleList': roles,
                'pageNum': pageNum,
                'pageSize': pageSize
            })
            
        except Exception as e:
            import traceback
            print(f"搜索角色错误: {e}")
            print(f"完整错误堆栈:\n{traceback.format_exc()}")
            return JsonResponse({'code': 500, 'errorInfo': f'搜索失败：{str(e)}'})


@method_decorator(csrf_exempt, name='dispatch')
class SaveView(View):
    """保存角色（新增/编辑）"""
    
    def post(self, request):
        try:
            data = json.loads(request.body.decode("utf-8"))
            role_id = data.get('id', -1)
            name = data.get('name', '').strip()
            code = data.get('code', '').strip()
            remark = data.get('remark', '').strip()
            
            if not name:
                return JsonResponse({'code': 500, 'errorInfo': '角色名不能为空！'})
            
            if not code:
                return JsonResponse({'code': 500, 'errorInfo': '权限字符不能为空！'})
            
            if role_id == -1:
                # 新增角色
                # 检查角色名是否已存在
                if SysRole.objects.filter(name=name).exists():
                    return JsonResponse({'code': 500, 'errorInfo': '角色名已存在！'})
                
                # 检查权限字符是否已存在
                if SysRole.objects.filter(code=code).exists():
                    return JsonResponse({'code': 500, 'errorInfo': '权限字符已存在！'})
                
                obj_role = SysRole(
                    name=name,
                    code=code,
                    remark=remark,
                    create_time=datetime.now().date(),
                    update_time=datetime.now().date()
                )
                obj_role.save()
                return JsonResponse({'code': 200, 'info': '添加成功！'})
            else:
                # 编辑角色
                try:
                    obj_role = SysRole.objects.get(id=role_id)
                except SysRole.DoesNotExist:
                    return JsonResponse({'code': 500, 'errorInfo': '角色不存在！'})
                
                # 检查角色名是否与其他角色冲突
                if SysRole.objects.filter(name=name).exclude(id=role_id).exists():
                    return JsonResponse({'code': 500, 'errorInfo': '角色名已存在！'})
                
                # 检查权限字符是否与其他角色冲突
                if SysRole.objects.filter(code=code).exclude(id=role_id).exists():
                    return JsonResponse({'code': 500, 'errorInfo': '权限字符已存在！'})
                
                obj_role.name = name
                obj_role.code = code
                obj_role.remark = remark
                obj_role.update_time = datetime.now().date()
                obj_role.save()
                return JsonResponse({'code': 200, 'info': '修改成功！'})
        except Exception as e:
            import traceback
            print(f"保存角色错误: {e}")
            print(f"完整错误堆栈:\n{traceback.format_exc()}")
            return JsonResponse({'code': 500, 'errorInfo': f'操作失败：{str(e)}'})


@method_decorator(csrf_exempt, name='dispatch')
class DeleteView(View):
    """删除角色"""
    
    def post(self, request):
        try:
            data = json.loads(request.body.decode("utf-8"))
            role_id = data.get('id')
            
            if not role_id:
                return JsonResponse({'code': 500, 'errorInfo': '角色ID不能为空！'})
            
            try:
                obj_role = SysRole.objects.get(id=role_id)
            except SysRole.DoesNotExist:
                return JsonResponse({'code': 500, 'errorInfo': '角色不存在！'})
            
            # 防止删除超级管理员
            if obj_role.name == '超级管理员':
                return JsonResponse({'code': 500, 'errorInfo': '不能删除超级管理员！'})
            
            # 先删除用户角色关联表中的记录（因为外键使用了 PROTECT）
            SysUserRole.objects.filter(role_id=role_id).delete()
            
            # 先删除角色菜单关联表中的记录（因为外键使用了 PROTECT）
            SysRoleMenu.objects.filter(role_id=role_id).delete()
            
            # 然后删除角色
            obj_role.delete()
            return JsonResponse({'code': 200, 'info': '删除成功！'})
        except Exception as e:
            import traceback
            print(f"删除角色错误: {e}")
            print(f"完整错误堆栈:\n{traceback.format_exc()}")
            return JsonResponse({'code': 500, 'errorInfo': f'删除失败：{str(e)}'})


@method_decorator(csrf_exempt, name='dispatch')
class GetRoleMenusView(View):
    """获取角色的菜单列表"""
    
    def get(self, request):
        try:
            role_id_str = request.GET.get('roleId')
            
            if not role_id_str:
                return JsonResponse({'code': 500, 'errorInfo': '角色ID不能为空！'})
            
            # 转换为整数类型
            try:
                role_id = int(role_id_str)
            except (ValueError, TypeError):
                return JsonResponse({'code': 500, 'errorInfo': '角色ID格式错误！'})
            
            # 验证角色是否存在
            try:
                SysRole.objects.get(id=role_id)
            except SysRole.DoesNotExist:
                return JsonResponse({'code': 500, 'errorInfo': '角色不存在！'})
            
            # 查询角色已分配的菜单ID列表
            role_menus = SysRoleMenu.objects.filter(role_id=role_id).values_list('menu_id', flat=True)
            menu_ids = list(role_menus)
            
            print(f"角色 {role_id} 已分配的菜单ID: {menu_ids}")
            
            return JsonResponse({'code': 200, 'menuIds': menu_ids})
        except Exception as e:
            import traceback
            print(f"获取角色菜单错误: {e}")
            print(f"完整错误堆栈:\n{traceback.format_exc()}")
            return JsonResponse({'code': 500, 'errorInfo': f'获取失败：{str(e)}'})


@method_decorator(csrf_exempt, name='dispatch')
class AssignPermissionView(View):
    """分配权限"""
    
    def post(self, request):
        try:
            data = json.loads(request.body.decode("utf-8"))
            role_id = data.get('roleId')
            menu_ids = data.get('menuIds', [])
            
            if not role_id:
                return JsonResponse({'code': 500, 'errorInfo': '角色ID不能为空！'})
            
            # 验证角色是否存在
            try:
                obj_role = SysRole.objects.get(id=role_id)
            except SysRole.DoesNotExist:
                return JsonResponse({'code': 500, 'errorInfo': '角色不存在！'})
            
            # 先删除该角色的所有菜单关联
            SysRoleMenu.objects.filter(role_id=role_id).delete()
            
            # 添加新的菜单关联
            if menu_ids and len(menu_ids) > 0:
                for menu_id in menu_ids:
                    try:
                        menu = SysMenu.objects.get(id=menu_id)
                        SysRoleMenu.objects.create(role=obj_role, menu=menu)
                    except SysMenu.DoesNotExist:
                        print(f"菜单ID {menu_id} 不存在，跳过")
            
            return JsonResponse({'code': 200, 'info': '权限分配成功！'})
        except Exception as e:
            import traceback
            print(f"分配权限错误: {e}")
            print(f"完整错误堆栈:\n{traceback.format_exc()}")
            return JsonResponse({'code': 500, 'errorInfo': f'分配权限失败：{str(e)}'})

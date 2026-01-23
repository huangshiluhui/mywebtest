from django.shortcuts import render
from django.views import View
from django.http import JsonResponse
from menu.models import SysMenu, SysRoleMenu
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
import json
from datetime import datetime


@method_decorator(csrf_exempt, name='dispatch')
class SearchAllMenuView(View):
    """获取所有菜单"""
    
    def get(self, request):
        try:
            print("开始获取菜单列表...")
            all_menus = SysMenu.objects.all().values(
                'id', 'name', 'icon', 'parent_id', 'order_num', 
                'path', 'component', 'menu_type', 'perms', 
                'create_time', 'update_time', 'remark'
            )
            all_menu_list = list(all_menus)
            print(f"获取到 {len(all_menu_list)} 个菜单")
            return JsonResponse({'code': 200, 'allMenus': all_menu_list})
        except Exception as e:
            import traceback
            error_trace = traceback.format_exc()
            print(f"获取菜单列表错误: {e}")
            print(f"完整错误堆栈:\n{error_trace}")
            return JsonResponse({
                'code': 500, 
                'errorInfo': f'获取菜单列表失败：{str(e)}',
                'debug': error_trace
            })


@method_decorator(csrf_exempt, name='dispatch')
class SearchView(View):
    """搜索菜单（返回树形结构）"""
    
    def get(self, request):
        try:
            # 获取所有菜单
            all_menus = SysMenu.objects.all().order_by('order_num', 'id').values(
                'id', 'name', 'icon', 'parent_id', 'order_num', 
                'path', 'component', 'menu_type', 'perms', 
                'create_time', 'update_time', 'remark'
            )
            menu_list = list(all_menus)
            
            # 构建树形结构
            menu_map = {}
            root_menus = []
            
            # 先创建所有菜单的映射
            for menu in menu_list:
                menu_map[menu['id']] = {
                    **menu,
                    'children': []
                }
            
            # 构建树结构
            for menu in menu_list:
                menu_node = menu_map[menu['id']]
                parent_id = menu['parent_id']
                if not parent_id or parent_id == 0:
                    root_menus.append(menu_node)
                elif parent_id in menu_map:
                    menu_map[parent_id]['children'].append(menu_node)
            
            return JsonResponse({'code': 200, 'menuList': root_menus})
        except Exception as e:
            import traceback
            print(f"搜索菜单错误: {e}")
            print(f"完整错误堆栈:\n{traceback.format_exc()}")
            return JsonResponse({'code': 500, 'errorInfo': f'搜索失败：{str(e)}'})


@method_decorator(csrf_exempt, name='dispatch')
class SaveView(View):
    """保存菜单（新增/编辑）"""
    
    def post(self, request):
        try:
            data = json.loads(request.body.decode("utf-8"))
            menu_id = data.get('id', -1)
            name = data.get('name', '').strip()
            icon = data.get('icon', '').strip()
            parent_id = data.get('parent_id', 0)
            order_num = data.get('order_num', 0)
            path = data.get('path', '').strip()
            component = data.get('component', '').strip()
            menu_type = data.get('menu_type', '').strip()
            perms = data.get('perms', '').strip()
            remark = data.get('remark', '').strip()
            
            if not name:
                return JsonResponse({'code': 500, 'errorInfo': '菜单名称不能为空！'})
            
            if menu_id == -1:
                # 新增菜单
                # 检查菜单名是否已存在
                if SysMenu.objects.filter(name=name).exists():
                    return JsonResponse({'code': 500, 'errorInfo': '菜单名称已存在！'})
                
                obj_menu = SysMenu(
                    name=name,
                    icon=icon if icon else None,
                    parent_id=parent_id if parent_id else None,
                    order_num=order_num if order_num else 0,
                    path=path if path else None,
                    component=component if component else None,
                    menu_type=menu_type if menu_type else None,
                    perms=perms if perms else None,
                    remark=remark if remark else None,
                    create_time=datetime.now().date(),
                    update_time=datetime.now().date()
                )
                obj_menu.save()
                return JsonResponse({'code': 200, 'info': '添加成功！'})
            else:
                # 编辑菜单
                try:
                    obj_menu = SysMenu.objects.get(id=menu_id)
                except SysMenu.DoesNotExist:
                    return JsonResponse({'code': 500, 'errorInfo': '菜单不存在！'})
                
                # 检查菜单名是否与其他菜单冲突
                if SysMenu.objects.filter(name=name).exclude(id=menu_id).exists():
                    return JsonResponse({'code': 500, 'errorInfo': '菜单名称已存在！'})
                
                # 不能将菜单设置为自己的子菜单
                if parent_id and parent_id == menu_id:
                    return JsonResponse({'code': 500, 'errorInfo': '不能将菜单设置为自己的子菜单！'})
                
                obj_menu.name = name
                obj_menu.icon = icon if icon else None
                obj_menu.parent_id = parent_id if parent_id else None
                obj_menu.order_num = order_num if order_num else 0
                obj_menu.path = path if path else None
                obj_menu.component = component if component else None
                obj_menu.menu_type = menu_type if menu_type else None
                obj_menu.perms = perms if perms else None
                obj_menu.remark = remark if remark else None
                obj_menu.update_time = datetime.now().date()
                obj_menu.save()
                return JsonResponse({'code': 200, 'info': '修改成功！'})
        except Exception as e:
            import traceback
            print(f"保存菜单错误: {e}")
            print(f"完整错误堆栈:\n{traceback.format_exc()}")
            return JsonResponse({'code': 500, 'errorInfo': f'操作失败：{str(e)}'})


@method_decorator(csrf_exempt, name='dispatch')
class DeleteView(View):
    """删除菜单"""
    
    def post(self, request):
        try:
            data = json.loads(request.body.decode("utf-8"))
            menu_id = data.get('id')
            
            if not menu_id:
                return JsonResponse({'code': 500, 'errorInfo': '菜单ID不能为空！'})
            
            try:
                obj_menu = SysMenu.objects.get(id=menu_id)
            except SysMenu.DoesNotExist:
                return JsonResponse({'code': 500, 'errorInfo': '菜单不存在！'})
            
            # 检查是否有子菜单
            if SysMenu.objects.filter(parent_id=menu_id).exists():
                return JsonResponse({'code': 500, 'errorInfo': '该菜单下存在子菜单，无法删除！'})
            
            # 检查是否被角色使用
            if SysRoleMenu.objects.filter(menu_id=menu_id).exists():
                return JsonResponse({'code': 500, 'errorInfo': '该菜单已被角色使用，无法删除！'})
            
            # 删除菜单
            obj_menu.delete()
            return JsonResponse({'code': 200, 'info': '删除成功！'})
        except Exception as e:
            import traceback
            print(f"删除菜单错误: {e}")
            print(f"完整错误堆栈:\n{traceback.format_exc()}")
            return JsonResponse({'code': 500, 'errorInfo': f'删除失败：{str(e)}'})

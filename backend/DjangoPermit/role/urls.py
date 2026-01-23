from django.urls import path

from role.views import SearchAllRoleView, SearchView, SaveView, DeleteView, GetRoleMenusView, AssignPermissionView

urlpatterns = [
    path('searchAllRole/', SearchAllRoleView.as_view(), name='searchAllRole'),  # 查询所有的角色
    path('search', SearchView.as_view(), name='search'),  # 搜索角色
    path('save', SaveView.as_view(), name='save'),  # 保存角色（新增/编辑）
    path('delete', DeleteView.as_view(), name='delete'),  # 删除角色
    path('getRoleMenus', GetRoleMenusView.as_view(), name='getRoleMenus'),  # 获取角色的菜单列表
    path('assignPermission', AssignPermissionView.as_view(), name='assignPermission'),  # 分配权限
]
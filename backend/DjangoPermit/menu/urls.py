from django.urls import path

from menu.views import SearchAllMenuView, SearchView, SaveView, DeleteView

urlpatterns = [
    path('searchAllMenu/', SearchAllMenuView.as_view(), name='searchAllMenu'),  # 查询所有菜单
    path('search', SearchView.as_view(), name='search'),  # 搜索菜单（树形结构）
    path('save', SaveView.as_view(), name='save'),  # 保存菜单（新增/编辑）
    path('delete', DeleteView.as_view(), name='delete'),  # 删除菜单
]

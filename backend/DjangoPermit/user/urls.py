from django.urls import path

from user.views import TestView, JwtTestView, LoginView, PwdView, SaveView, AvatarView, UploadImageView, SearchView, UpdateStatusView, DeleteView, ResetPasswordView, AssignRoleView

urlpatterns = [
    path('test/', TestView.as_view(), name='test'),  # 测试
    path('jwt_test/', JwtTestView.as_view(), name='jwt_test'),  
    path('login/', LoginView.as_view(), name='login'), # 登录
    path('updateUserPwd', PwdView.as_view(), name='updateUserPwd'),  # 修改密码
    path('save', SaveView.as_view(), name='save'),  # 保存用户
    path('uploadImage', UploadImageView.as_view(), name='uploadImage'),  # 上传头像图片
    path('updateAvatar', AvatarView.as_view(), name='updateAvatar'),  # 更新头像
    path('search', SearchView.as_view(), name='search'),  # 搜索用户
    path('updateStatus', UpdateStatusView.as_view(), name='updateStatus'),  # 更新用户状态
    path('resetPassword', ResetPasswordView.as_view(), name='resetPassword'),  # 重置密码
    path('delete', DeleteView.as_view(), name='delete'),  # 删除用户
    path('assignRole', AssignRoleView.as_view(), name='assignRole'),  # 分配角色
]
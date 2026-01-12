# models.py
from django.db import models
from django.contrib.auth.models import AbstractBaseUser
from django.contrib.auth.hashers import make_password, check_password, identify_hasher
from django.core.exceptions import ValidationError
import re
from rest_framework import serializers

class SysUser(AbstractBaseUser):  # 改为继承 AbstractBaseUser
    id = models.AutoField(primary_key=True)
    username = models.CharField(max_length=100, unique=True, verbose_name="用户名")
    # 注意：AbstractBaseUser 已经提供了 password 字段，但为了兼容现有数据库结构，我们保留这个字段定义
    # 如果数据库迁移时出现冲突，可能需要调整
    password = models.CharField(max_length=255, verbose_name="密码")  # 增加长度以容纳哈希密码
    avatar = models.CharField(max_length=255, null=True, blank=True, verbose_name="用户头像")
    email = models.CharField(max_length=100, null=True, blank=True, verbose_name="用户邮箱")
    phonenumber = models.CharField(max_length=11, null=True, blank=True, verbose_name="手机号码")
    login_date = models.DateField(null=True, blank=True, verbose_name="最后登录时间")
    status = models.IntegerField(default=0, verbose_name="帐号状态（0正常 1停用）")
    create_time = models.DateField(null=True, blank=True, verbose_name="创建时间")
    update_time = models.DateField(null=True, blank=True, verbose_name="更新时间")
    remark = models.CharField(max_length=500, null=True, blank=True, verbose_name="备注")
    
    # AbstractBaseUser 已经提供了 last_login 字段（DateTimeField）
    # 但如果你需要保留 login_date（DateField），可以同时保留
    
    # 必须添加 is_active 字段（AbstractBaseUser 需要）
    is_active = models.BooleanField(default=True, verbose_name="是否活跃")
    
    # 必须定义：指定用户名字段
    USERNAME_FIELD = 'username'
    
    # 必须定义：创建超级用户时需要的字段（除了 USERNAME_FIELD 和 password）
    REQUIRED_FIELDS = ['email']  # 如果 email 不是必需的，可以改为 []

    class Meta:
        db_table = "sys_user"
        verbose_name = "系统用户"
        verbose_name_plural = "系统用户列表"

    def save(self, *args, **kwargs):
        """
        重写save方法，在保存时自动加密密码
        """
        # 如果密码是明文（没有使用Django密码格式），则进行加密
        if self.password and not self.is_password_hashed():
            self.password = make_password(self.password)
        super().save(*args, **kwargs)

    def is_password_hashed(self):
        """
        检查密码是否已经是哈希格式
        """
        try:
            # 尝试识别密码哈希算法
            identify_hasher(self.password)
            return True
        except (ValueError, KeyError):
            # 如果无法识别哈希算法，说明是明文
            return False

    def set_password(self, raw_password):
        """
        设置加密密码（推荐使用此方法设置密码）
        注意：AbstractBaseUser 已经提供了这个方法，但我们重写以保持自定义逻辑
        """
        self.password = make_password(raw_password)

    def check_password(self, raw_password):
        """
        验证密码
        注意：AbstractBaseUser 已经提供了这个方法，但我们重写以兼容明文密码
        """
        # 如果是哈希密码，使用check_password验证
        if self.is_password_hashed():
            return check_password(raw_password, self.password)
        # 如果是明文密码（旧数据），直接比较
        else:
            return raw_password == self.password

    def validate_password_strength(self, password):
        """
        密码强度验证（可选）
        """
        if len(password) < 8:
            raise ValidationError("密码至少需要8个字符")

        # 检查是否包含数字
        if not re.search(r'\d', password):
            raise ValidationError("密码必须包含至少一个数字")

        # 检查是否包含字母
        if not re.search(r'[a-zA-Z]', password):
            raise ValidationError("密码必须包含至少一个字母")

        # 检查是否包含特殊字符（可选）
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
            raise ValidationError("密码必须包含至少一个特殊字符")

        return True

    def __str__(self):
        return self.username
    
    
    
class SysUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = SysUser
        fields = '__all__'
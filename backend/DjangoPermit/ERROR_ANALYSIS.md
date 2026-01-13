# Django WSGI 应用导入错误分析

## 错误信息

```
Exception in thread django-main-thread:
Traceback (most recent call last):
  File "F:\web_projects\mywebtest\backend\DjangoPermit\.venv\Lib\site-packages\django\core\servers\basehttp.py", line 49, in get_internal_wsgi_application
    return import_string(app_path)
```

## 可能的原因

### 1. 中间件导入错误（最可能）

在 `user/middleware.py` 中，第 3 行导入了 `api_settings`：

```python
from rest_framework_simplejwt.settings import api_settings
```

**问题**：`api_settings` 在 Django 启动时可能还没有完全初始化，导致导入失败。

### 2. WSGI 应用路径配置错误

检查 `settings.py` 中的配置：
```python
WSGI_APPLICATION = 'DjangoPermit.wsgi.application'
```

### 3. settings.py 中有语法错误

检查 `settings.py` 是否有未完成的配置或语法错误。

## 解决方案

### 方案 1：延迟导入 api_settings（推荐）

修改 `user/middleware.py`，在函数内部导入 `api_settings`，而不是在模块级别导入：

```python
from django.utils.deprecation import MiddlewareMixin
from django.http import HttpResponse
from rest_framework_simplejwt.exceptions import InvalidTokenError
from jwt import ExpiredSignatureError, PyJWTError

class JwtAuthenticationMiddleware(MiddlewareMixin):
    def process_request(self, request):
        # 在函数内部导入，避免启动时的导入错误
        from rest_framework_simplejwt.settings import api_settings
        
        white_list = ["/user/login"]
        path = request.path
        if path not in white_list and not path.startswith("/media"):
            # ... 其他代码 ...
            try:
                jwt_decode_handler = api_settings.JWT_DECODE_HANDLER
                payload = jwt_decode_handler(token)
                # ...
```

### 方案 2：检查 settings.py 语法

确保 `settings.py` 中没有语法错误，特别是：
- 所有列表和字典都正确闭合
- 所有字符串都正确引号
- 没有未完成的配置

### 方案 3：检查 Python 路径

确保在正确的目录下运行 Django：
```bash
cd backend/DjangoPermit
python manage.py runserver
```

## 快速修复

**立即尝试的修复**：修改 `user/middleware.py`，将 `api_settings` 的导入移到函数内部。

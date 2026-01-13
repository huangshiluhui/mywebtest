# SECRET_KEY 安全配置指南

## ⚠️ 为什么需要保护 SECRET_KEY？

### SECRET_KEY 的作用

1. **JWT Token 签名**：用于签名和验证 JWT Token
2. **Session 加密**：用于加密用户会话数据
3. **CSRF Token**：用于生成 CSRF 保护令牌
4. **密码重置令牌**：用于生成密码重置链接

### 如果 SECRET_KEY 泄露会怎样？

- ❌ 攻击者可以伪造 JWT Token（冒充任何用户）
- ❌ 攻击者可以解密用户会话
- ❌ 攻击者可以绕过 CSRF 保护
- ❌ 攻击者可以生成密码重置链接

**后果：整个系统的安全性被破坏！**

---

## 🔒 安全配置方案

### 方案 1：使用环境变量（推荐）

#### 优点
- ✅ 不将密钥写入代码
- ✅ 不同环境使用不同密钥
- ✅ 符合 12-Factor App 原则
- ✅ 易于部署和管理

#### 实现步骤

1. **安装 python-decouple**
```bash
pip install python-decouple
```

2. **创建 .env 文件**（不提交到 Git）
```env
# .env 文件（不要提交到 Git！）
SECRET_KEY=django-insecure-i0u9fcxf0v9^=p$h+xbw3trg61ac$p@ub-n+9np%ipb0_&)t0-
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1
```

3. **更新 settings.py**
```python
from decouple import config

SECRET_KEY = config('SECRET_KEY')
DEBUG = config('DEBUG', default=False, cast=bool)
ALLOWED_HOSTS = config('ALLOWED_HOSTS', default='localhost,127.0.0.1').split(',')
```

---

### 方案 2：使用 python-dotenv

#### 实现步骤

1. **安装 python-dotenv**
```bash
pip install python-dotenv
```

2. **更新 settings.py**
```python
from dotenv import load_dotenv
import os

# 加载 .env 文件
load_dotenv()

SECRET_KEY = os.getenv('SECRET_KEY')
DEBUG = os.getenv('DEBUG', 'False') == 'True'
ALLOWED_HOSTS = os.getenv('ALLOWED_HOSTS', 'localhost,127.0.0.1').split(',')
```

---

### 方案 3：使用 Django 的密钥管理（生产环境）

#### 使用系统环境变量

```python
import os

SECRET_KEY = os.environ.get('SECRET_KEY')
if not SECRET_KEY:
    raise ValueError("SECRET_KEY 环境变量未设置！")
```

#### 部署时设置环境变量

**Linux/Mac:**
```bash
export SECRET_KEY='your-secret-key-here'
python manage.py runserver
```

**Windows:**
```cmd
set SECRET_KEY=your-secret-key-here
python manage.py runserver
```

**Docker:**
```yaml
# docker-compose.yml
services:
  web:
    environment:
      - SECRET_KEY=${SECRET_KEY}
```

**云平台（如 Heroku、AWS、Azure）:**
- 在平台的控制面板中设置环境变量

---

## 📝 完整实现示例

### 1. 创建 .env.example（模板文件，可以提交到 Git）

```env
# Django 配置
SECRET_KEY=your-secret-key-here
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# 数据库配置
DB_NAME=db_admin
DB_USER=hualj
DB_PASSWORD=123456
DB_HOST=127.0.0.1
DB_PORT=3306
```

### 2. 创建 .env（实际配置文件，不提交到 Git）

```env
# 复制 .env.example 并填入实际值
SECRET_KEY=django-insecure-i0u9fcxf0v9^=p$h+xbw3trg61ac$p@ub-n+9np%ipb0_&)t0-
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1
```

### 3. 更新 .gitignore

```
# 环境变量文件
.env
.env.local
.env.*.local

# 但保留模板文件
!.env.example
```

### 4. 更新 settings.py

```python
from decouple import config, Csv
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

# 从环境变量读取 SECRET_KEY
SECRET_KEY = config('SECRET_KEY', default='django-insecure-fallback-key-for-dev-only')

# 安全警告：如果 SECRET_KEY 未设置，在生产环境应该抛出异常
if SECRET_KEY == 'django-insecure-fallback-key-for-dev-only':
    import sys
    if 'runserver' not in sys.argv:  # 非开发服务器
        raise ValueError("SECRET_KEY 环境变量未设置！生产环境必须设置 SECRET_KEY")

DEBUG = config('DEBUG', default=False, cast=bool)
ALLOWED_HOSTS = config('ALLOWED_HOSTS', default='localhost,127.0.0.1', cast=Csv())
```

---

## 🚀 部署流程

### 开发环境

1. 复制 `.env.example` 为 `.env`
2. 在 `.env` 中填入开发环境的配置
3. 运行项目

### 生产环境

#### 方式 1：使用环境变量（推荐）

```bash
# 设置环境变量
export SECRET_KEY='your-production-secret-key'
export DEBUG=False
export ALLOWED_HOSTS='yourdomain.com,www.yourdomain.com'

# 运行项目
python manage.py runserver
```

#### 方式 2：使用 .env 文件

1. 在服务器上创建 `.env` 文件
2. 填入生产环境的配置
3. 确保 `.env` 文件权限安全（只有应用用户可读）
```bash
chmod 600 .env  # 只有所有者可读写
```

#### 方式 3：使用密钥管理服务

**AWS Secrets Manager:**
```python
import boto3

def get_secret():
    client = boto3.client('secretsmanager')
    response = client.get_secret_value(SecretId='django-secret-key')
    return response['SecretString']

SECRET_KEY = get_secret()
```

**Azure Key Vault:**
```python
from azure.keyvault.secrets import SecretClient

def get_secret():
    client = SecretClient(vault_url="https://your-vault.vault.azure.net/", credential=credential)
    secret = client.get_secret("django-secret-key")
    return secret.value

SECRET_KEY = get_secret()
```

---

## 🔐 生成安全的 SECRET_KEY

### 方法 1：使用 Django 命令

```bash
python manage.py shell
>>> from django.core.management.utils import get_random_secret_key
>>> print(get_random_secret_key())
```

### 方法 2：使用 Python

```python
import secrets
print(secrets.token_urlsafe(50))
```

### 方法 3：在线生成器

- https://djecrety.ir/ （Django Secret Key Generator）

---

## ✅ 安全检查清单

- [ ] SECRET_KEY 不在代码中硬编码
- [ ] `.env` 文件已添加到 `.gitignore`
- [ ] `.env.example` 作为模板提交到 Git（不包含真实密钥）
- [ ] 生产环境使用强随机 SECRET_KEY
- [ ] 不同环境使用不同的 SECRET_KEY
- [ ] 生产环境的 SECRET_KEY 定期轮换（需要迁移）
- [ ] 服务器上的 `.env` 文件权限设置为 600
- [ ] 团队成员知道如何配置环境变量

---

## 📚 最佳实践

1. **永远不要提交 SECRET_KEY 到 Git**
2. **使用环境变量或密钥管理服务**
3. **不同环境使用不同的密钥**
4. **定期轮换密钥**（需要迁移现有数据）
5. **使用强随机密钥**（至少 50 个字符）
6. **限制密钥访问权限**

---

## 🆘 如果 SECRET_KEY 泄露了怎么办？

1. **立即更换 SECRET_KEY**
2. **使所有现有 Token 失效**（用户需要重新登录）
3. **检查是否有异常活动**
4. **通知用户更改密码**（如果可能）
5. **审查访问日志**

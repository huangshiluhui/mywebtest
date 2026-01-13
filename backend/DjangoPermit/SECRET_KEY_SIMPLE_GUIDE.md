# SECRET_KEY 安全配置 - 简单方案

## 方案：使用环境变量（不修改代码）

### 优点
- ✅ 不需要修改 `settings.py`
- ✅ 不需要安装额外包
- ✅ 使用 Python 标准库 `os.environ`

---

## 实现步骤

### 方式 1：在 settings.py 中添加环境变量支持（可选）

在 `settings.py` 文件开头添加：

```python
import os

# 从环境变量读取 SECRET_KEY，如果未设置则使用默认值
SECRET_KEY = os.environ.get('SECRET_KEY', 'django-insecure-i0u9fcxf0v9^=p$h+xbw3trg61ac$p@ub-n+9np%ipb0_&)t0-')
```

**或者保持原样，直接使用环境变量覆盖：**

### 方式 2：直接使用环境变量（推荐，无需修改代码）

#### Windows PowerShell:
```powershell
$env:SECRET_KEY="your-production-secret-key"
python manage.py runserver
```

#### Windows CMD:
```cmd
set SECRET_KEY=your-production-secret-key
python manage.py runserver
```

#### Linux/Mac:
```bash
export SECRET_KEY='your-production-secret-key'
python manage.py runserver
```

---

## 部署时的配置

### 开发环境
- 可以不设置环境变量，使用代码中的默认值

### 生产环境

#### 1. 使用系统环境变量

**Linux (systemd service):**
```ini
# /etc/systemd/system/django.service
[Service]
Environment="SECRET_KEY=your-production-secret-key"
Environment="DEBUG=False"
```

**Docker:**
```yaml
# docker-compose.yml
services:
  web:
    environment:
      - SECRET_KEY=${SECRET_KEY}
```

**云平台:**
- Heroku: `heroku config:set SECRET_KEY=your-key`
- AWS: 在 EC2 实例的环境变量中设置
- Azure: 在应用设置中配置

#### 2. 使用 .env 文件（需要修改代码）

如果使用 `.env` 文件，需要安装 `python-decouple` 或 `python-dotenv`。

---

## 生成安全的 SECRET_KEY

```bash
python manage.py shell
```

```python
from django.core.management.utils import get_random_secret_key
print(get_random_secret_key())
```

---

## 当前错误排查

如果你遇到了 `basehttp.py` 的错误，可能是：

1. **缺少依赖包**
```bash
pip install -r requirements.txt
```

2. **Python 版本不兼容**
- Django 6.0 需要 Python 3.10+

3. **虚拟环境问题**
```bash
# 激活虚拟环境
.venv\Scripts\activate  # Windows
source .venv/bin/activate  # Linux/Mac
```

4. **端口被占用**
```bash
# 使用其他端口
python manage.py runserver 8080
```

---

## 最简单的方案（推荐）

**不修改代码，直接使用环境变量：**

1. 生成新的 SECRET_KEY
2. 在启动服务器前设置环境变量
3. Django 会自动读取环境变量（如果代码支持）

**如果代码不支持环境变量，可以这样修改：**

在 `settings.py` 第 23 行改为：
```python
import os
SECRET_KEY = os.environ.get('SECRET_KEY', 'django-insecure-i0u9fcxf0v9^=p$h+xbw3trg61ac$p@ub-n+9np%ipb0_&)t0-')
```

这样：
- 如果设置了环境变量，使用环境变量的值
- 如果没有设置，使用默认值（开发环境）

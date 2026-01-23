# 前后端部署说明

本文档说明如何将 **Vue 3 前端** 与 **Django 6 后端** 部署到生产环境。推荐采用 **同域部署**：Nginx 提供静态前端，并把 `/api`、`/media` 代理到后端。

---

## 一、环境要求

| 组件 | 说明 |
|------|------|
| **Node.js** | 用于构建前端（如 18+） |
| **Python** | 3.10+，用于运行 Django |
| **MySQL** | 数据库，需提前创建库 `db_admin`（或你配置的 `DJANGO_DB_NAME`） |
| **Nginx** | 反向代理与静态资源（或同类 Web 服务器） |

---

## 二、前端部署

### 2.1 创建生产环境 API 地址配置（必做）

部署前**必须**在 `frontend/my-vue/` 下创建 `.env.production`，否则生产构建会继续使用默认 `http://localhost:8080`。

**同域部署（推荐）**：Nginx 将 `/api` 代理到后端，则：

```env
VUE_APP_BASE_API=/api
```

**前后端不同域**：直接写后端完整地址，例如：

```env
VUE_APP_BASE_API=https://api.你的域名
```

### 2.2 构建

```bash
cd frontend/my-vue
npm ci
npm run build
```

产物在 `frontend/my-vue/dist/`，将整个 `dist` 目录部署到 Nginx 的静态根目录（见下）。

### 2.3 publicPath 说明

当前 `vue.config.js` 未设置 `publicPath`，默认为 `'/'`，适合部署在站点根路径。若部署在子路径（如 `https://域名/app/`），需在 `vue.config.js` 中设置 `publicPath: '/app/'`，并在 Nginx 中相应调整 `root`/`location`。

---

## 三、后端部署

后端项目根目录：`backend/DjangoPermit/`（与 `manage.py` 同级）。

### 3.1 虚拟环境与依赖

```bash
cd backend/DjangoPermit
python -m venv .venv

# Linux / macOS
. .venv/bin/activate

# Windows
.venv\Scripts\activate

pip install -r requirements.txt
```

### 3.2 环境变量（生产必设）

在运行 Django / Gunicorn 的 shell 或 systemd/进程管理工具中配置：

| 变量 | 说明 | 示例 |
|------|------|------|
| `DJANGO_SECRET_KEY` | 密钥，生产务必重设 | 随机长字符串 |
| `DJANGO_DEBUG` | 是否调试 | `False` |
| `DJANGO_ALLOWED_HOSTS` | 允许的 Host，逗号分隔 | `yourdomain.com,www.yourdomain.com,服务器IP` |
| `DJANGO_DB_NAME` | 数据库名 | `db_admin` |
| `DJANGO_DB_USER` | 数据库用户 | `hualj` |
| `DJANGO_DB_PASSWORD` | 数据库密码 | 你的密码 |
| `DJANGO_DB_HOST` | 数据库主机 | `127.0.0.1` |
| `DJANGO_DB_PORT` | 数据库端口 | `3306` |
| `DJANGO_CORS_ORIGINS` | CORS 允许来源，逗号分隔（同域可少配） | `https://yourdomain.com` |

示例（Linux，临时导出）：

```bash
export DJANGO_SECRET_KEY="你的生产密钥"
export DJANGO_DEBUG=False
export DJANGO_ALLOWED_HOSTS="yourdomain.com,1.2.3.4"
export DJANGO_DB_NAME=db_admin
export DJANGO_DB_USER=hualj
export DJANGO_DB_PASSWORD=你的密码
export DJANGO_DB_HOST=127.0.0.1
export DJANGO_DB_PORT=3306
export DJANGO_CORS_ORIGINS="https://yourdomain.com"
```

### 3.3 数据库与迁移

确保 MySQL 已创建对应库，然后：

```bash
python manage.py migrate
```

若使用 Django 自带的 `admin` 等静态文件，可执行（非必须，本前端为 Vue 独立 SPA 可不做）：

```bash
python manage.py collectstatic --noinput
```

### 3.4 使用 Gunicorn 启动（Linux / macOS）

在 `backend/DjangoPermit` 下：

```bash
gunicorn DjangoPermit.wsgi:application -b 127.0.0.1:8000 -w 4
```

或使用项目内脚本（若已提供）：

```bash
# Linux / macOS
./deploy/start_gunicorn.sh
```

`-w 4` 为进程数，可按 CPU 调整。生产建议用 **systemd** 或 **supervisor** 管理进程、重启与日志。

### 3.5 Windows 下替代 Gunicorn：Waitress

Gunicorn 不支持 Windows，可安装 `waitress` 并启动：

```bash
pip install waitress
waitress-serve --listen=127.0.0.1:8000 DjangoPermit.wsgi:application
```

或使用：

```bat
deploy\start_waitress.bat
```

---

## 四、Nginx 配置示例（同域部署）

假设：

- 前端静态：`/var/www/mywebtest/dist`（即 `frontend/my-vue/dist` 的部署路径）
- 后端：`http://127.0.0.1:8000`
- 站点：`http://yourdomain.com` 或 `http://服务器IP`

要点：

- `/` → 前端 `dist`
- `/api/` → 反向代理到 `http://127.0.0.1:8000/`，路径会从 `/api/xxx` 变为 `/xxx`（如 `/api/user/login` → 后端 `/user/login`）
- `/media/` → 代理到 Django 的 `media`。若前端 `VUE_APP_BASE_API=/api`，则 `getServerUrl() + '/media/...'` 为 `/api/media/...`，需由 Nginx 把 `/api/media/` 转给后端 `/media/`；下面示例用 `location /api/` 统一代理到后端，因此 `/api/media/` 会变成 `/media/`，由 Django 的 `re_path('media/...')` 处理。

**重要**：当前前端 `getServerUrl()` 返回 `baseUrl`（即 `VUE_APP_BASE_API`）。若 `VUE_APP_BASE_API=/api`，则头像等地址为 `/api/media/userAvatar/xxx`，即 `/api/media/` 需落在 `location /api/` 的代理范围内。`proxy_pass http://127.0.0.1:8000/` 会把 `/api` 前缀去掉，故 `/api/media/userAvatar/a.jpg` → 后端收到 `/media/userAvatar/a.jpg`，与 Django `media` 路由一致。

下面配置已按此设计。

```nginx
server {
    listen 80;
    server_name yourdomain.com;   # 或 服务器IP、localhost

    # 前端静态
    root /var/www/mywebtest/dist;
    index index.html;
    location / {
        try_files $uri $uri/ /index.html;
    }

    # 后端 API 与 media：/api/ -> Django 根，/api/media/ -> /media/
    location /api/ {
        proxy_pass http://127.0.0.1:8000/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_connect_timeout 60s;
        proxy_read_timeout 60s;
    }

    # 若存在未通过 /api 访问的 /media（按需保留）
    location /media/ {
        proxy_pass http://127.0.0.1:8000/media/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

将 `root` 改为你实际存放 `dist` 的路径。配置后执行 `nginx -t` 再 `nginx -s reload`。

完整示例见：`deploy/nginx_example.conf`。

---

## 五、部署流程小结（同域）

1. **MySQL**：建库，导入或通过迁移建表。
2. **后端**：  
   - 虚拟环境、`pip install -r requirements.txt`  
   - 设置 `DJANGO_*` 环境变量  
   - `python manage.py migrate`  
   - 使用 Gunicorn（或 Windows 下 waitress）监听 `127.0.0.1:8000`，并用 systemd/supervisor 等做进程管理。
3. **前端**：  
   - 在 `frontend/my-vue/` 创建 `.env.production`，设置 `VUE_APP_BASE_API=/api`  
   - `npm ci && npm run build`  
   - 将 `dist` 放到 Nginx 的 `root` 目录。
4. **Nginx**：  
   - 按上面示例配置 `server`，`/`→`dist`，`/api/`→`http://127.0.0.1:8000/`，`/media/` 若单独访问则代理到 `http://127.0.0.1:8000/media/`  
   - `nginx -t && nginx -s reload`。

---

## 六、前后端分离、不同域

- 前端：`.env.production` 中 `VUE_APP_BASE_API=https://api.你的域名`。
- 后端：  
  - `DJANGO_ALLOWED_HOSTS` 包含 `api.你的域名`  
  - `DJANGO_CORS_ORIGINS` 包含 `https://你的前端域名`  
- 为 API 单独配置 Nginx（或等价）与 HTTPS。

---

## 七、故障排查

- **404 / 接口 404**：检查 `DJANGO_ALLOWED_HOSTS`、Nginx `proxy_pass` 与 `location /api/` 的斜杠是否一致（`/api/` 配 `http://127.0.0.1:8000/` 会去掉 `/api`）。
- **静态/前端路由 404**：确认 `try_files $uri $uri/ /index.html;` 和 `root` 指向的 `dist` 路径。
- **头像/媒体 404**：确认 `getServerUrl()` 为 `/api` 时请求为 `/api/media/...`，且 Nginx 将 `/api/` 代理到后端；或单独配置的 `/media/` 代理正确。
- **CORS 报错**：生产下 `DEBUG=False` 时，`DJANGO_CORS_ORIGINS` 需包含浏览器访问使用的前端完整来源（含协议、域名、端口）。

---

## 八、参考文件

- `deploy/nginx_example.conf`：Nginx 完整示例  
- `deploy/start_gunicorn.sh`：Linux/macOS 下 Gunicorn 启动  
- `deploy/start_waitress.bat`：Windows 下 Waitress 启动  

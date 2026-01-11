# CORS 跨域问题解决方案详解

## 一、跨域问题的根源

### 1. 浏览器的同源策略（Same-Origin Policy）

浏览器有一个安全机制叫"同源策略"，它规定：
- **同源**：协议、域名、端口三者完全相同
- **跨域**：只要协议、域名、端口有一个不同，就是跨域

**示例**：
```
前端：http://localhost:8081  (Vue 开发服务器)
后端：http://localhost:8000  (Django 服务器)

❌ 这是跨域请求（端口不同：8081 ≠ 8000）
```

### 2. 浏览器会阻止跨域请求

当浏览器检测到跨域请求时，会：
1. 发送请求到服务器（请求可以发出）
2. 服务器返回响应
3. **浏览器检查响应头中的 CORS 信息**
4. 如果没有正确的 CORS 响应头，**浏览器会阻止 JavaScript 访问响应数据**

## 二、CORS 如何解决跨域问题

### CORS 的核心原理

**CORS（Cross-Origin Resource Sharing）** 通过在 HTTP 响应头中添加特定的头部信息，告诉浏览器：
- "这个跨域请求是我允许的"
- "允许来自某个源（Origin）的请求"

### 关键：HTTP 响应头

CORS 不是"阻止"跨域请求，而是通过**响应头**告诉浏览器"允许"这个跨域请求。

## 三、前后端的绑定关系

### 1. 前端发送请求（浏览器自动添加 Origin）

```javascript
// 前端代码
axios.get('http://localhost:8000/user/test')
```

**浏览器自动添加的请求头**：
```
GET /user/test HTTP/1.1
Host: localhost:8000
Origin: http://localhost:8081  ← 浏览器自动添加，表示请求来源
```

### 2. 后端处理请求（CORS 中间件添加响应头）

Django 的 `corsheaders.middleware.CorsMiddleware` 会：

1. **检查请求头中的 `Origin`**
   ```
   Origin: http://localhost:8081
   ```

2. **根据 CORS 配置决定是否允许**
   ```python
   CORS_ALLOW_ALL_ORIGINS = True  # 允许所有来源
   # 或者
   CORS_ALLOWED_ORIGINS = ["http://localhost:8081"]  # 允许特定来源
   ```

3. **在响应头中添加 CORS 信息**
   ```
   HTTP/1.1 200 OK
   Access-Control-Allow-Origin: http://localhost:8081  ← 允许的来源
   Access-Control-Allow-Methods: GET, POST, PUT, DELETE  ← 允许的方法
   Access-Control-Allow-Headers: authorization, content-type  ← 允许的请求头
   Access-Control-Allow-Credentials: true  ← 允许携带凭证
   ```

### 3. 浏览器检查响应头

浏览器收到响应后：
1. 检查 `Access-Control-Allow-Origin` 是否匹配当前页面的 Origin
2. 如果匹配，**允许 JavaScript 访问响应数据**
3. 如果不匹配，**阻止访问，抛出 CORS 错误**

## 四、完整的请求-响应流程

### 简单请求（Simple Request）

```
┌─────────────┐                                    ┌─────────────┐
│   浏览器     │                                    │ Django 后端 │
│ (8081)      │                                    │  (8000)     │
└──────┬──────┘                                    └──────┬──────┘
       │                                                   │
       │ 1. GET /user/test                               │
       │    Origin: http://localhost:8081               │
       │─────────────────────────────────────────────────>│
       │                                                   │
       │                                                   │ 2. CORS 中间件检查
       │                                                   │    - 检查 Origin
       │                                                   │    - 检查 CORS 配置
       │                                                   │    - 添加响应头
       │                                                   │
       │ 3. HTTP 200 OK                                  │
       │    Access-Control-Allow-Origin: *            │
       │    Access-Control-Allow-Methods: GET, POST   │
       │    {data: ...}                                 │
       │<─────────────────────────────────────────────────│
       │                                                   │
       │ 4. 浏览器检查响应头                              │
       │    ✅ Origin 匹配，允许访问                      │
       │                                                   │
```

### 复杂请求（需要预检 Preflight）

对于复杂请求（如 POST with JSON），浏览器会先发送 OPTIONS 预检请求：

```
┌─────────────┐                                    ┌─────────────┐
│   浏览器     │                                    │ Django 后端 │
└──────┬──────┘                                    └──────┬──────┘
       │                                                   │
       │ 1. OPTIONS /user/test (预检请求)                 │
       │    Origin: http://localhost:8081               │
       │    Access-Control-Request-Method: POST         │
       │    Access-Control-Request-Headers: content-type│
       │─────────────────────────────────────────────────>│
       │                                                   │
       │                                                   │ 2. CORS 中间件处理预检
       │                                                   │    - 检查方法和请求头
       │                                                   │    - 返回允许的配置
       │                                                   │
       │ 3. HTTP 200 OK                                  │
       │    Access-Control-Allow-Origin: *            │
       │    Access-Control-Allow-Methods: POST        │
       │    Access-Control-Allow-Headers: content-type │
       │<─────────────────────────────────────────────────│
       │                                                   │
       │ 4. 浏览器检查预检响应                             │
       │    ✅ 允许，发送实际请求                          │
       │                                                   │
       │ 5. POST /user/test (实际请求)                    │
       │    Origin: http://localhost:8081               │
       │    Content-Type: application/json              │
       │    {username: "test", password: "123"}        │
       │─────────────────────────────────────────────────>│
       │                                                   │
       │                                                   │ 6. 处理请求，返回数据
       │                                                   │
       │ 7. HTTP 200 OK                                  │
       │    Access-Control-Allow-Origin: *            │
       │    {token: "xxx", user: {...}}                │
       │<─────────────────────────────────────────────────│
       │                                                   │
       │ 8. 浏览器检查响应头                              │
       │    ✅ 允许访问数据                               │
       │                                                   │
```

## 五、前后端的绑定关系详解

### 1. 请求绑定：Origin 头部

**前端**：浏览器自动在请求头中添加 `Origin`
```
Origin: http://localhost:8081
```

**后端**：CORS 中间件读取 `Origin`，决定是否允许
```python
# Django 检查
if request.headers.get('Origin') in CORS_ALLOWED_ORIGINS:
    # 允许
else:
    # 拒绝
```

### 2. 响应绑定：CORS 响应头

**后端**：CORS 中间件在响应头中添加允许信息
```
Access-Control-Allow-Origin: http://localhost:8081
Access-Control-Allow-Methods: GET, POST, PUT, DELETE
Access-Control-Allow-Headers: authorization, content-type
```

**前端**：浏览器检查这些响应头，决定是否允许访问

### 3. 配置绑定：Django settings.py

```python
# 允许的来源（绑定前端地址）
CORS_ALLOW_ALL_ORIGINS = True  # 允许所有
# 或
CORS_ALLOWED_ORIGINS = [
    "http://localhost:8081",  # 前端地址
]

# 允许的请求方法（绑定前端使用的 HTTP 方法）
CORS_ALLOW_METHODS = [
    'GET', 'POST', 'PUT', 'DELETE',  # 前端可能使用的方法
]

# 允许的请求头（绑定前端发送的请求头）
CORS_ALLOW_HEADERS = [
    'authorization',  # JWT token
    'content-type',   # JSON 数据
]
```

### 4. 代码绑定：前端请求配置

```javascript
// request.js
let baseUrl = "http://localhost:8080";  // 后端地址

// 请求拦截器添加 authorization 头
config.headers.AUTHORIZATION = window.sessionStorage.getItem('token');
```

**绑定关系**：
- 前端发送 `authorization` 头
- 后端 `CORS_ALLOW_HEADERS` 中必须包含 `'authorization'`
- 否则预检请求会失败

## 六、关键配置项说明

### CORS_ALLOW_ALL_ORIGINS

```python
CORS_ALLOW_ALL_ORIGINS = True
```

**作用**：允许所有来源的跨域请求

**响应头**：
```
Access-Control-Allow-Origin: *
```

**绑定**：不绑定特定前端，允许任何来源

### CORS_ALLOWED_ORIGINS

```python
CORS_ALLOWED_ORIGINS = [
    "http://localhost:8081",
    "http://127.0.0.1:8081",
]
```

**作用**：只允许指定的来源

**响应头**：
```
Access-Control-Allow-Origin: http://localhost:8081
```

**绑定**：严格绑定前端地址，更安全

### CORS_ALLOW_METHODS

```python
CORS_ALLOW_METHODS = ['GET', 'POST', 'PUT', 'DELETE']
```

**作用**：允许的 HTTP 方法

**绑定**：必须包含前端使用的所有 HTTP 方法

### CORS_ALLOW_HEADERS

```python
CORS_ALLOW_HEADERS = [
    'authorization',  # 必须包含，因为前端发送 JWT token
    'content-type',
]
```

**作用**：允许的请求头

**绑定**：必须包含前端发送的所有自定义请求头

### CORS_ALLOW_CREDENTIALS

```python
CORS_ALLOW_CREDENTIALS = True
```

**作用**：允许携带凭证（cookies、authorization headers）

**绑定**：如果前端需要发送 cookies 或认证信息，必须设置为 True

## 七、实际项目中的绑定关系

### 当前项目配置

**前端** (`request.js`):
```javascript
baseUrl = "http://localhost:8080"  // 后端地址
headers.AUTHORIZATION = token      // JWT token
```

**后端** (`settings.py`):
```python
CORS_ALLOW_ALL_ORIGINS = True           # 允许所有来源
CORS_ALLOW_METHODS = ['GET', 'POST', ...]  # 允许的方法
CORS_ALLOW_HEADERS = ['authorization', ...]  # 允许的请求头（包含 authorization）
CORS_ALLOW_CREDENTIALS = True           # 允许凭证
```

**绑定关系**：
1. ✅ 前端地址 → `CORS_ALLOW_ALL_ORIGINS = True`（允许所有）
2. ✅ 前端方法 → `CORS_ALLOW_METHODS`（包含所有可能的方法）
3. ✅ 前端请求头 → `CORS_ALLOW_HEADERS`（包含 `authorization`）
4. ✅ 前端凭证 → `CORS_ALLOW_CREDENTIALS = True`

## 八、为什么 CORS 能解决跨域问题？

### 关键理解

1. **跨域请求本身不会被阻止**
   - 浏览器会发送请求到服务器
   - 服务器会处理请求并返回响应

2. **浏览器会阻止 JavaScript 访问跨域响应**
   - 这是浏览器的安全机制
   - 除非响应头中有正确的 CORS 信息

3. **CORS 通过响应头告诉浏览器"允许"**
   - `Access-Control-Allow-Origin` 告诉浏览器允许的来源
   - 浏览器检查后，允许 JavaScript 访问响应数据

### 简单类比

想象一个门卫（浏览器）：
- 前端（访客）想进入后端（大楼）
- 门卫检查访客的身份证（Origin）
- 后端（大楼管理员）说："我允许这个访客进入"（CORS 响应头）
- 门卫看到允许信息后，放行（允许访问响应数据）

## 九、总结

### CORS 解决跨域的核心

1. **请求阶段**：浏览器自动添加 `Origin` 头部
2. **处理阶段**：后端 CORS 中间件检查并添加允许的响应头
3. **响应阶段**：浏览器检查响应头，决定是否允许访问

### 前后端绑定关系

| 前端行为 | 后端配置 | 绑定关系 |
|---------|---------|---------|
| 请求来源 (Origin) | `CORS_ALLOW_ALL_ORIGINS` 或 `CORS_ALLOWED_ORIGINS` | 来源绑定 |
| HTTP 方法 (GET/POST) | `CORS_ALLOW_METHODS` | 方法绑定 |
| 请求头 (authorization) | `CORS_ALLOW_HEADERS` | 请求头绑定 |
| 携带凭证 | `CORS_ALLOW_CREDENTIALS` | 凭证绑定 |

### 关键要点

> **CORS 不是"阻止"跨域，而是通过 HTTP 响应头告诉浏览器"允许"跨域。**  
> **前后端的绑定是通过请求头（Origin）和响应头（Access-Control-Allow-*）实现的。**

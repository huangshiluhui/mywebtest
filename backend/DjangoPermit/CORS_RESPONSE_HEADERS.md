# CORS 响应头机制详解

## 核心理解

**✅ 完全正确！后端配置 CORS 后，是通过 HTTP 响应头告诉浏览器允许跨域的。**

## 工作机制

### 1. 后端 CORS 中间件的作用

Django 的 `corsheaders.middleware.CorsMiddleware` 会在响应中添加 CORS 相关的响应头：

```python
# settings.py
MIDDLEWARE = [
    ...
    'corsheaders.middleware.CorsMiddleware',  # 这个中间件负责添加响应头
    ...
]
```

### 2. 响应头的内容

当后端配置了 CORS 后，响应头会包含：

```
HTTP/1.1 200 OK
Access-Control-Allow-Origin: *                    ← 告诉浏览器允许的来源
Access-Control-Allow-Methods: GET, POST, PUT, DELETE  ← 告诉浏览器允许的方法
Access-Control-Allow-Headers: authorization, content-type  ← 告诉浏览器允许的请求头
Access-Control-Allow-Credentials: true           ← 告诉浏览器允许携带凭证
Content-Type: application/json
{data: "..."}
```

### 3. 浏览器如何读取这些响应头

```
浏览器收到响应
    ↓
检查响应头中的 CORS 信息
    ↓
Access-Control-Allow-Origin: *  ← 浏览器读取这个
    ↓
检查当前页面的 Origin 是否匹配
    ↓
✅ 匹配 → 允许访问响应数据
❌ 不匹配 → 阻止访问，报 CORS 错误
```

## 配置与响应头的对应关系

### 配置项 → 响应头

| Django 配置 | HTTP 响应头 | 作用 |
|-----------|------------|------|
| `CORS_ALLOW_ALL_ORIGINS = True` | `Access-Control-Allow-Origin: *` | 允许所有来源 |
| `CORS_ALLOWED_ORIGINS = ["http://localhost:8081"]` | `Access-Control-Allow-Origin: http://localhost:8081` | 允许特定来源 |
| `CORS_ALLOW_METHODS = ['GET', 'POST']` | `Access-Control-Allow-Methods: GET, POST` | 允许的 HTTP 方法 |
| `CORS_ALLOW_HEADERS = ['authorization']` | `Access-Control-Allow-Headers: authorization` | 允许的请求头 |
| `CORS_ALLOW_CREDENTIALS = True` | `Access-Control-Allow-Credentials: true` | 允许携带凭证 |

## 实际示例

### 当前项目的配置

```python
# settings.py
CORS_ALLOW_ALL_ORIGINS = True
CORS_ALLOW_METHODS = ['GET', 'POST', 'PUT', 'DELETE']
CORS_ALLOW_HEADERS = ['authorization', 'content-type']
CORS_ALLOW_CREDENTIALS = True
```

### 实际响应头（浏览器收到的）

```
HTTP/1.1 200 OK
Access-Control-Allow-Origin: *
Access-Control-Allow-Methods: GET, POST, PUT, DELETE, OPTIONS
Access-Control-Allow-Headers: accept, accept-encoding, authorization, content-type, dnt, origin, user-agent, x-csrftoken, x-requested-with
Access-Control-Allow-Credentials: true
Access-Control-Max-Age: 86400
Content-Type: application/json
```

## 浏览器如何"读懂"这些响应头

### 步骤1：浏览器收到响应

```
前端请求：http://localhost:8000/user/test
Origin: http://localhost:8081

后端响应：
HTTP/1.1 200 OK
Access-Control-Allow-Origin: *
{data: "..."}
```

### 步骤2：浏览器检查响应头

```javascript
// 浏览器内部逻辑（伪代码）
const responseOrigin = response.headers['Access-Control-Allow-Origin'];
const requestOrigin = request.headers['Origin'];

if (responseOrigin === '*' || responseOrigin === requestOrigin) {
    // ✅ 允许访问
    allowAccess(response.data);
} else {
    // ❌ 阻止访问
    throw new CORS_ERROR('CORS policy blocked');
}
```

### 步骤3：决定是否允许访问

- ✅ 如果 `Access-Control-Allow-Origin` 是 `*` 或匹配当前 Origin
- ✅ 如果请求方法在 `Access-Control-Allow-Methods` 中
- ✅ 如果请求头在 `Access-Control-Allow-Headers` 中
- ✅ 如果 `Access-Control-Allow-Credentials` 为 true（需要时）

**→ 浏览器允许 JavaScript 访问响应数据**

## 预检请求（Preflight）的响应头

对于复杂请求，浏览器会先发送 OPTIONS 预检请求：

### 预检请求的响应头

```
OPTIONS /user/test HTTP/1.1
Origin: http://localhost:8081
Access-Control-Request-Method: POST
Access-Control-Request-Headers: content-type

↓ 后端响应

HTTP/1.1 200 OK
Access-Control-Allow-Origin: *                    ← 告诉浏览器允许的来源
Access-Control-Allow-Methods: POST               ← 告诉浏览器允许的方法
Access-Control-Allow-Headers: content-type       ← 告诉浏览器允许的请求头
Access-Control-Max-Age: 86400                     ← 告诉浏览器缓存时间
```

**浏览器检查这些响应头后**：
- ✅ 如果都符合要求 → 发送实际请求
- ❌ 如果不符合 → 不发送实际请求，直接报 CORS 错误

## 如何验证响应头

### 方法1：浏览器开发者工具

1. 打开开发者工具（F12）
2. 切换到 **Network** 标签
3. 发起一个 API 请求
4. 点击该请求
5. 查看 **Headers** 标签
6. 查看 **Response Headers** 部分

应该能看到：
```
Access-Control-Allow-Origin: *
Access-Control-Allow-Methods: GET, POST, PUT, DELETE
Access-Control-Allow-Headers: authorization, content-type
```

### 方法2：使用 curl 命令

```bash
curl -i -H "Origin: http://localhost:8081" http://localhost:8000/user/test
```

会显示完整的响应头，包括 CORS 相关的头部。

### 方法3：在代码中查看

```javascript
axios.get('http://localhost:8000/user/test')
  .then(response => {
    console.log('响应头:', response.headers);
    // 可以看到 Access-Control-Allow-Origin 等
  });
```

## 关键理解

### 1. 响应头是"通行证"

```
后端配置 CORS
    ↓
CORS 中间件添加响应头
    ↓
响应头 = "通行证"
    ↓
浏览器检查"通行证"
    ↓
✅ 有通行证 → 允许访问
❌ 无通行证 → 阻止访问
```

### 2. 响应头是浏览器和服务器之间的"协议"

- **服务器说**："我允许这个来源访问"（通过响应头）
- **浏览器说**："好的，我检查一下，如果匹配就允许"（检查响应头）

### 3. 这是 HTTP 协议的一部分

CORS 响应头是 HTTP 协议的标准头部，浏览器和服务器都遵循这个协议：
- 服务器：添加 CORS 响应头
- 浏览器：检查 CORS 响应头
- 结果：决定是否允许访问

## 总结

### 你的理解完全正确！

✅ **后端配置 CORS → 响应头告诉浏览器允许跨域**

### 工作流程

```
1. 前端发送请求（包含 Origin）
   ↓
2. 后端处理请求
   ↓
3. CORS 中间件添加响应头
   Access-Control-Allow-Origin: *
   Access-Control-Allow-Methods: GET, POST
   ...
   ↓
4. 浏览器收到响应
   ↓
5. 浏览器读取响应头中的 CORS 信息
   ↓
6. 浏览器检查是否允许
   ↓
7. ✅ 允许 → JavaScript 可以访问响应数据
   ❌ 不允许 → 报 CORS 错误
```

### 关键要点

> **CORS 响应头 = 后端告诉浏览器的"通行证"**  
> **浏览器检查响应头 = 验证"通行证"**  
> **允许访问 = "通行证"有效**

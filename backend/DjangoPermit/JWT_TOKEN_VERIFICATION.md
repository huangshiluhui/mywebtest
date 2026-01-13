# JWT Token 验证详细过程

## JWT Token 的结构

JWT Token 由三部分组成，用 `.` 分隔：

```
eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoxNzA0MDY3MjAwLCJpYXQiOjE3MDM5ODA4MDAsImp0aSI6Inh4eCIsInVzZXJfaWQiOjF9.signature
```

### 1. Header（头部）
```json
{
  "typ": "JWT",
  "alg": "HS256"  // 签名算法
}
```

### 2. Payload（载荷）
```json
{
  "token_type": "access",
  "exp": 1704067200,    // 过期时间（Unix 时间戳）
  "iat": 1703980800,    // 签发时间
  "jti": "xxx",         // Token ID
  "user_id": 1          // 用户 ID
}
```

### 3. Signature（签名）
```
HMACSHA256(
  base64UrlEncode(header) + "." + base64UrlEncode(payload),
  SECRET_KEY
)
```

---

## `jwt_decode_handler(token)` 验证详细过程

### 步骤 1：解析 Token 结构

```python
# 输入：token 字符串
token = "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoxNzA0MDY3MjAwLCJpYXQiOjE3MDM5ODA4MDAsImp0aSI6Inh4eCIsInVzZXJfaWQiOjF9.signature"

# 1.1 检查 Token 格式
# - 必须包含两个 `.` 分隔符
# - 必须有三部分：header.payload.signature
parts = token.split('.')
if len(parts) != 3:
    raise InvalidTokenError('Token 格式错误')
```

### 步骤 2：Base64 解码 Header

```python
# 2.1 解码 Header（第一部分）
header_encoded = parts[0]
header = base64_decode(header_encoded)

# 2.2 解析 Header JSON
header_data = json.loads(header)
# 结果：{"typ": "JWT", "alg": "HS256"}

# 2.3 检查算法
if header_data['alg'] != 'HS256':  # 根据配置检查
    raise InvalidTokenError('不支持的签名算法')
```

### 步骤 3：Base64 解码 Payload

```python
# 3.1 解码 Payload（第二部分）
payload_encoded = parts[1]
payload = base64_decode(payload_encoded)

# 3.2 解析 Payload JSON
payload_data = json.loads(payload)
# 结果：{"token_type": "access", "exp": 1704067200, "iat": 1703980800, "jti": "xxx", "user_id": 1}
```

### 步骤 4：验证签名（最重要！）

```python
# 4.1 重新计算签名
# 使用配置的 SECRET_KEY 和相同的算法
expected_signature = HMACSHA256(
    base64UrlEncode(header) + "." + base64UrlEncode(payload),
    SECRET_KEY  # 从 settings.SIMPLE_JWT['SIGNING_KEY'] 获取
)

# 4.2 比较签名
actual_signature = parts[2]  # Token 中的签名部分

if expected_signature != actual_signature:
    raise InvalidTokenError('Token 签名验证失败！')
    # 这意味着：
    # - Token 被篡改
    # - 使用了错误的密钥
    # - Token 不是由本系统签发的
```

### 步骤 5：验证过期时间（exp）

```python
# 5.1 检查 exp 字段是否存在
if 'exp' not in payload_data:
    raise InvalidTokenError('Token 缺少过期时间')

# 5.2 获取过期时间
exp_timestamp = payload_data['exp']  # Unix 时间戳

# 5.3 获取当前时间
current_timestamp = int(time.time())

# 5.4 比较时间
if current_timestamp > exp_timestamp:
    raise ExpiredSignatureError('Token 已过期')
    # 根据配置：ACCESS_TOKEN_LIFETIME = timedelta(days=1)
    # Token 在 1 天后过期
```

### 步骤 6：验证其他声明（可选）

```python
# 6.1 验证签发时间（iat）
if 'iat' in payload_data:
    iat_timestamp = payload_data['iat']
    # 可以检查签发时间是否在未来（防止时钟偏差）

# 6.2 验证受众（aud）- 如果配置了
if api_settings.AUDIENCE:
    if payload_data.get('aud') != api_settings.AUDIENCE:
        raise InvalidTokenError('Token 受众不匹配')

# 6.3 验证发行者（iss）- 如果配置了
if api_settings.ISSUER:
    if payload_data.get('iss') != api_settings.ISSUER:
        raise InvalidTokenError('Token 发行者不匹配')
```

### 步骤 7：返回 Payload

```python
# 7.1 如果所有验证都通过，返回解码后的 payload
return payload_data
# 返回：{
#   "token_type": "access",
#   "exp": 1704067200,
#   "iat": 1703980800,
#   "jti": "xxx",
#   "user_id": 1
# }
```

---

## 验证流程图

```
输入 Token
    ↓
[步骤 1] 解析 Token 结构（检查格式）
    ↓
[步骤 2] 解码 Header（检查算法）
    ↓
[步骤 3] 解码 Payload（获取数据）
    ↓
[步骤 4] 验证签名 ⚠️（最重要！）
    ├─ 重新计算签名
    ├─ 与 Token 中的签名比较
    └─ 不匹配 → InvalidTokenError
    ↓
[步骤 5] 验证过期时间
    ├─ 检查 exp 字段
    ├─ 与当前时间比较
    └─ 已过期 → ExpiredSignatureError
    ↓
[步骤 6] 验证其他声明（可选）
    ├─ 验证受众（aud）
    ├─ 验证发行者（iss）
    └─ 不匹配 → InvalidTokenError
    ↓
[步骤 7] 返回 Payload ✅
```

---

## 根据你的配置验证

### 当前配置（settings.py）

```python
SIMPLE_JWT = {
    'ALGORITHM': 'HS256',              # 使用 HS256 算法
    'SIGNING_KEY': SECRET_KEY,         # 使用 Django SECRET_KEY
    'ACCESS_TOKEN_LIFETIME': timedelta(days=1),  # Token 有效期 1 天
    'VERIFYING_KEY': None,             # HS256 不需要验证密钥
    'AUDIENCE': None,                  # 不验证受众
}
```

### 验证过程

1. **算法验证**：检查 Header 中的 `alg` 是否为 `HS256`
2. **签名验证**：使用 `SECRET_KEY` 重新计算签名并比较
3. **过期验证**：检查 `exp` 是否在当前时间之后（1 天内有效）
4. **其他验证**：不验证受众和发行者（因为配置为 None）

---

## 可能抛出的异常

### 1. `ExpiredSignatureError`
```python
# Token 已过期
raise ExpiredSignatureError('Token 已过期')
```
**触发条件**：当前时间 > `exp`（过期时间）

### 2. `InvalidTokenError`
```python
# Token 无效
raise InvalidTokenError('Token 验证失败')
```
**触发条件**：
- Token 格式错误（不是三部分）
- 签名验证失败
- 算法不匹配
- 受众/发行者不匹配

### 3. `PyJWTError`
```python
# 其他 JWT 相关错误
raise PyJWTError('Token 验证异常')
```
**触发条件**：
- Base64 解码失败
- JSON 解析失败
- 其他底层错误

---

## 实际代码执行流程

### 你的代码（middleware.py）

```python
try:
    # 1. 获取解码处理器
    jwt_decode_handler = api_settings.JWT_DECODE_HANDLER
    
    # 2. 调用验证函数（内部执行上述所有步骤）
    payload = jwt_decode_handler(token)
    # 如果成功，payload 包含：
    # {
    #   "token_type": "access",
    #   "exp": 1704067200,
    #   "iat": 1703980800,
    #   "jti": "xxx",
    #   "user_id": 1
    # }
    
    print("Token 验证成功，payload:", payload)
    
except ExpiredSignatureError:
    # Token 已过期
    return HttpResponse('Token过期，请重新登录！')
    
except InvalidTokenError:
    # Token 无效（签名错误、格式错误等）
    return HttpResponse('Token验证失败！')
    
except PyJWTError:
    # 其他 JWT 错误
    return HttpResponse('Token验证异常！')
```

---

## 安全要点

### 1. 签名验证的重要性
- **签名是 JWT 安全的核心**
- 如果签名验证失败，说明 Token 被篡改或不是本系统签发的
- 使用 `SECRET_KEY` 确保只有本系统能生成有效 Token

### 2. 过期时间验证
- 防止 Token 被长期使用
- 即使 Token 泄露，也有时间限制
- 你的配置：Token 有效期 1 天

### 3. 密钥安全
- `SECRET_KEY` 必须保密
- 如果 `SECRET_KEY` 泄露，攻击者可以伪造 Token
- 生产环境应使用强随机密钥

---

## 总结

`jwt_decode_handler(token)` 的验证过程：

1. ✅ **解析 Token 结构**（检查格式）
2. ✅ **解码 Header**（检查算法）
3. ✅ **解码 Payload**（获取数据）
4. ✅ **验证签名**（防止篡改）⚠️ 最重要
5. ✅ **验证过期时间**（防止长期使用）
6. ✅ **验证其他声明**（可选）
7. ✅ **返回 Payload**（验证成功）

如果任何一步失败，都会抛出相应的异常。

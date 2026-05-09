# AI 宠物健康助手 - API 接口文档

**文档版本**: v1.0
**更新日期**: 2026-04-09
**API 版本**: v1
**基础路径**: `/api/v1`

---

## 概述

本文档记录 AI 宠物健康助手后端 API 接口设计，包括认证接口、用户管理接口等。所有接口均遵循 RESTful 设计规范，使用 JSON 格式传输数据。

### 认证说明

除公开接口外，所有受保护接口需要在请求头中携带 JWT 令牌：

```
Authorization: Bearer <access_token>
```

### 通用响应格式

#### 成功响应
```json
{
  "code": 200,
  "message": "操作成功",
  "data": { ... }
}
```

#### 错误响应
```json
{
  "code": 400,
  "message": "错误描述",
  "detail": "详细错误信息"
}
```

### HTTP 状态码说明

| 状态码 | 说明 |
|--------|------|
| 200 | 操作成功 |
| 201 | 资源创建成功 |
| 400 | 请求参数错误 |
| 401 | 未授权/认证失败 |
| 403 | 权限不足 |
| 404 | 资源不存在 |
| 422 | 数据验证失败 |
| 500 | 服务器内部错误 |

---

## 一、用户认证接口

### 1.1 用户注册

**接口路径**: `POST /api/v1/auth/register`

**接口描述**: 用户注册接口，支持手机号或邮箱注册

**请求参数**:
```json
{
  "phone": "13800138000",        // 手机号（可选，与邮箱二选一）
  "email": "user@example.com",   // 邮箱（可选，与手机号二选一）
  "password": "password123"      // 密码（必填，至少8位，包含字母和数字）
}
```

**请求示例**:
```bash
curl -X POST "http://localhost:8000/api/v1/auth/register" \
  -H "Content-Type: application/json" \
  -d '{"phone":"13800138000","email":"user@example.com","password":"password123"}'
```

**响应参数**:
```json
{
  "user_id": "550e8400-e29b-41d4-a716-446655440000",
  "phone": "13800138000",
  "email": "user@example.com",
  "is_active": true,
  "created_at": "2026-04-09T10:30:00Z"
}
```

**响应状态码**: 201 Created

**错误响应**:
- 400: 手机号和邮箱至少填写一项
- 400: 该手机号已被注册
- 400: 该邮箱已被注册
- 422: 密码强度不符合要求

---

### 1.2 用户登录

**接口路径**: `POST /api/v1/auth/login`

**接口描述**: 用户登录接口，支持手机号或邮箱登录，返回访问令牌和刷新令牌

**请求格式**: `application/x-www-form-urlencoded`

**请求参数**:
```
username: 13800138000    // 手机号或邮箱
password: password123    // 密码
```

**请求示例**:
```bash
curl -X POST "http://localhost:8000/api/v1/auth/login" \
  -d "username=13800138000" \
  -d "password=password123"
```

**响应参数**:
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "expires_in": 1800
}
```

**响应状态码**: 200 OK

**错误响应**:
- 401: 用户名或密码错误
- 401: 用户不存在或已被禁用

---

### 1.3 刷新令牌

**接口路径**: `POST /api/v1/auth/refresh`

**接口描述**: 使用刷新令牌获取新的访问令牌

**请求参数**:
```json
{
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

**请求示例**:
```bash
curl -X POST "http://localhost:8000/api/v1/auth/refresh" \
  -H "Content-Type: application/json" \
  -d '{"refresh_token":"eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."}'
```

**响应参数**:
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "expires_in": 1800
}
```

**响应状态码**: 200 OK

**错误响应**:
- 401: 刷新令牌无效或已过期
- 401: 令牌类型错误

---

### 1.4 忘记密码

**接口路径**: `POST /api/v1/auth/forgot-password`

**接口描述**: 请求密码重置，会生成密码重置令牌（有效期6小时）

**请求参数**:
```json
{
  "phone": "13800138000"    // 手机号或邮箱
}
```

**请求示例**:
```bash
curl -X POST "http://localhost:8000/api/v1/auth/forgot-password" \
  -H "Content-Type: application/json" \
  -d '{"phone":"13800138000"}'
```

**响应参数**:
```json
{
  "message": "密码重置邮件已发送，请查收"
}
```

**响应状态码**: 200 OK

**错误响应**:
- 404: 用户不存在

**TODO**: 需要集成邮件服务发送实际的重置链接

---

### 1.5 重置密码

**接口路径**: `POST /api/v1/auth/reset-password`

**接口描述**: 使用密码重置令牌设置新密码

**请求参数**:
```json
{
  "reset_token": "abc123...",        // 密码重置令牌
  "new_password": "newpassword123"   // 新密码
}
```

**请求示例**:
```bash
curl -X POST "http://localhost:8000/api/v1/auth/reset-password" \
  -H "Content-Type: application/json" \
  -d '{"reset_token":"abc123...","new_password":"newpassword123"}'
```

**响应参数**:
```json
{
  "message": "密码重置成功，请使用新密码登录"
}
```

**响应状态码**: 200 OK

**错误响应**:
- 400: 令牌无效或已过期
- 422: 密码强度不符合要求

**TODO**: 完整实现令牌验证逻辑

---

## 二、用户管理接口

### 2.1 获取当前用户信息

**接口路径**: `GET /api/v1/users/me`

**接口描述**: 获取当前登录用户的完整信息

**认证要求**: 需要携带有效的访问令牌

**请求示例**:
```bash
curl -X GET "http://localhost:8000/api/v1/users/me" \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
```

**响应参数**:
```json
{
  "user": {
    "user_id": "550e8400-e29b-41d4-a716-446655440000",
    "phone": "13800138000",
    "email": "user@example.com",
    "is_active": true,
    "created_at": "2026-04-09T10:30:00Z",
    "last_login_at": "2026-04-09T12:00:00Z"
  },
  "profile": {
    "user_id": "550e8400-e29b-41d4-a716-446655440000",
    "nickname": "用户昵称",
    "avatar_url": "https://example.com/avatar.jpg",
    "pet_count": 2,
    "address": "北京市朝阳区",
    "bio": "我是一名宠物爱好者",
    "created_at": "2026-04-09T10:30:00Z",
    "updated_at": "2026-04-09T10:30:00Z"
  }
}
```

**响应状态码**: 200 OK

**错误响应**:
- 401: 未提供认证令牌
- 401: 令牌无效或已过期

---

### 2.2 更新当前用户信息

**接口路径**: `PUT /api/v1/users/me`

**接口描述**: 更新当前登录用户的基本信息

**认证要求**: 需要携带有效的访问令牌

**请求参数**:
```json
{
  "nickname": "新昵称",          // 昵称（可选）
  "avatar_url": "https://...",    // 头像URL（可选）
  "phone": "13800138001",        // 手机号（可选）
  "email": "new@example.com"     // 邮箱（可选）
}
```

**请求示例**:
```bash
curl -X PUT "http://localhost:8000/api/v1/users/me" \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..." \
  -H "Content-Type: application/json" \
  -d '{"nickname":"新昵称","phone":"13800138001"}'
```

**响应参数**:
```json
{
  "user_id": "550e8400-e29b-41d4-a716-446655440000",
  "phone": "13800138001",
  "email": "user@example.com",
  "is_active": true,
  "updated_at": "2026-04-09T14:00:00Z"
}
```

**响应状态码**: 200 OK

**错误响应**:
- 400: 手机号格式错误
- 400: 邮箱格式错误
- 400: 该手机号已被注册
- 400: 该邮箱已被注册
- 401: 未提供认证令牌

---

### 2.3 更新当前用户档案

**接口路径**: `PUT /api/v1/users/me/profile`

**接口描述**: 更新当前登录用户的详细档案信息

**认证要求**: 需要携带有效的访问令牌

**请求参数**:
```json
{
  "pet_count": 3,               // 宠物数量（可选）
  "address": "北京市海淀区",     // 地址（可选）
  "bio": "我是宠物爱好者"         // 个人简介（可选）
}
```

**请求示例**:
```bash
curl -X PUT "http://localhost:8000/api/v1/users/me/profile" \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..." \
  -H "Content-Type: application/json" \
  -d '{"pet_count":3,"address":"北京市海淀区"}'
```

**响应参数**:
```json
{
  "user_id": "550e8400-e29b-41d4-a716-446655440000",
  "nickname": "用户昵称",
  "avatar_url": "https://example.com/avatar.jpg",
  "pet_count": 3,
  "address": "北京市海淀区",
  "bio": "我是宠物爱好者",
  "created_at": "2026-04-09T10:30:00Z",
  "updated_at": "2026-04-09T15:00:00Z"
}
```

**响应状态码**: 200 OK

**错误响应**:
- 401: 未提供认证令牌
- 401: 令牌无效或已过期

---

## 三、宠物档案接口

### 3.1 创建宠物档案

**接口路径**: `POST /api/v1/pets`

**接口描述**: 为当前用户创建宠物档案

**认证要求**: 需要携带有效的访问令牌

**请求参数**:
```json
{
  "name": "旺财",                    // 宠物名称（必填，1-50字符）
  "species": "dog",                  // 物种（必填）: dog, cat, bird, rabbit, hamster, fish, other
  "breed": "金毛寻回犬",             // 品种（可选，最长50字符）
  "gender": "male",                  // 性别（可选）: male, female, unknown，默认unknown
  "birth_date": "2022-03-15",        // 出生日期（可选）
  "weight": 28.50,                   // 体重kg（可选，0-999.99）
  "photo_url": "https://...",        // 宠物照片URL（可选）
  "is_vaccinated": true,             // 是否已接种疫苗（可选，默认false）
  "is_neutered": false               // 是否已绝育（可选，默认false）
}
```

**响应参数**: 返回创建的宠物档案对象（状态码 201）

---

### 3.2 获取宠物列表

**接口路径**: `GET /api/v1/pets`

**接口描述**: 获取当前用户的所有宠物档案，支持分页

**认证要求**: 需要携带有效的访问令牌

**查询参数**:
- `page`: 页码（默认1）
- `page_size`: 每页数量（默认10，最大100）

**响应参数**:
```json
{
  "items": [PetResponse...],
  "total": 5,
  "page": 1,
  "page_size": 10
}
```

---

### 3.3 获取宠物详情

**接口路径**: `GET /api/v1/pets/{pet_id}`

**接口描述**: 获取指定宠物的详细信息

**认证要求**: 需要携带有效的访问令牌，且宠物必须属于当前用户

**错误响应**:
- 404: 宠物不存在
- 403: 无权访问该宠物信息

---

### 3.4 更新宠物档案

**接口路径**: `PUT /api/v1/pets/{pet_id}`

**接口描述**: 更新指定宠物的档案信息

**认证要求**: 需要携带有效的访问令牌，且宠物必须属于当前用户

**请求参数**: 与创建接口相同，所有字段均为可选（仅更新提交的字段）

**错误响应**:
- 404: 宠物不存在
- 403: 无权修改该宠物信息
- 422: 数据验证失败

---

### 3.5 删除宠物档案

**接口路径**: `DELETE /api/v1/pets/{pet_id}`

**接口描述**: 删除指定宠物的档案

**认证要求**: 需要携带有效的访问令牌，且宠物必须属于当前用户

**响应状态码**: 204 No Content

**错误响应**:
- 404: 宠物不存在
- 403: 无权删除该宠物信息

---

## 四、健康检查接口

### 3.1 服务健康检查

**接口路径**: `GET /health`

**接口描述**: 服务健康检查接口，用于监控服务状态

**认证要求**: 无需认证

**请求示例**:
```bash
curl -X GET "http://localhost:8000/health"
```

**响应参数**:
```json
{
  "status": "healthy",
  "service": "AI Pet Health Assistant"
}
```

**响应状态码**: 200 OK

---

## 附录

### A. 数据模型

#### 用户模型 (User)
| 字段 | 类型 | 说明 |
|------|------|------|
| user_id | UUID | 用户唯一标识符 |
| phone | String | 手机号（唯一，可为空）|
| email | String | 邮箱（唯一，可为空）|
| password_hash | String | 密码哈希值 |
| is_active | Boolean | 账户是否激活 |
| is_superuser | Boolean | 是否超级管理员 |
| created_at | DateTime | 创建时间 |
| updated_at | DateTime | 更新时间 |
| last_login_at | DateTime | 最后登录时间 |

#### 用户档案模型 (UserProfile)
| 字段 | 类型 | 说明 |
|------|------|------|
| profile_id | UUID | 档案ID |
| user_id | UUID | 用户ID（外键，唯一）|
| full_name | String | 真实姓名 |
| gender | String | 性别 |
| date_of_birth | Date | 出生日期 |
| avatar_url | String | 头像URL |
| pet_count | Integer | 宠物数量（自动同步） |
| address | String | 地址 |
| bio | String | 个人简介 |
| created_at | DateTime | 创建时间 |
| updated_at | DateTime | 更新时间 |

#### 宠物档案模型 (Pet)
| 字段 | 类型 | 说明 |
|------|------|------|
| pet_id | UUID | 宠物唯一标识符 |
| user_id | UUID | 所属用户ID（外键）|
| name | String | 宠物名称 |
| species | String | 物种: dog, cat, bird, rabbit, hamster, fish, other |
| breed | String | 品种 |
| gender | String | 性别: male, female, unknown |
| birth_date | Date | 出生日期 |
| weight | Decimal | 体重(kg) |
| photo_url | String | 宠物照片URL |
| is_vaccinated | Boolean | 是否已接种疫苗 |
| is_neutered | Boolean | 是否已绝育 |
| created_at | DateTime | 创建时间 |
| updated_at | DateTime | 更新时间 |

### B. 错误码定义

| 错误码 | 说明 |
|--------|------|
| AUTH_001 | 认证失败 |
| AUTH_002 | 令牌已过期 |
| AUTH_003 | 令牌无效 |
| USER_001 | 用户不存在 |
| USER_002 | 手机号已被注册 |
| USER_003 | 邮箱已被注册 |
| USER_004 | 密码验证失败 |
| VAL_001 | 数据验证失败 |
| VAL_002 | 密码强度不足 |
| PET_001 | 宠物不存在 |
| PET_002 | 无权访问该宠物 |
| PET_003 | 物种类型不合法 |
| PET_004 | 性别值不合法 |

### C. 联系方式

如有问题，请联系开发团队。

---

*文档版本记录*:
- v1.0 (2026-04-09): 初始版本，包含认证和用户管理接口
- v1.1 (2026-04-10): 新增宠物档案管理接口，新增 pet_count 同步

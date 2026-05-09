# API 接口文档汇总 - v9.0

**文档版本**: v9.0  
**更新日期**: 2026-04-18  
**API 版本**: v1  
**基础路径**: `/api/v1`  
**Swagger UI**: http://localhost:8000/docs

---

## 概述

本文档汇总 AI 宠物健康助手所有 API 接口，覆盖 9 个后端模块，共计 50+ 个端点。

### 认证说明

除公开接口外，所有受保护接口需要在请求头中携带 JWT 令牌：

```
Authorization: Bearer <access_token>
```

### 通用响应格式

**成功响应**:
```json
{
  "code": 200,
  "message": "操作成功",
  "data": { ... }
}
```

**错误响应**:
```json
{
  "code": 400,
  "message": "错误描述",
  "detail": "详细错误信息"
}
```

### HTTP 状态码

| 状态码 | 说明 |
|--------|------|
| 200 | 操作成功 |
| 201 | 资源创建成功 |
| 204 | 删除成功（无内容） |
| 400 | 请求参数错误 |
| 401 | 未授权/认证失败 |
| 403 | 权限不足 |
| 404 | 资源不存在 |
| 422 | 数据验证失败 |
| 500 | 服务器内部错误 |

---

## 接口总览

| 模块 | 端点数 | 路径前缀 | 认证 | 文档 |
|------|--------|----------|------|------|
| 用户认证 | 5 | /api/v1/auth | 部分 | [详情](#一用户认证接口) |
| 用户管理 | 3 | /api/v1/users | 是 | [详情](#二用户管理接口) |
| 宠物档案 | 5 | /api/v1/pets | 是 | [详情](#三宠物档案接口) |
| 健康咨询 | 5+ | /api/v1/health | 是 | 模块 M2 |
| 行为分析 | 3+ | /api/v1/behavior | 是 | 模块 M3 |
| 智能购物 | 9 | /api/v1/shopping | 是 | [详情](API接口文档_DEV007.md) |
| 知识管理 | 5+ | /api/v1/knowledge | 是 | 模块 M5 |
| 工具集成 | 3+ | /api/v1/tools | 是 | [详情](功能说明文档_DEV008.md) |
| **数据安全** | **10** | **/api/v1/security** | **是** | [详情](#十数据安全接口) |
| 健康检查 | 1 | /health | 否 | [详情](#十一健康检查) |
| **总计** | **50+** | - | - | - |

---

## 一、用户认证接口

### 1.1 用户注册
**POST** `/api/v1/auth/register`

注册新用户，支持手机号或邮箱。

**请求体**:
```json
{
  "phone": "13800138000",
  "email": "user@example.com",
  "password": "password123"
}
```

**响应**: 201 Created - 用户对象

### 1.2 用户登录
**POST** `/api/v1/auth/login`

用户登录，返回 JWT 令牌。

**请求格式**: `application/x-www-form-urlencoded`
- `username`: 手机号或邮箱
- `password`: 密码

**响应**:
```json
{
  "access_token": "eyJ...",
  "refresh_token": "eyJ...",
  "token_type": "bearer",
  "expires_in": 7200
}
```

### 1.3 刷新令牌
**POST** `/api/v1/auth/refresh`

使用刷新令牌获取新的访问令牌。

**请求体**: `{"refresh_token": "eyJ..."}`

### 1.4 忘记密码
**POST** `/api/v1/auth/forgot-password`

请求密码重置，生成重置令牌。

### 1.5 重置密码
**POST** `/api/v1/auth/reset-password`

使用重置令牌设置新密码。

---

## 二、用户管理接口

### 2.1 获取当前用户信息
**GET** `/api/v1/users/me`

返回用户基本信息 + 档案信息。

### 2.2 更新当前用户信息
**PUT** `/api/v1/users/me`

更新昵称、头像、手机号、邮箱。

### 2.3 更新当前用户档案
**PUT** `/api/v1/users/me/profile`

更新地址、个人简介、宠物数量等。

---

## 三、宠物档案接口

### 3.1 创建宠物档案
**POST** `/api/v1/pets`

创建新宠物档案。

### 3.2 获取宠物列表
**GET** `/api/v1/pets?page=1&page_size=10`

分页获取当前用户所有宠物。

### 3.3 获取宠物详情
**GET** `/api/v1/pets/{pet_id}`

获取指定宠物详细信息。

### 3.4 更新宠物档案
**PUT** `/api/v1/pets/{pet_id}`

更新宠物信息。

### 3.5 删除宠物档案
**DELETE** `/api/v1/pets/{pet_id}`

删除宠物档案。

---

## 四、健康咨询接口

### 4.1 症状分析
**POST** `/api/v1/health/analyze`

提交症状进行 AI 分析。

### 4.2 紧急度评估
**POST** `/api/v1/health/urgency`

评估症状紧急程度。

### 4.3 健康记录
**GET/POST/PUT/DELETE** `/api/v1/health/records`

健康记录 CRUD 操作。

---

## 五、行为分析接口

### 5.1 行为识别
**POST** `/api/v1/behavior/analyze`

提交行为描述进行 AI 分析。

### 5.2 训练建议
**GET** `/api/v1/behavior/training`

获取训练建议。

### 5.3 品种行为特征
**GET** `/api/v1/behavior/breed/{breed}`

获取品种相关行为特征。

---

## 六、智能购物接口

详见 [API接口文档_DEV007.md](API接口文档_DEV007.md)

| 方法 | 路径 | 功能 |
|------|------|------|
| GET | /api/v1/shopping/products | 搜索商品 |
| GET | /api/v1/shopping/products/{id} | 商品详情 |
| GET | /api/v1/shopping/recommend | 智能推荐 |
| GET | /api/v1/shopping/compare | 商品对比 |
| POST | /api/v1/shopping/analyze-ingredients | 成分分析 |
| POST | /api/v1/shopping/check-allergen | 过敏原检测 |
| GET | /api/v1/shopping/categories | 商品分类 |
| GET | /api/v1/shopping/behavior-tracking | 行为追踪 |
| GET | /api/v1/shopping/statistics | 购物统计 |

---

## 七、知识管理接口

### 7.1 文档管理
**GET/POST/PUT/DELETE** `/api/v1/knowledge/documents`

知识库文档 CRUD。

### 7.2 RAG 检索
**POST** `/api/v1/knowledge/search`

向量检索增强回答。

### 7.3 知识库统计
**GET** `/api/v1/knowledge/stats`

知识库统计信息。

---

## 八、工具集成接口

### 8.1 工具列表
**GET** `/api/v1/tools`

获取所有已注册工具。

### 8.2 工具执行
**POST** `/api/v1/tools/execute`

执行指定工具。

### 8.3 工具详情
**GET** `/api/v1/tools/{tool_name}`

获取工具详细信息。

---

## 九、工具集成说明

详见 [功能说明文档_DEV008.md](功能说明文档_DEV008.md)

**已注册工具清单 (15个)**:

| 工具名称 | 类型 | 功能 |
|---------|------|------|
| SymptomAnalyzer | 内部 | 症状分析 |
| UrgencyEvaluator | 内部 | 紧急度评估 |
| BehaviorAnalyzer | 内部 | 行为分析 |
| BreedAnalyzer | 内部 | 品种分析 |
| NutritionAdvisor | 内部 | 营养建议 |
| ProductSearcher | 内部 | 商品搜索 |
| RecommendationEngine | 内部 | 推荐引擎 |
| IngredientAnalyzer | 内部 | 成分分析 |
| KnowledgeRetriever | 内部 | 知识检索 |
| ContextManager | 内部 | 上下文管理 |
| **WeatherTool** | 外部 | 天气查询 + 宠物建议 |
| **MapServiceTool** | 外部 | 附近场所搜索 |
| **WebSearchTool** | 外部 | 网络信息搜索 |
| **ImageRecognitionTool** | 外部 | AI 图像识别 |
| **KnowledgeEnhanceTool** | 外部 | 多源知识增强 |

---

## 十、数据安全接口

### 10.1 加密数据
**POST** `/api/v1/security/encrypt`

使用 AES-256-GCM 加密数据。

**请求体**:
```json
{
  "plaintext": "需要加密的文本",
  "associated_data": "可选关联数据"
}
```

**响应**:
```json
{
  "encrypted_text": "base64编码的密文",
  "algorithm": "AES-256-GCM"
}
```

### 10.2 解密数据
**POST** `/api/v1/security/decrypt`

解密 AES-256-GCM 密文。

**请求体**:
```json
{
  "encrypted_text": "base64编码的密文",
  "associated_data": "可选关联数据"
}
```

### 10.3 数据脱敏
**POST** `/api/v1/security/mask`

预览数据脱敏效果。

**请求体**:
```json
{
  "data": "13800138000",
  "strategy": "phone"
}
```

**支持策略**: phone, email, id_card, name, address, bank_card, password, ip_address, custom

### 10.4 列出角色
**GET** `/api/v1/security/roles`

返回所有 RBAC 角色及其权限。

### 10.5 列出权限
**GET** `/api/v1/security/permissions`

返回所有权限类别及描述。

### 10.6 角色权限
**GET** `/api/v1/security/role/{name}/permissions`

获取指定角色的权限列表。

### 10.7 查询审计日志
**GET** `/api/v1/security/audit/logs`

查询操作审计日志，支持过滤。

**查询参数**:
- `user_id`: 用户ID
- `action_type`: 操作类型
- `severity`: 严重级别
- `start_date` / `end_date`: 日期范围
- `limit`: 返回数量

### 10.8 安全事件
**GET** `/api/v1/security/audit/security-events`

获取安全相关事件。

### 10.9 用户活动
**GET** `/api/v1/security/audit/user-activity/{user_id}`

获取指定用户的活动记录。

### 10.10 安全概览
**GET** `/api/v1/security/overview`

获取系统安全状态概览。

**响应**:
```json
{
  "total_users": 100,
  "active_roles": 5,
  "total_permissions": 14,
  "encryption_enabled": true,
  "masking_enabled": true,
  "audit_logs_count": 5000,
  "security_events_24h": 3
}
```

### 角色层级

```
SUPER_ADMIN (14权限) 
  → ADMIN (16权限，含SUPER_ADMIN权限)
    → VETERINARIAN (8权限)
      → USER (6权限)
        → GUEST (3权限)
```

---

## 十一、健康检查

### 11.1 服务健康检查
**GET** `/health`

无需认证，用于监控服务状态。

**响应**:
```json
{
  "status": "healthy",
  "service": "AI Pet Health Assistant"
}
```

---

## 附录

### A. 错误码定义

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
| SEC_001 | 加密失败 |
| SEC_002 | 解密失败（可能数据被篡改） |
| SEC_003 | 权限不足 |
| SEC_004 | 角色不存在 |

### B. RBAC 权限清单

| 类别 | 权限代码 | 说明 |
|------|---------|------|
| 用户 | user:read | 查看用户 |
| 用户 | user:write | 编辑用户 |
| 用户 | user:delete | 删除用户 |
| 宠物 | pet:read | 查看宠物 |
| 宠物 | pet:write | 编辑宠物 |
| 宠物 | pet:delete | 删除宠物 |
| 健康 | health:read | 查看健康信息 |
| 健康 | health:write | 编辑健康信息 |
| 购物 | shop:read | 查看购物 |
| 购物 | shop:write | 编辑购物 |
| 知识 | knowledge:read | 查看知识 |
| 知识 | knowledge:write | 编辑知识 |
| 管理 | admin:panel | 管理面板 |
| 审计 | audit:read | 查看审计日志 |
| 安全 | security:config | 安全配置 |
| 数据 | data:export | 数据导出 |
| 数据 | data:encryption | 数据加密 |

### C. 脱敏策略示例

| 策略 | 输入 | 输出 |
|------|------|------|
| phone | 13800138000 | 138****8000 |
| email | user@example.com | u***@example.com |
| id_card | 110101199001011234 | 110***********1234 |
| name | 张三丰 | 张*丰 |
| address | 北京市朝阳区某某路123号 | 北京市朝阳区**** |
| bank_card | 6222021234567890123 | **** **** **** 0123 |
| password | MySecret123! | ****** |
| ip_address | 192.168.1.100 | 192.168.*.* |
| custom | ABCDEFGHIJ | ABC*****IJ |

---

*文档版本记录*:
- v1.0 (2026-04-09): 初始版本，认证和用户管理接口
- v1.1 (2026-04-10): 新增宠物档案管理接口
- v9.0 (2026-04-18): 全面汇总，新增数据安全模块10个端点，覆盖全部50+端点

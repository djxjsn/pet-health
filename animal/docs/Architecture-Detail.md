# AI 宠物健康助手 - 精细化架构设计文档

**版本**: v1.0  
**日期**: 2026-04-06  
**状态**: 草案

---

## 1. 完整技术栈定义

### 1.1 前端技术栈

| 层级 | 技术选型 | 版本 | 选型理由 |
|------|----------|------|----------|
| **框架** | Next.js 14 (App Router) | 14.x | SSR/SSG 支持、API Routes、图片优化 |
| **语言** | TypeScript | 5.x | 类型安全、更好的 IDE 支持 |
| **样式** | Tailwind CSS | 3.x | 原子化 CSS、设计系统一致性 |
| **组件库** | shadcn/ui + Radix UI | latest | 无样式侵入、可定制性高 |
| **状态管理** | Zustand | 4.x | 轻量、TypeScript 友好 |
| **数据获取** | TanStack Query (React Query) | 5.x | 缓存、重试、乐观更新 |
| **表单处理** | React Hook Form + Zod | latest | 性能优秀、校验 schema |
| **动画** | Framer Motion | latest | React 友好、手势支持 |
| **图标** | Lucide React | latest | 与 UI 设计文档一致 |

### 1.2 后端技术栈补充

| 层级 | 技术选型 | 版本 | 用途 |
|------|----------|------|------|
| **框架** | FastAPI | 0.100+ | 高性能异步框架 |
| **数据库 ORM** | SQLAlchemy 2.0 | 2.x | 异步 ORM 支持 |
| **迁移工具** | Alembic | latest | 数据库版本管理 |
| **缓存** | Redis | 7.x | 会话、热点数据、限流 |
| **消息队列** | Celery + Redis | latest | 异步任务、图像处理 |
| **对象存储** | MinIO / 阿里云 OSS | - | 图片文件存储 |
| **搜索** | Elasticsearch (可选) | 8.x | 商品/知识库全文搜索 |
| **监控** | Prometheus + Grafana | - | 指标监控 |
| **日志** | ELK Stack / Loki | - | 日志聚合分析 |
| **APM** | Jaeger / Zipkin | - | 分布式链路追踪 |

---

## 2. 项目目录结构

### 2.1 后端目录结构 (FastAPI)

```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py                 # FastAPI 应用入口
│   ├── config.py               # 配置管理 (Pydantic Settings)
│   ├── dependencies.py         # 依赖注入
│   ├── api/
│   │   ├── __init__.py
│   │   ├── deps.py             # API 依赖 (DB 会话、当前用户)
│   │   ├── v1/
│   │   │   ├── __init__.py
│   │   │   ├── router.py       # API v1 路由聚合
│   │   │   ├── endpoints/
│   │   │   │   ├── auth.py     # 认证接口
│   │   │   │   ├── users.py    # 用户管理
│   │   │   │   ├── pets.py     # 宠物档案
│   │   │   │   ├── chat.py     # 对话接口
│   │   │   │   ├── health.py   # 健康咨询
│   │   │   │   ├── shop.py     # 商品推荐
│   │   │   │   └── upload.py   # 文件上传
│   │   │   └── websockets/
│   │   │       └── chat_ws.py  # WebSocket 流式对话
│   ├── core/
│   │   ├── __init__.py
│   │   ├── security.py         # JWT、密码哈希
│   │   ├── exceptions.py       # 自定义异常
│   │   ├── middleware.py       # 全局中间件
│   │   └── events.py           # 生命周期事件
│   ├── models/
│   │   ├── __init__.py
│   │   ├── base.py             # SQLAlchemy Base
│   │   ├── user.py             # 用户模型
│   │   ├── pet.py              # 宠物模型
│   │   ├── conversation.py     # 对话模型
│   │   └── health_record.py    # 健康记录模型
│   ├── schemas/
│   │   ├── __init__.py
│   │   ├── base.py             # Pydantic 基础 Schema
│   │   ├── user.py             # 用户相关 Schema
│   │   ├── pet.py              # 宠物相关 Schema
│   │   ├── chat.py             # 对话消息 Schema
│   │   └── shop.py             # 商品相关 Schema
│   ├── services/
│   │   ├── __init__.py
│   │   ├── user_service.py     # 用户业务逻辑
│   │   ├── pet_service.py      # 宠物业务逻辑
│   │   ├── chat_service.py     # 对话业务逻辑
│   │   ├── rag_service.py      # RAG 检索服务
│   │   ├── llm_service.py      # LLM 调用封装
│   │   └── image_service.py    # 图像处理服务
│   ├── agent/
│   │   ├── __init__.py
│   │   ├── core.py               # LangChain Agent 核心
│   │   ├── tools/
│   │   │   ├── __init__.py
│   │   │   ├── health_tools.py   # 健康咨询工具
│   │   │   ├── shop_tools.py     # 购物工具
│   │   │   └── image_tools.py    # 图像识别工具
│   │   ├── middleware/
│   │   │   ├── __init__.py
│   │   │   ├── context_injector.py # 上下文注入中间件
│   │   │   ├── safety_filter.py    # 安全过滤中间件
│   │   │   └── logging_middleware.py
│   │   ├── memory/
│   │   │   ├── __init__.py
│   │   │   ├── short_term.py     # 短期记忆实现
│   │   │   └── long_term.py      # 长期记忆实现
│   │   └── prompts/
│   │       ├── __init__.py
│   │       ├── system_prompts.py   # 系统提示词
│   │       └── templates.py        # Prompt 模板
│   ├── db/
│   │   ├── __init__.py
│   │   ├── session.py            # 数据库会话管理
│   │   └── migrations/           # Alembic 迁移文件
│   ├── tasks/
│   │   ├── __init__.py
│   │   ├── celery_app.py         # Celery 配置
│   │   ├── image_tasks.py        # 图像处理任务
│   │   └── memory_tasks.py       # 记忆更新任务
│   └── utils/
│       ├── __init__.py
│       ├── datetime_utils.py
│       ├── validators.py
│       └── logger.py
├── tests/
│   ├── __init__.py
│   ├── conftest.py               # pytest 配置
│   ├── unit/
│   │   ├── test_services/
│   │   └── test_agent/
│   ├── integration/
│   │   ├── test_api/
│   │   └── test_db/
│   └── e2e/
│       └── test_chat_flow.py
├── alembic.ini
├── celeryconfig.py
├── requirements/
│   ├── base.txt
│   ├── dev.txt
│   └── prod.txt
├── requirements.txt
├── Dockerfile
├── docker-compose.yml
├── .env.example
└── .env
```

### 2.2 前端目录结构 (Next.js)

```
frontend/
├── app/                          # App Router (Next.js 14)
│   ├── layout.tsx                # 根布局
│   ├── page.tsx                  # 首页 (重定向到 /chat)
│   ├── globals.css               # 全局样式
│   ├── (auth)/                   # 认证路由组
│   │   ├── layout.tsx
│   │   ├── login/
│   │   │   └── page.tsx
│   │   └── register/
│   │       └── page.tsx
│   ├── (main)/                   # 主应用路由组
│   │   ├── layout.tsx            # 带导航的主布局
│   │   ├── chat/
│   │   │   ├── page.tsx
│   │   │   └── loading.tsx       # 加载状态
│   │   ├── pets/
│   │   │   ├── page.tsx          # 宠物列表
│   │   │   ├── [id]/
│   │   │   │   └── page.tsx      # 宠物详情
│   │   │   └── new/
│   │   │       └── page.tsx      # 添加宠物
│   │   ├── history/
│   │   │   └── page.tsx
│   │   ├── shop/
│   │   │   └── page.tsx
│   │   └── profile/
│   │       ├── page.tsx
│   │       └── settings/
│   │           └── page.tsx
│   └── api/                      # Next.js API Routes (可选代理)
├── components/
│   ├── ui/                       # shadcn/ui 组件
│   │   ├── button.tsx
│   │   ├── input.tsx
│   │   ├── card.tsx
│   │   ├── dialog.tsx
│   │   ├── dropdown-menu.tsx
│   │   ├── avatar.tsx
│   │   ├── badge.tsx
│   │   ├── skeleton.tsx
│   │   └── toast.tsx
│   ├── common/                   # 通用业务组件
│   │   ├── Header.tsx
│   │   ├── BottomNav.tsx
│   │   ├── Sidebar.tsx
│   │   ├── PetSwitcher.tsx
│   │   └── ImageUploader.tsx
│   ├── chat/                     # 对话相关组件
│   │   ├── ChatContainer.tsx
│   │   ├── MessageBubble.tsx
│   │   ├── MessageInput.tsx
│   │   ├── TypingIndicator.tsx
│   │   ├── KnowledgeSource.tsx
│   │   ├── ProductCard.tsx
│   │   └── ImageMessage.tsx
│   ├── pet/                      # 宠物相关组件
│   │   ├── PetCard.tsx
│   │   ├── PetForm.tsx
│   │   ├── PetAvatar.tsx
│   │   ├── HealthRecord.tsx
│   │   └── AllergyTag.tsx
│   └── shop/                     # 商城相关组件
│       ├── ProductCard.tsx
│       ├── FilterBar.tsx
│       ├── ComparisonTable.tsx
│       └── IngredientAnalysis.tsx
├── hooks/                        # 自定义 React Hooks
│   ├── useAuth.ts
│   ├── useChat.ts
│   ├── usePets.ts
│   ├── useStreaming.ts
│   └── useToast.ts
├── lib/                          # 工具库
│   ├── api.ts                    # API 客户端 (axios/fetch)
│   ├── websocket.ts              # WebSocket 封装
│   ├── utils.ts                  # 工具函数
│   ├── constants.ts              # 常量定义
│   └── validators.ts             # 表单校验
├── stores/                       # Zustand 状态管理
│   ├── authStore.ts
│   ├── chatStore.ts
│   ├── petStore.ts
│   └── uiStore.ts
├── types/                        # TypeScript 类型定义
│   ├── api.ts
│   ├── models.ts
│   └── chat.ts
├── public/
│   ├── images/
│   └── icons/
├── styles/
│   └── theme.ts                  # Tailwind 主题扩展
├── middleware.ts                 # Next.js 中间件 (路由保护)
├── next.config.js
├── tailwind.config.ts
├── tsconfig.json
├── package.json
└── .env.local
```

---

## 3. 详细 API 接口规范

### 3.1 认证接口

#### POST /api/v1/auth/register
用户注册

```yaml
Request:
  body:
    phone: string      # 手机号，必填
    password: string   # 密码，6-20位，必填
    code: string       # 短信验证码，必填

Response (201):
  data:
    user_id: string
    phone: string
    access_token: string    # JWT Token
    refresh_token: string
    expires_in: int         # 秒
```

#### POST /api/v1/auth/login
用户登录

```yaml
Request:
  body:
    phone: string
    password: string

Response (200):
  data:
    user_id: string
    phone: string
    access_token: string
    refresh_token: string
    expires_in: int
```

#### POST /api/v1/auth/refresh
刷新 Token

```yaml
Request:
  body:
    refresh_token: string

Response (200):
  data:
    access_token: string
    expires_in: int
```

#### POST /api/v1/auth/logout
退出登录

```yaml
Headers:
  Authorization: Bearer {access_token}

Response (200):
  message: "Logged out successfully"
```

### 3.2 宠物档案接口

#### GET /api/v1/pets
获取宠物列表

```yaml
Headers:
  Authorization: Bearer {token}

Response (200):
  data:
    items:
      - pet_id: string
        name: string
        species: "cat" | "dog" | "other"
        breed: string
        avatar_url: string
        age: int           # 计算得出
        weight: float
        is_active: bool    # 当前对话宠物
        created_at: string
    total: int
```

#### POST /api/v1/pets
创建宠物档案

```yaml
Request:
  body:
    name: string
    species: "cat" | "dog" | "other"
    breed: string
    birth_date: string?   # ISO 8601
    gender: "male" | "female" | "unknown"
    weight: float?
    avatar: file?         # multipart/form-data

Response (201):
  data:
    pet_id: string
    name: string
    # ... 完整宠物信息
```

#### GET /api/v1/pets/{pet_id}
获取宠物详情

```yaml
Response (200):
  data:
    pet_id: string
    name: string
    species: string
    breed: string
    birth_date: string?
    gender: string
    weight: float?
    allergies: string[]
    medical_history:
      - record_id: string
        condition: string
        date: string
        notes: string
    current_medications:
      - name: string
        dosage: string
        frequency: string
    last_checkup: string?
    avatar_url: string
    created_at: string
```

#### PUT /api/v1/pets/{pet_id}
更新宠物档案

```yaml
Request:
  body:  # 支持部分更新
    name?: string
    weight?: float
    allergies?: string[]
    # ...

Response (200):
  data: # 更新后的完整信息
```

#### DELETE /api/v1/pets/{pet_id}
删除宠物档案

```yaml
Response (204):
  # No content
```

### 3.3 对话接口

#### GET /api/v1/conversations
获取对话列表

```yaml
Query:
  page: int?      # 默认 1
  size: int?      # 默认 20, 最大 100
  pet_id: string? # 筛选特定宠物

Response (200):
  data:
    items:
      - conversation_id: string
        pet_id: string
        pet_name: string
        title: string      # 自动生成或用户设置
        message_count: int
        last_message_at: string
        created_at: string
    total: int
    page: int
    size: int
```

#### POST /api/v1/conversations
创建新对话

```yaml
Request:
  body:
    pet_id: string
    title: string?    # 可选，否则自动生成

Response (201):
  data:
    conversation_id: string
    title: string
    created_at: string
```

#### GET /api/v1/conversations/{conversation_id}/messages
获取对话消息

```yaml
Query:
  before: string?   # 消息 ID，用于分页加载历史
  limit: int?       # 默认 50

Response (200):
  data:
    messages:
      - message_id: string
        role: "user" | "assistant"
        content: string
        attachments:
          - type: "image"
            url: string
            name: string
        sources:          # 助手消息特有
          - title: string
            url: string
        created_at: string
    has_more: bool
```

#### POST /api/v1/conversations/{conversation_id}/messages (非流式)
发送消息 (非流式，返回完整响应)

```yaml
Request:
  body:
    content: string
    image_urls: string[]?   # 已上传的图片 URL

Response (200):
  data:
    message_id: string
    role: "assistant"
    content: string
    sources:
      - title: string
        url: string
    related_products:
      - product_id: string
        name: string
        price: float
        image_url: string
    created_at: string
```

#### WebSocket /ws/v1/conversations/{conversation_id}
流式对话 (WebSocket)

```yaml
Connection:
  headers:
    Authorization: Bearer {token}

Client -> Server:
  {
    "type": "message",
    "content": "我家猫最近软便",
    "image_urls": []
  }

Server -> Client (流式):
  {
    "type": "token",
    "data": "根据"   // 逐字返回
  }
  {
    "type": "token",
    "data": "豆豆"
  }
  // ...
  {
    "type": "sources",
    "data": [
      {"title": "猫类消化系统疾病", "url": "..."}
    ]
  }
  {
    "type": "complete",
    "data": {
      "message_id": "msg_xxx",
      "content": "完整内容"
    }
  }

Server -> Client (错误):
  {
    "type": "error",
    "code": "RATE_LIMIT",
    "message": "请求过于频繁"
  }
```

### 3.4 文件上传接口

#### POST /api/v1/upload/image
上传图片

```yaml
Request (multipart/form-data):
  file: File           # 支持 jpg, png, webp
  type: "avatar" | "pet_photo" | "medical_image"

Response (200):
  data:
    url: string        # 可访问的图片 URL
    thumbnail_url: string
    filename: string
    size: int
    width: int
    height: int
```

### 3.5 商品推荐接口

#### GET /api/v1/shop/recommendations
获取个性化推荐

```yaml
Query:
  pet_id: string        # 基于该宠物档案推荐
  category: "food" | "toy" | "medicine" | "all"?
  limit: int?           # 默认 10

Response (200):
  data:
    items:
      - product_id: string
        name: string
        category: string
        brand: string
        price: float
        original_price: float?
        image_url: string
        rating: float
        review_count: int
        suitability_score: float   # 0-10
        tags:
          - "适合肠胃敏感"
          - "低敏配方"
        reason: string            # 推荐理由
        ingredients:
          - name: string
            is_allergen: bool
            is_beneficial: bool
    filters:
      categories: [...]
      tags: [...]
```

#### POST /api/v1/shop/compare
商品对比

```yaml
Request:
  body:
    product_ids: string[]   # 2-4 个商品
    pet_id: string

Response (200):
  data:
    products: [...]          # 完整商品信息
    comparison:
      dimensions:
        - name: "蛋白质含量"
          values: ["26%", "32%", "28%"]
          winner_index: 1
        - name: "价格"
          values: ["¥128", "¥245", "¥189"]
          winner_index: 0
    recommendation: string   # AI 生成的对比建议
```

---

## 4. 认证授权设计

### 4.1 JWT Token 设计

```python
# Access Token Payload
{
  "sub": "user_id",           # 主题 (用户ID)
  "phone": "138****8888",     # 手机号 (脱敏)
  "exp": 1704067200,          # 过期时间 (2小时)
  "iat": 1704060000,          # 签发时间
  "jti": "unique_token_id",   # Token 唯一标识 (用于黑名单)
  "type": "access"
}

# Refresh Token Payload
{
  "sub": "user_id",
  "exp": 1706659200,          # 过期时间 (30天)
  "iat": 1704060000,
  "jti": "unique_token_id",
  "type": "refresh"
}
```

### 4.2 认证流程

```
┌─────────┐     ┌──────────┐     ┌─────────┐     ┌─────────┐
│  用户   │────►│  登录    │────►│ 验证密码 │────►│ 生成    │
└─────────┘     └──────────┘     └─────────┘     │ Token   │
                                                  └────┬────┘
                                                       │
  ┌────────────────────────────────────────────────────┘
  │
  ▼
┌─────────┐     ┌──────────┐     ┌─────────┐
│ 客户端  │◄────│ 存储Token│     │  访问   │
│ 存储    │     │ (Secure) │     │  API    │
└────┬────┘     └──────────┘     └────┬────┘
     │                                  │
     │  ┌───────────────────────────────┘
     │  │
     │  ▼
     │ ┌─────────┐     ┌──────────┐     ┌─────────┐
     └►│ 请求API │────►│ 验证Token│────►│ 返回数据│
       │ (Header)│     │ (中间件) │     │         │
       └─────────┘     └──────────┘     └─────────┘
```

### 4.3 Token 刷新策略

```python
# 后端实现 (伪代码)
async def refresh_access_token(refresh_token: str):
    payload = verify_token(refresh_token)
    
    # 检查 refresh_token 是否在黑名单
    if await redis.exists(f"blacklist:{payload['jti']}"):
        raise TokenRevokedError()
    
    # 生成新的 token 对
    new_access_token = create_access_token(payload['sub'])
    new_refresh_token = create_refresh_token(payload['sub'])
    
    # 将旧 refresh_token 加入黑名单 (7天过期)
    await redis.setex(
        f"blacklist:{payload['jti']}", 
        7 * 24 * 3600, 
        "1"
    )
    
    return new_access_token, new_refresh_token
```

### 4.4 权限控制 (RBAC)

```python
# 角色定义
class UserRole:
    USER = "user"           # 普通用户
    VIP = "vip"             # VIP 用户 (更多额度)
    ADMIN = "admin"         # 管理员

# 权限装饰器
@router.get("/admin/users")
@require_role(UserRole.ADMIN)
async def list_all_users(...):
    pass

# 资源级权限检查 (只能访问自己的宠物)
@router.get("/pets/{pet_id}")
async def get_pet(
    pet_id: str,
    current_user: User = Depends(get_current_user)
):
    pet = await pet_service.get(pet_id)
    if pet.user_id != current_user.user_id:
        raise ForbiddenError("无权访问该宠物")
    return pet
```

---

## 5. 数据存储设计

### 5.1 MySQL 表结构补充

#### health_records 表 (健康记录)
```sql
CREATE TABLE health_records (
    record_id VARCHAR(36) PRIMARY KEY,
    pet_id VARCHAR(36) NOT NULL,
    record_type ENUM('disease', 'vaccine', 'checkup', 'surgery', 'other') NOT NULL,
    title VARCHAR(100) NOT NULL,
    description TEXT,
    diagnosis VARCHAR(255),
    treatment TEXT,
    veterinarian VARCHAR(100),
    clinic_name VARCHAR(100),
    cost DECIMAL(10,2),
    record_date DATE NOT NULL,
    attachments JSON,            -- [{"url": "...", "name": "..."}]
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (pet_id) REFERENCES pets(pet_id) ON DELETE CASCADE,
    INDEX idx_pet_id (pet_id),
    INDEX idx_record_date (record_date)
);
```

#### conversations 表 (补充字段)
```sql
ALTER TABLE conversations ADD COLUMN (
    title VARCHAR(200) GENERATED ALWAYS AS (
        JSON_UNQUOTE(JSON_EXTRACT(messages, '$[0].content'))
    ) STORED,
    message_count INT DEFAULT 0,
    last_message_at TIMESTAMP NULL,
    status ENUM('active', 'archived', 'deleted') DEFAULT 'active',
    INDEX idx_user_pet (user_id, pet_id),
    INDEX idx_last_message (last_message_at DESC)
);
```

#### messages 表 (独立存储消息)
```sql
CREATE TABLE messages (
    message_id VARCHAR(36) PRIMARY KEY,
    conversation_id VARCHAR(36) NOT NULL,
    role ENUM('user', 'assistant', 'system') NOT NULL,
    content TEXT NOT NULL,
    attachments JSON,            -- 图片、文件等
    token_count INT,           # LLM token 数 (用于计费)
    latency_ms INT,             # 响应延迟 (毫秒)
    model_version VARCHAR(50),  -- 使用的模型版本
    sources JSON,               -- RAG 来源
    feedback_score INT,         -- 用户反馈 (1-5, null=未评价)
    feedback_text VARCHAR(500),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (conversation_id) REFERENCES conversations(conversation_id) ON DELETE CASCADE,
    INDEX idx_conversation (conversation_id, created_at DESC)
);
```

#### user_settings 表 (用户设置)
```sql
CREATE TABLE user_settings (
    user_id VARCHAR(36) PRIMARY KEY,
    notification_enabled BOOLEAN DEFAULT TRUE,
    email_notifications BOOLEAN DEFAULT TRUE,
    sms_notifications BOOLEAN DEFAULT FALSE,
    theme_preference ENUM('light', 'dark', 'system') DEFAULT 'system',
    language VARCHAR(10) DEFAULT 'zh-CN',
    default_pet_id VARCHAR(36),
    subscription_tier ENUM('free', 'basic', 'pro') DEFAULT 'free',
    subscription_expires_at TIMESTAMP NULL,
    daily_quota_used INT DEFAULT 0,
    daily_quota_reset_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE,
    FOREIGN KEY (default_pet_id) REFERENCES pets(pet_id)
);
```

### 5.2 Redis 缓存策略

```
缓存 Key 设计:

# 会话缓存 (JWT 黑名单)
blacklist:{jti} -> "1"  (过期: token 剩余有效期)

# 用户会话
session:{user_id} -> {
    "access_jti": "...",
    "refresh_jti": "...",
    "device_info": "..."
} (过期: 7天)

# 宠物档案缓存
pet:{pet_id} -> PetProfile JSON (过期: 1小时)

# 用户宠物列表
user_pets:{user_id} -> [pet_id, ...] (过期: 30分钟)

# 限流计数
rate_limit:{user_id}:{endpoint} -> count (过期: 1分钟)

# API 响应缓存
api_cache:{hash} -> response JSON (过期: 5分钟)

# 对话历史 (短期记忆)
chat_history:{conversation_id} -> [messages] (过期: 24小时)
```

### 5.3 对象存储 (MinIO/OSS) 结构

```
bucket: pet-health-assistant
├── avatars/
│   ├── users/
│   │   └── {user_id}.jpg
│   └── pets/
│       └── {pet_id}.jpg
├── uploads/
│   └── {user_id}/
│       └── {uuid}.jpg
├── thumbnails/
│   └── {uuid}_thumb.jpg
└── exports/
    └── health_reports/
        └── {pet_id}_{date}.pdf
```

---

## 6. 异步任务与消息队列

### 6.1 Celery 任务定义

```python
# tasks/image_tasks.py
from celery import shared_task
from app.services import image_service, pet_service

@shared_task(bind=True, max_retries=3)
def process_image_upload(self, file_path: str, pet_id: str = None):
    """处理图片上传后的异步任务"""
    try:
        # 1. 生成缩略图
        thumbnail_path = image_service.generate_thumbnail(file_path)
        
        # 2. 如果是宠物照片，进行品种识别
        if pet_id:
            pet = pet_service.get(pet_id)
            if not pet.breed:
                breed_result = image_service.recognize_breed(file_path)
                if breed_result.confidence > 0.8:
                    pet_service.update_breed(pet_id, breed_result.breed)
        
        # 3. 上传到对象存储
        url = image_service.upload_to_oss(file_path)
        thumbnail_url = image_service.upload_to_oss(thumbnail_path)
        
        return {
            "url": url,
            "thumbnail_url": thumbnail_url,
            "status": "success"
        }
    except Exception as exc:
        raise self.retry(exc=exc, countdown=60)

@shared_task
def cleanup_temp_files(file_paths: list):
    """清理临时文件"""
    for path in file_paths:
        image_service.delete_local_file(path)

# tasks/memory_tasks.py
@shared_task
def update_long_term_memory(conversation_id: str):
    """异步更新长期记忆"""
    from app.agent.memory import long_term
    
    conversation = conversation_service.get(conversation_id)
    summary = llm_service.summarize_conversation(conversation.messages)
    
    long_term.store(
        pet_id=conversation.pet_id,
        conversation_id=conversation_id,
        summary=summary,
        key_facts=summary.extracted_facts
    )

@shared_task
def generate_health_report(pet_id: str):
    """生成宠物健康报告 PDF"""
    from app.services import report_service
    
    report = report_service.generate_pdf(pet_id)
    # 上传到对象存储
    url = report_service.upload_report(report)
    
    # 发送通知给用户
    notification_service.send(
        user_id=report.user_id,
        title="健康报告已生成",
        body=f"{report.pet_name}的月度健康报告已准备好"
    )
```

### 6.2 任务队列配置

```python
# celeryconfig.py
broker_url = "redis://localhost:6379/1"
result_backend = "redis://localhost:6379/2"

task_serializer = "json"
result_serializer = "json"
accept_content = ["json"]

timezone = "Asia/Shanghai"
enable_utc = True

task_routes = {
    "tasks.image_tasks.*": {"queue": "image"},
    "tasks.memory_tasks.*": {"queue": "memory"},
    "tasks.report_tasks.*": {"queue": "report"},
}

task_default_queue = "default"

# 任务执行时间限制
task_time_limit = 300  # 5分钟
task_soft_time_limit = 240  # 4分钟警告

# 重试策略
task_default_retry_delay = 60
task_max_retries = 3
```

---

## 7. 监控与可观测性

### 7.1 日志规范

```python
# app/utils/logger.py
import structlog
import logging
from pythonjsonlogger import jsonlogger

# 结构化日志配置
structlog.configure(
    processors=[
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.UnicodeDecoder(),
        structlog.processors.JSONRenderer()
    ],
    context_class=dict,
    logger_factory=structlog.stdlib.LoggerFactory(),
    wrapper_class=structlog.stdlib.BoundLogger,
    cache_logger_on_first_use=True,
)

# 日志字段规范
{
    "timestamp": "2026-04-06T12:00:00Z",
    "level": "info",
    "logger": "app.api.v1.chat",
    "event": "chat_message_sent",
    "user_id": "uuid",
    "pet_id": "uuid",
    "conversation_id": "uuid",
    "message_length": 100,
    "response_time_ms": 1500,
    "model": "gpt-4o",
    "request_id": "req_uuid"
}
```

### 7.2 指标监控 (Prometheus)

```python
# app/core/metrics.py
from prometheus_client import Counter, Histogram, Gauge, Info

# 业务指标
chat_messages_total = Counter(
    "chat_messages_total",
    "Total chat messages",
    ["role", "model"]
)

chat_latency_seconds = Histogram(
    "chat_latency_seconds",
    "Chat response latency",
    buckets=[0.5, 1.0, 2.0, 5.0, 10.0, 30.0]
)

llm_tokens_total = Counter(
    "llm_tokens_total",
    "Total LLM tokens consumed",
    ["model", "token_type"]  # prompt/completion
)

active_conversations = Gauge(
    "active_conversations",
    "Number of active conversations"
)

# 系统指标
from prometheus_fastapi_instrumentator import Instrumentator

instrumentator = Instrumentator()
instrumentator.instrument(app).expose(app)
```

### 7.3 链路追踪 (OpenTelemetry + Jaeger)

```python
# app/core/tracing.py
from opentelemetry import trace
from opentelemetry.exporter.jaeger.thrift import JaegerExporter
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.instrumentation.redis import RedisInstrumentor
from opentelemetry.instrumentation.sqlalchemy import SQLAlchemyInstrumentor

# 配置 Tracer
trace.set_tracer_provider(TracerProvider())
tracer = trace.get_tracer(__name__)

# Jaeger 导出器
jaeger_exporter = JaegerExporter(
    agent_host_name="localhost",
    agent_port=6831,
)

span_processor = BatchSpanProcessor(jaeger_exporter)
trace.get_tracer_provider().add_span_processor(span_processor)

# 自动埋点
FastAPIInstrumentor.instrument_app(app)
RedisInstrumentor().instrument()
SQLAlchemyInstrumentor().instrument()

# 自定义追踪示例
@tracer.start_as_current_span("process_chat_message")
async def process_message(message: str, pet_id: str):
    with tracer.start_as_current_span("retrieve_context") as span:
        span.set_attribute("pet_id", pet_id)
        context = await retrieve_pet_context(pet_id)
    
    with tracer.start_as_current_span("llm_generation") as span:
        span.set_attribute("model", "gpt-4o")
        response = await llm.generate(message, context)
    
    return response
```

### 7.4 健康检查端点

```python
# app/api/v1/endpoints/health.py
@router.get("/health")
async def health_check():
    """基础健康检查"""
    return {"status": "healthy"}

@router.get("/health/ready")
async def readiness_check():
    """就绪检查 (K8s)"""
    checks = {
        "database": await check_database(),
        "redis": await check_redis(),
        "minio": await check_minio()
    }
    
    all_ready = all(checks.values())
    status = 200 if all_ready else 503
    
    return JSONResponse(
        content={"status": "ready" if all_ready else "not_ready", "checks": checks},
        status_code=status
    )

@router.get("/health/live")
async def liveness_check():
    """存活检查 (K8s)"""
    return {"status": "alive"}
```

---

## 8. 部署架构

### 8.1 容器化配置

```dockerfile
# Dockerfile (Backend)
FROM python:3.12-slim as builder

WORKDIR /app

# 安装依赖
COPY requirements.txt .
RUN pip install --user --no-cache-dir -r requirements.txt

# 生产镜像
FROM python:3.12-slim

WORKDIR /app

# 复制依赖
COPY --from=builder /root/.local /root/.local
ENV PATH=/root/.local/bin:$PATH

# 复制应用代码
COPY app/ ./app/
COPY alembic.ini .

# 非 root 用户运行
RUN useradd -m appuser && chown -R appuser:appuser /app
USER appuser

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

```dockerfile
# Dockerfile (Frontend)
FROM node:20-alpine as builder

WORKDIR /app

COPY package*.json ./
RUN npm ci

COPY . .
RUN npm run build

# 生产镜像
FROM node:20-alpine

WORKDIR /app

ENV NODE_ENV=production

COPY --from=builder /app/.next/standalone ./
COPY --from=builder /app/.next/static ./.next/static
COPY --from=builder /app/public ./public

EXPOSE 3000

CMD ["node", "server.js"]
```

### 8.2 Docker Compose 开发环境

```yaml
# docker-compose.yml
version: '3.8'

services:
  backend:
    build: ./backend
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=mysql+pymysql://user:pass@mysql:3306/pet_health
      - REDIS_URL=redis://redis:6379/0
      - MINIO_ENDPOINT=minio:9000
    volumes:
      - ./backend/app:/app/app  # 热重载
    depends_on:
      - mysql
      - redis
      - minio
    command: uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

  frontend:
    build: ./frontend
    ports:
      - "3000:3000"
    environment:
      - NEXT_PUBLIC_API_URL=http://localhost:8000
    volumes:
      - ./frontend:/app
    command: npm run dev

  mysql:
    image: mysql:8.0
    environment:
      MYSQL_ROOT_PASSWORD: rootpass
      MYSQL_DATABASE: pet_health
      MYSQL_USER: user
      MYSQL_PASSWORD: pass
    ports:
      - "3306:3306"
    volumes:
      - mysql_data:/var/lib/mysql

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data

  minio:
    image: minio/minio:latest
    environment:
      MINIO_ROOT_USER: minioadmin
      MINIO_ROOT_PASSWORD: minioadmin
    ports:
      - "9000:9000"
      - "9001:9001"  # Console
    volumes:
      - minio_data:/data
    command: server /data --console-address ":9001"

  celery_worker:
    build: ./backend
    environment:
      - DATABASE_URL=mysql+pymysql://user:pass@mysql:3306/pet_health
      - REDIS_URL=redis://redis:6379/0
    depends_on:
      - redis
      - mysql
    command: celery -A app.tasks worker --loglevel=info --queues=image,memory,report

  celery_beat:
    build: ./backend
    environment:
      - DATABASE_URL=mysql+pymysql://user:pass@mysql:3306/pet_health
      - REDIS_URL=redis://redis:6379/0
    depends_on:
      - redis
    command: celery -A app.tasks beat --loglevel=info

volumes:
  mysql_data:
  redis_data:
  minio_data:
```

### 8.3 Kubernetes 生产部署

```yaml
# k8s/namespace.yaml
apiVersion: v1
kind: Namespace
metadata:
  name: pet-health

---
# k8s/backend-deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: backend
  namespace: pet-health
spec:
  replicas: 3
  selector:
    matchLabels:
      app: backend
  template:
    metadata:
      labels:
        app: backend
    spec:
      containers:
        - name: backend
          image: pet-health/backend:latest
          ports:
            - containerPort: 8000
          envFrom:
            - configMapRef:
                name: backend-config
            - secretRef:
                name: backend-secrets
          resources:
            requests:
              memory: "512Mi"
              cpu: "500m"
            limits:
              memory: "1Gi"
              cpu: "1000m"
          livenessProbe:
            httpGet:
              path: /api/v1/health/live
              port: 8000
            initialDelaySeconds: 30
            periodSeconds: 10
          readinessProbe:
            httpGet:
              path: /api/v1/health/ready
              port: 8000
            initialDelaySeconds: 5
            periodSeconds: 5

---
# k8s/hpa.yaml (水平自动扩缩容)
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: backend-hpa
  namespace: pet-health
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: backend
  minReplicas: 3
  maxReplicas: 20
  metrics:
    - type: Resource
      resource:
        name: cpu
        target:
          type: Utilization
          averageUtilization: 70
    - type: Resource
      resource:
        name: memory
        target:
          type: Utilization
          averageUtilization: 80
```

---

## 9. 安全与防护

### 9.1 API 限流策略

```python
# app/core/rate_limit.py
from fastapi_limiter import FastAPILimiter
from fastapi_limiter.depends import RateLimiter
import redis.asyncio as redis

# 初始化限流器
async def init_rate_limiter():
    redis_connection = await redis.from_url(
        "redis://localhost:6379/0",
        encoding="utf-8",
        decode_responses=True
    )
    await FastAPILimiter.init(redis_connection)

# 限流规则
# 1. 普通用户: 60请求/分钟
# 2. VIP用户: 120请求/分钟
# 3. 对话接口: 10请求/分钟 (更严格)
# 4. 图片上传: 10次/小时

async def get_rate_limit_params(request: Request) -> list:
    """根据用户等级动态返回限流参数"""
    user = request.state.user
    
    # 免费用户
    if user.subscription_tier == "free":
        return [RateLimiter(times=60, seconds=60)]
    # VIP用户
    elif user.subscription_tier == "vip":
        return [RateLimiter(times=120, seconds=60)]
    else:
        return [RateLimiter(times=60, seconds=60)]

# 应用限流
@router.post("/chat", dependencies=[Depends(RateLimiter(times=10, seconds=60))])
async def chat_endpoint(...):
    pass

@router.post("/upload", dependencies=[Depends(RateLimiter(times=10, seconds=3600))])
async def upload_image(...):
    pass
```

### 9.2 内容安全过滤 (增强)

```python
# app/core/content_safety.py
from transformers import pipeline
import re

class ContentSafetyChecker:
    """内容安全检测器"""
    
    # 敏感词列表
    SENSITIVE_WORDS = [
        "安乐死", "剧毒", "自杀", "杀人", "..."
    ]
    
    # PII 检测正则
    PII_PATTERNS = {
        "phone": re.compile(r'1[3-9]\d{9}'),
        "id_card": re.compile(r'\d{17}[\dXx]'),
        "email": re.compile(r'[\w.-]+@[\w.-]+\.\w+')
    }
    
    def __init__(self):
        # 加载轻量级敏感内容分类模型 (可选)
        self.classifier = pipeline(
            "text-classification",
            model="distilbert-base-uncased-finetuned-sst-2-english",
            device=-1
        )
    
    def check_input(self, text: str) -> dict:
        """检查用户输入"""
        result = {
            "is_safe": True,
            "violations": [],
            "pii_detected": [],
            "masked_text": text
        }
        
        # 1. 敏感词检测
        for word in self.SENSITIVE_WORDS:
            if word in text:
                result["is_safe"] = False
                result["violations"].append(f"敏感词: {word}")
        
        # 2. PII 检测与脱敏
        for pii_type, pattern in self.PII_PATTERNS.items():
            matches = pattern.findall(text)
            if matches:
                result["pii_detected"].append({"type": pii_type, "count": len(matches)})
                # 脱敏处理
                for match in matches:
                    masked = self._mask_pii(match, pii_type)
                    result["masked_text"] = result["masked_text"].replace(match, masked)
        
        return result
    
    def _mask_pii(self, value: str, pii_type: str) -> str:
        if pii_type == "phone":
            return value[:3] + "****" + value[-4:]
        elif pii_type == "id_card":
            return value[:6] + "********" + value[-4:]
        elif pii_type == "email":
            parts = value.split("@")
            return parts[0][:2] + "***@" + parts[1]
        return value

# 中间件集成
@app.middleware("http")
async def content_safety_middleware(request: Request, call_next):
    if request.method == "POST":
        body = await request.body()
        try:
            data = json.loads(body)
            if "content" in data:
                checker = ContentSafetyChecker()
                check_result = checker.check_input(data["content"])
                
                if not check_result["is_safe"]:
                    return JSONResponse(
                        status_code=400,
                        content={
                            "error": "Content violates safety policy",
                            "violations": check_result["violations"]
                        }
                    )
                
                # 更新请求体为脱敏后的内容
                if check_result["pii_detected"]:
                    data["content"] = check_result["masked_text"]
                    request._body = json.dumps(data).encode()
        except:
            pass  # 非 JSON 请求直接放行
    
    return await call_next(request)
```

### 9.3 CORS 与安全头

```python
# app/main.py
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.middleware.gzip import GZipMiddleware

app = FastAPI()

# CORS (严格配置)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://pet-health.example.com"],  # 生产环境
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["Authorization", "Content-Type"],
    max_age=600
)

# 可信 Host
app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=["pet-health.example.com", "*.pet-health.example.com"]
)

# Gzip 压缩
app.add_middleware(GZipMiddleware, minimum_size=1000)

# 安全响应头
@app.middleware("http")
async def security_headers(request: Request, call_next):
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
    response.headers["Content-Security-Policy"] = "default-src 'self'"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    return response
```

---

## 10. 测试策略

### 10.1 测试金字塔

```
        /\
       /  \     E2E 测试 (少量)
      /----\    用户场景验证
     /      \
    /--------\  集成测试 (中等)
   /          \ API 契约、数据库交互
  /------------\
 /              \ 单元测试 (大量)
/----------------\ 业务逻辑、工具函数
```

### 10.2 测试目录结构

```
tests/
├── conftest.py              # pytest 全局配置
├── fixtures/                # 测试数据
│   ├── users.py
│   ├── pets.py
│   └── conversations.py
├── unit/                    # 单元测试
│   ├── test_models.py
│   ├── test_services/
│   │   ├── test_user_service.py
│   │   ├── test_pet_service.py
│   │   └── test_chat_service.py
│   ├── test_agent/
│   │   ├── test_tools.py
│   │   ├── test_middleware.py
│   │   └── test_memory.py
│   └── test_utils/
├── integration/             # 集成测试
│   ├── test_api/
│   │   ├── test_auth.py
│   │   ├── test_pets.py
│   │   └── test_chat.py
│   ├── test_db/
│   │   └── test_migrations.py
│   └── test_external/
│       ├── test_llm.py
│       └── test_image_recognition.py
├── e2e/                     # E2E 测试
│   ├── test_user_journey.py
│   └── test_chat_flow.py
└── load/                    # 性能测试
    ├── locustfile.py
    └── k6_script.js
```

### 10.3 关键测试用例

```python
# tests/unit/test_agent/test_tools.py
import pytest
from unittest.mock import Mock, patch
from app.agent.tools.health_tools import HealthConsultationTool

class TestHealthConsultationTool:
    @pytest.fixture
    def tool(self):
        return HealthConsultationTool()
    
    @pytest.fixture
    def mock_pet_profile(self):
        return {
            "pet_id": "pet_123",
            "name": "豆豆",
            "breed": "金毛",
            "age": 2,
            "medical_history": ["皮肤病"]
        }
    
    async def test_symptom_analysis_with_context(self, tool, mock_pet_profile):
        """测试结合宠物档案的症状分析"""
        with patch('app.services.rag_service.retrieve') as mock_retrieve:
            mock_retrieve.return_value = [
                {"content": "金毛常见皮肤病...", "source": "犬类皮肤病指南"}
            ]
            
            result = await tool.run(
                symptom="皮肤发红",
                pet_profile=mock_pet_profile
            )
            
            assert "金毛" in result["analysis"]
            assert "皮肤病史" in result["considerations"]
            assert len(result["recommendations"]) > 0
    
    async def test_urgency_level_classification(self, tool):
        """测试紧急程度分级"""
        urgent_cases = ["吐血", "抽搐", "呼吸困难"]
        non_urgent_cases = ["轻微掉毛", "食欲略减"]
        
        for symptom in urgent_cases:
            result = await tool.run(symptom=symptom)
            assert result["urgency_level"] >= 4
            
        for symptom in non_urgent_cases:
            result = await tool.run(symptom=symptom)
            assert result["urgency_level"] <= 2

# tests/integration/test_api/test_chat.py
class TestChatAPI:
    async def test_streaming_response(self, client, auth_headers):
        """测试流式对话响应"""
        response = client.post(
            "/api/v1/conversations/conv_123/messages",
            headers=auth_headers,
            json={"content": "我家猫软便"},
            stream=True
        )
        
        # 验证 SSE 格式
        chunks = []
        for line in response.iter_lines():
            if line.startswith(b"data: "):
                data = json.loads(line[6:])
                chunks.append(data)
        
        # 验证流式响应包含完整内容
        assert any(chunk["type"] == "token" for chunk in chunks)
        assert any(chunk["type"] == "complete" for chunk in chunks)
    
    async def test_chat_with_image(self, client, auth_headers, mock_image):
        """测试图片上传对话"""
        # 1. 上传图片
        upload_response = client.post(
            "/api/v1/upload/image",
            headers=auth_headers,
            files={"file": ("test.jpg", mock_image, "image/jpeg")}
        )
        image_url = upload_response.json()["data"]["url"]
        
        # 2. 发送带图片的消息
        response = client.post(
            "/api/v1/conversations/conv_123/messages",
            headers=auth_headers,
            json={
                "content": "这是皮肤照片",
                "image_urls": [image_url]
            }
        )
        
        assert response.status_code == 200
        assert "皮肤病" in response.json()["data"]["content"]

# tests/e2e/test_chat_flow.py
class TestChatFlow:
    async def test_complete_consultation_flow(self, client, auth_headers):
        """测试完整咨询流程"""
        # 1. 创建宠物档案
        pet_response = client.post(
            "/api/v1/pets",
            headers=auth_headers,
            json={
                "name": "咪咪",
                "species": "cat",
                "breed": "布偶"
            }
        )
        pet_id = pet_response.json()["data"]["pet_id"]
        
        # 2. 开始对话
        conv_response = client.post(
            "/api/v1/conversations",
            headers=auth_headers,
            json={"pet_id": pet_id}
        )
        conv_id = conv_response.json()["data"]["conversation_id"]
        
        # 3. 咨询症状
        chat_response = client.post(
            f"/api/v1/conversations/{conv_id}/messages",
            headers=auth_headers,
            json={"content": "猫咪最近软便"}
        )
        
        # 4. 验证响应包含免责声明
        content = chat_response.json()["data"]["content"]
        assert "免责声明" in content
        assert "仅供参考" in content
        
        # 5. 验证宠物上下文被使用
        assert "咪咪" in content or "布偶" in content
```

### 10.4 性能测试

```python
# tests/load/locustfile.py
from locust import HttpUser, task, between

class PetHealthUser(HttpUser):
    wait_time = between(1, 3)
    
    def on_start(self):
        # 登录获取 token
        response = self.client.post("/api/v1/auth/login", json={
            "phone": "13800138000",
            "password": "test1234"
        })
        self.token = response.json()["data"]["access_token"]
        self.headers = {"Authorization": f"Bearer {self.token}"}
    
    @task(3)
    def get_pets(self):
        self.client.get("/api/v1/pets", headers=self.headers)
    
    @task(2)
    def create_conversation(self):
        self.client.post(
            "/api/v1/conversations",
            headers=self.headers,
            json={"pet_id": "some_pet_id"}
        )
    
    @task(1)
    def send_message(self):
        self.client.post(
            "/api/v1/conversations/conv_id/messages",
            headers=self.headers,
            json={"content": "测试消息"}
        )
```

---

## 11. 遗漏点补充总结

### 11.1 已补充内容

| 类别 | 补充内容 | 文档位置 |
|------|---------|---------|
| **技术栈** | 前端 Next.js + shadcn/ui 详细选型 | 第 1 章 |
| **项目结构** | 前后端完整目录结构 | 第 2 章 |
| **API 规范** | 9 个模块 RESTful API + WebSocket 定义 | 第 3 章 |
| **认证授权** | JWT 设计、刷新策略、RBAC | 第 4 章 |
| **数据存储** | 完整表结构、Redis 缓存、对象存储 | 第 5 章 |
| **异步任务** | Celery 任务队列、消息队列设计 | 第 6 章 |
| **可观测性** | 日志、监控、链路追踪、健康检查 | 第 7 章 |
| **部署架构** | Docker、K8s、HPA 配置 | 第 8 章 |
| **安全防护** | 限流、内容安全、CORS、安全头 | 第 9 章 |
| **测试策略** | 单元/集成/E2E/性能测试 | 第 10 章 |

### 11.2 待决策事项

| 事项 | 选项 | 建议 |
|------|------|------|
| LLM 提供商 | OpenAI / DeepSeek / 阿里云 | 初期用 DeepSeek (成本低)，生产用 GPT-4o |
| 向量数据库 | ChromaDB / Milvus / PGVector | 初期 ChromaDB，数据量大后迁移 Milvus |
| 对象存储 | MinIO / 阿里云 OSS | 开发 MinIO，生产 OSS |
| 部署平台 | 自建 K8s / 云托管 (EKS/ACK) | 初期 ACK (阿里云) |

### 11.3 相关文档

| 文档 | 说明 | 关联章节 |
|------|------|---------|
| `PRD.md` | 产品需求文档 | 本文档的输入，定义了核心功能需求 |
| `模块划分与职责分配.md` | 功能模块化划分 | 本文档 §2 项目目录结构、§3 API接口规范的来源 |
| `UI-Design.md` | 前端页面与组件设计 | 本文档 §1 前端技术栈的详细应用 |

> **文档关系说明**：
> - 本文档是 `PRD.md` §2 系统架构设计的详细扩展
> - 本文档 §3 API接口规范与 `模块划分与职责分配.md` 的接口定义保持一致（均使用 `/api/v1/` 前缀）
> - 本文档 §1 前端技术栈与 `UI-Design.md` 的组件规范相呼应

---

**文档历史**:

| 版本 | 日期 | 作者 | 变更内容 |
|------|------|------|---------|
| v1.0 | 2026-04-06 | AI Assistant | 初始版本，补充架构细节 |

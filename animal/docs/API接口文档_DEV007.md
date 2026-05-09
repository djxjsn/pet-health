# DEV-007 智能购物助手 API 接口文档

## 概述

本文档描述了智能购物助手模块（DEV-007）的所有 RESTful API 接口，包括请求参数、响应格式、错误码说明等。

**基础路径**: `/api/v1/shopping`

---

## 1. 商品搜索

### POST /api/v1/shopping/search

根据关键词和筛选条件搜索商品。

#### 请求

```json
{
  "query": "狗粮",           // 可选，搜索关键词
  "category": "food",        // 可选，商品分类
  "brand": "Royal Canin",    // 可选，品牌
  "price_min": 100,          // 可选，最低价格
  "price_max": 500,          // 可选，最高价格
  "sort_by": "rating",       // 可选，排序字段
  "order": "desc",           // 可选，排序方向
  "skip": 0,                 // 可选，跳过数量
  "limit": 20                // 可选，返回数量
}
```

#### 响应 (200 OK)

```json
{
  "products": [
    {
      "_id": "obj_001",
      "product_id": "prod_food_001",
      "name": "皇家狗粮成犬",
      "category": "food",
      "price": 299.0,
      "brand": "Royal Canin",
      "rating": 4.8,
      "description": "优质成犬粮",
      "image_url": null,
      "stock_status": "in_stock",
      "currency": "CNY"
    }
  ],
  "total": 1,
  "returned": 1,
  "query": {
    "keyword": "狗粮",
    "category": null
  }
}
```

#### 错误响应 (500)

```json
{
  "detail": "搜索服务异常"
}
```

---

## 2. 获取商品详情

### GET /api/v1/shopping/products/{product_id}

获取指定商品的详细信息。

#### 路径参数

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| product_id | string | 是 | 商品ID |

#### 响应 (200 OK)

```json
{
  "_id": "obj_001",
  "product_id": "prod_food_001",
  "name": "皇家狗粮成犬",
  "category": "food",
  "price": 299.0,
  "brand": "Royal Canin",
  "rating": 4.8,
  "description": "优质成犬粮",
  "image_url": null,
  "stock_status": "in_stock",
  "currency": "CNY",
  "subcategory": "dry_food",
  "ingredients": [
    {"name": "鸡肉", "percentage": 25.0},
    {"name": "糙米", "percentage": 20.0}
  ],
  "nutrition_info": {
    "protein": 25.0,
    "fat": 14.0,
    "carbs": 40.0
  },
  "suitable_for": ["adult_dog", "medium_breed"],
  "tags": ["天然", "无谷"]
}
```

#### 错误响应

- **404 Not Found**: `{"detail": "商品不存在"}`
- **500 Internal Server Error**: `{"detail": "获取商品详情失败"}`

---

## 3. 创建商品

### POST /api/v1/shopping/products

创建新商品记录（管理员功能）。

#### 请求

```json
{
  "name": "新狗粮产品",
  "category": "food",
  "price": 199.9,
  "brand": "TestBrand",
  "subcategory": "grain_free",
  "image_url": "https://example.com/image.jpg",
  "description": "产品描述",
  "ingredients": [
    {"name": "鸡肉", "percentage": 35.0}
  ],
  "nutrition_info": {
    "protein": 30.0,
    "fat": 15.0
  },
  "suitable_for": ["adult_dog"],
  "tags": ["无谷", "高蛋白"]
}
```

#### 必填字段

| 字段 | 类型 | 说明 |
|------|------|------|
| name | string | 商品名称 |
| category | string | 分类：food/toy/accessory/medicine/hygiene/clothing |
| price | float | 价格 |

#### 响应 (200 OK)

```json
{
  "_id": "obj_new_001",
  "product_id": "prod_food_new123",
  "name": "新狗粮产品",
  "message": "商品创建成功"
}
```

#### 错误响应

- **400 Bad Request**: `{"detail": "无效的商品分类: xxx"}`
- **500 Internal Server Error**: `{"detail": "创建商品失败"}`

---

## 4. 成分分析

### POST /api/v1/shopping/analyze

分析宠物食品成分的安全性和营养价值。

#### 请求

```json
{
  "ingredients_text": "鸡肉, 糙米, 鱼油, 维生素E",
  "pet_type": "dog",
  "age_group": "adult",
  "health_conditions": ["过敏"]
}
```

#### 字段说明

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| ingredients_text | string | 是 | 成分文本 |
| pet_type | string | 是 | 宠物类型：dog/cat |
| age_group | string | 否 | 年龄阶段：puppy/kitten/adult/senior |
| health_conditions | array | 否 | 健康问题列表 |

#### 响应 (200 OK)

```json
{
  "overall_safety": "safe",
  "safety_score": 85,
  "safe_ingredients": [
    {
      "name": "鸡肉",
      "reason": "优质动物蛋白来源",
      "benefits": ["提供必需氨基酸"],
      "risk_level": "none"
    }
  ],
  "caution_ingredients": [],
  "unsafe_ingredients": [],
  "allergen_warnings": [],
  "recommendations": [
    "该配方营养均衡，适合大多数健康犬只",
    "建议配合充足饮水使用"
  ],
  "total_analyzed": 4,
  "parsed_ingredients": ["鸡肉", "糙米", "鱼油", "维生素E"]
}
```

#### 安全等级说明

| 等级 | 分数范围 | 说明 |
|------|---------|------|
| safe | 80-100 | 安全，可放心使用 |
| cautionary | 50-79 | 谨慎使用，需关注特定成分 |
| unsafe | 0-49 | 存在风险，不建议使用 |

---

## 5. 获取个性化推荐

### POST /api/v1/shopping/recommendations

基于用户历史和宠物信息获取个性化商品推荐。

#### 请求

```json
{
  "user_id": "user_001",
  "pet_type": "dog",
  "pet_age_group": "adult",
  "health_conditions": ["过敏"],
  "limit": 10
}
```

#### 响应 (200 OK)

```json
{
  "recommendations": [
    {
      "_id": "obj_rec_001",
      "product_id": "prod_food_003",
      "name": "低敏狗粮",
      "category": "food",
      "price": 328.0,
      "brand": "Hills",
      "rating": 4.7
    }
  ],
  "sources": {
    "personalized_count": 1,
    "knowledge_based_count": 2,
    "popular_count": 3,
    "health_focused_count": 2
  }
}
```

#### 推荐来源说明

| 来源 | 说明 |
|------|------|
| personalized | 基于用户历史购买/浏览行为 |
| knowledge_based | 基于RAG知识库匹配 |
| popular | 热门商品推荐 |
| health_focused | 针对健康问题的推荐 |

---

## 6. 记录购物行为

### POST /api/v1/shopping/action?user_id={user_id}

记录用户的购物相关行为（浏览、加购、购买等）。

#### 查询参数

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| user_id | string | 是 | 用户ID |

#### 请求体

```json
{
  "product_id": "prod_toy_001",
  "action_type": "view",
  "pet_id": "pet_001",
  "search_query": "磨牙玩具"
}
```

#### 操作类型

| 类型 | 说明 |
|------|------|
| search | 搜索 |
| view | 浏览详情 |
| cart | 加入购物车 |
| purchase | 购买 |
| wishlist | 加入收藏夹 |

#### 响应 (200 OK)

```json
{
  "message": "行为记录成功",
  "history_id": "history_abc12345"
}
```

---

## 7. 商品对比

### GET /api/v1/shopping/compare?product_ids=p1,p2,p3

对比多个商品的详细信息。

#### 查询参数

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| product_ids | string | 是 | 商品ID列表，逗号分隔（2-5个） |

#### 响应 (200 OK)

```json
{
  "total": 2,
  "products": [
    {
      "product_id": "p1",
      "name": "产品A",
      "price": 299.0,
      "rating": 4.5
    },
    {
      "product_id": "p2",
      "name": "产品B",
      "price": 358.0,
      "rating": 4.7
    }
  ]
}
```

#### 错误响应

- **400 Bad Request**: `{"detail": "请提供2-5个商品ID进行对比"}`
- **404 Not Found**: `{"detail": "未找到有效的商品信息"}`

---

## 8. 分类统计

### GET /api/v1/shopping/categories

获取各分类的商品数量统计。

#### 响应 (200 OK)

```json
{
  "total_products": 150,
  "by_category": {
    "food": 50,
    "toy": 30,
    "accessory": 25,
    "medicine": 20,
    "hygiene": 15,
    "clothing": 10
  }
}
```

---

## 9. 相似商品推荐

### GET /api/v1/shopping/similar/{product_id}?limit=5

获取与指定商品相似的其他商品。

#### 路径参数

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| product_id | string | 是 | 参考商品ID |

#### 查询参数

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| limit | int | 5 | 返回数量（1-10）|

#### 响应 (200 OK)

```json
{
  "reference_product_id": "prod_food_001",
  "total": 2,
  "products": [
    {
      "product_id": "sim_001",
      "name": "相似商品1",
      "price": 280.0,
      "rating": 4.6
    },
    {
      "product_id": "sim_002",
      "name": "相似商品2",
      "price": 320.0,
      "rating": 4.4
    }
  ]
}
```

---

## 数据模型

### ProductResponse

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| _id | string | 是 | MongoDB对象ID |
| product_id | string | 是 | 业务商品ID |
| name | string | 是 | 商品名称 |
| category | string | 是 | 商品分类 |
| price | float | 是 | 价格 |
| brand | string | 否 | 品牌 |
| rating | float | 是 | 评分(0-5) |
| description | string | 否 | 描述 |
| image_url | string | 否 | 图片URL |
| stock_status | string | 是 | 库存状态 |
| currency | string | 是 | 货币单位 |
| subcategory | string | 否 | 子分类 |
| ingredients | array | 否 | 成分列表 |
| nutrition_info | object | 否 | 营养信息 |
| suitable_for | array | 否 | 适用对象 |
| tags | array | 否 | 标签 |
| review_count | int | 是 | 评论数量 |

---

## 版本历史

| 版本 | 日期 | 作者 | 变更内容 |
|------|------|------|----------|
| v1.0 | 2026-04-17 | AI Assistant | 初始版本，覆盖全部9个API端点 |

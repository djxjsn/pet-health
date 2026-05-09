# 智能购物助手模块使用指南

## 概述

智能购物助手模块（DEV-007）为AI宠物健康助手提供智能商品推荐、成分分析和个性化购物建议功能。

## 架构组成

### 核心组件

1. **数据层**
   - `Product` 模型：商品信息模型
   - `ShoppingHistory` 模型：用户行为记录
   - `IngredientAnalysis` 模型：成分分析结果

2. **业务层**
   - `ShoppingService`：购物业务逻辑

3. **核心引擎**
   - `ProductSearcher`：商品搜索引擎
   - `RecommendationEngine`：推荐引擎（4种推荐策略）
   - `IngredientAnalyzer`：成分安全分析器

4. **API层**
   - RESTful API接口（10个端点）

## API接口说明

### 商品搜索

#### POST /api/v1/shopping/search

搜索宠物用品商品

**请求体**:
```json
{
  "query": "狗粮",
  "category": "food",
  "price_min": 50,
  "price_max": 200,
  "limit": 20
}
```

**响应**:
```json
{
  "products": [...],
  "total": 45,
  "returned": 20,
  "query": {
    "keyword": "狗粮",
    "category": "food"
  }
}
```

### 成分分析

#### POST /api/v1/shopping/analyze

分析宠物食品成分安全性

**请求体**:
```json
{
  "ingredients_text": "鸡肉, 糙米, 鱼油, 胡萝卜, 蓝莓",
  "pet_type": "dog",
  "breed": "金毛",
  "age_group": "adult",
  "health_conditions": ["皮肤过敏"]
}
```

**响应**:
```json
{
  "overall_safety": "safe",
  "safety_score": 92.5,
  "safe_ingredients": [
    {"name": "鸡肉", "benefit": "优质蛋白质来源"}
  ],
  "caution_ingredients": [],
  "unsafe_ingredients": [],
  "allergen_warnings": [],
  "recommendations": ["✅ 配方健康，适合日常喂养"],
  "total_analyzed": 5
}
```

### 个性化推荐

#### POST /api/v1/shopping/recommendations

获取个性化商品推荐

**请求体**:
```json
{
  "user_id": "user_123",
  "pet_type": "dog",
  "pet_age_group": "adult",
  "health_conditions": ["肥胖", "关节问题"],
  "limit": 10
}
```

**响应**:
```json
{
  "recommendations": [...],
  "sources": {
    "personalized_count": 3,
    "knowledge_based_count": 2,
    "popular_count": 3,
    "health_focused_count": 2
  }
}
```

### 其他端点

| 端点 | 方法 | 说明 |
|------|------|------|
| /shopping/products | GET | 获取商品列表 |
| /shopping/products | POST | 创建商品（管理员） |
| /shopping/products/{id} | GET | 获取商品详情 |
| /shopping/action | POST | 记录购物行为 |
| /shopping/compare | GET | 对比多个商品 |
| /shopping/categories | GET | 分类统计 |
| /shopping/similar/{id} | GET | 相似商品推荐 |

## 推荐策略说明

### 1. 个性化推荐（Personalized）
- 基于用户历史浏览/购买行为
- 推荐同分类的其他商品
- 权重：高

### 2. 健康导向推荐（Health-Focused）
- 基于RAG知识检索
- 针对健康问题推荐相关产品
- 如：皮肤病→洗护用品，肠胃问题→特殊食品

### 3. 热门推荐（Popular）
- 高评分、高销量商品
- 新品上架
- 权重：中

### 4. RAG知识增强（Knowledge-Based）
- 使用DEV-006的RAG检索能力
- 结合营养学、用药指南知识库
- 提供专业依据的推荐理由

## 成分分析功能

### 安全等级

| 等级 | 分数范围 | 说明 |
|------|---------|------|
| safe (安全) | ≥80分 | 可放心使用 |
| cautionary (需注意) | 50-79分 | 有少量需注意成分 |
| unsafe (不安全) | <50分 | 含不安全成分，不建议使用 |

### 过敏原检测

支持检测：
- **犬类过敏原**：谷物（小麦、玉米）、肉类（牛肉、鸡肉）、乳制品等
- **猫类过敏原**：鱼类（金枪鱼）、肉类、谷物等

### 个性化建议生成

根据以下因素生成：
- 宠物类型和品种
- 年龄阶段（幼年/成年/老年）
- 健康问题（肥胖、糖尿病、皮肤病等）
- 成分安全性评估结果

## 使用示例

### Python代码示例

```python
from src.core.product_searcher import ProductSearcher
from src.core.recommendation_engine import RecommendationEngine
from src.core.ingredient_analyzer import IngredientAnalyzer

# 1. 搜索商品
searcher = ProductSearcher()
results = searcher.search(query="狗粮", category="food")
print(f"找到 {results['total']} 个商品")

# 2. 成分分析
analyzer = IngredientAnalyzer()
analysis = analyzer.analyze(
    ingredients_text="鸡肉, 糙米, 鱼油, BHA防腐剂",
    pet_type="dog",
    age_group="adult"
)
print(f"安全分数: {analysis['safety_score']}")
print(f"建议: {analysis['recommendations']}")

# 3. 个性化推荐
engine = RecommendationEngine()
recommendations = engine.get_recommendations(
    user_id="user_123",
    pet_type="dog",
    health_conditions=["皮肤过敏"]
)
for product in recommendations["recommendations"][:5]:
    print(f"- {product['name']}")
```

## 注意事项

1. **成分数据库**：当前为内置基础版本，可扩展专业营养数据库
2. **推荐准确性**：依赖用户历史数据积累，新用户可能效果有限
3. **价格信息**：需要实际对接电商平台API或手动维护
4. **成分解析**：复杂配方可能需要人工校验

---

**文档版本**：v1.0
**更新日期**：2026-04-17
**维护人员**：后端开发团队

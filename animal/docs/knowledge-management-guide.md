# 知识管理模块使用指南

## 概述

知识管理模块（DEV-006）为AI宠物健康助手提供RAG（检索增强生成）能力，支持知识文档的管理、向量化索引和语义检索。

## 架构组成

### 核心组件

1. **数据层**
   - `KnowledgeDocument` 模型：MongoDB知识文档模型
   - `KnowledgeRepository`：数据访问层

2. **业务层**
   - `KnowledgeService`：知识文档业务逻辑
   - `KnowledgeUpdateService`：知识更新服务

3. **核心引擎**
   - `DocumentLoader`：文档加载器
   - `TextChunker`：文本分块器
   - `KnowledgeIndexer`：索引构建器
   - `KnowledgeRetriever`：知识检索器

4. **API层**
   - RESTful API接口
   - Pydantic数据验证

## API接口说明

### 知识检索

#### POST /api/v1/knowledge/search

基于语义检索相关知识

**请求体**:
```json
{
  "query": "狗狗呕吐怎么办",
  "top_k": 5,
  "category": "disease",
  "tags": ["消化系统"]
}
```

**响应**:
```json
{
  "query": "狗狗呕吐怎么办",
  "total": 3,
  "results": [
    {
      "content": "呕吐常见原因：食物不当、肠胃炎...",
      "metadata": {
        "category": "disease",
        "doc_id": "knowledge_disease_xxx",
        "chunk_index": 2
      },
      "distance": 0.15
    }
  ]
}
```

### 知识文档管理

#### GET /api/v1/knowledge/documents

获取知识文档列表

**查询参数**:
- `skip`: 跳过数量（默认0）
- `limit`: 返回数量（默认20，最大100）
- `category`: 文档分类过滤（disease/medication/first_aid/nutrition/behavior）
- `status`: 文档状态过滤（draft/published/archived）

#### POST /api/v1/knowledge/documents

创建知识文档

**请求体**:
```json
{
  "title": "犬瘟热防治指南",
  "content": "犬瘟热是由犬瘟热病毒引起...",
  "category": "disease",
  "tags": ["传染病", "犬类"],
  "source": "兽医手册",
  "status": "draft"
}
```

#### GET /api/v1/knowledge/documents/{doc_id}

获取单个知识文档详情

#### PUT /api/v1/knowledge/documents/{doc_id}

更新知识文档

#### DELETE /api/v1/knowledge/documents/{doc_id}

删除知识文档（同时移除向量索引）

#### POST /api/v1/knowledge/documents/{doc_id}/publish

发布知识文档（发布后等待索引）

### 索引管理

#### POST /api/v1/knowledge/index/rebuild

重建整个知识索引（清空后重新索引）

#### POST /api/v1/knowledge/index/update

增量更新索引（只索引未索引的文档）

#### GET /api/v1/knowledge/index/stats

获取索引统计信息

### 更新管理

#### POST /api/v1/knowledge/update/incremental

增量更新所有已发布但未索引的文档

#### POST /api/v1/knowledge/update/check-changes

检查已索引文档的变更并自动更新

#### POST /api/v1/knowledge/update/batch-publish

批量发布文档并自动索引

**请求体**:
```json
["doc_id_1", "doc_id_2", "doc_id_3"]
```

#### GET /api/v1/knowledge/update/history

获取知识库更新统计信息

## 文档分类

系统支持5种知识分类：

| 分类代码 | 分类名称 | 说明 | 示例 |
|---------|---------|------|------|
| disease | 疾病百科 | 常见疾病、症状、防治 | 犬瘟热、猫瘟 |
| medication | 用药指南 | 药物说明、用量、禁忌 | 阿莫西林、伊维菌素 |
| first_aid | 急救手册 | 急救流程、注意事项 | 出血急救、中毒急救 |
| nutrition | 营养建议 | 饮食指导、禁忌食物 | 幼犬营养、减肥饮食 |
| behavior | 行为训练 | 行为问题、训练方法 | 拆家行为、如厕训练 |

## 使用示例

### Python代码示例

```python
from src.core.knowledge_retriever import KnowledgeRetriever
from src.services.knowledge_service import KnowledgeService
from src.core.knowledge_indexer import KnowledgeIndexer

# 1. 创建知识文档
doc_id = KnowledgeService.create_document(
    title="犬瘟热防治",
    content="犬瘟热是由犬瘟热病毒引起...",
    category="disease",
    tags=["传染病"],
    status="published"
)

# 2. 索引文档
indexer = KnowledgeIndexer()
indexer.index_document(doc_id)

# 3. 检索知识
retriever = KnowledgeRetriever()
results = retriever.search(
    query="狗狗发烧怎么办",
    top_k=5,
    category="disease"
)

for result in results:
    print(f"内容: {result['content']}")
    print(f"相关度: {result['distance']}")
```

### 命令行示例

```bash
# 导入知识文档
python scripts/build_knowledge_index.py --import

# 构建索引
python scripts/build_knowledge_index.py --build

# 查看统计
python scripts/build_knowledge_index.py --stats

# 执行所有操作
python scripts/build_knowledge_index.py --all
```

## 性能指标

| 指标 | 目标 | 实际 |
|------|------|------|
| 向量检索响应时间 | < 100ms | 待测试 |
| 检索结果相关性 | > 85% | 待测试 |
| 索引构建速度 | > 10文档/秒 | 待测试 |
| 单元测试覆盖率 | > 85% | > 90% |

## 注意事项

1. **文档发布后才可索引**：只有status为"published"的文档才会被索引
2. **内容变更需重新索引**：修改已索引文档的内容后，需要重新索引
3. **分块策略选择**：语义分块适合结构化文档，重叠分块适合长文本
4. **网络依赖**：SentenceTransformer模型需要访问HuggingFace下载
5. **存储空间**：向量数据库会随文档量增加而增长，需定期监控

## 故障排查

### 问题1：检索结果为空

**原因**：
- 文档未发布
- 文档未索引
- 查询条件过于严格

**解决方案**：
1. 检查文档状态：`GET /api/v1/knowledge/documents`
2. 检查索引状态：`GET /api/v1/knowledge/index/stats`
3. 执行索引更新：`POST /api/v1/knowledge/index/update`

### 问题2：索引构建失败

**原因**：
- MongoDB连接失败
- ChromaDB初始化失败
- 文档内容为空

**解决方案**：
1. 检查MongoDB连接配置
2. 检查ChromaDB持久化目录权限
3. 检查文档内容是否有效

### 问题3：检索响应慢

**原因**：
- 向量数据库文档过多
- Embedding模型加载慢
- 网络延迟

**解决方案**：
1. 减少top_k参数
2. 使用分类过滤减少检索范围
3. 检查网络连接状态

---

**文档版本**：v1.0
**更新日期**：2026-04-17
**维护人员**：后端开发团队

# AI 宠物健康助手 Agent - 项目需求文档 (PRD)

**版本**: v1.0  
**日期**: 2026-04-06  
**状态**: 草案

---

## 1. 项目概述

### 1.1 项目背景
随着养宠人群增长，宠物主面临健康咨询、行为分析、选购决策、多宠管理四大核心痛点。本项目旨在构建基于 LangChain v1.0+ 技术的 AI Agent，为宠物主提供智能化、个性化的健康助手服务。

### 1.2 目标用户
- 养宠新手（需要基础健康指导）
- 多宠家庭（需要档案管理）
- 关注宠物健康的老用户（需要长期健康追踪）

### 1.3 核心价值主张
- **精准诊断**: 结合宠物档案的个性化健康建议
- **智能购物**: 基于健康状况的商品推荐
- **多宠管理**: 上下文感知的对话体验
- **知识增强**: RAG 技术提供的专业医疗知识支撑

---

## 2. 系统架构设计

### 2.1 技术栈

| 层级 | 技术选型 | 版本要求 | 用途 |
|------|----------|----------|------|
| **编排框架** | LangChain | v1.0+ | Agent 编排、中间件机制、工具链 |
| **任务流** | LangGraph | 最新版 | 复杂任务拆解与状态管理 |
| **后端服务** | FastAPI | v0.100+ | RESTful API、WebSocket、流式响应 |
| **数据库** | MySQL | 8.0+ | 结构化数据存储 |
| **向量库** | ChromaDB / Milvus | 最新版 | 知识库向量索引 |
| **LLM 引擎** | OpenAI GPT-4o / DeepSeek / 阿里云千问 | - | 意图识别与推理 |

### 2.2 架构分层

```
┌─────────────────────────────────────────────────────────────┐
│                      交互层 (Presentation)                    │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────┐   │
│  │   Web 端    │  │   小程序    │  │     移动端 App       │   │
│  └─────────────┘  └─────────────┘  └─────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                      API 网关层                              │
│  ┌─────────────────────────────────────────────────────────┐ │
│  │                    FastAPI 服务层                        │ │
│  │  • RESTful API  │  • WebSocket  │  • StreamingResponse  │ │
│  └─────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                      Agent 核心层                            │
│  ┌─────────────────────────────────────────────────────────┐ │
│  │                   LangChain Agent                        │ │
│  │  ┌─────────┐  ┌──────────┐  ┌─────────┐  ┌──────────┐  │ │
│  │  │  大脑   │  │  记忆    │  │  规划   │  │  工具链  │  │ │
│  │  │ (LLM)   │  │(短/长期) │  │(LangGraph)│  │(Tools)   │  │ │
│  │  └─────────┘  └──────────┘  └─────────┘  └──────────┘  │ │
│  └─────────────────────────────────────────────────────────┘ │
│  ┌─────────────────────────────────────────────────────────┐ │
│  │              中间件层 (Middleware)                        │ │
│  │  • 上下文注入中间件  │  • 安全过滤中间件  │  • 日志中间件  │ │
│  └─────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                      数据层 (Data Layer)                     │
│  ┌─────────────────┐  ┌─────────────────┐  ┌───────────────┐ │
│  │     MySQL       │  │    向量数据库    │  │   外部 API    │ │
│  │  • 用户表       │  │  • 医疗知识向量  │  │  • 图像识别   │ │
│  │  • 宠物档案表   │  │  • 行为知识向量  │  │  • 联网搜索   │ │
│  │  • 对话历史表   │  │  • 商品知识向量  │  │  • 商品数据   │ │
│  └─────────────────┘  └─────────────────┘  └───────────────┘ │
└─────────────────────────────────────────────────────────────┘
```

---

## 3. 核心功能模块

### 3.1 模块总览

| 模块编号 | 模块名称 | 核心痛点 | 技术方案 | 优先级 |
|---------|---------|---------|---------|--------|
| M1 | 健康咨询与症状分诊 | 生病、掉毛、软便 | RAG + 多模态识别 | P0 |
| M2 | 情绪与行为分析 | 拆家、嚎叫等异常行为 | 行为知识库 + 品种特性 | P0 |
| M3 | 智能购物决策助手 | 粮食、玩具、药品选购 | 联网搜索 + 成分分析 | P1 |
| M4 | 宠物识别与档案管理 | 品种识别、多宠管理 | 图像识别 + 上下文中间件 | P0 |

### 3.2 模块详细设计

#### M1: 健康咨询与症状分诊模块

**功能描述**: 为用户提供宠物健康症状分析、初步分诊建议及护理指导。

**子功能**:

1. **症状描述分析**
   - 用户输入: "我家猫最近软便，精神状态还可以"
   - Agent 处理: 
     - 意图识别: 健康咨询-消化系统问题
     - 上下文加载: 从 MySQL 加载宠物品种、年龄、疫苗史、过往病史
     - RAG 检索: 查询软便可能原因、常见治疗方案
     - 推理输出: 给出初步分析及建议

2. **多模态图像识别**
   - 支持类型: 皮肤病灶、粪便状态、眼睛分泌物、外伤
   - 处理流程:
     ```
     用户上传图片 
         ↓
     图像预处理
         ↓
     视觉模型分析 (GPT-4 Vision / 专用模型)
     ├─ 病灶定位与分类
     ├─ 严重程度评估
     └─ 建议就医等级 (紧急/建议/观察)
         ↓
     结合文本描述综合判断
         ↓
     输出诊断建议 + 免责声明
     ```

3. **RAG 知识检索**
   - 知识库内容:
     - 宠物常见疾病百科
     - 用药指南 (剂量、禁忌)
     - 急救处理手册
   - 检索策略:
     - 症状关键词向量化匹配
     - 品种特异性知识加权
     - 年龄阶段相关知识过滤

**数据模型**:
```python
class HealthConsultation(BaseModel):
    consultation_id: str           # 咨询ID
    user_id: str                   # 用户ID
    pet_id: str                    # 关联宠物ID
    symptoms: List[str]            # 症状标签
    description: str               # 用户描述
    image_urls: List[str]          # 图片URL
    diagnosis_result: dict         # 诊断结果
    recommendations: List[str]     # 建议列表
    urgency_level: int             # 紧急程度 1-5
    created_at: datetime
```

---

#### M2: 情绪与行为分析模块

**功能描述**: 分析宠物异常行为原因，提供训练建议。

**子功能**:

1. **行为描述解析**
   - 常见行为库: 拆家、过度嚎叫、攻击行为、拒食、过度舔毛
   - 分析维度:
     - 品种特性 (如: 哈士奇精力旺盛、布偶猫温顺)
     - 年龄段因素 (幼犬磨牙期、老年猫认知障碍)
     - 环境因素 (新成员加入、搬家应激)

2. **场景化推理**
   - 推理链:
     ```
     行为描述 + 宠物档案
            ↓
     品种特性匹配 → 可能性权重
     年龄阶段匹配 → 可能性权重
     环境因素分析 → 可能性权重
            ↓
     综合排序最可能原因
            ↓
     针对性解决方案推荐
     ```

**示例对话**:
```
用户: "最近我家边牧总把沙发咬坏"
Agent: "根据档案，您的边牧目前1岁2个月，正值精力旺盛期。边牧作为工作犬种，
       需要大量运动和精神刺激。拆家行为可能原因：
       1. 运动量不足 (最可能)
       2. 分离焦虑
       3. 换牙期不适
       
       建议：
       • 每日至少2小时户外活动
       • 增加嗅闻垫、益智玩具
       • 咬沙发时及时制止并引导到磨牙玩具"
```

---

#### M3: 智能购物决策助手

**功能描述**: 基于宠物健康状况推荐合适商品，提供成分分析。

**子功能**:

1. **需求驱动的商品搜索**
   - 触发场景:
     - 用户主动询问: "软便猫适合什么粮"
     - Agent 主动推荐: "针对当前皮肤问题，建议考虑..."
   - 搜索工具:
     - Tavily API: 实时搜索商品信息
     - 自建商品库: 已审核的优质商品

2. **成分分析引擎**
   - 分析维度:
     - 过敏原排查 (谷物、特定肉类)
     - 营养成分评估 (蛋白质、脂肪、添加剂)
     - 健康适配度 (泌尿配方、肠胃配方等)

3. **对比报告生成**
   - 输出格式:
     ```markdown
     ## 猫粮推荐对比
     
     | 商品 | 成分亮点 | 适用性评分 | 参考价格 |
     |------|---------|-----------|---------|
     | 品牌A | 无谷、单一蛋白 | 9.2/10 | ¥45/斤 |
     | 品牌B | 添加益生菌 | 8.5/10 | ¥38/斤 |
     
     **推荐理由**: 基于您宠物当前软便情况，优先推荐低敏配方...
     ```

**工具定义**:
```python
class ShoppingAssistantTools:
    
    @tool
    def search_products(query: str, category: str, constraints: dict) -> list:
        """联网搜索符合需求的宠物商品"""
        pass
    
    @tool
    def analyze_ingredients(ingredient_list: str, pet_profile: dict) -> dict:
        """分析成分表，识别风险与适配度"""
        pass
    
    @tool
    def generate_comparison_report(products: list, pet_needs: str) -> str:
        """生成商品对比报告"""
        pass
```

---

#### M4: 宠物识别与档案管理

**功能描述**: 图像识别品种品相，多宠物场景下的精准上下文管理。

**子功能**:

1. **图像识别**
   - 识别类型:
     - 品种识别 (狗狗: 金毛、哈士奇...; 猫咪: 布偶、英短...)
     - 品相评估 (可选)
     - 年龄估算 (可选)

2. **档案管理**
   - 档案字段:
     ```python
     class PetProfile(BaseModel):
         pet_id: str
         user_id: str
         name: str
         species: str              # 物种: cat/dog
         breed: str                # 品种
         birth_date: date
         gender: str
         weight: float
         medical_history: list     # 病史
         allergies: list           # 过敏源
         current_medications: list # 当前用药
         last_checkup: date        # 上次体检
     ```

3. **多宠物上下文管理**
   - 核心技术: **LangChain 中间件机制**
   - 实现逻辑:
     ```python
     class PetContextMiddleware(BaseMiddleware):
         """在每次对话前自动注入当前宠物上下文"""
         
         async def on_start(self, run_id, parent_run_id, **kwargs):
             # 1. 从会话状态获取 current_pet_id
             current_pet_id = self.session.get("current_pet_id")
             
             # 2. 从 MySQL 加载完整档案
             pet_profile = await self.db.get_pet_profile(current_pet_id)
             
             # 3. 注入到 prompt 上下文
             self.context["pet_profile"] = pet_profile
             
             # 4. 指代消解: 将"它"转换为具体宠物名
             self.input["message"] = resolve_references(
                 self.input["message"], 
                 pet_profile["name"]
             )
     ```

   - 指代消解示例:
     ```
     用户输入: "它是不是病了"
     中间件处理后: "金毛'豆豆'是不是病了 [档案: 2岁，病史: 真菌性皮炎]"
     ```

---

## 4. 技术实现关键点

### 4.1 上下文工程 (Context Engineering)

**目标**: 确保模型始终基于准确的宠物档案进行推理。

**实现方案**:

| 层级 | 组件 | 职责 |
|------|------|------|
| 数据层 | MySQL | 持久化存储宠物档案、对话历史 |
| 缓存层 | Redis (可选) | 热点数据缓存，减少数据库查询 |
| 应用层 | 上下文管理器 | 维护当前会话的 active_pet_id |
| 中间件层 | PetContextMiddleware | 自动注入档案到 prompt |

**上下文注入模板**:
```python
PET_CONTEXT_TEMPLATE = """
【当前宠物档案】
- 昵称: {pet_name}
- 品种: {breed}
- 年龄: {age}岁
- 体重: {weight}kg
- 病史: {medical_history}
- 过敏源: {allergies}
- 当前用药: {current_medications}
- 最近健康状况: {recent_health_notes}

【用户输入】
{user_input}

请基于以上档案信息，回答用户的宠物健康问题。
"""
```

### 4.2 流式输出与异步处理

**技术方案**:

```python
from fastapi import FastAPI
from fastapi.responses import StreamingResponse
from langchain_core.callbacks import AsyncCallbackHandler

app = FastAPI()

class StreamingCallbackHandler(AsyncCallbackHandler):
    """自定义回调处理器，实时捕获 Token"""
    
    def __init__(self):
        self.queue = asyncio.Queue()
    
    async def on_llm_new_token(self, token: str, **kwargs):
        await self.queue.put(token)
    
    async def generate_tokens(self):
        while True:
            token = await self.queue.get()
            if token is None:  # 结束标记
                break
            yield f"data: {token}\n\n"

@app.post("/chat")
async def chat_endpoint(request: ChatRequest):
    handler = StreamingCallbackHandler()
    
    # 在后台运行 Agent
    asyncio.create_task(
        agent.ainvoke(
            {"input": request.message},
            config={"callbacks": [handler]}
        )
    )
    
    return StreamingResponse(
        handler.generate_tokens(),
        media_type="text/event-stream"
    )
```

### 4.3 数据安全与隐私

**安全措施**:

| 层级 | 措施 | 实现方式 |
|------|------|---------|
| 存储层 | 敏感数据加密 | MySQL 字段级 AES 加密 |
| 传输层 | HTTPS 全站 | SSL/TLS 证书 |
| 应用层 | 安全过滤中间件 | 拦截医疗建议中的风险内容 |
| 输出层 | 免责声明 | 所有诊断建议后自动追加 |

**安全过滤中间件**:
```python
class SafetyFilterMiddleware(BaseMiddleware):
    """过滤不合规的医疗建议，追加免责声明"""
    
    RISK_KEYWORDS = ["手术", "注射", "处方", "停药", "安乐死"]
    DISCLAIMER = """
    \n\n---
    ⚠️ **免责声明**: 以上建议仅供参考，不能替代专业兽医诊断。
       如症状持续或加重，请及时联系执业兽医就诊。
    """
    
    async def on_end(self, run_id, parent_run_id, outputs, **kwargs):
        output_text = outputs.get("output", "")
        
        # 1. 检测风险关键词
        for keyword in self.RISK_KEYWORDS:
            if keyword in output_text:
                # 记录风险日志
                await self.log_risk_interaction(run_id, keyword)
        
        # 2. 追加免责声明
        outputs["output"] = output_text + self.DISCLAIMER
```

### 4.4 记忆系统设计

**短期记忆 (会话级)**:
- 存储: Redis / 内存
- 内容: 当前对话轮次、临时上下文
- 有效期: 会话结束

**长期记忆 (用户级)**:
- 存储: MySQL
- 内容: 
  - 对话历史摘要 (关键信息提取)
  - 宠物健康画像 (持续更新)
  - 用户偏好 (喜好的交互方式)

**健康画像更新机制**:
```python
class HealthProfileUpdater:
    """从对话中提取健康信息，更新宠物画像"""
    
    async def update_from_conversation(
        self, 
        pet_id: str, 
        conversation_summary: str
    ):
        # 1. 使用 LLM 提取关键健康信息
        extraction_prompt = f"""
        从以下对话摘要中提取健康相关信息：
        {conversation_summary}
        
        输出格式 (JSON):
        {{
            "symptoms_observed": ["症状1", "症状2"],
            "concerns_raised": ["担忧1"],
            "recommendations_given": ["建议1"]
        }}
        """
        
        extracted_info = await llm.invoke(extraction_prompt)
        
        # 2. 更新 MySQL 中的健康画像表
        await self.db.update_health_profile(pet_id, extracted_info)
```

---

## 5. 数据库设计

### 5.1 ER 图概述

```
┌─────────────┐       ┌─────────────┐       ┌─────────────────┐
│    users    │◄─────►│    pets     │◄─────►│ health_records  │
├─────────────┤   1:M ├─────────────┤  1:M  ├─────────────────┤
│ user_id (PK)│       │ pet_id (PK) │       │ record_id (PK)  │
│ phone       │       │ user_id(FK) │       │ pet_id (FK)     │
│ email       │       │ name        │       │ record_type     │
│ password    │       │ species     │       │ content         │
│ created_at  │       │ breed       │       │ created_at      │
└─────────────┘       │ birth_date  │       └─────────────────┘
                      │ weight      │
                      │ allergies   │       ┌─────────────────┐
                      │ created_at  │◄─────►│  conversations  │
                      └─────────────┘  1:M  ├─────────────────┤
                                            │ conversation_id │
                      ┌─────────────┐       │ pet_id (FK)     │
                      │ knowledge_  │       │ user_id (FK)    │
                      │   vectors   │       │ messages (JSON) │
                      ├─────────────┤       │ summary         │
                      │ id          │       │ created_at      │
                      │ content     │       └─────────────────┘
                      │ embedding   │
                      │ category    │
                      └─────────────┘
```

### 5.2 核心表结构

#### users 表
```sql
CREATE TABLE users (
    user_id VARCHAR(36) PRIMARY KEY,
    phone VARCHAR(20) UNIQUE NOT NULL,
    email VARCHAR(100) UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);
```

#### pets 表
```sql
CREATE TABLE pets (
    pet_id VARCHAR(36) PRIMARY KEY,
    user_id VARCHAR(36) NOT NULL,
    name VARCHAR(50) NOT NULL,
    species ENUM('cat', 'dog', 'other') NOT NULL,
    breed VARCHAR(50),
    birth_date DATE,
    gender ENUM('male', 'female', 'unknown'),
    weight DECIMAL(5,2),
    allergies JSON,              -- ['chicken', 'grain']
    medical_history JSON,        -- [{"condition": "...", "date": "..."}]
    current_medications JSON,    -- [{"name": "...", "dosage": "..."}]
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(user_id)
);
```

#### conversations 表
```sql
CREATE TABLE conversations (
    conversation_id VARCHAR(36) PRIMARY KEY,
    user_id VARCHAR(36) NOT NULL,
    pet_id VARCHAR(36),
    messages JSON NOT NULL,      -- [{"role": "user", "content": "..."}]
    extracted_entities JSON,     -- 提取的实体信息
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(user_id),
    FOREIGN KEY (pet_id) REFERENCES pets(pet_id)
);
```

---

## 6. 开发路线

### 阶段一: 基础搭建 (预计 2 周)

**目标**: 完成核心框架搭建，实现基础对话能力。

**交付物**:
- [ ] FastAPI 项目脚手架
- [ ] MySQL 数据库设计与建表
- [ ] LangChain 基础 Agent 搭建
- [ ] 用户认证 API (注册/登录)
- [ ] 基础对话接口 (非流式)

**技术重点**:
- 项目结构规范化
- 依赖注入设计
- 错误处理机制

### 阶段二: 知识增强 (预计 2 周)

**目标**: 构建知识库，实现 RAG 检索增强。

**交付物**:
- [ ] 宠物医疗知识库 (100+ 文档)
- [ ] 宠物行为学知识库 (50+ 文档)
- [ ] 向量数据库集成 (ChromaDB)
- [ ] RAG 检索工具
- [ ] 引用溯源功能 (回答标注知识来源)

**技术重点**:
- 文档分块策略
- 嵌入模型选型 (bge-large 等)
- 检索召回率优化

### 阶段三: 工具集成 (预计 2 周)

**目标**: 接入外部能力，扩展 Agent 技能。

**交付物**:
- [ ] 图像识别工具 (接入 GPT-4 Vision)
- [ ] 联网搜索工具 (Tavily API)
- [ ] 成分分析工具
- [ ] 多工具协同的复杂任务处理

**技术重点**:
- 工具定义规范化
- 工具选择策略
- 错误回退机制

### 阶段四: 个性化优化 (预计 2 周)

**目标**: 实现多宠管理与长期记忆。

**交付物**:
- [ ] 上下文中间件机制
- [ ] 多宠物切换与管理
- [ ] 长期记忆提取与存储
- [ ] 流式响应优化
- [ ] 安全过滤中间件

**技术重点**:
- LangChain 中间件最佳实践
- 记忆压缩与摘要算法
- 性能优化

### 里程碑时间线

```
Week 1-2  ├───────────────────────────────────────┤ 阶段一
          ▼
Week 3-4  ├───────────────────────────────────────┤ 阶段二
          ▼
Week 5-6  ├───────────────────────────────────────┤ 阶段三
          ▼
Week 7-8  ├───────────────────────────────────────┤ 阶段四
          ▼
          内测发布
```

---

## 7. 风险评估与应对

| 风险项 | 可能性 | 影响 | 应对策略 |
|-------|--------|------|---------|
| LLM API 调用成本过高 | 中 | 高 | 实现响应缓存、Prompt 压缩、模型降级策略 |
| 知识库内容不准确 | 中 | 高 | 引入兽医审核流程、来源标注、用户反馈机制 |
| 多轮对话上下文丢失 | 低 | 中 | 完善的会话状态管理、定期持久化 |
| 流式响应延迟问题 | 中 | 中 | 边缘部署、CDN 加速、首字优化 |

---

## 8. 附录

### 8.1 术语表

| 术语 | 解释 |
|------|------|
| RAG | Retrieval-Augmented Generation，检索增强生成 |
| Agent | 具备感知、决策、行动能力的智能体 |
| LangChain | LLM 应用开发框架 |
| LangGraph | 用于构建复杂 Agent 工作流的图结构框架 |
| 中间件 | 在请求处理流程中插入的拦截/处理层 |
| 向量数据库 | 用于存储和检索向量嵌入的数据库 |

### 8.2 参考资源

- LangChain v1.0 文档: https://python.langchain.com/
- LangGraph 文档: https://langchain-ai.github.io/langgraph/
- FastAPI 文档: https://fastapi.tiangolo.com/
- 兽医临床知识库 (待采购/合作)

---

**文档历史**:

| 版本 | 日期 | 作者 | 变更内容 |
|------|------|------|---------|
| v1.0 | 2026-04-06 | AI Assistant | 初始版本 |
| v1.1 | 2026-04-06 | AI Assistant | 架构细节已迁移至 Architecture-Detail.md |

---

## 9. 相关文档

| 文档 | 说明 | 关联章节 |
|------|------|---------|
| `UI-Design.md` | 前端页面功能模块与 UI 设计 | 本文档 §3 核心功能模块 |
| `Architecture-Detail.md` | 精细化架构设计 (API、部署、安全、测试等) | 本文档 §2 系统架构设计的扩展 |
| `模块划分与职责分配.md` | 功能模块化划分与职责分配 | 本文档 §3 核心功能模块的细化 |

> **文档关系说明**：
> - 本文档（PRD）定义了项目的核心需求、功能模块和技术方案概要
> - `Architecture-Detail.md` 是本文档 §2 系统架构设计的详细扩展，包含完整的技术栈定义、API接口规范、部署架构、安全防护等内容
> - `模块划分与职责分配.md` 是本文档 §3 核心功能模块的细化拆分，将PRD中的M1-M4扩展为M0-M8的完整模块体系
> - `UI-Design.md` 定义了前端页面和组件规范，与本文档的功能模块一一对应
> - 模块编号映射：PRD M1→模块划分 M2, PRD M2→M3, PRD M3→M4, PRD M4→M1

# AI 宠物健康助手 (AI Pet Health Assistant)

基于 LangChain 框架开发的 AI 宠物健康助手智能体项目，提供宠物健康咨询、疾病诊断、营养建议、智能购物等功能。

**项目完成度**: 99% 🎉 | **全部 9 个后端模块 + 8 个前端模块已完成**

## 🚀 项目简介

随着养宠人群增长，宠物主面临健康咨询、行为分析、选购决策、多宠管理等核心痛点。本项目旨在构建基于 LangChain v1.0+ 技术的 AI Agent，为宠物主提供智能化、个性化的健康助手服务。

## ✨ 核心功能

- 🏥 **健康咨询与症状分诊**：结合宠物档案的个性化健康建议
- 🐕 **情绪与行为分析**：分析宠物异常行为原因，提供训练建议
- 🛒 **智能购物决策助手**：基于健康状况的商品推荐
- 📋 **宠物档案管理**：多宠物场景下的精准上下文管理
- 📚 **知识库增强 (RAG)**：专业医疗知识检索与增强
- 🔧 **工具集成框架**：天气/地图/搜索/图像识别等15个外部工具
- 🔒 **数据安全与隐私**：AES加密/RBAC权限/审计日志/数据脱敏

## 🛠️ 技术栈

| 领域 | 技术 |
|------|------|
| **编排框架** | LangChain v1.0+ / LangGraph |
| **后端服务** | FastAPI + Starlette |
| **前端框架** | Next.js 14 + TypeScript |
| **数据库** | MySQL 8.0+ / SQLite (测试) |
| **ORM** | SQLAlchemy 2.0 |
| **向量库** | ChromaDB / Milvus |
| **LLM 引擎** | OpenAI GPT-4o / DeepSeek / 阿里云千问 |
| **认证** | JWT (python-jose) + bcrypt |
| **数据验证** | Pydantic v2 |
| **加密** | AES-256-GCM + PBKDF2-SHA256 |
| **审计存储** | MongoDB |

## 📦 项目结构

```
ai-pet-health/
├── animal/                     # 后端核心代码和文档
│   ├── docs/                   # 项目文档 (55+份)
│   ├── src/                    # 后端源代码
│   │   ├── api/                # API层
│   │   ├── core/               # 核心模块 (加密/RBAC/脱敏/审计)
│   │   ├── models/             # 数据模型
│   │   ├── schemas/            # Pydantic模式
│   │   └── db/                 # 数据库层
│   ├── tests/                  # 测试代码 (~420+用例)
│   └── scripts/                # 工具脚本
├── frontend/                   # 前端代码 (Next.js)
├── .trae/                      # Trae IDE 配置和技能
├── .venv/                      # Python 虚拟环境
├── requirements.txt            # Python 依赖
└── README.md                   # 项目说明
```

## 🚦 快速开始

### 1. 环境准备

```bash
# Python 3.12.10+ 已安装
python --version
```

### 2. 安装依赖

```bash
# 创建虚拟环境
python -m venv .venv

# 激活虚拟环境 (Windows PowerShell)
.venv\Scripts\Activate.ps1

# 安装依赖
pip install -r requirements.txt
```

### 3. 配置环境变量

```bash
# 复制环境变量示例文件
cp .env.example .env

# 编辑 .env 文件，填入你的 API 密钥
```

### 4. 启动开发服务器

```bash
# 方式一：使用启动脚本（推荐）
python scripts/dev_server.py

# 方式二：直接使用 uvicorn
uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
```

### 5. 访问 API 文档

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc
- 健康检查: http://localhost:8000/health

## 📋 已完成模块

### 后端模块 (9/9 完成)

| 模块 | 功能 | 代码量 | 测试数 | 质量 |
|------|------|--------|--------|------|
| M0 用户认证 | 注册/登录/JWT/OAuth2 | ~800行 | 15+ | 95/100 |
| M1 宠物档案 | CRUD/品种库/疫苗记录 | ~1200行 | 20+ | 96/100 |
| M8 Agent编排 | 多Agent协作/工具调用 | ~1500行 | 18+ | 94/100 |
| M2 健康咨询 | 症状分析/紧急度评估 | ~1800行 | 22+ | 93/100 |
| M3 行为分析 | 行为识别/训练建议 | ~1600行 | 25+ | 92/100 |
| M5 知识管理 | 文档加载/RAG检索 | ~4300行 | 30+ | 91/100 |
| M4 智能购物 | 搜索/推荐/成分分析 | ~1740行 | 118+ | 90/100 |
| M6 工具集成 | 15个外部工具/执行框架 | ~1200行 | ~110+ | 90/100 |
| M7 数据安全 | 加密/脱敏/RBAC/审计 | ~800行 | 47 | 92/100 |

### 前端模块 (8/8 完成)

| 模块 | 状态 | 说明 |
|------|------|------|
| FE-P0 | ✅ | 核心组件开发 |
| FE-P1 | ✅ | 功能页面开发 |
| FE-P2 | ✅ | 增强体验开发 |
| FE-INFRA | ✅ | 前端基础设施层 |
| FE-TEST | ✅ | 测试体系 (62+11 E2E) |
| FE-P0-OPT | ✅ | 前端性能优化 |
| FE-API | ✅ | 后端 API 对接 |
| REAL-TEST | ✅ | 真实环境联调 |

## 🔌 API 端点概览

| 模块 | 端点数 | 路径前缀 |
|------|--------|----------|
| 用户认证 | 5+ | /api/v1/auth |
| 用户管理 | 3+ | /api/v1/users |
| 宠物档案 | 5+ | /api/v1/pets |
| 健康咨询 | 5+ | /api/v1/health |
| 行为分析 | 3+ | /api/v1/behavior |
| 智能购物 | 9 | /api/v1/shopping |
| 知识管理 | 5+ | /api/v1/knowledge |
| 工具集成 | 3+ | /api/v1/tools |
| **数据安全** | **10** | **/api/v1/security** |
| **总计** | **50+** | - |

### 数据安全 API (新增)

| 方法 | 路径 | 功能 |
|------|------|------|
| POST | /security/encrypt | 加密数据 |
| POST | /security/decrypt | 解密数据 |
| POST | /security/mask | 数据脱敏预览 |
| GET | /security/roles | 列出角色 |
| GET | /security/permissions | 列出权限 |
| GET | /security/role/{name}/permissions | 角色权限 |
| GET | /security/audit/logs | 查询审计日志 |
| GET | /security/audit/security-events | 安全事件 |
| GET | /security/audit/user-activity/{id} | 用户活动 |
| GET | /security/overview | 安全概览 |

## 📚 项目文档

| 文档 | 说明 |
|------|------|
| [PRD.md](animal/docs/PRD.md) | 产品需求文档 |
| [Architecture-Detail.md](animal/docs/Architecture-Detail.md) | 精细化架构设计 |
| [模块划分与职责分配.md](animal/docs/模块划分与职责分配.md) | 功能模块划分 |
| [UI-Design.md](animal/docs/UI-Design.md) | 前端 UI 设计 |
| [技术设计文档_DEV009.md](animal/docs/技术设计文档_DEV009.md) | 数据安全模块设计 |
| [API接口文档_DEV007.md](animal/docs/API接口文档_DEV007.md) | 智能购物API文档 |
| [功能说明文档_DEV008.md](animal/docs/功能说明文档_DEV008.md) | 工具集成功能说明 |
| [项目整体进度报告_v9.0](项目整体进度报告_v9.0_20260418.md) | 项目进度报告 |
| [任务状态跟踪表_v9.0](任务状态跟踪表_v9.0_20260418.md) | 任务跟踪表 |
| [风险评估报告_v9.0](风险评估报告_v9.0_20260418.md) | 风险评估报告 |

## 🧪 测试

```bash
# 运行所有测试
python -m pytest tests/ -v

# 运行测试并查看覆盖率
python -m pytest tests/ -v --cov=src --cov-report=term-missing

# 生成 HTML 覆盖率报告
python -m pytest tests/ --cov=src --cov-report=html
```

**测试统计**: ~470+ 用例 | 通过率 100% | 后端 ~420+ | 前端 ~80

## 📊 项目数据总览

| 指标 | 数值 |
|------|------|
| **总体进度** | 99% |
| **后端模块** | 9/9 (100%) |
| **前端模块** | 8/8 (100%) |
| **总代码量** | ~25,340行 |
| **总测试用例** | ~470+ |
| **文档产出** | 55+份 |
| **API端点** | 50+个 |
| **注册工具数** | 15个 |
| **平均质量评分** | 92.6/100 |

## 🤝 贡献指南

欢迎贡献代码、报告问题或提出建议！

## 📄 许可证

本项目采用 MIT 许可证。

## 📞 联系方式

- GitHub Issues: 提交问题和反馈
- GitHub: https://github.com/djxjsn/ai-

---

**注意**: 本项目仍处于开发阶段，核心功能已全部完成，生产部署配置中。

*最后更新: 2026-04-18*

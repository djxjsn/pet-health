# AI 宠物健康助手

一个基于 LangChain 和 FastAPI 的智能宠物健康咨询平台，为宠物主人提供个性化的健康建议和医疗服务。

**项目完成度**: 99% 🎉

## 项目简介

本项目旨在构建一个 AI 驱动的宠物健康助手，能够：

- 🐾 **精准诊断**: 结合宠物档案的个性化健康建议
- 🛒 **智能购物**: 基于健康状况的商品推荐
- 🐕 **多宠管理**: 上下文感知的对话体验
- 📚 **知识增强**: RAG 技术提供的专业医疗知识支撑
- 🔧 **工具集成**: 15个外部工具（天气/地图/搜索/图像识别等）
- 🔒 **数据安全**: AES-256加密/RBAC权限/审计日志/数据脱敏

## 技术栈

### 后端
- **框架**: FastAPI + Starlette
- **数据库**: MySQL 8.0+ / SQLite (测试)
- **ORM**: SQLAlchemy 2.0
- **认证**: JWT (python-jose) + bcrypt
- **数据验证**: Pydantic v2
- **加密**: AES-256-GCM + PBKDF2-SHA256
- **审计存储**: MongoDB

### 前端
- React + TypeScript
- Next.js 14
- Ant Design

### AI 能力
- LangChain Agent
- LangGraph 任务流编排
- OpenAI GPT / DeepSeek
- RAG 知识库

## 项目结构

```
animal/
├── src/                      # 源代码
│   ├── main.py               # FastAPI 应用入口
│   ├── api/                  # API 层
│   │   ├── deps.py          # 依赖注入
│   │   └── v1/
│   │       ├── router.py    # 路由配置
│   │       └── endpoints/   # 端点实现
│   ├── core/                 # 核心模块
│   │   ├── config.py        # 配置管理
│   │   ├── database.py      # 数据库连接
│   │   ├── security.py      # JWT/密码哈希
│   │   ├── encryption.py    # AES-256-GCM加密服务
│   │   ├── data_masker.py   # 数据脱敏服务 (9种策略)
│   │   ├── rbac.py          # RBAC权限控制 (5角色+14权限)
│   │   └── audit.py         # 审计日志 (MongoDB不可变存储)
│   ├── models/              # 数据模型
│   ├── schemas/             # Pydantic 模式
│   └── db/                  # 数据库层
│       └── crud/           # CRUD 操作
├── tests/                    # 测试代码 (~420+用例)
├── scripts/                  # 工具脚本
│   └── dev_server.py       # 开发服务器启动
├── docs/                     # 项目文档 (55+份)
├── alembic/                  # 数据库迁移
├── .env                      # 环境变量
└── pyproject.toml           # 项目配置
```

## 快速开始

### 1. 环境要求

- Python 3.12+
- MySQL 8.0+ (生产环境)
- pip 或 conda

### 2. 安装依赖

```bash
# 克隆项目
git clone https://github.com/djxjsn/ai-.git
cd animal

# 创建虚拟环境
python -m venv .venv

# 激活虚拟环境
# Windows
.venv\Scripts\Activate.ps1

# 安装依赖
pip install -r requirements.txt
```

### 3. 配置环境变量

```bash
# 复制环境变量模板
cp .env.example .env

# 编辑 .env 文件，配置数据库和 API 密钥
```

### 4. 启动开发服务器

```bash
# 方式一：使用启动脚本（推荐）
python scripts/dev_server.py

# 方式二：直接使用 uvicorn
uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
```

### 5. 访问 API 文档

启动后访问以下地址：

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc
- 健康检查: http://localhost:8000/health

## 已完成功能

### M0 用户认证模块 ✅
- ✅ 用户注册（手机号/邮箱）
- ✅ 用户登录
- ✅ JWT 令牌认证
- ✅ 令牌刷新机制
- ✅ 密码重置（邮件待集成）
- ✅ 用户信息管理
- ✅ 单元测试（15+ 用例）

### M1 宠物档案模块 ✅
- ✅ 宠物 CRUD 操作
- ✅ 宠物健康档案
- ✅ 宠物关系管理
- ✅ 品种数据库
- ✅ 疫苗记录
- ✅ 照片管理

### M2 健康咨询模块 ✅
- ✅ 症状分析
- ✅ 紧急度评估
- ✅ LLM 诊断建议
- ✅ 健康记录管理

### M3 行为分析模块 ✅
- ✅ 行为识别
- ✅ 品种相关分析
- ✅ 训练建议生成

### M4 智能购物模块 ✅
- ✅ 商品搜索与过滤
- ✅ 智能推荐引擎
- ✅ 成分分析与过敏原检测
- ✅ 商品对比功能
- ✅ 购物行为追踪
- ✅ 109个测试用例

### M5 知识管理模块 (RAG) ✅
- ✅ 文档加载与分块
- ✅ 向量存储与检索
- ✅ 知识库管理
- ✅ RAG 增强问答

### M6 工具集成模块 ✅
- ✅ 天气查询工具
- ✅ 地图搜索工具
- ✅ 网络搜索工具
- ✅ 图像识别工具
- ✅ 知识增强工具
- ✅ 工具执行框架 (缓存/重试/并行/链式)
- ✅ 15个工具统一注册

### M7 数据安全与隐私模块 ✅
- ✅ AES-256-GCM 数据加密
- ✅ 9种数据脱敏策略
- ✅ RBAC 权限控制 (5角色+14权限)
- ✅ MongoDB 审计日志
- ✅ 10个安全管理API
- ✅ 47个测试用例

## API 文档

详细的 API 接口文档请查看 [API 接口文档](./docs/API%20接口文档.md)。

### 认证接口

| 方法 | 路径 | 说明 |
|------|------|------|
| POST | /api/v1/auth/register | 用户注册 |
| POST | /api/v1/auth/login | 用户登录 |
| POST | /api/v1/auth/refresh | 刷新令牌 |
| POST | /api/v1/auth/forgot-password | 忘记密码 |
| POST | /api/v1/auth/reset-password | 重置密码 |

### 用户接口

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | /api/v1/users/me | 获取当前用户信息 |
| PUT | /api/v1/users/me | 更新当前用户信息 |
| PUT | /api/v1/users/me/profile | 更新用户档案 |

### 数据安全接口 (新增)

| 方法 | 路径 | 说明 |
|------|------|------|
| POST | /api/v1/security/encrypt | 加密数据 |
| POST | /api/v1/security/decrypt | 解密数据 |
| POST | /api/v1/security/mask | 数据脱敏 |
| GET | /api/v1/security/roles | 列出角色 |
| GET | /api/v1/security/permissions | 列出权限 |
| GET | /api/v1/security/audit/logs | 查询审计日志 |

## 测试

```bash
# 运行所有测试
python -m pytest tests/ -v

# 运行测试并查看覆盖率
python -m pytest tests/ -v --cov=src --cov-report=term-missing

# 生成 HTML 覆盖率报告
python -m pytest tests/ --cov=src --cov-report=html
```

## 开发指南

### 代码规范

- 遵循 PEP 8 规范
- 使用类型注解
- 编写 docstring
- 单元测试覆盖率不低于 80%

### 分支管理

- `master`: 主分支，稳定版本
- `dev/xxx`: 开发分支

### 提交规范

```
feat: 新功能
fix: 修复 bug
docs: 文档更新
style: 代码格式
refactor: 重构
test: 测试相关
chore: 构建/工具
```

## 项目文档

- [需求文档 (PRD)](./docs/PRD.md)
- [架构设计文档](./docs/Architecture-Detail.md)
- [数据库设计文档](./docs/数据库设计文档.md)
- [API 接口文档](./docs/API%20接口文档.md)
- [技术设计文档_DEV009](./docs/技术设计文档_DEV009.md)
- [项目整体进度报告_v9.0](../../项目整体进度报告_v9.0_20260418.md)
- [任务状态跟踪表_v9.0](../../任务状态跟踪表_v9.0_20260418.md)
- [风险评估报告_v9.0](../../风险评估报告_v9.0_20260418.md)
- [面试项目知识文档](../../docs/面试项目知识文档/README.md)

## 项目进度

| 模块 | 状态 | 进度 |
|------|------|------|
| 项目管理 | ✅ 已完成 | 100% |
| 环境搭建 | ✅ 已完成 | 100% |
| 数据库设计 | ✅ 已完成 | 100% |
| M0 用户认证 | ✅ 已完成 | 100% |
| M1 宠物档案 | ✅ 已完成 | 100% |
| M2 健康咨询 | ✅ 已完成 | 100% |
| M3 行为分析 | ✅ 已完成 | 100% |
| M4 智能购物 | ✅ 已完成 | 100% |
| M5 知识管理(RAG) | ✅ 已完成 | 100% |
| M6 工具集成 | ✅ 已完成 | 100% |
| M7 数据安全 | ✅ 已完成 | 100% |
| 前端开发 | ✅ 已完成 | 100% |

**总体进度**: 约 99%

## 常见问题

### Q: 数据库连接失败？
A: 检查 `.env` 文件中的 `DATABASE_URL` 配置，确保 MySQL 服务正在运行，且密码正确。

### Q: 测试运行失败？
A: 确保已安装所有测试依赖：`pip install pytest pytest-cov`

### Q: API 文档无法访问？
A: 检查服务器是否正常启动，端口是否被占用。

## 许可证

MIT License

## 联系方式

- GitHub: https://github.com/djxjsn/ai-

## 致谢

- LangChain 团队
- FastAPI 社区
- 所有开源贡献者

---

*最后更新: 2026-04-18*

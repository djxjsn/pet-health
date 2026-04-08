# AI 宠物健康助手 (AI Pet Health Assistant)

基于 LangChain 框架开发的 AI 宠物健康助手智能体项目，提供宠物健康咨询、疾病诊断、营养建议等功能。

## 🚀 项目简介

随着养宠人群增长，宠物主面临健康咨询、行为分析、选购决策、多宠管理等核心痛点。本项目旨在构建基于 LangChain v1.0+ 技术的 AI Agent，为宠物主提供智能化、个性化的健康助手服务。

## ✨ 核心功能

- **健康咨询与症状分诊**：结合宠物档案的个性化健康建议
- **情绪与行为分析**：分析宠物异常行为原因，提供训练建议
- **智能购物决策助手**：基于健康状况的商品推荐
- **宠物档案管理**：多宠物场景下的精准上下文管理

## 🛠️ 技术栈

- **编排框架**：LangChain v1.0+
- **任务流**：LangGraph
- **后端服务**：FastAPI
- **前端框架**：Next.js 14 + TypeScript
- **数据库**：MySQL 8.0+
- **向量库**：ChromaDB / Milvus
- **LLM 引擎**：OpenAI GPT-4o / DeepSeek / 阿里云千问

## 📚 项目文档

| 文档 | 说明 |
|------|------|
| [PRD.md](animal/docs/PRD.md) | 产品需求文档 |
| [Architecture-Detail.md](animal/docs/Architecture-Detail.md) | 精细化架构设计 |
| [模块划分与职责分配.md](animal/docs/模块划分与职责分配.md) | 功能模块化划分 |
| [UI-Design.md](animal/docs/UI-Design.md) | 前端 UI 设计 |

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

## 📦 项目结构

```
ai-pet-health/
├── animal/                     # 项目核心代码和文档
│   ├── docs/                   # 项目文档
│   ├── app/                    # 后端代码
│   └── frontend/               # 前端代码
├── .trae/                      # Trae IDE 配置和技能
│   ├── skills/                 # 技能插件
│   └── specs/                  # 项目规范
├── .venv/                      # Python 虚拟环境
├── requirements.txt            # Python 依赖
└── README.md                   # 项目说明
```

## 📋 开发计划

- [x] 项目规划与文档编写
- [x] 环境搭建与依赖安装
- [x] 技能插件配置
- [ ] 核心功能开发
- [ ] 测试与优化
- [ ] 部署上线

## 🤝 贡献指南

欢迎贡献代码、报告问题或提出建议！

## 📄 许可证

本项目采用 MIT 许可证。

## 📞 联系方式

- GitHub Issues: 提交问题和反馈
- Email: your-email@example.com

---

**注意**：本项目仍处于开发阶段，部分功能尚未实现。

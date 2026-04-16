# Trae IDE MCP 工具安装指南

**创建日期**: 2026-04-16  
**适用项目**: AI 宠物健康助手  
**MCP 版本**: v1.0

---

## 📦 已安装的 MCP 工具

### 1. Plan / Workflow MCP ⭐ 最推荐

**功能**:
- ✅ 多步任务拆解
- ✅ 依赖调度管理
- ✅ 自动重试机制
- ✅ 回滚操作支持
- ✅ 状态持久化

**适合场景**:
- 复杂长流程 Agent 开发
- 自动开发流水线
- 批处理任务管理

**配置位置**: `.trae/mcp-settings.json` → `plan-workflow`

**使用命令**:
```bash
# 使用 uvx 运行（推荐）
uvx devgenius-mcp-client
```

**可用工具** (21 个 MCP Tools):
- **项目上下文**: get_project_context
- **里程碑管理**: list_project_milestones, get_milestone_detail
- **任务管理**: get_task_detail, get_my_tasks, claim_task, update_task_status, release_task_lock, split_task_into_subtasks
- **子任务管理**: get_task_subtasks, update_subtask_status, delete_subtask
- **文档管理**: get_document_categories, create_document_category, list_documents, get_document_by_title, search_documents, create_document, update_document, delete_document, get_document_versions

---

### 2. Memory / Vector DB MCP

**功能**:
- ✅ 长期记忆存储
- ✅ 向量检索
- ✅ 上下文总结
- ✅ 历史关联查询

**适合场景**:
- RAG 类 Agent 开发
- 知识库问答系统
- 代码上下文记忆

**配置位置**: `.trae/mcp-settings.json` → `memory-vector`

**使用命令**:
```bash
# 使用 npx 运行
npx -y @modelcontextprotocol/server-memory
```

**环境变量**:
- `MEMORY_FILE_PATH`: 记忆文件存储路径（默认：./.trae/memory.json）

---

### 3. Skill / Function Hub MCP

**功能**:
- ✅ 统一管理工具集
- ✅ 权限控制
- ✅ 参数校验
- ✅ 调用日志记录

**适合场景**:
- 多工具组合 Agent
- 动态技能扩展
- 安全管控需求

**配置位置**: `.trae/mcp-settings.json` → `skill-hub`

**使用命令**:
```bash
# 使用 npx 运行
npx -y @modelcontextprotocol/server-filesystem
```

**环境变量**:
- `ALLOWED_DIRECTORIES`: 允许访问的目录（默认：./skills,./tools）

---

## 🔧 安装步骤

### 前置要求

1. **Node.js 和 npm** (用于 npx 命令)
   ```powershell
   # 检查是否已安装
   node --version
   npm --version
   
   # 如未安装，访问 https://nodejs.org/ 下载安装
   ```

2. **uv 工具** (用于 uvx 命令，Plan MCP 需要)
   ```powershell
   # Windows PowerShell 安装 uv
   irm https://astral.sh/uv/install.ps1 | iex
   
   # 验证安装
   uv --version
   ```

### 步骤 1: 配置文件已创建

MCP 配置文件已创建在：
```
e:\学习\trae project\pei health agent\.trae\mcp-settings.json
```

### 步骤 2: 在 Trae IDE 中配置 MCP

1. **打开 Trae IDE**
   - 打开项目：`e:\学习\trae project\pei health agent`

2. **进入 MCP 设置**
   - 左侧导航栏选择 **MCP**
   - 点击 **添加** > **手动添加**

3. **导入配置**
   - 复制 `.trae/mcp-settings.json` 中的配置内容
   - 粘贴到 Trae MCP 设置窗口
   - 或者手动添加每个 MCP Server

### 步骤 3: 验证安装

**Plan / Workflow MCP 验证**:
```bash
# 测试运行
uvx devgenius-mcp-client --help
```

**Memory / Vector DB MCP 验证**:
```bash
# 测试运行
npx -y @modelcontextprotocol/server-memory --help
```

**Skill / Function Hub MCP 验证**:
```bash
# 测试运行
npx -y @modelcontextprotocol/server-filesystem --help
```

---

## 📁 目录结构

```
pei health agent/
├── .trae/
│   ├── mcp-settings.json          # MCP 配置文件（已创建）
│   ├── memory.json                # 记忆存储文件（运行时自动创建）
│   ├── rules/                     # 规则文件目录
│   └── skills/                    # 技能文件目录
└── ...
```

---

## 🚀 使用方法

### 在 Trae AI Agent 中使用 MCP 工具

#### 1. Plan / Workflow MCP 使用示例

**任务拆解**:
```
请帮我拆解这个任务：实现用户注册功能
- 需要创建用户模型
- 实现注册 API 端点
- 添加单元测试
- 编写 API 文档
```

**查询我的任务**:
```
查看我当前的任务列表
```

**更新任务状态**:
```
将任务 "用户注册 API 开发" 状态更新为 "已完成"
```

#### 2. Memory / Vector DB MCP 使用示例

**存储记忆**:
```
记住这个设计模式：我们使用 Repository 模式来封装数据库操作
```

**检索相关记忆**:
```
查找之前关于用户认证的讨论
```

**上下文总结**:
```
总结这个项目中使用的所有设计模式
```

#### 3. Skill / Function Hub MCP 使用示例

**列出可用技能**:
```
显示当前项目中可用的所有技能和工具
```

**调用技能**:
```
使用代码审查技能检查最新的提交
```

**添加新技能**:
```
创建一个新的技能来自动生成 API 文档
```

---

## ⚙️ 环境变量配置

### Plan / Workflow MCP 环境变量

在 `.trae/mcp-settings.json` 中配置：

```json
{
  "DEVGENIUS_MCP_TOKEN": "mcp_your_token_here",
  "DEVGENIUS_API_URL": "http://localhost:8000/api/v1/mcp",
  "DEVGENIUS_IDE_TYPE": "trae",
  "DEVGENIUS_PROJECT_PATH": "e:\\学习\\trae project\\pei health agent",
  "DEVGENIUS_AUTO_WRITE_RULES": "true"
}
```

**获取 Token**:
- 访问 DevGenius 平台注册账号
- 在个人设置中生成 MCP Token
- 替换配置文件中的 `mcp_your_token_here`

### Memory / Vector DB MCP 环境变量

```json
{
  "MEMORY_FILE_PATH": "./.trae/memory.json"
}
```

### Skill / Function Hub MCP 环境变量

```json
{
  "ALLOWED_DIRECTORIES": "./skills,./tools,./src"
}
```

---

## 🔍 故障排查

### 问题 1: MCP Server 无法启动

**可能原因**:
- Node.js 未安装或版本过低
- uv 工具未安装
- 网络连接问题

**解决方案**:
```powershell
# 检查 Node.js 版本
node --version  # 应该 >= 16.x

# 检查 uv 是否安装
uv --version

# 重新安装依赖
npm install -g @modelcontextprotocol/server-memory
npm install -g @modelcontextprotocol/server-filesystem
```

### 问题 2: Plan MCP Token 错误

**解决方案**:
1. 检查 `.trae/mcp-settings.json` 中的 `DEVGENIUS_MCP_TOKEN`
2. 确保 Token 格式正确（以 `mcp_` 开头）
3. 验证 DevGenius 后端服务是否运行

### 问题 3: Memory MCP 无法写入记忆

**解决方案**:
1. 检查 `.trae/memory.json` 文件权限
2. 确保目录存在：`mkdir .trae`
3. 检查磁盘空间

### 问题 4: Skill Hub 无法访问某些目录

**解决方案**:
1. 在 `ALLOWED_DIRECTORIES` 中添加需要访问的目录
2. 使用绝对路径而不是相对路径
3. 检查目录权限

---

## 📚 进阶使用

### 组合使用多个 MCP

**场景**: 开发一个新功能

1. **使用 Plan MCP 拆解任务**:
   ```
   帮我规划实现宠物健康咨询功能的任务列表
   ```

2. **使用 Memory MCP 检索相关知识**:
   ```
   查找之前关于健康咨询模块的设计讨论
   ```

3. **使用 Skill Hub 调用代码生成技能**:
   ```
   使用 FastAPI 代码生成技能创建健康咨询 API 端点
   ```

### 自动化工作流

**示例**: 自动代码审查流程

```
1. Plan MCP 创建代码审查任务
2. Skill Hub 调用代码审查技能
3. Memory MCP 存储审查结果
4. Plan MCP 更新任务状态为已完成
```

---

## 🎯 最佳实践

### 1. 任务管理最佳实践

- ✅ 使用 Plan MCP 拆解所有复杂任务
- ✅ 为每个任务设置明确的验收标准
- ✅ 及时更新任务状态
- ✅ 使用子任务管理细化工作

### 2. 记忆管理最佳实践

- ✅ 定期总结重要决策和设计模式
- ✅ 使用标签分类记忆内容
- ✅ 定期清理过期记忆
- ✅ 为关键讨论创建永久记忆

### 3. 技能管理最佳实践

- ✅ 为常用操作创建技能
- ✅ 技能命名清晰易懂
- ✅ 记录技能使用日志
- ✅ 定期审查和更新技能

---

## 📖 参考资源

### 官方文档

- [Trae MCP 文档](https://docs.trae.ai/ide/add-mcp-servers)
- [DevGenius MCP Client](https://pypi.org/project/devgenius-mcp-client/)
- [Model Context Protocol](https://modelcontextprotocol.io/)

### 社区资源

- [MCP Servers 集合](https://github.com/modelcontextprotocol/servers)
- [DevGenius 文档](https://devgenius.ai/docs)

---

## 🆘 获取帮助

如遇到问题：

1. 查看本文档的故障排查部分
2. 检查 MCP Server 日志
3. 查看 Trae IDE 的错误提示
4. 联系项目管理员

---

**文档版本**: v1.0  
**最后更新**: 2026-04-16  
**维护者**: AI 宠物健康助手项目组

# MCP 配置文件使用说明

**重要提示**: Trae IDE 一次只能添加一个 MCP Server，因此我们将三个 MCP 的配置分成了独立的文件。

---

## 📁 配置文件清单

| 序号 | 文件名 | MCP 名称 | 功能描述 |
|------|--------|---------|---------|
| 1 | `mcp-settings-01-plan.json` | Plan / Workflow MCP | 多步任务拆解、依赖调度、重试、回滚 |
| 2 | `mcp-settings-02-memory.json` | Memory / Vector DB MCP | 长期记忆、向量检索、上下文总结 |
| 3 | `mcp-settings-03-skill.json` | Skill / Function Hub MCP | 统一管理工具集、权限、参数校验 |

---

## 🚀 配置步骤

### 步骤 1: 打开 Trae MCP 设置

1. 启动 Trae IDE
2. 打开项目：`e:\学习\trae project\pei health agent`
3. 点击左侧导航栏的 **MCP** 图标
4. 点击右上角的 **添加** > **手动添加**

### 步骤 2: 依次导入三个配置文件

#### 2.1 导入 Plan / Workflow MCP

1. 打开文件：`.trae/mcp-settings-01-plan.json`
2. 全选并复制所有内容 (Ctrl+A, Ctrl+C)
3. 粘贴到 Trae MCP 配置窗口
4. 点击 "保存"

⚠️ **重要**: 配置 Plan MCP 后需要修改 Token：
```json
{
  "DEVGENIUS_MCP_TOKEN": "mcp_你的实际 Token"
}
```

#### 2.2 导入 Memory / Vector DB MCP

1. **再次点击**右上角 "添加" 按钮
2. 打开文件：`.trae/mcp-settings-02-memory.json`
3. 全选并复制所有内容
4. 粘贴到 Trae MCP 配置窗口
5. 点击 "保存"

#### 2.3 导入 Skill / Function Hub MCP

1. **再次点击**右上角 "添加" 按钮
2. 打开文件：`.trae/mcp-settings-03-skill.json`
3. 全选并复制所有内容
4. 粘贴到 Trae MCP 配置窗口
5. 点击 "保存"

### 步骤 3: 启用所有 MCP Server

在 MCP 设置面板中，确保三个 MCP Server 都已启用：
- ✅ plan-workflow
- ✅ memory-vector
- ✅ skill-hub

---

## 📋 配置文件内容

### 1. Plan / Workflow MCP 配置

**文件**: `mcp-settings-01-plan.json`

```json
{
  "mcpServers": {
    "plan-workflow": {
      "command": "uvx",
      "args": ["--from", "devgenius-mcp-client", "devgenius-mcp"],
      "env": {
        "DEVGENIUS_MCP_TOKEN": "mcp_your_token_here",
        "DEVGENIUS_API_URL": "http://localhost:8000/api/v1/mcp",
        "DEVGENIUS_IDE_TYPE": "trae",
        "DEVGENIUS_PROJECT_PATH": "e:\\学习\\trae project\\pei health agent",
        "DEVGENIUS_AUTO_WRITE_RULES": "true"
      },
      "description": "Plan / Workflow MCP - 多步任务拆解、依赖调度、重试、回滚、状态持久化 (21 个工具)",
      "enabled": true
    }
  }
}
```

**可用工具** (21 个):
- get_project_context
- list_project_milestones, get_milestone_detail
- get_task_detail, get_my_tasks, claim_task, update_task_status, release_task_lock, split_task_into_subtasks
- get_task_subtasks, update_subtask_status, delete_subtask
- get_document_categories, create_document_category, list_documents, get_document_by_title, search_documents, create_document, update_document, delete_document, get_document_versions

### 2. Memory / Vector DB MCP 配置

**文件**: `mcp-settings-02-memory.json`

```json
{
  "mcpServers": {
    "memory-vector": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-memory"],
      "env": {
        "MEMORY_FILE_PATH": "./.trae/memory.json"
      },
      "description": "Memory / Vector DB MCP - 长期记忆、向量检索、上下文总结、历史关联",
      "enabled": true
    }
  }
}
```

### 3. Skill / Function Hub MCP 配置

**文件**: `mcp-settings-03-skill.json`

```json
{
  "mcpServers": {
    "skill-hub": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-filesystem", "./skills"],
      "env": {},
      "description": "Skill / Function Hub MCP - 统一管理工具集、权限、参数校验、调用日志",
      "enabled": true
    }
  }
}
```

---

## ⚠️ 注意事项

### 1. Plan MCP Token 配置

Plan / Workflow MCP **必须配置有效的 Token** 才能使用：

1. 访问 DevGenius 平台注册账号
2. 在个人设置中生成 MCP Token
3. 编辑 `mcp-settings-01-plan.json`
4. 替换 `DEVGENIUS_MCP_TOKEN` 为你的实际 Token
5. 保存并重启 Trae IDE

### 2. 导入顺序

建议按以下顺序导入：
1. **先导入** Plan / Workflow MCP (最重要)
2. **再导入** Memory / Vector DB MCP
3. **最后导入** Skill / Function Hub MCP

### 3. 网络连接

Memory MCP 和 Skill Hub MCP 首次运行时需要下载包：
- 确保网络连接正常
- 如下载缓慢，配置 npm 镜像：
  ```powershell
  npm config set registry https://registry.npmmirror.com
  ```

---

## ✅ 验收清单

- [ ] Trae IDE 已打开项目
- [ ] MCP 设置面板已打开
- [ ] 已导入 `mcp-settings-01-plan.json`
- [ ] 已导入 `mcp-settings-02-memory.json`
- [ ] 已导入 `mcp-settings-03-skill.json`
- [ ] Plan MCP Token 已配置
- [ ] 三个 MCP Server 都已启用
- [ ] 测试命令可以正常响应

---

## 🧪 测试 MCP

在 Trae AI 对话框中测试：

**测试 Plan MCP**:
```
查看我的任务列表
```

**测试 Memory MCP**:
```
记住这个项目使用 FastAPI 框架
```

**测试 Skill Hub MCP**:
```
列出 skills 目录中的文件
```

---

## 📚 更多资源

- **快速开始**: `快速开始.md` (5 分钟上手)
- **详细指南**: `MCP 安装指南.md` (完整文档)
- **安装报告**: `MCP 安装完成报告.md` (验收清单)
- **官方文档**: https://docs.trae.ai/ide/add-mcp-servers

---

**文档版本**: v1.0  
**更新日期**: 2026-04-16

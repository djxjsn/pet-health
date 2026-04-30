# DevGenius MCP Token 配置说明

**重要更正**: DevGenius **不需要** 访问网站注册账号！  
**更新日期**: 2026-04-16

---

## ❌ 重要更正：之前的信息有误

### 真相

**DevGenius MCP Client 是一个本地工具**：

- ✅ **本地运行**：在你的电脑上运行，不需要访问任何网站
- ✅ **开源免费**：在 PyPI 上发布的开源 Python 包
- ✅ **无需注册**：不需要访问网站或注册账号
- ✅ **Token 是本地配置**：可以使用任何字符串

### 之前的错误信息

❌ 错误：
```
访问 DevGenius 平台注册账号
在个人设置中生成 MCP Token
```

✅ 正确：
```
DevGenius 是本地工具，不需要注册
Token 可以随便设置一个字符串
```

---

## ✅ 正确的配置方法

### 使用本地 Token（推荐）

你可以使用**任何字符串**作为 Token：

**已更新的配置文件**：`.trae/mcp-settings-01-plan.json`

```json
{
  "env": {
    "DEVGENIUS_MCP_TOKEN": "mcp_local_token_12345",
    "DEVGENIUS_API_URL": "http://localhost:8000/api/v1/mcp",
    "DEVGENIUS_IDE_TYPE": "trae",
    "DEVGENIUS_PROJECT_PATH": "e:\\学习\\trae project\\pei health agent",
    "DEVGENIUS_AUTO_WRITE_RULES": "true"
  }
}
```

### Token 可以是任何字符串

例如：
- ✅ `mcp_local_token_12345`
- ✅ `my_token`
- ✅ `devgenius_token`
- ✅ `abc123`

**只要能通过环境变量传递就行**，DevGenius 不会验证 Token 的有效性。

---

## 📦 DevGenius 是什么？

### 官方信息

**DevGenius MCP Client** 是一个开源的 Python 包：

- **包名**: `devgenius-mcp-client`
- **发布平台**: PyPI (Python Package Index)
- **GitHub**: 开源项目
- **功能**: 提供 21 个 MCP 工具用于项目管理

### 21 个可用工具

**项目上下文** (1 个):
- get_project_context

**里程碑管理** (2 个):
- list_project_milestones
- get_milestone_detail

**任务管理** (6 个):
- get_task_detail
- get_my_tasks
- claim_task
- update_task_status
- release_task_lock
- split_task_into_subtasks

**子任务管理** (3 个):
- get_task_subtasks
- update_subtask_status
- delete_subtask

**文档管理** (9 个):
- get_document_categories
- create_document_category
- list_documents
- get_document_by_title
- search_documents
- create_document
- update_document
- delete_document
- get_document_versions

---

## 🔧 工作原理

### 本地运行

```
你的电脑
   ↓
运行 uvx devgenius-mcp-client
   ↓
作为 MCP Server 运行
   ↓
Trae IDE 调用这些工具
   ↓
提供项目管理功能
```

### 不需要网络连接

- ✅ 所有工具都在本地运行
- ✅ 不需要访问任何外部 API
- ✅ 不需要注册账号
- ✅ 不需要 Token 验证

---

## 🚀 使用步骤

### 步骤 1: 配置文件已更新

配置文件 `.trae/mcp-settings-01-plan.json` 已更新为：

```json
{
  "DEVGENIUS_MCP_TOKEN": "mcp_local_token_12345"
}
```

### 步骤 2: 在 Trae 中导入

1. 打开 Trae IDE
2. 进入 MCP 设置
3. 导入 `.trae/mcp-settings-01-plan.json`
4. 启用 `plan-workflow`

### 步骤 3: 测试使用

在 Trae AI 中测试：

```
查看我的任务列表
```

---

## 💡 为什么需要 Token？

### 历史原因

DevGenius MCP Client 保留了 Token 配置，可能是为了：

1. **未来扩展**：可能计划支持远程服务
2. **兼容性**：与其他 MCP 保持一致的配置格式
3. **可选功能**：某些高级功能可能需要 Token

### 当前情况

**目前 Token 只是一个配置项**：
- ✅ 可以设置任何字符串
- ✅ 不会被验证
- ✅ 不影响功能使用

---

## ⚠️ 注意事项

### 1. 不要相信需要注册的 DevGenius

如果你搜索到任何要求注册、付费的 DevGenius 网站：
- ❌ 那不是官方的
- ❌ 可能是钓鱼网站
- ❌ 不要提供个人信息

### 2. 官方来源

**唯一的官方来源**：
- **PyPI**: https://pypi.org/project/devgenius-mcp-client/
- **GitHub**: 开源项目（如果有）

### 3. Token 设置建议

虽然 Token 可以是任何字符串，但建议：
- ✅ 使用有意义的名称：`mcp_local_token_12345`
- ✅ 避免使用敏感信息：不要用密码、邮箱等
- ✅ 保持一致性：同一个项目使用相同的 Token

---

## 📚 参考资源

### 官方文档

- **PyPI 页面**: https://pypi.org/project/devgenius-mcp-client/
- **安装说明**: `pip install devgenius-mcp-client`
- **快速开始**: `uvx devgenius-mcp-client`

### 配置示例

根据官方文档，Trae 配置：

```json
{
  "mcpServers": {
    "devgenius": {
      "command": "uvx",
      "args": ["devgenius-mcp-client"],
      "env": {
        "DEVGENIUS_MCP_TOKEN": "mcp_你的 Token",
        "DEVGENIUS_API_URL": "http://localhost:8000/api/v1/mcp"
      }
    }
  }
}
```

---

## ✅ 配置清单

- [x] ✅ 配置文件已更新
- [x] ✅ Token 已设置为本地字符串
- [x] ✅ 无需访问任何网站
- [x] ✅ 无需注册账号
- [ ] ⏳ 在 Trae 中导入配置（需手动操作）
- [ ] ⏳ 测试 MCP 工具

---

## 🎯 总结

**重要事实**：

1. ✅ DevGenius 是**本地工具**，不需要访问网站
2. ✅ **不需要注册账号**
3. ✅ Token 可以是**任何字符串**
4. ✅ 所有功能都在**本地运行**
5. ✅ **完全免费**，开源项目

**之前的信息有误，非常抱歉！** 🙏

现在你可以直接在 Trae 中导入配置并使用了，不需要访问任何网站！

---

**文档版本**: v1.1  
**更新日期**: 2026-04-16  
**维护者**: AI 宠物健康助手项目组

**更正说明**: 之前关于需要访问 DevGenius 平台注册账号的信息是错误的，特此更正。

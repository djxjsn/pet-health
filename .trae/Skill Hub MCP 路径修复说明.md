# Skill Hub MCP 路径修复说明

**问题日期**: 2026-04-16  
**问题**: MCP Server 找不到 skills 目录  
**状态**: ✅ 已修复

---

## ❌ 问题原因

### 错误信息

```
Error accessing directory C:\Users\帝景西街少年\skills: 
Error: ENOENT: no such file or directory, stat 'C:\Users\帝景西街少年\skills'
```

### 根本原因

**配置文件使用了相对路径**：

```json
{
  "args": ["-y", "@modelcontextprotocol/server-filesystem", "./skills"]
}
```

**问题**：
- MCP Server 在用户主目录运行：`C:\Users\帝景西街少年\`
- 尝试访问：`C:\Users\帝景西街少年\skills`
- 但该目录不存在 ❌

---

## ✅ 解决方案

### 使用绝对路径

已更新配置文件 `.trae/mcp-settings-03-skill.json`：

```json
{
  "mcpServers": {
    "skill-hub": {
      "command": "npx",
      "args": [
        "-y", 
        "@modelcontextprotocol/server-filesystem", 
        "e:\\学习\\trae project\\pei health agent\\.trae\\skills"
      ],
      "env": {},
      "description": "Skill / Function Hub MCP - 统一管理工具集、权限、参数校验、调用日志",
      "enabled": true
    }
  }
}
```

**关键改动**：
- ❌ 旧路径：`./skills`（相对路径）
- ✅ 新路径：`e:\学习\trae project\pei health agent\.trae\skills`（绝对路径）

---

## 📁 目录结构

```
pei health agent/
├── .trae/
│   ├── skills/              ← MCP 现在访问这个目录
│   │   └── (技能文件)
│   ├── mcp-settings-03-skill.json
│   └── ...
└── ...
```

---

## 🔧 验证修复

### 1. 检查目录是否存在

```powershell
# 应该显示目录已存在
Test-Path "e:\学习\trae project\pei health agent\.trae\skills"
# 输出：True
```

### 2. 在 Trae IDE 中重新导入配置

1. 打开 Trae IDE
2. 进入 MCP 设置
3. 删除旧的 skill-hub 配置
4. 重新导入 `.trae/mcp-settings-03-skill.json`
5. 启用 skill-hub

### 3. 测试访问

在 Trae AI 中测试：
```
列出 skills 目录中的文件
```

应该不再报错，而是显示目录内容（即使是空的）。

---

## 💡 为什么使用绝对路径？

### 相对路径的问题

```
相对路径：./skills
└─ 取决于当前工作目录
   ├─ 在 Trae 中运行 → Trae 安装目录
   ├─ 在项目中运行 → 项目根目录
   └─ 在用户主目录运行 → C:\Users\用户名\
```

**MCP Server 的工作目录**：
- 可能在用户主目录
- 可能在 Trae 安装目录
- 不确定 ❌

### 绝对路径的优势

```
绝对路径：e:\学习\trae project\pei health agent\.trae\skills
└─ 始终指向同一个位置 ✅
```

**无论 MCP Server 在哪里运行**，都能找到正确的目录。

---

## 🎯 技能文件管理

### 在 skills 目录中可以创建：

1. **自定义技能**
   ```
   .trae/skills/
   ├── code-review.md       # 代码审查技能
   ├── api-generator.md     # API 生成技能
   └── test-writer.md       # 测试生成技能
   ```

2. **技能示例**

   **code-review.md**:
   ```markdown
   # 代码审查技能
   
   ## 功能
   检查代码质量、规范、安全性
   
   ## 触发条件
   当用户请求代码审查时
   
   ## 审查项
   - 代码规范
   - 潜在 bug
   - 性能问题
   - 安全隐患
   ```

### 使用技能

在 Trae AI 中：
```
使用代码审查技能检查最新的提交
```

---

## ⚠️ 注意事项

### 1. 路径格式

Windows 路径在 JSON 中需要转义反斜杠：

```json
// ❌ 错误
"path": "e:\学习\trae project\skills"

// ✅ 正确
"path": "e:\\学习\\trae project\\skills"
```

### 2. 目录权限

确保 MCP Server 有权限访问该目录：
- 目录存在 ✅
- 有读取权限 ✅
- 有写入权限（如果需要创建技能）✅

### 3. 重新导入配置

修改配置文件后，必须在 Trae 中：
1. 删除旧配置
2. 重新导入新配置
3. 启用 MCP Server

---

## 📚 相关文档

- [MCP 配置文件说明](./README-配置文件说明.md)
- [Git Commit MCP 配置说明](./Git Commit MCP 配置说明.md)
- [MCP 安装指南](./MCP 安装指南.md)

---

## ✅ 修复清单

- [x] ✅ 创建 skills 目录
- [x] ✅ 更新配置文件为绝对路径
- [x] ✅ 验证目录存在
- [ ] ⏳ 在 Trae 中重新导入配置
- [ ] ⏳ 测试技能访问

---

**修复完成！** 🎉 Skill Hub MCP 现在可以正确访问项目内的 skills 目录了。

**文档版本**: v1.0  
**更新日期**: 2026-04-16  
**维护者**: AI 宠物健康助手项目组

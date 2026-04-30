# Git Commit MCP 工具安装指南

**工具名称**: Git Commit Generator MCP  
**包名**: `git-commit-mcp`  
**功能**: 智能分析代码变更并自动生成规范的提交信息  
**安装日期**: 2026-04-16

---

## 📦 工具介绍

### 主要功能

- ✅ **智能分析 Git Diff**: 自动分析暂存区的代码变更
- ✅ **生成规范提交信息**: 根据变更内容生成 Conventional Commits 格式的提交信息
- ✅ **支持多种提交类型**: feat, fix, docs, style, refactor, test, chore 等
- ✅ **自动识别影响范围**: 识别受影响的模块和文件
- ✅ **生成提交摘要**: 提供清晰的变更说明

### 工作原理

1. 读取 Git 暂存区的变更
2. 分析代码 diff 内容
3. 使用 AI 生成符合规范的提交信息
4. 返回给 MCP 客户端（Trae IDE）

---

## 🚀 安装步骤

### 步骤 1: 确认前置依赖

确保已安装：
- ✅ Node.js 和 npm
- ✅ Git 已配置
- ✅ 项目已初始化 Git 仓库

### 步骤 2: 配置 Git 用户信息（重要）

编辑配置文件 `.trae/mcp-settings-04-git-commit.json`，替换为你的 Git 信息：

```json
{
  "env": {
    "GIT_AUTHOR_NAME": "你的名字",
    "GIT_AUTHOR_EMAIL": "your-email@example.com",
    "GIT_COMMITTER_NAME": "你的名字",
    "GIT_COMMITTER_EMAIL": "your-email@example.com"
  }
}
```

**或者** 在全局配置 Git：

```bash
git config --global user.name "你的名字"
git config --global user.email "your-email@example.com"
```

### 步骤 3: 在 Trae IDE 中导入配置

1. **打开 Trae IDE**
   - 打开项目：`e:\学习\trae project\pei health agent`

2. **进入 MCP 设置**
   - 点击左侧导航栏的 **MCP** 图标
   - 点击右上角的 **添加** 按钮

3. **导入配置**
   - 打开文件：`.trae/mcp-settings-04-git-commit.json`
   - 全选并复制所有内容 (Ctrl+A, Ctrl+C)
   - 粘贴到 Trae MCP 配置窗口
   - 点击 "保存"

4. **启用 MCP Server**
   - 确保 `git-commit-mcp` 已启用 ✅

---

## 💡 使用方法

### 在 Trae AI 中使用

#### 场景 1: 分析变更并生成提交信息

```
请分析当前的代码变更，生成一个提交信息
```

#### 场景 2: 生成特定格式的提交

```
帮我生成一个 conventional commits 格式的提交信息
```

#### 场景 3: 查看变更摘要

```
查看我暂存了哪些变更，并建议提交信息
```

### 配合 Git 命令行使用

#### 完整提交流程

```bash
# 1. 添加变更到暂存区
git add .

# 2. 在 Trae AI 中请求生成提交信息
# 输入："请分析当前变更并生成提交信息"

# 3. 复制 AI 生成的提交信息

# 4. 执行提交
git commit -m "feat: 添加用户认证模块

- 实现用户注册 API
- 实现用户登录 API
- 添加 JWT 令牌认证
- 包含单元测试"
```

#### 使用 Git Hook 自动提交（高级）

可以配置 Git commit-msg hook，在提交时自动调用 MCP 生成信息。

---

## 📋 提交信息规范

生成的提交信息遵循 **Conventional Commits** 规范：

### 提交类型

| 类型 | 说明 | 示例 |
|------|------|------|
| `feat` | 新功能 | `feat: 添加用户注册功能` |
| `fix` | 修复 bug | `fix: 修复登录验证逻辑` |
| `docs` | 文档更新 | `docs: 更新 API 文档` |
| `style` | 代码格式 | `style: 格式化代码` |
| `refactor` | 代码重构 | `refactor: 优化数据库连接` |
| `test` | 测试相关 | `test: 添加单元测试` |
| `chore` | 构建/工具 | `chore: 更新依赖版本` |
| `perf` | 性能优化 | `perf: 优化查询性能` |
| `ci` | CI 配置 | `ci: 添加 GitHub Actions` |

### 提交格式

```
<type>: <subject>

<body>

<footer>
```

**示例**:

```
feat: 添加 MCP 工具集成

- 安装 Plan/Workflow MCP
- 安装 Memory/Vector DB MCP
- 安装 Skill/Function Hub MCP
- 添加配置文档和使用指南

Closes #123
```

---

## 🔧 配置选项

### 环境变量说明

| 变量名 | 说明 | 示例 |
|--------|------|------|
| `GIT_AUTHOR_NAME` | 提交者姓名 | `张三` |
| `GIT_AUTHOR_EMAIL` | 提交者邮箱 | `zhang@example.com` |
| `GIT_COMMITTER_NAME` | 提交者姓名 | `张三` |
| `GIT_COMMITTER_EMAIL` | 提交者邮箱 | `zhang@example.com` |

### 自定义提交模板

可以配置提交信息的默认模板（需要 git-commit-mcp 支持）。

---

## ⚠️ 注意事项

### 1. Git 配置

确保 Git 已正确配置：

```bash
# 检查 Git 配置
git config user.name
git config user.email

# 如未配置，执行：
git config --global user.name "你的名字"
git config --global user.email "your-email@example.com"
```

### 2. 暂存区要求

Git Commit MCP 只能分析**已暂存**的变更：

```bash
# 必须先执行 git add
git add .

# 然后才能生成提交信息
```

### 3. 网络连接

首次运行时需要下载 npm 包：

```bash
# 如下载缓慢，配置 npm 镜像
npm config set registry https://registry.npmmirror.com
```

### 4. 提交信息审核

AI 生成的提交信息仅供参考，建议：
- ✅ 检查提交类型是否正确
- ✅ 确认变更描述是否准确
- ✅ 补充必要的上下文信息

---

## 🧪 测试安装

### 测试步骤

1. **修改一个文件**
   ```bash
   # 创建一个测试文件
   echo "test" > test.txt
   ```

2. **添加到暂存区**
   ```bash
   git add test.txt
   ```

3. **在 Trae AI 中测试**
   ```
   请分析当前的代码变更，生成一个提交信息
   ```

4. **验证结果**
   - 应该看到类似：`chore: 添加测试文件 test.txt`
   - 包含变更说明

---

## 🔍 故障排查

### 问题 1: MCP Server 无法启动

**错误信息**: `command not found: git-commit-mcp`

**解决方案**:
```bash
# 全局安装
npm install -g git-commit-mcp

# 或者使用 npx（推荐）
npx git-commit-mcp
```

### 问题 2: Git 配置缺失

**错误信息**: `Please tell me who you are`

**解决方案**:
```bash
git config --global user.name "你的名字"
git config --global user.email "your-email@example.com"
```

### 问题 3: 无法分析变更

**可能原因**: 暂存区为空

**解决方案**:
```bash
# 先添加变更到暂存区
git add .

# 查看暂存区状态
git status
```

### 问题 4: 生成的提交信息不准确

**解决方案**:
- 手动修改提交信息
- 提供更详细的上下文
- 在 Trae AI 中补充说明：`请只关注 src 目录的变更`

---

## 📚 参考资源

### 官方文档

- [git-commit-mcp npm](https://www.npmjs.com/package/git-commit-mcp)
- [Conventional Commits 规范](https://www.conventionalcommits.org/)
- [Model Context Protocol](https://modelcontextprotocol.io/)

### 相关工具

- **git-mcp-server**: 更全面的 Git MCP 工具
- **@cyanheads/git-mcp-server**: 另一个 Git MCP 实现

---

## ✅ 验收清单

- [ ] Node.js 和 npm 已安装
- [ ] Git 已配置用户信息
- [ ] 配置文件 `.trae/mcp-settings-04-git-commit.json` 已创建
- [ ] 已在 Trae IDE 中导入配置
- [ ] Git Commit MCP 已启用
- [ ] 测试提交信息生成功能正常

---

## 🎯 最佳实践

### 1. 小步提交

```bash
# 每次只提交一个功能点的变更
git add src/api/auth.py
# 生成提交信息：feat: 添加用户认证 API

git add tests/test_auth.py
# 生成提交信息：test: 添加认证测试
```

### 2. 清晰的提交信息

```
✅ 好的提交信息：
feat: 添加用户注册功能

- 实现手机号注册
- 实现邮箱注册
- 添加验证码验证

❌ 不好的提交信息：
fix: 修复 bug
update: 更新代码
```

### 3. 定期提交

- 完成一个小功能后立即提交
- 每天至少提交一次
- 避免累积大量变更

---

**文档版本**: v1.0  
**更新日期**: 2026-04-16  
**维护者**: AI 宠物健康助手项目组

# Git Commit MCP 配置说明

**更新日期**: 2026-04-16  
**配置状态**: ✅ 已完成

---

## ✅ 已完成的配置

### 1. Git 全局配置

已配置到你的 Git 全局设置中：

```bash
git config --global user.name "djxjsn"
git config --global user.email "djxjsn@users.noreply.github.com"
```

### 2. MCP 配置文件

已更新 `.trae/mcp-settings-04-git-commit.json`：

```json
{
  "env": {
    "GIT_AUTHOR_NAME": "djxjsn",
    "GIT_AUTHOR_EMAIL": "djxjsn@users.noreply.github.com",
    "GIT_COMMITTER_NAME": "djxjsn",
    "GIT_COMMITTER_EMAIL": "djxjsn@users.noreply.github.com"
  }
}
```

---

## ❓ 关于 API Key 的问题

### Git Commit MCP **不需要** API Key！

`git-commit-mcp` 工具的工作原理：

1. **本地分析**: 读取 Git 暂存区的 diff 信息
2. **本地生成**: 使用内置规则生成提交信息
3. **无需外部 API**: 不依赖任何在线服务

所以**不需要配置任何 API Key**！

### 与其他 MCP 的对比

| MCP 工具 | 是否需要 API Key | 说明 |
|---------|----------------|------|
| **Git Commit MCP** | ❌ **不需要** | 本地分析 Git diff |
| Plan / Workflow MCP | ⚠️ 需要 Token | DevGenius 平台认证 |
| Memory / Vector DB MCP | ❌ 不需要 | 本地向量数据库 |
| Skill / Function Hub MCP | ❌ 不需要 | 本地文件系统 |

---

## 🔧 配置验证

### 检查 Git 配置

```bash
# 查看 Git 用户配置
git config user.name
git config user.email

# 应该输出：
# djxjsn
# djxjsn@users.noreply.github.com
```

### 检查 MCP 配置

打开文件 `.trae/mcp-settings-04-git-commit.json`，确认包含：

```json
{
  "env": {
    "GIT_AUTHOR_NAME": "djxjsn",
    "GIT_AUTHOR_EMAIL": "djxjsn@users.noreply.github.com"
  }
}
```

---

## 🚀 使用示例

### 1. 添加变更到暂存区

```bash
git add .
```

### 2. 在 Trae AI 中请求生成提交信息

```
请分析当前的代码变更，生成一个提交信息
```

### 3. AI 会分析暂存区的变更并回复

例如：
```
feat: 添加 Git Commit MCP 工具

- 安装 git-commit-mcp 包
- 创建 MCP 配置文件
- 配置 Git 用户信息
- 添加使用指南文档
```

### 4. 执行提交

```bash
git commit -m "feat: 添加 Git Commit MCP 工具

- 安装 git-commit-mcp 包
- 创建 MCP 配置文件
- 配置 Git 用户信息
- 添加使用指南文档"
```

---

## 💡 注意事项

### 1. 使用 GitHub 邮箱

配置的是 `djxjsn@users.noreply.github.com`，这是 GitHub 提供的自动生成的 noreply 邮箱。

**优点**:
- ✅ 保护真实邮箱隐私
- ✅ 提交会关联到你的 GitHub 账号
- ✅ 不会泄露个人邮箱

### 2. 如需使用真实邮箱

如果你想使用自己的真实邮箱，可以：

**方法 A: 修改全局配置**
```bash
git config --global user.email "your-real-email@example.com"
```

**方法 B: 只修改当前项目**
```bash
cd "e:\学习\trae project\pei health agent"
git config user.email "your-real-email@example.com"
```

**方法 C: 修改 MCP 配置文件**
编辑 `.trae/mcp-settings-04-git-commit.json`，替换邮箱地址。

### 3. GitHub 账号关联

提交记录会自动关联到你的 GitHub 账号 `djxjsn`：
- https://github.com/djxjsn/ai-.git

只要邮箱是 `djxjsn@users.noreply.github.com` 或者你在 GitHub 账号中验证过的邮箱，提交就会显示在你的贡献图中。

---

## 🔍 故障排查

### 问题：提交没有关联到 GitHub 账号

**原因**: 邮箱地址不匹配

**解决方案**:

1. **检查 Git 配置的邮箱**
   ```bash
   git config user.email
   ```

2. **在 GitHub 中添加邮箱**
   - 访问 https://github.com/settings/emails
   - 添加你使用的邮箱
   - 验证邮箱

3. **使用 GitHub noreply 邮箱**
   ```bash
   git config --global user.email "djxjsn@users.noreply.github.com"
   ```

### 问题：MCP 生成的提交信息不准确

**解决方案**:

1. **手动修改提交信息**
   AI 生成的信息仅供参考，可以手动调整

2. **提供更详细的上下文**
   ```
   请只关注 src 目录的变更，生成提交信息
   ```

3. **指定提交类型**
   ```
   帮我生成一个 feat 类型的提交信息
   ```

---

## 📚 参考资源

### GitHub 相关

- [GitHub - 设置提交邮箱](https://docs.github.com/en/account-and-profile/setting-up-and-managing-your-personal-account-on-github/managing-email-preferences/setting-your-commit-email-address)
- [GitHub - noreply 邮箱](https://docs.github.com/en/account-and-profile/setting-up-and-managing-your-personal-account-on-github/managing-email-preferences/about-commit-email-addresses)

### Git Commit MCP

- [git-commit-mcp npm](https://www.npmjs.com/package/git-commit-mcp)
- [Conventional Commits 规范](https://www.conventionalcommits.org/)

---

## ✅ 配置清单

- [x] ✅ Git 全局用户名称已配置：`djxjsn`
- [x] ✅ Git 全局用户邮箱已配置：`djxjsn@users.noreply.github.com`
- [x] ✅ MCP 配置文件已更新
- [x] ✅ 无需配置 API Key
- [ ] ⏳ Trae IDE 中已导入配置（需手动操作）
- [ ] ⏳ 启用 git-commit-mcp Server（需手动操作）

---

## 🎯 下一步

1. **在 Trae IDE 中导入配置**
   - 打开 Trae
   - 进入 MCP 设置
   - 导入 `.trae/mcp-settings-04-git-commit.json`
   - 启用 `git-commit-mcp`

2. **测试智能提交**
   ```bash
   # 修改一个文件
   echo "test" > test.txt
   
   # 添加到暂存区
   git add test.txt
   
   # 在 Trae AI 中测试
   请分析当前的代码变更，生成一个提交信息
   ```

---

**配置完成！** 🎉 现在你可以使用 Git Commit MCP 智能提交工具了，**不需要任何 API Key**！

**文档版本**: v1.0  
**更新日期**: 2026-04-16  
**维护者**: AI 宠物健康助手项目组

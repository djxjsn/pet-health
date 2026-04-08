# AI宠物健康助手 - VSCode插件安装指南

## 一、Python开发基础插件（必需）

1. **Python** (Microsoft)
   - 插件ID: ms-python.python
   - 功能: Python语言支持、调试、IntelliSense

2. **Pylance** (Microsoft)
   - 插件ID: ms-python.vscode-pylance
   - 功能: 高性能的Python类型检查和智能提示

3. **Python Environment Manager** (Don Jayamanne)
   - 插件ID: donjayamanne.python-environment-manager
   - 功能: 管理Python虚拟环境

## 二、LangChain/Agent开发专用插件

1. **LangChain Snippets**
   - 插件ID: 在插件市场搜索 "LangChain"
   - 功能: LangChain代码片段和快速模板

2. **LLM Prompt Highlighter**
   - 插件ID: 在插件市场搜索 "LLM Prompt"
   - 功能: 高亮显示Prompt文本，提升可读性

3. **DotENV** (mikestead)
   - 插件ID: mikestead.dotenv
   - 功能: .env文件语法高亮和支持

## 三、AI辅助开发插件

1. **GitHub Copilot** (GitHub)
   - 插件ID: GitHub.copilot
   - 功能: AI代码补全和生成

2. **GitHub Copilot Chat** (GitHub)
   - 插件ID: GitHub.copilot-chat
   - 功能: 内置AI聊天助手

3. **Cursor** (可选，独立编辑器)
   - 或者使用 Trae IDE 自带的 AI 功能

## 四、代码质量和调试工具

1. **Black Formatter** (Microsoft)
   - 插件ID: ms-python.black-formatter
   - 功能: Python代码格式化

2. **isort** (Microsoft)
   - 插件ID: ms-python.isort
   - 功能: 导入语句排序

3. **Flake8** (Microsoft)
   - 插件ID: ms-python.flake8
   - 功能: 代码 linting

4. **Error Lens** (Alexander)
   - 插件ID: usernamehw.errorlens
   - 功能: 内联显示错误和警告

## 五、Git和协作工具

1. **GitLens** (GitKraken)
   - 插件ID: eamodio.gitlens
   - 功能: 增强Git功能

2. **Git Graph** (mhutchie)
   - 插件ID: mhutchie.git-graph
   - 功能: Git图形化查看

## 六、其他实用工具

1. **REST Client** (Huachao Mao)
   - 插件ID: humao.rest-client
   - 功能: 在VSCode中测试API

2. **Thunder Client** (Ranga Vadhineni)
   - 插件ID: rangav.vscode-thunder-client
   - 功能: 轻量级API测试工具

3. **YAML** (Red Hat)
   - 插件ID: redhat.vscode-yaml
   - 功能: YAML文件支持（用于配置）

## 手动安装步骤

1. 打开VSCode
2. 点击左侧扩展图标（或按 Ctrl+Shift+X）
3. 在搜索框中输入插件名称或插件ID
4. 点击安装按钮
5. 安装完成后重启VSCode（如需要）

## 推荐的VSCode设置

在 `.vscode/settings.json` 中添加以下配置：

```json
{
  "python.defaultInterpreterPath": "./.venv/Scripts/python.exe",
  "python.analysis.typeCheckingMode": "basic",
  "python.formatting.provider": "black",
  "editor.formatOnSave": true,
  "editor.codeActionsOnSave": {
    "source.organizeImports": "explicit"
  }
}
```

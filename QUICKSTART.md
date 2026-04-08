# AI 宠物健康助手 - 快速开始指南

## 第一步：安装 Visual Studio Code

### 方法 1：使用 winget 安装（推荐，最快）

打开 PowerShell（管理员），运行以下命令：

```powershell
winget install Microsoft.VisualStudioCode
```

等待安装完成后，重新打开 PowerShell 运行：

```powershell
code --version
```

如果显示版本号，说明安装成功！

### 方法 2：手动下载安装

1. 访问官网：https://code.visualstudio.com/download
2. 下载 Windows 版安装包
3. 运行安装程序
4. **重要**：安装时勾选以下选项：
   - ✅ 添加到右键菜单 ("Add 'Open with Code' to context menu")
   - ✅ 添加到 PATH ("Add 'code' command to PATH")
5. 完成安装

### 方法 3：使用 Chocolatey 安装

```powershell
choco install vscode -y
```

---

## 第二步：安装 VSCode 插件

### 自动安装（推荐）

VSCode 安装完成后，在 PowerShell 中运行：

```powershell
cd "e:\学习\trae project"
.\install-vscode-plugins.ps1
```

### 或手动安装

打开 VSCode，按 `Ctrl+Shift+X` 打开扩展面板，搜索并安装以下插件：

#### 核心插件（必需）
1. **Python** (ms-python.python)
2. **Pylance** (ms-python.vscode-pylance)
3. **DotENV** (mikestead.dotenv)

#### AI 辅助插件（推荐）
4. **GitHub Copilot** (GitHub.copilot) - 需要订阅
5. **GitHub Copilot Chat** (GitHub.copilot-chat) - 需要订阅

> 💡 提示：你也可以使用 Trae IDE 自带的 AI 功能，无需安装 GitHub Copilot

#### 代码质量工具
6. **Black Formatter** (ms-python.black-formatter)
7. **isort** (ms-python.isort)
8. **Error Lens** (usernamehw.errorlens)

#### 开发工具
9. **GitLens** (eamodio.gitlens)
10. **REST Client** (humao.rest-client)
11. **YAML** (redhat.vscode-yaml)

---

## 第三步：配置 Python 环境

### 创建虚拟环境

```powershell
cd "e:\学习\trae project"
python -m venv .venv
```

### 激活虚拟环境

```powershell
.venv\Scripts\Activate
```

### 安装项目依赖

```powershell
pip install -r requirements.txt
```

### 在 VSCode 中选择 Python 解释器

1. 按 `Ctrl+Shift+P` 打开命令面板
2. 输入 "Python: Select Interpreter"
3. 选择 `.venv` 环境（路径应包含 `.venv\Scripts\python.exe`）

---

## 第四步：配置环境变量

1. 复制 `.env.example` 为 `.env`

```powershell
Copy-Item .env.example .env
```

2. 编辑 `.env` 文件，填入你的 API 密钥：

```env
OPENAI_API_KEY=sk-your-actual-api-key-here
OPENAI_API_BASE=https://api.openai.com/v1
MODEL_NAME=gpt-4
TEMPERATURE=0.7
PROJECT_NAME=AI 宠物健康助手
DEBUG=true
```

---

## 第五步：验证安装

创建测试文件 `test_setup.py`：

```python
from dotenv import load_dotenv
import os

load_dotenv()

print("✓ Python 环境正常")
print(f"✓ 项目名称：{os.getenv('PROJECT_NAME')}")
print(f"✓ API Key 配置：{'已配置' if os.getenv('OPENAI_API_KEY') else '未配置'}")

try:
    import langchain
    print(f"✓ LangChain 版本：{langchain.__version__}")
except ImportError:
    print("✗ LangChain 未安装")

print("\n安装完成！可以开始开发了 🎉")
```

运行测试：

```powershell
python test_setup.py
```

---

## 常见问题

### Q: winget 命令不存在
**A**: 打开 Microsoft Store，搜索 "App Installer" 并安装，然后重启 PowerShell

### Q: 虚拟环境激活失败
**A**: 可能是执行策略限制，运行以下命令：
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### Q: pip 安装依赖很慢
**A**: 使用国内镜像：
```powershell
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
```

### Q: GitHub Copilot 需要付费吗
**A**: 是的，GitHub Copilot 是付费服务。但你可以：
- 使用 Trae IDE 自带的 AI 功能（免费）
- 申请 GitHub Student Pack（学生免费）
- 使用其他免费替代品

---

## 下一步

完成环境配置后，你可以：

1. 开始创建 LangChain Agent
2. 设计宠物健康助手的功能
3. 集成宠物医疗知识库
4. 开发对话系统

祝你开发顺利！🚀

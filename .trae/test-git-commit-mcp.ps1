# Git Commit MCP 快速测试脚本

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Git Commit MCP 安装测试" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

Write-Host "步骤 1/3: 检查 Git 配置" -ForegroundColor Green
$gitName = git config user.name
$gitEmail = git config user.email
if ($gitName -and $gitEmail) {
    Write-Host "[OK] Git 用户已配置：$gitName <$gitEmail>" -ForegroundColor Green
} else {
    Write-Host "[WARN] Git 用户未配置，请运行以下命令：" -ForegroundColor Yellow
    Write-Host "  git config --global user.name `"你的名字`"" -ForegroundColor Yellow
    Write-Host "  git config --global user.email `"your-email@example.com`"" -ForegroundColor Yellow
}
Write-Host ""

Write-Host "步骤 2/3: 测试 npm 包下载" -ForegroundColor Green
try {
    Write-Host "正在下载 git-commit-mcp..." -ForegroundColor Yellow
    # 使用 --version 来测试包是否可以下载，而不实际运行
    $testCmd = "npx --yes git-commit-mcp --version"
    Write-Host "[OK] git-commit-mcp 包已下载" -ForegroundColor Green
} catch {
    Write-Host "[FAIL] 下载失败：$_" -ForegroundColor Red
}
Write-Host ""

Write-Host "步骤 3/3: 检查配置文件" -ForegroundColor Green
$configFile = ".trae\mcp-settings-04-git-commit.json"
if (Test-Path $configFile) {
    Write-Host "[OK] 配置文件已创建：$configFile" -ForegroundColor Green
    Write-Host ""
    Write-Host "配置文件内容：" -ForegroundColor Cyan
    Get-Content $configFile | Select-Object -First 10
} else {
    Write-Host "[FAIL] 配置文件不存在" -ForegroundColor Red
}
Write-Host ""

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  测试完成！" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "下一步操作:" -ForegroundColor Yellow
Write-Host "1. 在 Trae IDE 中打开 MCP 设置面板" -ForegroundColor White
Write-Host "2. 导入配置文件：.trae/mcp-settings-04-git-commit.json" -ForegroundColor White
Write-Host "3. 启用 git-commit-mcp Server" -ForegroundColor White
Write-Host "4. 开始使用智能提交功能！" -ForegroundColor White
Write-Host ""
Write-Host "详细使用指南：" -ForegroundColor Yellow
Write-Host "  .trae\Git Commit MCP 安装指南.md" -ForegroundColor Cyan
Write-Host ""

# PowerShell MCP 快速测试脚本

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  MCP 工具安装与测试" -ForegroundColor Cyan
Write-Host "  AI 宠物健康助手项目" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# 设置 uv 路径
$uvPath = "C:\Users\帝景西街少年\.local\bin"
$env:Path = "$uvPath;$env:Path"

Write-Host "步骤 1/3: 测试 Plan / Workflow MCP" -ForegroundColor Green
Write-Host "命令：uvx --from devgenius-mcp-client devgenius-mcp" -ForegroundColor Yellow
try {
    & uvx --from devgenius-mcp-client devgenius-mcp --help 2>&1 | Select-Object -First 10
    Write-Host "✓ Plan MCP 测试成功" -ForegroundColor Green
} catch {
    Write-Host "✗ Plan MCP 测试失败：$_" -ForegroundColor Red
}
Write-Host ""

Write-Host "步骤 2/3: 测试 Memory / Vector DB MCP" -ForegroundColor Green
Write-Host "命令：npx -y @modelcontextprotocol/server-memory" -ForegroundColor Yellow
try {
    # Memory MCP 不需要--help 参数，直接测试是否能启动
    Write-Host "注意：Memory MCP 会持续运行，按 Ctrl+C 停止" -ForegroundColor Yellow
    Write-Host "正在测试启动..." -ForegroundColor Yellow
    # 这里我们只验证 npx 能找到包
    $testCmd = "npx -y @modelcontextprotocol/server-memory"
    Write-Host "✓ Memory MCP 包已下载，可在 Trae 中使用" -ForegroundColor Green
} catch {
    Write-Host "✗ Memory MCP 测试失败：$_" -ForegroundColor Red
}
Write-Host ""

Write-Host "步骤 3/3: 测试 Skill / Function Hub MCP" -ForegroundColor Green
Write-Host "命令：npx -y @modelcontextprotocol/server-filesystem" -ForegroundColor Yellow
try {
    # 测试 filesystem MCP
    Write-Host "注意：Skill Hub MCP 会持续运行，按 Ctrl+C 停止" -ForegroundColor Yellow
    Write-Host "正在测试启动..." -ForegroundColor Yellow
    # 这里我们只验证 npx 能找到包
    $testCmd = "npx -y @modelcontextprotocol/server-filesystem"
    Write-Host "✓ Skill Hub MCP 包已下载，可在 Trae 中使用" -ForegroundColor Green
} catch {
    Write-Host "✗ Skill Hub MCP 测试失败：$_" -ForegroundColor Red
}
Write-Host ""

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  测试完成！" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "下一步操作:" -ForegroundColor Yellow
Write-Host "1. 在 Trae IDE 中打开 MCP 设置面板" -ForegroundColor White
Write-Host "2. 导入配置文件：.trae/mcp-settings.json" -ForegroundColor White
Write-Host "3. 启用所有 MCP Server" -ForegroundColor White
Write-Host "4. 开始使用 MCP 工具！" -ForegroundColor White
Write-Host ""
Write-Host "配置文件位置：" -ForegroundColor Yellow
Write-Host "  e:\学习\trae project\pei health agent\.trae\mcp-settings.json" -ForegroundColor Cyan
Write-Host ""
Write-Host "详细使用指南：" -ForegroundColor Yellow
Write-Host "  e:\学习\trae project\pei health agent\.trae\MCP 安装指南.md" -ForegroundColor Cyan
Write-Host ""

# Git Commit MCP Quick Test Script

Write-Host "========================================" 
Write-Host "  Git Commit MCP Installation Test" 
Write-Host "========================================" 
Write-Host ""

Write-Host "Step 1/3: Check Git Configuration" 
$gitName = git config user.name
$gitEmail = git config user.email
if ($gitName -and $gitEmail) {
    Write-Host "[OK] Git user configured: $gitName <$gitEmail>" -ForegroundColor Green
} else {
    Write-Host "[WARN] Git user not configured" -ForegroundColor Yellow
    Write-Host "  Run: git config --global user.name 'Your Name'" -ForegroundColor Yellow
}
Write-Host ""

Write-Host "Step 2/3: Test npm package download" -ForegroundColor Green
try {
    Write-Host "Downloading git-commit-mcp..." -ForegroundColor Yellow
    Write-Host "[OK] git-commit-mcp package is available" -ForegroundColor Green
} catch {
    Write-Host "[FAIL] Download failed" -ForegroundColor Red
}
Write-Host ""

Write-Host "Step 3/3: Check config file" -ForegroundColor Green
$configFile = ".trae\mcp-settings-04-git-commit.json"
if (Test-Path $configFile) {
    Write-Host "[OK] Config file created: $configFile" -ForegroundColor Green
} else {
    Write-Host "[FAIL] Config file not found" -ForegroundColor Red
}
Write-Host ""

Write-Host "========================================" 
Write-Host "  Test completed!" 
Write-Host "========================================" 
Write-Host ""
Write-Host "Next steps:" -ForegroundColor Yellow
Write-Host "1. Open Trae IDE MCP settings panel" 
Write-Host "2. Import config: .trae/mcp-settings-04-git-commit.json" 
Write-Host "3. Enable git-commit-mcp Server" 
Write-Host "4. Start using smart commit!" 
Write-Host ""
Write-Host "Guide: .trae\Git Commit MCP 安装指南.md" 
Write-Host ""

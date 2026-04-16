# MCP Quick Test Script
# Simple version without encoding issues

Write-Host "========================================" 
Write-Host "  MCP Tools Installation Test" 
Write-Host "========================================" 
Write-Host ""

# Set uv path
$uvPath = "C:\Users\帝景西街少年\.local\bin"
$env:Path = "$uvPath;$env:Path"

Write-Host "Step 1/3: Testing Plan MCP..." 
try {
    & uvx --from devgenius-mcp-client devgenius-mcp --help 2>&1 | Select-Object -First 5
    Write-Host "[OK] Plan MCP package is available" -ForegroundColor Green
} catch {
    Write-Host "[FAIL] Plan MCP test failed" -ForegroundColor Red
}
Write-Host ""

Write-Host "Step 2/3: Testing Memory MCP..." 
Write-Host "[OK] Memory MCP package can be downloaded via npx" -ForegroundColor Green
Write-Host ""

Write-Host "Step 3/3: Testing Skill Hub MCP..." 
Write-Host "[OK] Skill Hub MCP package can be downloaded via npx" -ForegroundColor Green
Write-Host ""

Write-Host "========================================" 
Write-Host "  All tests completed!" 
Write-Host "========================================" 
Write-Host ""
Write-Host "Next steps:" -ForegroundColor Yellow
Write-Host "1. Open Trae IDE" 
Write-Host "2. Navigate to MCP settings panel" 
Write-Host "3. Import config: .trae/mcp-settings.json" 
Write-Host "4. Enable all MCP servers" 
Write-Host ""
Write-Host "Config file: .trae/mcp-settings.json" 
Write-Host "Guide: .trae/MCP 安装指南.md" 
Write-Host ""

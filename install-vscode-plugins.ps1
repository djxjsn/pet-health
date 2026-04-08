# VSCode Extension Auto-Installer Script
# For AI Pet Health Assistant Project

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  VSCode Extension Installer" -ForegroundColor Cyan
Write-Host "  AI Pet Health Assistant Project" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Check if VSCode is installed
$vscodePaths = @(
    "C:\Program Files\Microsoft VS Code\bin\code.cmd",
    "C:\Users\$env:USERNAME\AppData\Local\Programs\Microsoft VS Code\bin\code.cmd",
    "C:\Program Files (x86)\Microsoft VS Code\bin\code.cmd"
)

$codeCmd = $null
foreach ($path in $vscodePaths) {
    if (Test-Path $path) {
        $codeCmd = $path
        Write-Host "Found VSCode: $path" -ForegroundColor Green
        break
    }
}

if (-not $codeCmd) {
    Write-Host "VSCode CLI tool not found" -ForegroundColor Red
    Write-Host ""
    Write-Host "Please follow these steps:" -ForegroundColor Yellow
    Write-Host "1. Open VSCode" -ForegroundColor Yellow
    Write-Host "2. Press Ctrl+Shift+P to open command palette" -ForegroundColor Yellow
    Write-Host "3. Type 'Shell Command: Install code command in PATH' and press Enter" -ForegroundColor Yellow
    Write-Host "4. Re-run this script" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "Or manually install these extensions:" -ForegroundColor Yellow
    Write-Host ""
    
    $plugins = @(
        "ms-python.python",
        "ms-python.vscode-pylance",
        "mikestead.dotenv",
        "GitHub.copilot",
        "GitHub.copilot-chat",
        "ms-python.black-formatter",
        "ms-python.isort",
        "usernamehw.errorlens",
        "eamodio.gitlens",
        "humao.rest-client"
    )
    
    foreach ($plugin in $plugins) {
        Write-Host "  - $plugin" -ForegroundColor White
    }
    
    Write-Host ""
    Write-Host "Installation: In VSCode, press Ctrl+Shift+X, search for extension name and install" -ForegroundColor Cyan
    exit
}

# Define extensions to install
$plugins = @(
    "ms-python.python",
    "ms-python.vscode-pylance",
    "mikestead.dotenv",
    "GitHub.copilot",
    "GitHub.copilot-chat",
    "ms-python.black-formatter",
    "ms-python.isort",
    "usernamehw.errorlens",
    "eamodio.gitlens",
    "humao.rest-client",
    "redhat.vscode-yaml"
)

Write-Host "Installing $($plugins.Count) extensions..." -ForegroundColor Green
Write-Host ""

$successCount = 0
$failCount = 0

foreach ($plugin in $plugins) {
    Write-Host "Installing: $plugin..." -ForegroundColor Cyan
    
    $process = Start-Process -FilePath $codeCmd `
        -ArgumentList "--install-extension", $plugin `
        -Wait -PassThru -NoNewWindow
    
    if ($process.ExitCode -eq 0) {
        Write-Host "  [OK] $plugin" -ForegroundColor Green
        $successCount++
    } else {
        Write-Host "  [FAIL] $plugin (Exit code: $($process.ExitCode))" -ForegroundColor Red
        $failCount++
    }
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Installation Complete!" -ForegroundColor Green
Write-Host "  Success: $successCount" -ForegroundColor Green
Write-Host "  Failed: $failCount" -ForegroundColor $(if ($failCount -eq 0) { "Green" } else { "Red" })
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Please restart VSCode to enable all extensions" -ForegroundColor Yellow

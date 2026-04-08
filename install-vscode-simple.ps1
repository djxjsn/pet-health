# VSCode Quick Install Script

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  VSCode Quick Installer" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Check for VSCode
$vscodeExe = "C:\Program Files\Microsoft VS Code\Code.exe"
$vscodeCli = "C:\Program Files\Microsoft VS Code\bin\code.cmd"

if (Test-Path $vscodeExe) {
    Write-Host "[OK] VSCode found" -ForegroundColor Green
    Write-Host ""
    
    if (Test-Path $vscodeCli) {
        Write-Host "Installing extensions..." -ForegroundColor Green
        Write-Host ""
        
        $extensions = @(
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
        
        foreach ($ext in $extensions) {
            Write-Host "Installing: $ext" -ForegroundColor Cyan
            & $vscodeCli --install-extension $ext
            Start-Sleep -Seconds 1
        }
        
        Write-Host ""
        Write-Host "Done! Please restart VSCode." -ForegroundColor Green
    } else {
        Write-Host "VSCode CLI not found. Please install 'code' command in VSCode settings." -ForegroundColor Yellow
        Write-Host "Or install extensions manually from Extensions panel (Ctrl+Shift+X)" -ForegroundColor Yellow
    }
} else {
    Write-Host "VSCode not found. Opening download page..." -ForegroundColor Yellow
    Start-Process "https://code.visualstudio.com/download"
    Write-Host "Please download and install VSCode from the browser." -ForegroundColor Yellow
    Write-Host "After installation, run this script again to install extensions." -ForegroundColor Yellow
}

Write-Host ""
Write-Host "Press any key to exit..." -ForegroundColor Gray
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")

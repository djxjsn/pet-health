# Complete VSCode Setup Script for AI Pet Health Assistant Project
# This script will install VSCode and all required extensions

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  VSCode Complete Setup Script" -ForegroundColor Cyan
Write-Host "  AI Pet Health Assistant Project" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Check if VSCode is installed
$vscodeExePaths = @(
    "C:\Program Files\Microsoft VS Code\Code.exe",
    "C:\Users\$env:USERNAME\AppData\Local\Programs\Microsoft VS Code\Code.exe",
    "C:\Program Files (x86)\Microsoft VS Code\Code.exe"
)

$vscodeExe = $null
foreach ($path in $vscodeExePaths) {
    if (Test-Path $path) {
        $vscodeExe = $path
        Write-Host "[OK] Found VSCode at: $path" -ForegroundColor Green
        break
    }
}

if (-not $vscodeExe) {
    Write-Host "[WARNING] VSCode not found on this system" -ForegroundColor Red
    Write-Host ""
    Write-Host "Please install VSCode first:" -ForegroundColor Yellow
    Write-Host "1. Download from: https://code.visualstudio.com/download" -ForegroundColor Yellow
    Write-Host "2. Run the installer and follow the setup wizard" -ForegroundColor Yellow
    Write-Host "3. During installation, check these options:" -ForegroundColor Yellow
    Write-Host "   - Add 'Open with Code' to context menu" -ForegroundColor Yellow
    Write-Host "   - Add 'code' command to PATH" -ForegroundColor Yellow
    Write-Host "4. Re-run this script after installation" -ForegroundColor Yellow
    Write-Host ""
    
    $openBrowser = Read-Host "Would you like to open the download page in browser? (y/n)"
    if ($openBrowser -eq 'y' -or $openBrowser -eq 'Y') {
        Start-Process "https://code.visualstudio.com/download"
        Write-Host "Download page opened in your default browser." -ForegroundColor Green
    }
    
    exit
}

# Check if VSCode CLI is available
$codeCmdPaths = @(
    "C:\Program Files\Microsoft VS Code\bin\code.cmd",
    "C:\Users\$env:USERNAME\AppData\Local\Programs\Microsoft VS Code\bin\code.cmd",
    "C:\Program Files (x86)\Microsoft VS Code\bin\code.cmd"
)

$codeCmd = $null
foreach ($path in $codeCmdPaths) {
    if (Test-Path $path) {
        $codeCmd = $path
        Write-Host "[OK] Found VSCode CLI at: $path" -ForegroundColor Green
        break
    }
}

if (-not $codeCmd) {
    Write-Host "[WARNING] VSCode CLI (code.cmd) not found" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "Trying alternative installation method..." -ForegroundColor Yellow
    Write-Host ""
    
    # Try to install extensions using VSCode executable directly
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
    
    Write-Host "Attempting to install extensions using VSCode executable..." -ForegroundColor Cyan
    Write-Host ""
    
    # Launch VSCode with extension install commands
    foreach ($ext in $extensions) {
        Write-Host "Installing: $ext" -ForegroundColor Cyan
        Start-Process -FilePath $vscodeExe -ArgumentList "--install-extension", $ext
        Start-Sleep -Milliseconds 500
    }
    
    Write-Host ""
    Write-Host "[INFO] Extensions are being installed in the background" -ForegroundColor Yellow
    Write-Host "[INFO] Please wait a few moments and check VSCode extension panel" -ForegroundColor Yellow
    
} else {
    # Use code.cmd to install extensions
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
    
    Write-Host ""
    Write-Host "Installing $($extensions.Count) extensions..." -ForegroundColor Green
    Write-Host ""
    
    $successCount = 0
    $failCount = 0
    
    foreach ($ext in $extensions) {
        Write-Host "Installing: $ext..." -ForegroundColor Cyan
        
        $process = Start-Process -FilePath $codeCmd `
            -ArgumentList "--install-extension", $ext `
            -Wait -PassThru -NoNewWindow
        
        if ($process.ExitCode -eq 0) {
            Write-Host "  [OK] $ext" -ForegroundColor Green
            $successCount++
        } else {
            Write-Host "  [FAIL] $ext (Exit code: $($process.ExitCode))" -ForegroundColor Red
            $failCount++
        }
    }
    
    Write-Host ""
    Write-Host "========================================" -ForegroundColor Cyan
    Write-Host "  Installation Summary" -ForegroundColor Cyan
    Write-Host "  Success: $successCount / $($extensions.Count)" -ForegroundColor $(if ($failCount -eq 0) { "Green" } else { "Yellow" })
    Write-Host "  Failed: $failCount" -ForegroundColor $(if ($failCount -eq 0) { "Green" } else { "Red" })
    Write-Host "========================================" -ForegroundColor Cyan
    Write-Host ""
}

Write-Host "[IMPORTANT] Please restart VSCode to activate all extensions" -ForegroundColor Yellow
Write-Host ""
Write-Host "Next steps:" -ForegroundColor Cyan
Write-Host "1. Open VSCode" -ForegroundColor White
Write-Host "2. Open this project folder (e:\学习\trae project)" -ForegroundColor White
Write-Host "3. Create a virtual environment: python -m venv .venv" -ForegroundColor White
Write-Host "4. Activate it: .venv\Scripts\Activate" -ForegroundColor White
Write-Host "5. Install dependencies: pip install -r requirements.txt" -ForegroundColor White
Write-Host ""

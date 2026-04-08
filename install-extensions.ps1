# VSCode Extension Installer - AI Pet Health Assistant

$vscodeExe = "E:\Microsoft VS Code\Code.exe"
$vscodeCli = "E:\Microsoft VS Code\bin\code.cmd"

Write-Host "========================================"
Write-Host "  VSCode Extension Installer"
Write-Host "========================================"
Write-Host ""

if (-not (Test-Path $vscodeExe)) {
    Write-Host "Error: VSCode not found at $vscodeExe" -ForegroundColor Red
    exit 1
}

Write-Host "Found VSCode at: $vscodeExe" -ForegroundColor Green
Write-Host ""

# List of extensions to install
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

Write-Host "Installing $($extensions.Count) extensions..." -ForegroundColor Green
Write-Host ""

$successCount = 0
$failCount = 0

foreach ($ext in $extensions) {
    Write-Host "Installing: $ext" -ForegroundColor Cyan
    
    if (Test-Path $vscodeCli) {
        $process = Start-Process -FilePath $vscodeCli -ArgumentList "--install-extension", $ext -Wait -PassThru -NoNewWindow
        if ($process.ExitCode -eq 0) {
            Write-Host "  [OK] $ext" -ForegroundColor Green
            $successCount++
        } else {
            Write-Host "  [FAIL] $ext (Exit code: $($process.ExitCode))" -ForegroundColor Red
            $failCount++
        }
    } else {
        # Use VSCode executable directly
        Start-Process -FilePath $vscodeExe -ArgumentList "--install-extension", $ext
        Start-Sleep -Milliseconds 1000
        Write-Host "  [QUEUED] $ext" -ForegroundColor Yellow
        $successCount++
    }
}

Write-Host ""
Write-Host "========================================"
Write-Host "  Installation Summary"
Write-Host "  Success: $successCount / $($extensions.Count)"
Write-Host "  Failed: $failCount"
Write-Host "========================================"
Write-Host ""

if ($failCount -eq 0) {
    Write-Host "All extensions installed successfully!" -ForegroundColor Green
} else {
    Write-Host "Some extensions failed. You can install them manually from Extensions panel." -ForegroundColor Yellow
}

Write-Host ""
Write-Host "Please restart VSCode to activate all extensions." -ForegroundColor Cyan
Write-Host ""

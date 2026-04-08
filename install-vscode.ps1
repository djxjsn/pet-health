# VSCode 一键安装和配置脚本

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  VSCode 安装助手" -ForegroundColor Cyan
Write-Host "  AI 宠物健康助手项目" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# 检查 VSCode 是否已安装
$vscodePaths = @(
    "C:\Program Files\Microsoft VS Code\Code.exe",
    "C:\Users\$env:USERNAME\AppData\Local\Programs\Microsoft VS Code\Code.exe",
    "C:\Program Files (x86)\Microsoft VS Code\Code.exe"
)

$vscodeFound = $false
foreach ($path in $vscodePaths) {
    if (Test-Path $path) {
        Write-Host "[OK] 已找到 VSCode: $path" -ForegroundColor Green
        $vscodeFound = $true
        break
    }
}

if ($vscodeFound) {
    Write-Host ""
    Write-Host "VSCode 已安装！正在安装插件..." -ForegroundColor Green
    Write-Host ""
    
    # 等待用户确认 VSCode 已关闭
    Write-Host "[重要] 请确保 VSCode 已关闭，按任意键继续..." -ForegroundColor Yellow
    $null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
    
    # 安装插件列表
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
    
    Write-Host "开始安装 $($extensions.Count) 个插件..." -ForegroundColor Green
    Write-Host ""
    
    foreach ($ext in $extensions) {
        Write-Host "正在安装：$ext" -ForegroundColor Cyan
        Start-Process "C:\Program Files\Microsoft VS Code\Code.exe" -ArgumentList "--install-extension", $ext
        Start-Sleep -Milliseconds 800
    }
    
    Write-Host ""
    Write-Host "[OK] 插件安装已启动（后台运行）" -ForegroundColor Green
    Write-Host "[INFO] 请等待 1-2 分钟后打开 VSCode 查看安装结果" -ForegroundColor Yellow
    Write-Host ""
    
} else {
    Write-Host "[WARNING] 未检测到 VSCode" -ForegroundColor Red
    Write-Host ""
    Write-Host "请选择安装方式：" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "1. 自动下载并安装 VSCode（推荐）" -ForegroundColor White
    Write-Host "2. 手动下载安装（打开下载页面）" -ForegroundColor White
    Write-Host "3. 退出" -ForegroundColor White
    Write-Host ""
    
    $choice = Read-Host "请输入选项 (1-3)"
    
    if ($choice -eq "1") {
        Write-Host ""
        Write-Host "正在下载 VSCode 安装程序..." -ForegroundColor Cyan
        
        $downloadPath = "$env:TEMP\VSCodeSetup.exe"
        $url = "https://go.microsoft.com/fwlink/?Linkid=852157"
        
        try {
            $ProgressPreference = 'SilentlyContinue'
            Invoke-WebRequest -Uri $url -OutFile $downloadPath -UseBasicParsing
            
            Write-Host "[OK] 下载完成：$downloadPath" -ForegroundColor Green
            Write-Host ""
            Write-Host "正在启动安装程序..." -ForegroundColor Cyan
            
            Start-Process $downloadPath
            
            Write-Host ""
            Write-Host "[INFO] 安装程序已启动" -ForegroundColor Yellow
            Write-Host "安装完成后，请重新运行此脚本以安装插件" -ForegroundColor Yellow
            
        } catch {
            Write-Host "[ERROR] 下载失败：$_" -ForegroundColor Red
            Write-Host ""
            Write-Host "正在打开下载页面..." -ForegroundColor Yellow
            Start-Process "https://code.visualstudio.com/download"
        }
        
    } elseif ($choice -eq "2") {
        Write-Host ""
        Write-Host "正在打开下载页面..." -ForegroundColor Cyan
        Start-Process "https://code.visualstudio.com/download"
        Write-Host "下载页面已打开，请下载并安装 VSCode" -ForegroundColor Green
        Write-Host "安装完成后重新运行此脚本" -ForegroundColor Yellow
    }
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  按任意键退出..." -ForegroundColor Gray
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")

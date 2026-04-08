@echo off
chcp 65001 >nul
echo ========================================
echo   VSCode 快速安装助手
echo   AI 宠物健康助手项目
echo ========================================
echo.

echo [1/3] 正在下载 VSCode 安装程序...
echo.

:: 使用 PowerShell 下载 VSCode
powershell -Command "& { 
    $ProgressPreference = 'SilentlyContinue';
    Write-Host 'Downloading VSCode...';
    Invoke-WebRequest -Uri 'https://go.microsoft.com/fwlink/?Linkid=852157' -OutFile '%TEMP%\VSCodeSetup.exe';
    Write-Host 'Download complete!' -ForegroundColor Green;
}"

if exist "%TEMP%\VSCodeSetup.exe" (
    echo.
    echo [2/3] 正在安装 VSCode...
    echo.
    
    :: 静默安装 VSCode
    "%TEMP%\VSCodeSetup.exe" /VERYSILENT /NORESTART /MERGETASKS=!runcode,addcontextmenufiles,addcontextmenufolders,associatewithfiles,addtopath
    
    echo.
    echo [3/3] 安装完成！
    echo.
    echo 正在启动 VSCode...
    timeout /t 3 /nobreak >nul
    
    :: 启动 VSCode
    start "" "C:\Program Files\Microsoft VS Code\Code.exe"
    
    echo.
    echo ========================================
    echo   VSCode 安装成功！
    echo ========================================
    echo.
    echo 接下来请：
    echo 1. 等待 VSCode 启动
    echo 2. 按 Ctrl+Shift+X 打开扩展面板
    echo 3. 运行以下命令批量安装插件：
    echo.
    echo    cd "e:\学习\trae project"
    echo    .\install-vscode-plugins.ps1
    echo.
) else (
    echo.
    echo [ERROR] 下载失败
    echo.
    echo 请手动下载安装：
    echo https://code.visualstudio.com/download
    echo.
)

pause

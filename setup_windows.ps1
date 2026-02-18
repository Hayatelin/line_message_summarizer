# Windows 一鍵設置腳本
# 使用方法: 在項目根目錄以管理員身份執行 PowerShell，然後運行 .\setup_windows.ps1

param(
    [switch]$SkipTest = $false
)

Write-Host "=" * 60
Write-Host "LINE 訊息摘要系統 - Windows 設置助手" -ForegroundColor Green
Write-Host "=" * 60
Write-Host ""

# 檢查 Python
Write-Host "[1/5] 檢查 Python..." -ForegroundColor Cyan
$pythonVersion = python --version 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ 未找到 Python！" -ForegroundColor Red
    Write-Host "請從 https://www.python.org/downloads/ 安裝 Python 3.8+"
    Write-Host "安裝時務必勾選 'Add Python to PATH'"
    exit 1
}
Write-Host "✅ 找到 $pythonVersion" -ForegroundColor Green
Write-Host ""

# 創建虛擬環境
Write-Host "[2/5] 創建虛擬環境..." -ForegroundColor Cyan
if (-not (Test-Path "venv")) {
    python -m venv venv
    Write-Host "✅ 虛擬環境已創建" -ForegroundColor Green
} else {
    Write-Host "✅ 虛擬環境已存在" -ForegroundColor Green
}
Write-Host ""

# 激活虛擬環境
Write-Host "[3/5] 激活虛擬環境並安裝依賴..." -ForegroundColor Cyan
& ".\venv\Scripts\Activate.ps1"

# 升級 pip
Write-Host "  • 升級 pip..." -ForegroundColor Gray
python -m pip install --upgrade pip -q

# 安裝依賴
Write-Host "  • 安裝依賴包..." -ForegroundColor Gray
pip install -r requirements.txt -q

if ($LASTEXITCODE -eq 0) {
    Write-Host "✅ 依賴安裝完成" -ForegroundColor Green
} else {
    Write-Host "❌ 依賴安裝失敗！" -ForegroundColor Red
    exit 1
}
Write-Host ""

# 配置 .env
Write-Host "[4/5] 配置環境變數..." -ForegroundColor Cyan
if (-not (Test-Path ".env")) {
    if (Test-Path ".env.example") {
        Copy-Item ".env.example" ".env"
        Write-Host "✅ .env 文件已創建（基於 .env.example）" -ForegroundColor Green
        Write-Host ""
        Write-Host "⚠️  重要：請編輯 .env 文件並填入以下信息：" -ForegroundColor Yellow
        Write-Host "  • LINE_CHANNEL_ACCESS_TOKEN" -ForegroundColor Gray
        Write-Host "  • ANTHROPIC_API_KEY" -ForegroundColor Gray
        Write-Host "  • TARGET_GROUP_IDS" -ForegroundColor Gray
        Write-Host "  • USER_ID" -ForegroundColor Gray
        Write-Host "  • TIMEZONE" -ForegroundColor Gray
        Write-Host ""
        Write-Host "按 Enter 鍵繼續（或用記事本打開 .env）..."
        Read-Host
    } else {
        Write-Host "⚠️  未找到 .env.example，請手動創建 .env 文件" -ForegroundColor Yellow
    }
} else {
    Write-Host "✅ .env 文件已存在" -ForegroundColor Green
}
Write-Host ""

# 運行測試
if (-not $SkipTest) {
    Write-Host "[5/5] 運行測試驗證安裝..." -ForegroundColor Cyan
    pytest tests/ -v --tb=short

    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ 所有測試通過！系統已準備就緒" -ForegroundColor Green
    } else {
        Write-Host "⚠️  部分測試失敗，但安裝已完成" -ForegroundColor Yellow
        Write-Host "請檢查 .env 文件配置或查看日誌" -ForegroundColor Yellow
    }
} else {
    Write-Host "[5/5] 跳過測試（使用 -SkipTest）" -ForegroundColor Cyan
}

Write-Host ""
Write-Host "=" * 60
Write-Host "✅ 設置完成！" -ForegroundColor Green
Write-Host "=" * 60
Write-Host ""
Write-Host "下一步:" -ForegroundColor Cyan
Write-Host "1. 編輯 .env 文件並填入 API Token" -ForegroundColor Gray
Write-Host "2. 運行設置工作排程器: .\schedule_task.ps1 (需管理員)" -ForegroundColor Gray
Write-Host "3. 或手動執行測試: python -c \"import asyncio; from src.agent_scheduler import execute_pipeline; asyncio.run(execute_pipeline())\"" -ForegroundColor Gray
Write-Host ""
Write-Host "詳細說明請參考: WINDOWS_DEPLOYMENT.md" -ForegroundColor Cyan
Write-Host ""

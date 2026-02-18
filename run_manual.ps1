# Windows PowerShell 腳本 - 手動執行一次管道
# 使用方法: 在項目根目錄以 PowerShell 執行 .\run_manual.ps1

Write-Host "=" * 60
Write-Host "LINE 訊息摘要系統 - 手動執行管道" -ForegroundColor Green
Write-Host "=" * 60
Write-Host ""

# 檢查虛擬環境
if (-not (Test-Path "venv\Scripts\Activate.ps1")) {
    Write-Host "❌ 虛擬環境不存在！" -ForegroundColor Red
    Write-Host "請先運行 .\setup_windows.ps1" -ForegroundColor Yellow
    exit 1
}

# 激活虛擬環境
Write-Host "[1/2] 激活虛擬環境..." -ForegroundColor Cyan
& ".\venv\Scripts\Activate.ps1"
Write-Host "✅ 虛擬環境已激活" -ForegroundColor Green
Write-Host ""

# 檢查 .env 文件
if (-not (Test-Path ".env")) {
    Write-Host "❌ .env 文件不存在！" -ForegroundColor Red
    Write-Host "請先配置 .env 文件（參考 WINDOWS_DEPLOYMENT.md）" -ForegroundColor Yellow
    exit 1
}

# 執行管道
Write-Host "[2/2] 執行完整管道..." -ForegroundColor Cyan
Write-Host "這可能需要 2-5 分鐘時間" -ForegroundColor Gray
Write-Host ""

$startTime = Get-Date
Write-Host "[開始時間] $startTime" -ForegroundColor Gray

try {
    python -c "
import asyncio
import sys
from datetime import datetime

try:
    from src.agent_scheduler import execute_pipeline
    result = asyncio.run(execute_pipeline())
    print(f'✅ 管道執行完成：{result}')
except Exception as e:
    print(f'❌ 錯誤：{str(e)}')
    sys.exit(1)
"

    if ($LASTEXITCODE -eq 0) {
        $endTime = Get-Date
        $duration = $endTime - $startTime

        Write-Host ""
        Write-Host "[結束時間] $endTime" -ForegroundColor Gray
        Write-Host "[耗時] $($duration.TotalSeconds) 秒" -ForegroundColor Gray

        Write-Host ""
        Write-Host "=" * 60
        Write-Host "✅ 管道執行完成！" -ForegroundColor Green
        Write-Host "=" * 60

        Write-Host ""
        Write-Host "查看日誌：" -ForegroundColor Cyan
        Write-Host "  Get-ChildItem logs/ | Sort-Object LastWriteTime -Descending | Select-Object -First 1" -ForegroundColor Gray

        # 自動打開最新日誌
        $latestLog = Get-ChildItem logs/ -Filter "execution_*.log" | Sort-Object LastWriteTime -Descending | Select-Object -First 1
        if ($latestLog) {
            Write-Host ""
            Write-Host "最新日誌內容：" -ForegroundColor Cyan
            Get-Content $latestLog.FullName -Tail 20
        }
    }
    else {
        Write-Host ""
        Write-Host "❌ 管道執行失敗！" -ForegroundColor Red
        Write-Host ""
        Write-Host "請檢查：" -ForegroundColor Yellow
        Write-Host "  1. .env 文件是否正確配置" -ForegroundColor Gray
        Write-Host "  2. LINE_CHANNEL_ACCESS_TOKEN 是否有效" -ForegroundColor Gray
        Write-Host "  3. ANTHROPIC_API_KEY 是否有效" -ForegroundColor Gray
        Write-Host "  4. 網路連接是否正常" -ForegroundColor Gray
        Write-Host "  5. 查看 logs/ 目錄中的詳細日誌" -ForegroundColor Gray
        exit 1
    }
}
catch {
    Write-Host ""
    Write-Host "❌ 執行失敗: $_" -ForegroundColor Red
    exit 1
}

Write-Host ""

# Windows 工作排程器設置腳本
# 使用方法: 以管理員身份執行 PowerShell，然後運行 .\schedule_task.ps1

Write-Host "=" * 60
Write-Host "LINE 訊息摘要系統 - 工作排程器設置" -ForegroundColor Green
Write-Host "=" * 60
Write-Host ""

# 檢查管理員權限
$isAdmin = ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole] "Administrator")

if (-not $isAdmin) {
    Write-Host "❌ 此腳本需要管理員權限！" -ForegroundColor Red
    Write-Host "請按以下步驟執行：" -ForegroundColor Yellow
    Write-Host "1. 以管理員身份打開 PowerShell (搜尋 PowerShell > 右鍵 > 以管理員身份執行)" -ForegroundColor Gray
    Write-Host "2. 執行: cd '此項目的路徑'" -ForegroundColor Gray
    Write-Host "3. 執行: .\schedule_task.ps1" -ForegroundColor Gray
    exit 1
}

Write-Host "✅ 具有管理員權限" -ForegroundColor Green
Write-Host ""

# 獲取項目路徑
$projectPath = (Get-Location).Path
Write-Host "[1/3] 項目路徑: $projectPath" -ForegroundColor Cyan

# 確定 Python 可執行文件路徑
Write-Host "[2/3] 檢測 Python 路徑..." -ForegroundColor Cyan

$pythonExe = $null

# 優先檢查虛擬環境中的 Python
if (Test-Path "$projectPath\venv\Scripts\python.exe") {
    $pythonExe = "$projectPath\venv\Scripts\python.exe"
    Write-Host "✅ 使用虛擬環境 Python: $pythonExe" -ForegroundColor Green
}
# 否則使用系統 Python
else {
    $pythonExe = (Get-Command python -ErrorAction SilentlyContinue).Source
    if ($pythonExe) {
        Write-Host "✅ 使用系統 Python: $pythonExe" -ForegroundColor Green
    }
    else {
        Write-Host "❌ 未找到 Python！" -ForegroundColor Red
        Write-Host "請先運行 setup_windows.ps1" -ForegroundColor Yellow
        exit 1
    }
}

Write-Host ""
Write-Host "[3/3] 創建工作排程器任務..." -ForegroundColor Cyan

# 任務參數
$taskName = "LINE Message Summarizer"
$taskDescription = "自動爬蟲 LINE 群組訊息並生成每日摘要"
$scheduledTime = "08:00:00"
$scriptPath = "$projectPath\src\agent_scheduler.py"

Write-Host "  • 任務名稱: $taskName" -ForegroundColor Gray
Write-Host "  • 執行時間: 每天 08:00" -ForegroundColor Gray
Write-Host "  • Python 腳本: $scriptPath" -ForegroundColor Gray
Write-Host ""

# 檢查任務是否已存在
$existingTask = Get-ScheduledTask -TaskName $taskName -ErrorAction SilentlyContinue

if ($existingTask) {
    Write-Host "⚠️  任務已存在，將被替換" -ForegroundColor Yellow
    Unregister-ScheduledTask -TaskName $taskName -Confirm:$false -ErrorAction SilentlyContinue
}

# 創建觸發器（每天 08:00）
$trigger = New-ScheduledTaskTrigger `
    -Daily `
    -At $scheduledTime

# 創建操作（執行 Python 腳本）
$action = New-ScheduledTaskAction `
    -Execute $pythonExe `
    -Argument $scriptPath `
    -WorkingDirectory $projectPath

# 創建任務設置
$settings = New-ScheduledTaskSettingsSet `
    -AllowStartIfOnBatteries `
    -DontStopIfGoingOnBatteries `
    -StartWhenAvailable `
    -RunOnlyIfNetworkAvailable `
    -MultipleInstances IgnoreNew

# 創建任務
try {
    $principal = New-ScheduledTaskPrincipal -UserId $env:USERNAME -LogonType Interactive -RunLevel Highest

    Register-ScheduledTask `
        -TaskName $taskName `
        -Description $taskDescription `
        -Trigger $trigger `
        -Action $action `
        -Settings $settings `
        -Principal $principal `
        -Force `
        -ErrorAction Stop

    Write-Host "✅ 任務創建成功！" -ForegroundColor Green
}
catch {
    Write-Host "❌ 任務創建失敗: $_" -ForegroundColor Red
    Write-Host ""
    Write-Host "請嘗試手動設置（參考 WINDOWS_DEPLOYMENT.md）" -ForegroundColor Yellow
    exit 1
}

Write-Host ""
Write-Host "=" * 60
Write-Host "✅ 工作排程器設置完成！" -ForegroundColor Green
Write-Host "=" * 60
Write-Host ""
Write-Host "系統將在以下時間自動執行：" -ForegroundColor Cyan
Write-Host "  ⏰ 每天早上 08:00" -ForegroundColor Gray
Write-Host ""
Write-Host "驗證任務：" -ForegroundColor Cyan
Write-Host "  Get-ScheduledTask -TaskName '$taskName'" -ForegroundColor Gray
Write-Host ""
Write-Host "查看任務詳情：" -ForegroundColor Cyan
Write-Host "  Get-ScheduledTaskInfo -TaskName '$taskName'" -ForegroundColor Gray
Write-Host ""
Write-Host "立即測試任務（可選）：" -ForegroundColor Cyan
Write-Host "  Start-ScheduledTask -TaskName '$taskName'" -ForegroundColor Gray
Write-Host ""
Write-Host "查看日誌：" -ForegroundColor Cyan
Write-Host "  Get-WinEvent -LogName 'Microsoft-Windows-TaskScheduler/Operational' | Where-Object {$_.Message -contains '$taskName'}" -ForegroundColor Gray
Write-Host ""
Write-Host "刪除任務（如需要）：" -ForegroundColor Cyan
Write-Host "  Unregister-ScheduledTask -TaskName '$taskName' -Confirm" -ForegroundColor Gray
Write-Host ""

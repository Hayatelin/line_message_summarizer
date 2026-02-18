# Windows 簡化部署指南

## 📋 目錄
1. [快速開始（5分鐘）](#快速開始5分鐘)
2. [詳細步驟](#詳細步驟)
3. [Windows工作排程器設置](#windows工作排程器設置)
4. [常見問題排除](#常見問題排除)
5. [卸載/重新安裝](#卸載重新安裝)

---

## 快速開始（5分鐘）

### 前置條件
- Windows 10 / 11
- Python 3.8+ （從 [python.org](https://www.python.org/downloads/) 下載，安裝時勾選「Add Python to PATH」）
- LINE Channel Access Token
- Anthropic API Key

### 一鍵設置步驟

1. **下載並解壓項目**
   ```
   下載 line_message_summarizer 到任意位置
   例: C:\Users\YourName\Documents\line_message_summarizer
   ```

2. **執行設置腳本**
   ```bash
   # 在項目根目錄打開 PowerShell（按 Shift + 右鍵 > 在此處開啟 PowerShell）
   .\setup_windows.ps1
   ```

3. **配置 .env 文件**
   ```bash
   # 編輯 .env 文件（自動生成的文件）
   # 填入您的 TOKEN 和 API KEY
   ```

4. **驗證安裝**
   ```bash
   .\run_test.bat
   ```

5. **設置自動排程**
   ```bash
   .\schedule_task.ps1
   ```

完成！🎉 系統將在每天 08:00 自動執行。

---

## 詳細步驟

### 步驟 1: 準備環境

#### 1.1 檢查 Python 版本
```bash
python --version
# 應該顯示 Python 3.8 或更新版本
```

如果沒有安裝 Python：
- 訪問 [python.org](https://www.python.org/downloads/)
- 下載 Python 3.11 或 3.13
- 安裝時**必須勾選** "Add Python to PATH"

#### 1.2 建立虛擬環境（可選，但建議）
```bash
cd C:\Users\YourName\Documents\line_message_summarizer
python -m venv venv
venv\Scripts\activate
```

### 步驟 2: 安裝依賴

```bash
# 確保在項目目錄
cd C:\Users\YourName\Documents\line_message_summarizer

# 安裝所有依賴
pip install -r requirements.txt
```

預期輸出應該包含：
```
Successfully installed line-bot-sdk-3.22.0 anthropic pytz jieba ...
```

### 步驟 3: 配置 .env 文件

1. **複製模板文件**
   ```bash
   copy .env.example .env
   ```

2. **編輯 .env 文件**（用任意文本編輯器打開）
   ```
   # LINE 配置
   LINE_CHANNEL_ACCESS_TOKEN=你的_channel_access_token_here

   # Anthropic 配置
   ANTHROPIC_API_KEY=你的_anthropic_api_key_here

   # 目標群組（可填多個，用逗號分隔）
   TARGET_GROUP_IDS=C1234567890abcdef,C0987654321fedcba

   # 使用者 ID
   USER_ID=U1234567890abcdef

   # 時區
   TIMEZONE=Asia/Taipei
   ```

3. **保存文件**

### 步驟 4: 測試系統

#### 4.1 運行單元測試
```bash
pytest tests/ -v
```

預期結果：
```
67 passed in X.XXs
```

#### 4.2 手動執行一次管道（測試功能）
```bash
python -c "
import asyncio
from src.agent_scheduler import execute_pipeline
result = asyncio.run(execute_pipeline())
print(f'結果: {result}')
"
```

這會執行一次完整的爬蟲→處理→摘要→發送流程。

---

## Windows工作排程器設置

### 方式 1: 使用 PowerShell 腳本自動設置（推薦）

創建文件 `schedule_task.ps1`：

```powershell
# 以管理員身份運行此腳本

# 定義參數
$projectPath = "C:\Users\YourName\Documents\line_message_summarizer"
$pythonExe = "$projectPath\venv\Scripts\python.exe"  # 如果使用虛擬環境
# 或
$pythonExe = "python"  # 如果系統 Python 在 PATH

$taskName = "LINE Message Summarizer"
$taskDescription = "自動爬蟲 LINE 群組訊息並生成每日摘要"
$time = "08:00:00"

# 創建觸發器（每天 08:00）
$trigger = New-ScheduledTaskTrigger -Daily -At $time

# 創建行動（執行 Python 腳本）
$action = New-ScheduledTaskAction `
    -Execute $pythonExe `
    -Argument "$projectPath\src\agent_scheduler.py" `
    -WorkingDirectory $projectPath

# 創建任務設置
$settings = New-ScheduledTaskSettingsSet `
    -AllowStartIfOnBatteries `
    -DontStopIfGoingOnBatteries `
    -StartWhenAvailable `
    -RunOnlyIfNetworkAvailable

# 創建或更新任務
Register-ScheduledTask `
    -TaskName $taskName `
    -Description $taskDescription `
    -Trigger $trigger `
    -Action $action `
    -Settings $settings `
    -Force

Write-Host "✅ 任務已創建！將在每天 $time 自動執行"
```

**執行步驟：**
1. 以**管理員身份**打開 PowerShell
2. 編輯腳本中的 `$projectPath` 為您的實際路徑
3. 運行：`.\schedule_task.ps1`

### 方式 2: 手動設置（如果腳本失敗）

#### 2.1 打開工作排程器
- 按 `Win + R`
- 輸入 `taskschd.msc`
- 按 Enter

#### 2.2 創建基本任務
1. 左側選單 → "建立基本工作"
2. 名稱：`LINE Message Summarizer`
3. 描述：`自動爬蟲 LINE 群組訊息並生成每日摘要`
4. 按 "下一步"

#### 2.3 設置觸發器
1. 選擇 "每天"
2. 時間：08:00
3. 按 "下一步"

#### 2.4 設置操作
1. 選擇 "啟動程式"
2. 程式/指令碼：`C:\Users\YourName\Documents\line_message_summarizer\venv\Scripts\python.exe`
   （或直接 `python` 如果已在 PATH）
3. 新增引數：`src\agent_scheduler.py`
4. 開始位置：`C:\Users\YourName\Documents\line_message_summarizer`
5. 按 "下一步"

#### 2.5 完成
1. 按 "完成"
2. 完成！✅

### 驗證任務是否設置成功

```bash
# 查看所有排程任務
Get-ScheduledTask | Where-Object {$_.TaskName -eq "LINE Message Summarizer"}

# 查看任務詳情
Get-ScheduledTaskInfo -TaskName "LINE Message Summarizer"
```

---

## 常見問題排除

### ❌ 問題 1: "Python not found" 錯誤

**症狀：**
```
python: command not found
```

**解決方案：**
1. 重新安裝 Python，**必須勾選** "Add Python to PATH"
2. 安裝後重啟 PowerShell/CMD
3. 驗證：`python --version`

---

### ❌ 問題 2: 找不到模塊錯誤

**症狀：**
```
ModuleNotFoundError: No module named 'linebot'
```

**解決方案：**
```bash
# 重新安裝依賴
pip install -r requirements.txt --force-reinstall
```

---

### ❌ 問題 3: .env 文件找不到

**症狀：**
```
KeyError: 'LINE_CHANNEL_ACCESS_TOKEN'
```

**解決方案：**
1. 確認 `.env` 文件在項目根目錄
2. 確認 `.env` 不是 `.env.txt`（需要無副檔名）
3. 確認已填入必要的值
4. 重新啟動程式

---

### ❌ 問題 4: 工作排程器任務未執行

**診斷步驟：**
1. 在工作排程器中右鍵點擊任務
2. 選擇 "執行"
3. 查看日誌檔案：`logs/execution_YYYY-MM-DD.log`

**常見原因：**
- Python 路徑不正確 → 使用完整路徑（如 `C:\Python313\python.exe`）
- 網路未連接 → 確認網路連接
- API Key 無效 → 驗證 .env 文件中的 TOKEN

---

### ❌ 問題 5: 編碼錯誤（中文亂碼）

**症狀：**
```
UnicodeEncodeError: 'gbk' codec can't encode
```

**解決方案：**
1. 在 PowerShell 中設置編碼：
   ```bash
   [Console]::OutputEncoding = [System.Text.Encoding]::UTF8
   ```
2. 在虛擬環境中設置環境變數：
   ```bash
   $env:PYTHONIOENCODING="utf-8"
   ```

---

## 日誌查看

### 查看最新執行日誌
```bash
# 列出所有日誌
dir logs/

# 查看今天的日誌
type logs/execution_2026-02-18.log

# 實時查看（如果正在執行）
tail -f logs/execution_2026-02-18.log
```

### 日誌位置
```
line_message_summarizer/
└── logs/
    ├── execution_2026-02-17.log
    ├── execution_2026-02-18.log
    └── ...
```

---

## 監控和維護

### 檢查系統狀態

```bash
# 驗證配置
python -c "
from src.config import Config
config = Config()
print(f'目標群組: {len(config.target_group_ids)} 個')
print(f'時區: {config.timezone}')
print(f'排程時間: 08:00')
"
```

### 手動執行測試

```bash
# 執行完整管道
python -c "
import asyncio
from src.agent_scheduler import execute_pipeline
result = asyncio.run(execute_pipeline())
print(result)
"

# 運行單元測試
pytest tests/ -v

# 生成覆蓋率報告
pytest tests/ --cov=src --cov-report=html
```

---

## 卸載/重新安裝

### 卸載

**步驟 1: 刪除工作排程器任務**
```bash
# 以管理員身份執行
Unregister-ScheduledTask -TaskName "LINE Message Summarizer" -Confirm:$false
```

**步驟 2: 刪除虛擬環境（可選）**
```bash
# 在項目目錄
rmdir /s venv
```

**步驟 3: 刪除項目文件夾**
```bash
# 直接在檔案管理器中刪除文件夾
```

### 重新安裝

```bash
# 重複「快速開始」中的步驟 1-5
```

---

## 快速參考命令

| 操作 | 命令 |
|------|------|
| 激活虛擬環境 | `venv\Scripts\activate` |
| 停用虛擬環境 | `deactivate` |
| 安裝依賴 | `pip install -r requirements.txt` |
| 運行測試 | `pytest tests/ -v` |
| 手動執行管道 | `python -c "import asyncio; from src.agent_scheduler import execute_pipeline; asyncio.run(execute_pipeline())"` |
| 查看日誌 | `dir logs/` |
| 刪除任務 | `Unregister-ScheduledTask -TaskName "LINE Message Summarizer"` |

---

## 故障排除流程圖

```
出現錯誤？
    ↓
檢查錯誤訊息
    ├─ "Python not found" → 重新安裝 Python，勾選 PATH
    ├─ "ModuleNotFoundError" → pip install -r requirements.txt
    ├─ "KeyError" → 檢查 .env 文件配置
    ├─ 任務未執行 → 工作排程器中驗證任務
    └─ 查看 logs/ 目錄中的詳細日誌
```

---

## 後續支持

如有問題：
1. 查看 `logs/` 目錄中的執行日誌
2. 檢查 `.env` 文件配置
3. 嘗試手動執行管道測試
4. 參考 [CONTRIBUTING.md](./.github/CONTRIBUTING.md) 提交 Issue

---

**最後更新**: 2026-02-18
**適用於**: Windows 10 / Windows 11
**Python 版本**: 3.8+
**LINE Bot SDK**: v3.0+

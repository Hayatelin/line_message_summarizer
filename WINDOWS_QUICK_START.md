# ⚡ Windows 快速開始卡片

> 5分鐘內將系統部署到您的Windows電腦上

## 📋 前置條件

- Windows 10 或 11
- Python 3.8+ （[下載](https://www.python.org/downloads/)）
  - ⚠️ **安裝時必須勾選** "Add Python to PATH"
- LINE Channel Access Token
- Anthropic API Key

## 🚀 5分鐘快速部署

### 步驟 1: 設置環境（自動化）
```powershell
# 在項目根目錄打開 PowerShell（Shift + 右鍵 > 在此處開啟 PowerShell）
.\setup_windows.ps1
```

**這個腳本會自動：**
- ✅ 檢查 Python 版本
- ✅ 創建虛擬環境
- ✅ 安裝所有依賴
- ✅ 生成 .env 文件
- ✅ 運行測試驗證

### 步驟 2: 配置 API Token
```
編輯 .env 文件（記事本或任何文本編輯器）
填入：
  LINE_CHANNEL_ACCESS_TOKEN = 你的token
  ANTHROPIC_API_KEY = 你的api key
  TARGET_GROUP_IDS = C12345...
  USER_ID = U12345...
  TIMEZONE = Asia/Taipei
```

### 步驟 3: 設置自動排程
```powershell
# 以管理員身份打開 PowerShell，然後執行
.\schedule_task.ps1
```

**完成！** ✅ 系統將在每天 08:00 自動執行

---

## 📚 常用命令

### 激活虛擬環境
```bash
# 激活
venv\Scripts\activate

# 停用
deactivate
```

### 手動執行一次
```powershell
# 方法 1: 執行 PowerShell 腳本
.\run_manual.ps1

# 方法 2: 直接執行 Python
python -c "import asyncio; from src.agent_scheduler import execute_pipeline; asyncio.run(execute_pipeline())"
```

### 運行測試
```bash
# 所有測試
pytest tests/ -v

# 單個模塊測試
pytest tests/test_crawler.py -v
pytest tests/test_processor.py -v
pytest tests/test_summarizer.py -v
pytest tests/test_scheduler.py -v

# 生成覆蓋率報告
pytest tests/ --cov=src --cov-report=html
```

### 查看日誌
```bash
# 列出所有日誌
dir logs/

# 查看最新日誌
type logs/execution_2026-02-18.log

# 搜索錯誤
findstr ERROR logs/*.log
```

### 工作排程器管理
```powershell
# 查看任務
Get-ScheduledTask -TaskName "LINE Message Summarizer"

# 查看任務詳情
Get-ScheduledTaskInfo -TaskName "LINE Message Summarizer"

# 立即執行任務
Start-ScheduledTask -TaskName "LINE Message Summarizer"

# 刪除任務
Unregister-ScheduledTask -TaskName "LINE Message Summarizer" -Confirm
```

---

## ⚠️ 常見問題速查

| 問題 | 解決方案 |
|------|--------|
| **"python: command not found"** | 重新安裝 Python，勾選 "Add Python to PATH" |
| **"ModuleNotFoundError"** | `pip install -r requirements.txt` |
| **".env 文件找不到"** | `copy .env.example .env` |
| **工作排程器任務不執行** | 檢查 .env 配置，查看 logs/ 日誌 |
| **中文亂碼** | `$env:PYTHONIOENCODING="utf-8"` |
| **任務需要管理員** | 以管理員身份運行 schedule_task.ps1 |

詳細說明參考 **WINDOWS_DEPLOYMENT.md**

---

## 📁 重要文件位置

```
line_message_summarizer/
├── setup_windows.ps1          ← 一鍵設置
├── schedule_task.ps1          ← 配置自動排程（需管理員）
├── run_manual.ps1             ← 手動執行一次
├── .env                        ← API 配置（編輯此文件）
├── .env.example                ← 配置模板
├── WINDOWS_DEPLOYMENT.md       ← 詳細指南
├── requirements.txt            ← 依賴列表
├── venv/                       ← 虛擬環境
├── logs/                       ← 執行日誌
├── src/
│   ├── agent_scheduler.py      ← 排程器（自動執行）
│   ├── agent_crawler.py        ← 訊息爬蟲
│   ├── agent_processor.py      ← 訊息處理
│   ├── agent_summarizer.py     ← 摘要生成
│   └── utils/
│       ├── line_handler.py     ← LINE API 整合
│       └── sender.py           ← 訊息發送
├── tests/                      ← 67 個單元測試
└── data/                       ← 中間數據
```

---

## 🔍 驗證安裝成功

```powershell
# 檢查 Python
python --version              # 應顯示 3.8+

# 檢查依賴
pip list | grep linebot        # 應顯示 line-bot-sdk 3.22.0+

# 運行測試
pytest tests/ -v               # 應顯示 67 passed

# 檢查工作排程器任務
Get-ScheduledTask -TaskName "LINE Message Summarizer"
# 應該能看到任務信息
```

---

## 🛠️ 維護和故障排除

### 完全卸載（如需重新安裝）
```powershell
# 1. 刪除工作排程器任務
Unregister-ScheduledTask -TaskName "LINE Message Summarizer" -Confirm:$false

# 2. 刪除虛擬環境
rmdir /s venv

# 3. 删除或重新配置 .env
del .env
```

### 查看詳細日誌
```bash
# 實時日誌查看
python -c "
import os, time
log_dir = 'logs'
if os.path.exists(log_dir):
    files = sorted(os.listdir(log_dir), reverse=True)
    if files:
        print(open(os.path.join(log_dir, files[0])).read())
"
```

### 測試 API 連接
```python
# 運行以下 Python 代碼測試
python -c "
from src.config import Config
from src.utils.line_handler import LineHandler

config = Config()
handler = LineHandler(config.line_channel_access_token)

print(f'✅ LINE Token 有效')
print(f'✅ 目標群組: {len(config.target_group_ids)} 個')
"
```

---

## 📞 需要幫助？

1. **查看詳細文檔**：WINDOWS_DEPLOYMENT.md
2. **查看執行日誌**：logs/ 目錄
3. **檢查配置**：.env 文件
4. **運行測試**：`pytest tests/ -v`

---

**最後更新**: 2026-02-18 | **適用於**: Windows 10/11 | **Python**: 3.8+

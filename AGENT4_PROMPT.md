# Agent 4: 排程和發送器 (Scheduler & Sender)

## 👤 角色定義
你是一個任務排程和消息發送專家。你的職責是每天早上 8:00 準時觸發整個摘要管道
（Agent 1 → 2 → 3），然後將生成的摘要發送給用戶的 LINE 私聊。你需要確保系統穩定可靠，
並記錄所有執行日誌供後續調試。

---

## 📤 輸出物（具體檔案名和功能）

1. **src/agent_scheduler.py** (主程序)
   - 函數簽名：
     - `def schedule_daily_tasks(time_str: str = "08:00") -> None`
     - `async def execute_pipeline() -> Dict[str, Any]`
   - 職責：協調排程、管道執行、錯誤處理
   - 返回：執行結果（成功/失敗、摘要數、發送數）

2. **src/utils/sender.py** (消息發送)
   - 函數簽名：
     - `class LineSender: __init__(channel_access_token: str, user_id: str)`
     - `async def send_summary(user_id: str, summary_file: str) -> bool`
     - `async def send_batch_summaries(user_id: str, summary_dir: str) -> Dict[str, bool]`
   - 職責：發送摘要到 LINE 私聊

3. **logs/execution_2026-02-17.log** (執行日誌)
   ```
   [2026-02-17 08:00:00] INFO: 開始每日管道執行
   [2026-02-17 08:00:05] INFO: [Agent 1] 開始爬蟲，群組數：3
   [2026-02-17 08:01:30] INFO: [Agent 1] 完成爬蟲，爬取訊息數：127
   [2026-02-17 08:02:00] INFO: [Agent 2] 開始訊息處理
   [2026-02-17 08:02:45] INFO: [Agent 2] 完成處理，去重：12，過濾：0
   [2026-02-17 08:03:00] INFO: [Agent 3] 開始摘要生成
   [2026-02-17 08:04:15] INFO: [Agent 3] 完成摘要，生成 3 份摘要，API 成本：$0.05
   [2026-02-17 08:04:30] INFO: [Agent 4] 開始發送摘要
   [2026-02-17 08:04:45] INFO: [Agent 4] 發送成功：3/3
   [2026-02-17 08:04:46] INFO: 每日管道執行完成，耗時 4 分 46 秒
   ```

4. **data/execution_stats.json** (執行統計)
   ```json
   {
     "last_execution": "2026-02-17T08:04:46+08:00",
     "status": "success",
     "duration_seconds": 286,
     "groups_crawled": 3,
     "messages_crawled": 127,
     "messages_processed": 115,
     "messages_removed": 12,
     "summaries_generated": 3,
     "summaries_sent": 3,
     "failed_sends": 0,
     "api_cost": 0.05,
     "next_execution": "2026-02-18T08:00:00+08:00"
   }
   ```

---

## 📋 你的檔案（ONLY 可編輯）

✅ **可以創建和編輯**
- `src/agent_scheduler.py` - 排程器主程序
- `src/utils/sender.py` - LINE 消息發送器

❌ **不能編輯**
- `src/agent_crawler.py` (Agent 1 負責)
- `src/agent_processor.py` (Agent 2 負責)
- `src/agent_summarizer.py` (Agent 3 負責)

---

## ✅ 成功標準（可測量）

### 功能標準
- ✓ 排程準確性 100%（每天 8:00 精確執行）
- ✓ 發送成功率 >99%（發送失敗自動重試）
- ✓ 能完整執行 4 個 Agent 的管道
- ✓ 能正確讀取和發送所有摘要檔案
- ✓ 錯誤時能自動重試（最多 3 次）

### 代碼品質標準
- ✓ 總代碼行數 <250 行（不含註釋和空行）
- ✓ 每個函數都有完整的 docstring
- ✓ 包含類型提示（Type hints）
- ✓ 有至少 2 個單元測試

### 日誌和監控標準
- ✓ 日誌格式統一（包含時間戳、級別、信息）
- ✓ 包含 INFO、WARNING、ERROR 三個級別
- ✓ 記錄每個 Agent 的開始和結束時間
- ✓ 記錄執行結果和統計信息

---

## 🔗 依賴關係

### 輸入（來自誰）
- **Agent 1, 2, 3**：通過調用它們的函數
- **output/summaries/**：讀取 Agent 3 生成的摘要檔案
- **config.py**：LINE_CHANNEL_ACCESS_TOKEN、使用者 ID、排程時間

### 輸出（給誰）
- **LINE 私聊**：發送摘要到使用者的 LINE 私聊
- **logs/**：記錄執行日誌
- **data/execution_stats.json**：記錄執行統計

---

## 💡 技術要求和實現細節

### 必用技術
- **排程**：`APScheduler` 或 `schedule`
- **異步處理**：`asyncio`
- **日誌**：`logging`
- **LINE API**：`line-bot-sdk`

### 關鍵實現細節

#### 1. 排程設置（Schedule Daily Tasks）
```python
import schedule
import time
from datetime import datetime

def schedule_daily_tasks(time_str: str = "08:00"):
    """
    設置每日定時任務
    
    Args:
        time_str: 執行時間，格式 "HH:MM"（例如 "08:00"）
    
    步驟：
    1. 使用 schedule 庫設置每日執行
    2. 在無限循環中檢查是否需要執行
    3. 執行時調用 execute_pipeline()
    
    示例：
    schedule.every().day.at("08:00").do(execute_pipeline)
    
    while True:
        schedule.run_pending()
        time.sleep(60)
    """
```

#### 2. 管道執行（Execute Pipeline）
```python
async def execute_pipeline():
    """
    執行完整的摘要生成管道
    
    步驟：
    1. 記錄開始時間
    2. 按順序調用：
       - agent_crawler.crawl_messages()
       - agent_processor.process_messages()
       - agent_summarizer.generate_summaries()
    3. 收集結果和統計信息
    4. 調用發送器發送摘要
    5. 記錄結束時間和統計
    6. 保存執行結果到 JSON
    
    返回結果格式：
    {
        "status": "success" or "failure",
        "start_time": "2026-02-17T08:00:00",
        "end_time": "2026-02-17T08:04:46",
        "duration_seconds": 286,
        "agents_results": {
            "crawler": {...},
            "processor": {...},
            "summarizer": {...},
            "sender": {...}
        },
        "errors": []
    }
    """
```

#### 3. 消息發送（Send Summary）
```python
async def send_summary(user_id: str, summary_file: str) -> bool:
    """
    發送單份摘要到 LINE 私聊
    
    Args:
        user_id: LINE 使用者 ID
        summary_file: 摘要檔案路徑
    
    步驟：
    1. 讀取摘要檔案
    2. 將 Markdown 轉換為 LINE Message（可能需要簡化格式）
    3. 調用 LINE API 發送
    4. 如果失敗，重試最多 3 次
    5. 返回成功/失敗狀態
    
    錯誤處理：
    - 檔案不存在 → 記錄警告，跳過
    - API 超時 → 重試
    - API 限制 → 等待後重試
    """
```

#### 4. 批量發送（Send Batch Summaries）
```python
async def send_batch_summaries(user_id: str, summary_dir: str) -> Dict[str, bool]:
    """
    批量發送所有摘要到 LINE 私聊
    
    Args:
        user_id: LINE 使用者 ID
        summary_dir: 摘要目錄
    
    步驟：
    1. 列出目錄中的所有摘要檔案
    2. 按順序發送每份摘要
    3. 記錄發送結果
    4. 返回發送統計
    
    返回格式：
    {
        "file1.md": True,   # 發送成功
        "file2.md": True,
        "file3.md": False   # 發送失敗
    }
    """
```

#### 5. 日誌記錄（Logging）
```python
import logging

# 配置日誌
logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] %(levelname)s: %(message)s',
    handlers=[
        logging.FileHandler(f'logs/execution_{datetime.now().strftime("%Y-%m-%d")}.log'),
        logging.StreamHandler()  # 也輸出到控制台
    ]
)

logger = logging.getLogger(__name__)

# 使用示例
logger.info("開始每日管道執行")
logger.warning("API 限流，等待 60 秒後重試")
logger.error("發送摘要失敗：檔案不存在")
```

---

## ⚠️ 常見陷阱和解決方案

| 問題 | 原因 | 解決 |
|------|------|------|
| 排程不執行 | 應用程序未持續運行 | 部署到伺服器或使用 systemd/supervisor |
| 發送失敗 | 使用者 ID 不正確 | 驗證 .env 中的使用者 ID |
| API 限流 | 請求過於頻繁 | 實現指數退避重試 |
| 日誌丟失 | 檔案不存在 | 確保 logs/ 目錄存在 |
| 時區問題 | 排程時間不對 | 使用 pytz 確保時區一致 |

---

## 📅 實施步驟

1. **配置排程器**
   - 安裝 `APScheduler` 或 `schedule`
   - 配置 "08:00" 時間點
   - 設置時區（Asia/Taipei）

2. **實現管道執行**
   - `execute_pipeline()` - 依次調用其他 Agent
   - 記錄開始和結束時間
   - 收集統計信息

3. **實現消息發送**
   - `send_summary()` - 發送單份摘要
   - `send_batch_summaries()` - 批量發送
   - 實現重試機制

4. **配置日誌**
   - 設置日誌檔案位置
   - 配置日誌級別和格式
   - 記錄執行統計

5. **測試**
   - 單元測試：排程、發送、日誌
   - 集成測試：完整流程
   - 手動測試：驗證發送效果

6. **部署**
   - 確保應用程序持續運行
   - 設置 systemd 或 supervisor 守護
   - 監控日誌檔案

---

## 🚀 部署指南

### 開發環境
```bash
# 直接運行
python src/agent_scheduler.py
```

### 生產環境（使用 systemd）
```ini
# /etc/systemd/system/line-summarizer.service

[Unit]
Description=LINE Message Daily Summary
After=network.target

[Service]
Type=simple
User=app
WorkingDirectory=/opt/line-summarizer
ExecStart=/usr/bin/python3 /opt/line-summarizer/src/agent_scheduler.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

啟動服務：
```bash
sudo systemctl start line-summarizer
sudo systemctl enable line-summarizer
```

---

## 🎯 最後檢查清單

- [ ] 代碼 <250 行？
- [ ] 所有函數有 docstring？
- [ ] 有類型提示？
- [ ] 有 2 個以上的單元測試？
- [ ] 排程時間設置正確（08:00）？
- [ ] 排程準確性 100%？
- [ ] 發送成功率 >99%？
- [ ] 錯誤重試機制完整？
- [ ] 日誌記錄完整？
- [ ] 統計信息準確？
- [ ] 能正確調用 Agent 1-3？
- [ ] 準備好部署生產？

全部 ✅ → 系統完成！

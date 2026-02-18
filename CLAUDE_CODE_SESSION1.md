# 🔴 Claude Code Session 1 - Agent 1 開發 Prompt

**Session 目標**：開發訊息爬蟲 (Agent 1)  
**預計時間**：2 小時  
**輸出物**：3 個 Python 檔案 + 測試  

---

## 📋 背景信息

### 系統概覽
你正在開發一個 **LINE 訊息每日摘要系統**。這是一個 4-Agent 系統：

```
Agent 1: 訊息爬蟲 ← 你現在開發的
    ↓ (輸出: raw_messages.json)
Agent 2: 訊息處理器
    ↓ (輸出: processed_messages.json)
Agent 3: 摘要生成器
    ↓ (輸出: summaries/*.md)
Agent 4: 排程和發送器
    ↓ (發送到 LINE 私聊)
```

### 項目信息
- **語言**：Python 3.8+
- **主要依賴**：`line-bot-sdk`, `asyncio`, `aiohttp`, `pytz`
- **代碼風格**：async/await, 完整 docstring, 類型提示

---

## 👤 你的角色：Agent 1 開發者

你的責任：
- ✅ 從 LINE 群組爬蟲前一天的所有訊息
- ✅ 轉換為標準的 JSON 格式
- ✅ 支持多個群組同時爬蟲
- ✅ 正確處理中文訊息和附件
- ✅ 包含完整的錯誤處理和日誌

---

## 📤 具體任務

### 任務 1：實現 `src/utils/line_handler.py`

**職責**：封裝所有 LINE API 調用

**需要實現的函數**：

```python
class LineHandler:
    """LINE Messaging API 處理器"""
    
    def __init__(self, channel_access_token: str):
        """初始化 LINE Handler
        
        Args:
            channel_access_token: LINE Channel Access Token
        """
        
    async def get_group_messages(
        self, 
        group_id: str, 
        start_time: int, 
        end_time: int
    ) -> List[dict]:
        """從 LINE API 獲取群組訊息
        
        Args:
            group_id: LINE 群組 ID (格式: C + 32 個字符)
            start_time: 開始時間戳 (毫秒級 Unix time)
            end_time: 結束時間戳 (毫秒級 Unix time)
        
        Returns:
            訊息列表，每個訊息包含以下字段：
            {
                "message_id": str,
                "timestamp": str (ISO 8601 格式),
                "sender_id": str,
                "sender_name": str,
                "message_type": str (text, image, file, video, audio, etc.),
                "content": str,
                "attachments": List[str]  # URL 列表
            }
        
        Raises:
            Exception: API 調用失敗時
        """
    
    async def get_group_members(self, group_id: str) -> Dict[str, str]:
        """獲取群組成員映射 (user_id → name)
        
        Args:
            group_id: LINE 群組 ID
        
        Returns:
            {"U123...": "Alice", "U456...": "Bob", ...}
        
        Raises:
            Exception: API 調用失敗時
        """
```

**技術要求**：
- 使用 `line-bot-sdk` 的 `LineMessagingApi`
- 使用 `asyncio` 進行異步調用
- 實現重試機制（最多 3 次，指數退避）
- 正確處理時間戳轉換（毫秒 → ISO 8601）
- 處理各種訊息類型（text, image, file, etc.）

---

### 任務 2：實現 `src/agent_crawler.py`

**職責**：協調整個爬蟲流程

**需要實現的函數**：

```python
async def crawl_messages(
    group_ids: List[str], 
    date: str
) -> Dict[str, List[dict]]:
    """爬蟲 LINE 群組訊息
    
    Args:
        group_ids: 群組 ID 列表
        date: 日期字符串 (格式: "YYYY-MM-DD", 例如 "2026-02-17")
    
    Returns:
        {
            "group_id_1": [messages],
            "group_id_2": [messages],
            ...
        }
    
    Raises:
        Exception: 爬蟲失敗時
    """
```

**邏輯**：
1. 根據 `date` 計算開始時間和結束時間（前一天 00:00 - 23:59）
2. 時區：使用 Asia/Taipei（台灣時區）
3. 並發爬蟲所有群組（使用 `asyncio.gather()`）
4. 獲取群組成員映射
5. 處理每個訊息（轉換格式、提取內容）
6. 保存為 JSON 檔案
7. 返回結果

---

### 任務 3：實現 `tests/test_crawler.py`

**最少需要 1 個測試**（推薦 3+ 個）：

```python
@pytest.mark.asyncio
async def test_crawl_messages_basic():
    """測試基本爬蟲功能"""
    # Mock LINE API
    # 調用 crawl_messages()
    # 驗證返回的 JSON 格式和內容
    pass

# 其他可能的測試：
# - test_chinese_message_handling: 中文訊息編碼
# - test_attachment_handling: 附件處理
# - test_multiple_groups: 多群組爬蟲
# - test_error_handling: 錯誤處理和重試
```

---

## 📋 檔案結構

你需要創建或修改的檔案：

```
src/
├── config.py                  ← 已存在（讀取 .env）
├── models.py                  ← 已存在（數據模型）
├── agent_crawler.py           ← 你要創建 ✨
│
└── utils/
    └── line_handler.py        ← 你要創建 ✨

tests/
└── test_crawler.py            ← 你要創建 ✨

data/
└── raw_messages/              ← 爬蟲輸出檔案位置

logs/                           ← 日誌檔案位置
```

---

## 📤 輸出 JSON 格式（必須精確符合）

```json
{
  "group_id": "C1234567890abcdef",
  "group_name": "我的工作群",
  "date": "2026-02-17",
  "total_messages": 42,
  "messages": [
    {
      "message_id": "100001",
      "timestamp": "2026-02-17T09:15:30+08:00",
      "sender_id": "U1234567890abcdef",
      "sender_name": "Alice",
      "message_type": "text",
      "content": "今天的會議時間是？",
      "attachments": []
    },
    {
      "message_id": "100002",
      "timestamp": "2026-02-17T09:16:00+08:00",
      "sender_id": "U0987654321fedcba",
      "sender_name": "Bob",
      "message_type": "image",
      "content": "[Image]",
      "attachments": ["https://example.com/image.jpg"]
    },
    {
      "message_id": "100003",
      "timestamp": "2026-02-17T09:17:00+08:00",
      "sender_id": "U1111111111111111",
      "sender_name": "Charlie",
      "message_type": "text",
      "content": "會議改到下午3點",
      "attachments": []
    }
  ]
}
```

**重點**：
- ✅ `timestamp` 必須是 ISO 8601 格式（+08:00 台灣時區）
- ✅ `message_type` 根據訊息類型填寫（text, image, file, video, audio, sticker）
- ✅ 中文訊息必須正確顯示（使用 `ensure_ascii=False`）
- ✅ `attachments` 是 URL 列表（如果沒有附件就是 `[]`）

---

## ✅ 成功標準（必須全部達到）

### 功能標準
- [ ] 能無錯誤連接 LINE Messaging API
- [ ] 能爬取指定日期的所有訊息（100% 正確率）
- [ ] 支持多個群組同時爬蟲
- [ ] 正確處理中文訊息（編碼和顯示）
- [ ] 處理圖片、語音、檔案等附件
- [ ] 包含群組成員信息（sender_name 正確映射）
- [ ] 輸出 JSON 檔案到 `data/raw_messages/{group_id}_{date}.json`

### 代碼品質標準
- [ ] 總代碼行數 **<350 行**（不含註釋和空行）
- [ ] 所有函數都有**完整的 docstring**（三引號文檔字符串）
- [ ] 包含**完整的類型提示**（Type hints）
- [ ] **異常處理完整**（try-except, 重試機制）
- [ ] **有至少 1 個單元測試**（推薦 3 個）
- [ ] **日誌清晰**（使用 Python logging）
- [ ] 遵守 **PEP 8** 風格指南

### 測試標準
- [ ] 單元測試至少 1 個（使用 pytest）
- [ ] 測試覆蓋率 >70%
- [ ] 包含對 mock 的 LINE API 的測試

---

## 🔗 環境配置

### 你的環境已準備好：

1. **Python 3.8+** 已安裝
2. **虛擬環境** 已激活
3. **依賴** 已安裝（requirements.txt）
4. **.env 檔案** 已準備：
   ```
   LINE_CHANNEL_ACCESS_TOKEN=your_token
   ANTHROPIC_API_KEY=your_key
   TARGET_GROUP_IDS=C1234567890abcdef,C0987654321fedcba
   USER_ID=U1234567890abcdef
   TIMEZONE=Asia/Taipei
   ```

### 你需要檢查：
- [ ] `.env` 檔案中的 `LINE_CHANNEL_ACCESS_TOKEN` 正確
- [ ] 至少有一個有效的群組 ID（格式：C + 32 個字符）

---

## 💡 實現提示

### 時間戳轉換示例
```python
import datetime
import pytz

# LINE API 返回毫秒級 Unix time，需轉換為 ISO 8601

# 範例：獲取昨天的時間範圍
tz = pytz.timezone('Asia/Taipei')
today = datetime.datetime.now(tz).date()
yesterday = today - datetime.timedelta(days=1)

# 昨天 00:00:00
start_time = int(datetime.datetime.combine(
    yesterday, 
    datetime.time.min
).replace(tzinfo=tz).timestamp() * 1000)  # 轉為毫秒

# 昨天 23:59:59
end_time = int(datetime.datetime.combine(
    yesterday,
    datetime.time.max
).replace(tzinfo=tz).timestamp() * 1000)  # 轉為毫秒

# 轉換訊息時間戳為 ISO 8601
message_timestamp_ms = 1708133730000  # 毫秒級
dt = datetime.datetime.fromtimestamp(message_timestamp_ms / 1000, tz=tz)
iso_timestamp = dt.isoformat()  # "2026-02-17T09:15:30+08:00"
```

### 異步並發示例
```python
import asyncio

async def crawl_messages(group_ids, date):
    # 並發爬蟲所有群組
    tasks = [
        crawl_single_group(gid, date) 
        for gid in group_ids
    ]
    results = await asyncio.gather(*tasks)
    return dict(zip(group_ids, results))

async def crawl_single_group(group_id, date):
    # 爬蟲單個群組
    pass
```

### 重試機制示例
```python
import asyncio

async def api_call_with_retry(func, *args, max_retries=3, **kwargs):
    """呼叫 API，失敗時重試（指數退避）"""
    for attempt in range(max_retries):
        try:
            return await func(*args, **kwargs)
        except Exception as e:
            if attempt == max_retries - 1:
                raise
            wait_time = 2 ** attempt  # 1, 2, 4 秒
            logger.warning(f"API 調用失敗，{wait_time} 秒後重試: {e}")
            await asyncio.sleep(wait_time)
```

---

## 📊 代碼結構參考

```python
# src/agent_crawler.py

import logging
from typing import Dict, List
import asyncio
from datetime import datetime, timedelta
import pytz
from pathlib import Path

from src.config import Config
from src.utils.line_handler import LineHandler

logger = logging.getLogger(__name__)

async def crawl_messages(
    group_ids: List[str], 
    date: str
) -> Dict[str, List[dict]]:
    """
    爬蟲 LINE 群組訊息
    
    完整的 docstring...
    """
    logger.info(f"開始爬蟲，日期：{date}，群組數：{len(group_ids)}")
    
    # 初始化 LineHandler
    handler = LineHandler(Config.LINE_CHANNEL_ACCESS_TOKEN)
    
    # 計算時間範圍
    # ... 時間轉換邏輯 ...
    
    # 並發爬蟲所有群組
    # ... asyncio.gather 邏輯 ...
    
    # 保存為 JSON
    # ... JSON 保存邏輯 ...
    
    logger.info(f"爬蟲完成，爬取訊息數：...")
    return results
```

---

## 🚀 執行步驟

### 步驟 1：創建檔案框架
你會創建 3 個檔案：
1. `src/agent_crawler.py`
2. `src/utils/line_handler.py`
3. `tests/test_crawler.py`

### 步驟 2：實現 LineHandler
- 類初始化
- `get_group_members()` 方法
- `get_group_messages()` 方法
- 附加：時間戳轉換、訊息類型判斷

### 步驟 3：實現 crawl_messages()
- 時間範圍計算
- 並發爬蟲邏輯
- JSON 保存邏輯

### 步驟 4：編寫測試
- 至少 1 個基本測試
- Mock LINE API

### 步驟 5：驗證
- 代碼行數 <350
- 所有函數有 docstring
- 有類型提示
- 測試通過

---

## ⚠️ 常見陷阱（避免）

| 陷阱 | 症狀 | 解決 |
|------|------|------|
| 中文亂碼 | 訊息顯示為 `\u1234` | 使用 `json.dump(..., ensure_ascii=False)` |
| 時間戳錯誤 | 時間不對或格式混亂 | 確保轉換為 ISO 8601，時區為 +08:00 |
| 附件丟失 | 沒有得到圖片 URL | 確保檢查 `ImageSendMessage` 等類型 |
| API 限流 | 請求被拒絕 | 添加重試機制和延遲 |
| 缺少成員信息 | sender_name 為空 | 確保調用 `get_group_members()` |

---

## 📝 檢查清單（完成前必讀）

開始編碼前，確認：

```
準備部分
□ 你已讀了本 Prompt 的所有內容
□ 你理解了 4-Agent 系統的架構
□ 你知道自己要實現什麼

環境部分
□ 虛擬環境已激活
□ .env 檔案已準備
□ LINE_CHANNEL_ACCESS_TOKEN 正確
□ 至少有一個有效的群組 ID

代碼規範部分
□ 代碼行數目標：<350 行
□ 所有函數要有 docstring
□ 所有函數要有類型提示
□ 要有錯誤處理

測試部分
□ 要有至少 1 個單元測試
□ 測試要使用 mock
□ 測試要能運行並通過

完成後
□ 代碼行數檢查？
□ 所有測試通過？
□ JSON 格式符合示例？
□ 中文訊息正確？
```

---

## 🎯 開始吧！

準備好了嗎？

1. **閱讀** 本 Prompt 的所有內容
2. **提出問題** 如果有不清楚的地方
3. **開始編碼** 實現上述 3 個檔案
4. **測試** 確保所有功能正常
5. **驗證** 檢查所有成功標準

---

## 💬 如果你卡住了

### 常見問題

**Q: 不知道怎麼使用 LINE API？**
A: 查看 `line-bot-sdk` 的文檔和示例

**Q: 中文訊息亂碼？**
A: 在 JSON 保存時使用 `ensure_ascii=False`

**Q: 時間戳轉換出錯？**
A: 參考上面的「時間戳轉換示例」部分

**Q: 不知道怎麼寫測試？**
A: 使用 `pytest` 和 `unittest.mock`

---

**準備好開發了嗎？讓我們開始吧！** 🚀

首先，請確認：
1. 你已讀了本 Prompt
2. 你的環境已準備好
3. 你理解了目標和要求

然後回覆：「準備好開發 Agent 1 了」，我們就開始！

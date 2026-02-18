# 📅 Claude Code 其他 Session 的 Prompt

**用途**：Session 2, 3, 4 的參考模板  
**何時用**：Agent 1 完成後，開啟新 Session 時

---

## 🟠 Session 2 - Agent 2 開發 Prompt

**何時使用**：Agent 1 完成並測試通過後  
**所需上傳**：
- AGENT2_PROMPT.md
- 你已完成的 agent_crawler.py（作為參考）

---

### 給 Claude Code 的 Session 2 Prompt

```markdown
# 🟠 Claude Code Session 2 - Agent 2 開發 Prompt

**Session 目標**：開發訊息處理器 (Agent 2)  
**預計時間**：2 小時  
**輸出物**：2 個 Python 檔案 + 5+ 個測試  

---

## 背景

Agent 1（訊息爬蟲）已完成，輸出了原始訊息 JSON：

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
    }
    // ... 更多訊息
  ]
}
```

你現在需要處理這些訊息：
- ✅ 去除重複訊息
- ✅ 過濾垃圾訊息
- ✅ 分類訊息
- ✅ 提取關鍵詞
- ✅ 計算統計信息

---

## 👤 你的角色：Agent 2 開發者

責任：
- 從 Agent 1 讀取原始訊息 JSON
- 進行多層面的數據清理
- 輸出結構化的、高質量的訊息數據

---

## 📤 具體任務

### 任務 1：實現 `src/utils/message_parser.py`

需要實現的函數：

```python
def remove_duplicates(messages: List[dict]) -> List[dict]:
    """去除重複訊息
    
    重複定義：
    - 同一人在 5 分鐘內發送的完全相同的訊息
    - OR 訊息內容完全相同且時間相近（<10 分鐘）
    
    Args:
        messages: 原始訊息列表
    
    Returns:
        去重後的訊息列表（保留第一條，刪除後續重複）
    """

def filter_noise(messages: List[dict]) -> List[dict]:
    """過濾垃圾訊息
    
    過濾規則：
    - 機器人訊息（sender_name 包含 "Bot", "System"）
    - 斜線命令（content 以 "/" 開頭）
    - 僅包含表情符號的訊息
    - 空訊息
    
    Args:
        messages: 訊息列表
    
    Returns:
        過濾後的訊息列表
    """

def classify_messages(messages: List[dict]) -> List[dict]:
    """分類訊息
    
    分類規則：
    - "question": 包含 "？", "?", "怎樣", "如何" 等疑問詞
    - "action": 包含 "需要", "完成", "提醒", "會議"
    - "announcement": 以特定格式開頭（如 "【公告】"）
    - "discussion": 多人互動，長度 >100 字
    - "other": 其他
    
    Returns 格式：訊息增加 "category" 和 "importance" 字段
    """

def extract_keywords(messages: List[dict], top_n: int = 10) -> Dict[str, List[str]]:
    """提取關鍵詞
    
    步驟：
    1. 使用 jieba 進行中文分詞
    2. 去除停用詞
    3. 統計詞頻
    4. 返回出現最多的前 N 個詞
    
    Args:
        messages: 訊息列表
        top_n: 返回的關鍵詞數量
    
    Returns:
        {"keywords": ["會議", "完成", "報告"]}
    """

def calculate_importance(message: dict) -> float:
    """計算訊息重要性分數（0-1）
    
    計算公式：
    重要性 = 0.4 * 分類權重 + 0.3 * 詞頻權重 + 0.3 * 長度權重
    
    分類權重：
    - question: 0.9
    - action: 0.95
    - announcement: 0.8
    - discussion: 0.6
    - other: 0.3
    """
```

---

### 任務 2：實現 `src/agent_processor.py`

```python
def process_messages(
    raw_messages_dir: str,
    output_dir: str
) -> Dict[str, dict]:
    """處理訊息的主函數
    
    流程：
    1. 讀取 Agent 1 輸出的 JSON 檔案
    2. 調用去重、過濾、分類、關鍵詞提取
    3. 計算統計信息
    4. 輸出為 processed_messages/{group_id}_{date}.json
    5. 輸出統計信息到 processed_messages/stats_{date}.json
    
    Returns:
        {"group_id": {"messages": [...], "stats": {...}}}
    """
```

---

### 任務 3：實現 `tests/test_processor.py`

**最少 5 個測試**：

```python
def test_remove_duplicates():
    """測試去重功能"""
    
def test_filter_noise():
    """測試過濾功能"""
    
def test_classify_messages():
    """測試分類功能"""
    
def test_extract_keywords():
    """測試關鍵詞提取"""
    
def test_calculate_importance():
    """測試重要性計算"""
```

---

## 📋 輸出格式

### processed_messages JSON

```json
{
  "group_id": "C1234567890abcdef",
  "group_name": "我的工作群",
  "date": "2026-02-17",
  "total_original": 42,
  "total_processed": 38,
  "messages": [
    {
      "message_id": "100001",
      "timestamp": "2026-02-17T09:15:30+08:00",
      "sender_id": "U1234567890abcdef",
      "sender_name": "Alice",
      "message_type": "text",
      "content": "今天的會議時間是？",
      "importance": 0.85,
      "category": "question",
      "keywords": ["會議", "時間"],
      "attachments": []
    }
  ]
}
```

### stats JSON

```json
{
  "date": "2026-02-17",
  "total_groups": 3,
  "stats_by_group": {
    "C1234567890abcdef": {
      "group_name": "我的工作群",
      "total_messages": 38,
      "removed_duplicates": 4,
      "filtered_noise": 0,
      "top_senders": [
        {"name": "Alice", "count": 12},
        {"name": "Bob", "count": 10}
      ],
      "top_keywords": ["會議", "專案", "完成"],
      "message_types": {"text": 30, "image": 5, "file": 3}
    }
  }
}
```

---

## ✅ 成功標準

- [ ] 代碼 <400 行
- [ ] 去重率 100%
- [ ] 分類準確 >85%
- [ ] 關鍵詞有意義
- [ ] 統計信息準確
- [ ] 有 5 個以上的單元測試
- [ ] 所有函數有 docstring 和類型提示

---

## 重要提示

上傳時包括：
1. AGENT2_PROMPT.md（完整的技術要求）
2. 你已完成的 agent_crawler.py（作為參考）
3. 一份 Agent 1 的輸出示例 JSON（作為測試數據）

開始吧！
```

---

## 🟡 Session 3 - Agent 3 開發 Prompt

**何時使用**：Agent 2 完成並測試通過後  
**所需上傳**：
- AGENT3_PROMPT.md
- 你已完成的 agent_processor.py（作為參考）

---

### 給 Claude Code 的 Session 3 Prompt

```markdown
# 🟡 Claude Code Session 3 - Agent 3 開發 Prompt

**Session 目標**：開發摘要生成器 (Agent 3)  
**預計時間**：2.5 小時  
**輸出物**：2 個 Python 檔案 + 測試 + HTML 索引  

---

## 背景

Agent 2（訊息處理器）已完成，輸出了清理和分類的訊息。

你現在需要：
- ✅ 使用 Claude API 生成高質量的摘要
- ✅ **控制成本**（減少 70-80% 的 API 成本）
- ✅ 生成 Markdown 格式的摘要
- ✅ 生成索引頁面

---

## 👤 你的角色：Agent 3 開發者

責任：
- 從 Agent 2 讀取處理後的訊息
- 設計高效的 Claude Prompt
- 調用 Claude API 生成摘要
- 格式化為 Markdown
- 生成 HTML 索引頁面

---

## 📤 具體任務

### 任務 1：實現 `src/utils/summarizer_utils.py`

```python
def create_summary_prompt(group_data: dict) -> str:
    """構建發送給 Claude 的 prompt
    
    關鍵：
    - 只傳遞**已過濾和分類**的訊息（不傳原始訊息）
    - 明確指定字數限制（200-500 字）
    - 給出清晰的輸出格式
    
    Args:
        group_data: 處理後的群組訊息數據
    
    Returns:
        完整的 prompt 字符串
    """

async def call_claude_api(
    prompt: str, 
    model: str = "claude-3-5-sonnet-20241022"
) -> str:
    """調用 Claude API 生成摘要
    
    Args:
        prompt: 完整的 prompt
        model: 使用的模型
    
    Returns:
        生成的摘要文本
    
    錯誤處理：
    - API 超時時重試（最多 3 次）
    - 記錄 API 調用日誌
    """

def format_summary_markdown(
    group_name: str,
    date: str,
    summary: str,
    metadata: dict
) -> str:
    """格式化為 Markdown
    
    輸出格式：
    # 群組名稱 - 日報摘要
    
    **日期**：...
    **訊息數**：...
    
    ## 核心要點
    ...
    
    ## 關鍵發言
    ...
    
    ## 待辦事項
    ...
    
    ## 統計信息
    ...
    """
```

---

### 任務 2：實現 `src/agent_summarizer.py`

```python
async def generate_summaries(
    processed_dir: str,
    output_dir: str
) -> Dict[str, str]:
    """生成所有摘要的主函數
    
    流程：
    1. 讀取 Agent 2 的輸出 JSON
    2. 為每個群組構建 prompt
    3. 調用 Claude API
    4. 格式化為 Markdown
    5. 輸出為 output/summaries/{group_id}_{date}.md
    6. 生成 HTML 索引頁面
    
    Returns:
        {"group_id": "summary_file_path"}
    """
```

---

### 任務 3：實現 `tests/test_summarizer.py`

```python
@pytest.mark.asyncio
async def test_create_summary_prompt():
    """測試 prompt 構建"""
    
@pytest.mark.asyncio
async def test_format_summary_markdown():
    """測試 Markdown 格式化"""
    
# 其他測試...
```

---

## 📤 輸出格式

### Markdown 摘要檔案

```markdown
# 📱 我的工作群 - 日報摘要

**日期**：2026-02-17  
**訊息數**：38  
**活躍成員**：Alice, Bob, Charlie  

---

## 🎯 核心要點

### 1. 會議時間確認
- 今天下午 3 點開會
- 地點：會議室 A
- 需要準備：季度報告

### 2. 專案進度更新
- 開發模塊已完成 80%
- 預計週五前完成

---

## 👥 關鍵發言

**Alice**（12 條訊息）：
> 「會議時間改到下午 3 點」

**Bob**（10 條訊息）：
> 「開發進度已更新」

---

## ⚠️ 待辦事項

- [ ] Alice 準備季度報告
- [ ] Bob 完成集成測試

---

## 📊 群組統計

- 總訊息：38
- 文本：30 | 圖片：5 | 檔案：3
```

---

## ✅ 成功標準

- [ ] 代碼 <400 行
- [ ] 摘要長度 200-500 字
- [ ] API 成本優化 >70%
- [ ] Markdown 格式正確
- [ ] 中文顯示正常
- [ ] HTML 索引頁面可打開
- [ ] 有至少 1 個單元測試

---

## 重要提示

這是最複雜的 Agent，重點是：
1. **Prompt 設計**：少傳訊息，多傳指導
2. **成本優化**：減少 API 調用的 token 數
3. **質量控制**：驗證摘要質量

上傳時包括：
1. AGENT3_PROMPT.md（特別注意「成本優化策略」部分）
2. 你已完成的 agent_processor.py
3. Agent 2 的輸出示例 JSON

開始吧！
```

---

## 🟢 Session 4 - Agent 4 開發 Prompt

**何時使用**：Agent 3 完成並測試通過後  
**所需上傳**：
- AGENT4_PROMPT.md
- 你已完成的 agent_summarizer.py（作為參考）

---

### 給 Claude Code 的 Session 4 Prompt

```markdown
# 🟢 Claude Code Session 4 - Agent 4 開發 Prompt

**Session 目標**：開發排程和發送器 (Agent 4)  
**預計時間**：2 小時  
**輸出物**：2 個 Python 檔案 + 測試 + 部署腳本  

---

## 背景

Agent 1-3 都已完成。你現在需要：
- ✅ 每天早上 8:00 自動執行整個管道
- ✅ 將摘要發送到用戶的 LINE 私聊
- ✅ 記錄完整的執行日誌
- ✅ 準備生產部署

---

## 👤 你的角色：Agent 4 開發者

責任：
- 設置每日定時執行
- 協調 Agent 1-3 的執行
- 發送摘要到 LINE 私聊
- 記錄日誌和統計

---

## 📤 具體任務

### 任務 1：實現 `src/utils/sender.py`

```python
class LineSender:
    """LINE 消息發送器"""
    
    async def send_summary(
        self,
        user_id: str,
        summary_file: str
    ) -> bool:
        """發送單份摘要到 LINE 私聊
        
        Args:
            user_id: LINE 使用者 ID
            summary_file: 摘要檔案路徑（.md）
        
        Returns:
            是否發送成功
        
        錯誤處理：
        - 檔案不存在時記錄警告
        - API 失敗時重試（最多 3 次）
        """
    
    async def send_batch_summaries(
        self,
        user_id: str,
        summary_dir: str
    ) -> Dict[str, bool]:
        """批量發送所有摘要
        
        Args:
            user_id: LINE 使用者 ID
            summary_dir: 摘要目錄
        
        Returns:
            {"file.md": True/False, ...}
        """
```

---

### 任務 2：實現 `src/agent_scheduler.py`

```python
def schedule_daily_tasks(time_str: str = "08:00") -> None:
    """設置每日定時任務
    
    Args:
        time_str: 執行時間（格式：\"HH:MM\"）
    
    邏輯：
    1. 使用 APScheduler 或 schedule 設置
    2. 每天 08:00 執行 execute_pipeline()
    3. 無限循環監控
    """

async def execute_pipeline() -> Dict[str, Any]:
    """執行完整的管道
    
    流程：
    1. 記錄開始時間
    2. 調用 agent_crawler.crawl_messages()
    3. 調用 agent_processor.process_messages()
    4. 調用 agent_summarizer.generate_summaries()
    5. 調用 sender.send_batch_summaries()
    6. 記錄統計信息
    7. 保存執行結果
    
    Returns:
        {
            "status": "success",
            "duration_seconds": 286,
            "agents_results": {...}
        }
    """
```

---

### 任務 3：實現 `tests/test_scheduler.py`

```python
def test_schedule_time_parsing():
    """測試時間解析"""
    
def test_pipeline_execution():
    """測試管道執行（mock 其他 Agent）"""
    
def test_error_handling():
    """測試錯誤處理和恢復"""
```

---

## 📤 輸出格式

### 執行日誌

```
[2026-02-17 08:00:00] INFO: 開始每日管道執行
[2026-02-17 08:00:05] INFO: [Agent 1] 開始爬蟲，群組數：3
[2026-02-17 08:01:30] INFO: [Agent 1] 完成爬蟲，訊息數：127
[2026-02-17 08:02:00] INFO: [Agent 2] 開始訊息處理
[2026-02-17 08:02:45] INFO: [Agent 2] 完成處理，去重：12
[2026-02-17 08:03:00] INFO: [Agent 3] 開始摘要生成
[2026-02-17 08:04:15] INFO: [Agent 3] 完成摘要，成本：$0.05
[2026-02-17 08:04:30] INFO: [Agent 4] 開始發送摘要
[2026-02-17 08:04:45] INFO: [Agent 4] 發送成功：3/3
[2026-02-17 08:04:46] INFO: 完成，耗時 4 分 46 秒
```

### 執行統計 JSON

```json
{
  "last_execution": "2026-02-17T08:04:46+08:00",
  "status": "success",
  "duration_seconds": 286,
  "groups_crawled": 3,
  "messages_crawled": 127,
  "messages_processed": 115,
  "summaries_generated": 3,
  "summaries_sent": 3,
  "next_execution": "2026-02-18T08:00:00+08:00"
}
```

---

## ✅ 成功標準

- [ ] 代碼 <250 行
- [ ] 排程準確性 100%
- [ ] 發送成功率 >99%
- [ ] 日誌記錄完整
- [ ] 錯誤重試機制完整
- [ ] 有至少 2 個單元測試
- [ ] 準備好生產部署

---

## 生產部署

包含使用 systemd 的部署腳本：

```ini
[Unit]
Description=LINE Message Daily Summary
After=network.target

[Service]
Type=simple
User=app
ExecStart=/usr/bin/python3 /opt/line-summarizer/src/agent_scheduler.py
Restart=always

[Install]
WantedBy=multi-user.target
```

---

重要提示

這是最後一個 Agent！完成後系統就完全可用了。

上傳時包括：
1. AGENT4_PROMPT.md（特別注意「生產部署指南」部分）
2. 你已完成的 agent_summarizer.py
3. Agent 3 的輸出示例文件

開始吧！
```

---

## 📋 總結

```
Session 1: Agent 1 (訊息爬蟲)
  └─ 上傳：AGENT1_PROMPT.md
  └─ 輸出：agent_crawler.py, line_handler.py, test_crawler.py

Session 2: Agent 2 (訊息處理)
  └─ 上傳：AGENT2_PROMPT.md + Agent 1 代碼
  └─ 輸出：agent_processor.py, message_parser.py, test_processor.py

Session 3: Agent 3 (摘要生成)
  └─ 上傳：AGENT3_PROMPT.md + Agent 2 代碼
  └─ 輸出：agent_summarizer.py, summarizer_utils.py, test_summarizer.py

Session 4: Agent 4 (排程發送)
  └─ 上傳：AGENT4_PROMPT.md + Agent 3 代碼
  └─ 輸出：agent_scheduler.py, sender.py, test_scheduler.py, systemd 腳本
```

---

**每個 Session 完成後，下一個 Session 開始前，一定要上傳上一個 Agent 的代碼供參考！** 🔗

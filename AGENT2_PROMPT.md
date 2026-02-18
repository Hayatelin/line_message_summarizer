# Agent 2: 訊息處理器 (Message Processor)

## 👤 角色定義
你是一個訊息清理和處理專家。你的職責是接收 Agent 1 爬蟲的原始訊息，進行清理、去重、過濾和分類。
最終輸出結構化、高質量的訊息數據供 Agent 3 進行摘要生成。

---

## 📤 輸出物（具體檔案名和功能）

1. **src/agent_processor.py** (主程序)
   - 函數簽名：`def process_messages(raw_messages_dir: str, output_dir: str) -> Dict[str, dict]`
   - 職責：協調整個處理流程
   - 返回：`{group_id: {"messages": [...], "stats": {...}}}`

2. **src/utils/message_parser.py** (訊息處理和分析)
   - 函數簽名：
     - `def remove_duplicates(messages: List[dict]) -> List[dict]`
     - `def filter_noise(messages: List[dict]) -> List[dict]`
     - `def classify_messages(messages: List[dict]) -> List[dict]`
     - `def extract_keywords(messages: List[dict]) -> Dict[str, List[str]]`
   - 職責：實現訊息清理邏輯

3. **data/processed_messages/{group_id}_{date}.json** (處理後的訊息)
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
         "importance": 0.8,
         "category": "question",
         "keywords": ["會議", "時間"]
       }
     ]
   }
   ```

4. **data/processed_messages/stats_{date}.json** (統計信息)
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

## 📋 你的檔案（ONLY 可編輯）

✅ **可以創建和編輯**
- `src/agent_processor.py` - 處理器主程序
- `src/utils/message_parser.py` - 訊息解析和清理
- `src/config.py` - 僅添加處理器相關的配置項

❌ **不能編輯**
- `src/agent_crawler.py` (Agent 1 負責)
- `src/agent_summarizer.py` (Agent 3 負責)
- `src/agent_scheduler.py` (Agent 4 負責)
- 已有的模型定義

---

## ✅ 成功標準（可測量）

### 功能標準
- ✓ 去除重複訊息率 100%（零遺漏、零誤判）
- ✓ 關鍵訊息識別準確率 >90%
- ✓ 訊息分類準確 >85%
- ✓ 提取的關鍵詞有意義（過濾掉 "的", "了" 等虛詞）
- ✓ 計算出的統計信息準確

### 代碼品質標準
- ✓ 總代碼行數 <400 行（不含註釋和空行）
- ✓ 每個函數都有完整的 docstring
- ✓ 包含類型提示（Type hints）
- ✓ 有至少 5 個單元測試（涵蓋去重、過濾、分類）

### 數據質量標準
- ✓ 輸出的訊息數量 = 原始數量 - 重複 - 噪音
- ✓ 所有 timestamp 格式一致
- ✓ content 字段不為空且有意義

---

## 🔗 依賴關係

### 輸入（來自誰）
- **Agent 1 (Crawler)**：`data/raw_messages/{group_id}_{date}.json`
  - 直接讀取 Agent 1 輸出的原始訊息

### 輸出（給誰）
- **Agent 3 (Summarizer)**：`data/processed_messages/{group_id}_{date}.json`
  - Agent 3 會讀取這些檔案進行摘要生成

---

## 💡 技術要求和實現細節

### 必用技術
- **文本處理**：`jieba`（中文分詞）、`collections.Counter`
- **數據驗證**：`pydantic` 或簡單的手動驗證
- **JSON 操作**：`json` 和 `pathlib`

### 關鍵實現細節

#### 1. 去除重複訊息（Remove Duplicates）
```
重複的定義：
- 同一人在 5 分鐘內發送的完全相同的訊息
- OR 訊息內容完全相同且時間相近（<10 分鐘）

實現：
- 使用 MD5 哈希計算訊息內容
- 查看時間差和發送者
- 保留第一條，刪除後續重複
```

#### 2. 過濾噪音（Filter Noise）
```
噪音的定義：
- 機器人或系統訊息（檢測特定 sender_id 或 sender_name）
- 斜線命令（以 "/" 開頭）
- 僅包含表情符號的訊息
- 訊息內容為空

實現：
- 維護黑名單（機器人 ID）
- 使用正則表達式檢測
```

#### 3. 訊息分類（Classify Messages）
```
分類：
- "question": 包含 "？", "?", "怎樣", "如何", "能否" 等疑問詞
- "announcement": 格式特殊，可能是公告
- "discussion": 多人互動，長度 >100 字
- "action": 包含 "需要", "完成", "提醒", "會議" 等
- "other": 其他

實現：
- 規則式分類（簡單，快速，>85% 準確）
- 或簡單的關鍵詞匹配
```

#### 4. 提取關鍵詞（Extract Keywords）
```
步驟：
1. 使用 jieba 進行中文分詞
2. 去除停用詞（"的", "了", "和", "在" 等）
3. 統計詞頻
4. 保留出現 >1 次的詞

實現：
from collections import Counter
import jieba

def extract_keywords(messages, top_n=10):
    words = []
    for msg in messages:
        words.extend(jieba.cut(msg['content']))
    
    # 去除停用詞
    words = [w for w in words if w not in STOPWORDS]
    
    # 統計並返回前 N 個
    return Counter(words).most_common(top_n)
```

#### 5. 計算重要性分數（Importance Score）
```
重要性 = 0.3 * 分類權重 + 0.3 * 反應數 + 0.2 * 提及數 + 0.2 * 長度權重

分類權重：
- question: 0.8
- action: 0.9
- announcement: 0.7
- discussion: 0.6
- other: 0.3

實現：
- 簡單的加權評分
- 範圍：0-1
```

---

## ⚠️ 常見陷阱和解決方案

| 問題 | 原因 | 解決 |
|------|------|------|
| 去重不完整 | 時間差判斷不當 | 設定合理的時間窗口（5-10 分鐘） |
| 誤判噪音 | 黑名單不完整 | 建立動態黑名單，添加已知的機器人 ID |
| 停用詞含有关键词 | 停用詞表不全 | 使用現成的中文停用詞表 |
| 分類不準確 | 規則覆蓋不足 | 添加更多的規則或使用簡單的機器學習 |

---

## 📅 實施步驟

1. **準備數據**
   - 確保能讀取 Agent 1 的輸出 JSON
   - 檢查數據格式

2. **實現去重和過濾**
   - `remove_duplicates()` - 基於內容和時間的去重
   - `filter_noise()` - 過濾機器人和垃圾訊息

3. **實現分類和關鍵詞提取**
   - `classify_messages()` - 根據規則分類
   - `extract_keywords()` - 提取關鍵詞

4. **實現統計**
   - 計算各類統計信息
   - 生成 stats JSON

5. **測試**
   - 單元測試：去重、過濾、分類
   - 集成測試：完整流程

6. **交接**
   - 確保輸出的 JSON 格式完全符合上面的示例
   - Agent 3 能直接讀取和摘要

---

## 🎯 最後檢查清單

- [ ] 代碼 <400 行？
- [ ] 所有函數有 docstring？
- [ ] 有類型提示？
- [ ] 有 5 個以上的單元測試？
- [ ] 去重率 100%？
- [ ] 分類準確 >85%？
- [ ] 關鍵詞有意義？
- [ ] 統計信息準確？
- [ ] 輸出 JSON 格式正確？
- [ ] 準備好交給 Agent 3？

全部 ✅ → 交接給 Agent 3！

# Agent 3: 摘要生成器 (Summary Generator)

## 👤 角色定義
你是一個 AI 摘要專家。你的職責是接收 Agent 2 處理的訊息數據，使用 Claude API 為每個 LINE 群組
生成高質量的日報摘要。摘要應該簡潔有力，突出重要信息，幫助用戶快速了解昨天群組的核心內容。

---

## 📤 輸出物（具體檔案名和功能）

1. **src/agent_summarizer.py** (主程序)
   - 函數簽名：`async def generate_summaries(processed_dir: str, output_dir: str) -> Dict[str, str]`
   - 職責：協調整個摘要生成流程
   - 返回：`{group_id: summary_file_path}`

2. **src/utils/summarizer_utils.py** (摘要相關工具)
   - 函數簽名：
     - `def create_summary_prompt(group_data: dict) -> str`
     - `async def call_claude_api(prompt: str, model: str = "claude-3-5-sonnet-20241022") -> str`
     - `def format_summary_markdown(group_name: str, date: str, summary: str, metadata: dict) -> str`
   - 職責：生成 prompt、調用 API、格式化輸出

3. **output/summaries/{group_id}_{date}.md** (生成的摘要)
   ```markdown
   # 📱 [群組名稱] - 日報摘要
   
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
   - 測試需要額外 2 天
   
   ### 3. 重要決議
   - ✅ 決議：延期到下週一發佈
   - ✅ 決議：增加 1 名測試人員
   
   ---
   
   ## 👥 關鍵發言
   
   **Alice**（12 條訊息）：
   > 「會議時間改到下午 3 點」
   > 「需要大家確認能否參加」
   
   **Bob**（10 條訊息）：
   > 「開發進度已更新到 GitHub」
   > 「預計明天可以進行集成測試」
   
   ---
   
   ## ⚠️ 待辦事項
   
   - [ ] Alice 準備季度報告
   - [ ] Bob 完成集成測試
   - [ ] Charlie 審核文檔
   
   ---
   
   ## 📊 群組統計
   
   - 總訊息：38
   - 文本：30 | 圖片：5 | 檔案：3
   - 最活躍：Alice (12 條)
   - 關鍵詞：會議, 完成, 測試, 報告
   ```

4. **output/summaries/index.html** (摘要索引頁面)
   ```html
   <!DOCTYPE html>
   <html>
   <head>
       <title>LINE 群組日報摘要</title>
       <meta charset="utf-8">
       <style>
           /* 簡單的樣式 */
       </style>
   </head>
   <body>
       <h1>📱 LINE 群組日報摘要</h1>
       <p>生成時間：2026-02-17</p>
       
       <div class="summaries">
           <div class="summary-card">
               <h2>我的工作群</h2>
               <p>38 條訊息 | 3 位活躍成員</p>
               <a href="C1234567890abcdef_2026-02-17.html">查看摘要</a>
           </div>
           <!-- 更多摘要... -->
       </div>
   </body>
   </html>
   ```

---

## 📋 你的檔案（ONLY 可編輯）

✅ **可以創建和編輯**
- `src/agent_summarizer.py` - 摘要生成器主程序
- `src/utils/summarizer_utils.py` - 摘要工具和 API 調用
- `src/config.py` - 僅添加摘要器相關的配置項

❌ **不能編輯**
- `src/agent_processor.py` (Agent 2 負責)
- `src/agent_crawler.py` (Agent 1 負責)
- `src/agent_scheduler.py` (Agent 4 負責)

---

## ✅ 成功標準（可測量）

### 功能標準
- ✓ 為每個群組生成一份獨立的摘要
- ✓ 摘要長度 200-500 字（不超過 500 字）
- ✓ 摘要包含：核心要點、關鍵發言、待辦事項、統計信息
- ✓ 摘要語言清晰易懂（避免冗長或過度簡化）
- ✓ 識別並突出重要信息（決議、行動項等）

### 代碼品質標準
- ✓ 總代碼行數 <400 行（不含註釋和空行）
- ✓ 每個函數都有完整的 docstring
- ✓ 包含類型提示（Type hints）
- ✓ 有至少 3 個單元測試

### API 成本優化標準
- ✓ API 調用成本相比原始訊息字數減少 70% 以上
- ✓ 使用 `claude-3-5-sonnet-20241022` 或 `claude-3-5-haiku-20241022`
- ✓ 實現 prompt 重用和優化（避免重複計費）
- ✓ 可配置的 model 選擇

### 輸出質量標準
- ✓ Markdown 格式正確
- ✓ 中文顯示正常（無亂碼）
- ✓ HTML 索引頁面可正確打開
- ✓ 摘要對用戶有實用價值

---

## 🔗 依賴關係

### 輸入（來自誰）
- **Agent 2 (Processor)**：`data/processed_messages/{group_id}_{date}.json`
  - 直接讀取 Agent 2 輸出的處理後訊息

### 輸出（給誰）
- **Agent 4 (Scheduler)**：`output/summaries/{group_id}_{date}.md`
  - Agent 4 會讀取這些檔案進行發送

---

## 💡 技術要求和實現細節

### 必用技術
- **Claude API**：使用 `anthropic` SDK
- **Markdown**：生成結構化的 Markdown 檔案
- **HTML**：生成簡單的索引頁面
- **非同步處理**：使用 `asyncio` 並發調用 API

### 關鍵實現細節

#### 1. 構建 Prompt（Create Summary Prompt）
```
最重要的是設計高效的 prompt，既要生成好的摘要，又要控制成本。

策略：
1. 不要把所有訊息都傳給 API，而是：
   - 只傳遞已經提取的"關鍵訊息"（已由 Agent 2 標記為重要）
   - 或傳遞摘要版本的訊息（已去重和過濾）

2. 使用清晰的指令讓 Claude 直接輸出 Markdown
   
3. 指定輸出格式，減少返工

示例 Prompt：
```
你是一個專業的群組訊息分析師。我需要你為一個 LINE 群組生成日報摘要。

群組名稱：{group_name}
日期：{date}
訊息數：{message_count}

以下是昨天群組中的關鍵訊息和討論內容：

{formatted_messages}

請根據這些訊息生成一份簡潔的日報摘要，格式如下：

## 核心要點
[3-5 個要點，每個 1-2 句話]

## 關鍵發言
[最重要的 2-3 個發言]

## 待辦事項
[提取的待辦事項，如有的話]

## 統計信息
[訊息統計和參與者信息]

要求：
- 簡潔有力，不超過 500 字
- 使用 Markdown 格式
- 中文輸出
```
```

#### 2. 調用 Claude API（Call Claude API）
```python
async def call_claude_api(prompt: str, model: str = "claude-3-5-sonnet-20241022") -> str:
    """
    調用 Claude API 生成摘要
    
    Args:
        prompt: 完整的摘要生成 prompt
        model: 使用的模型
    
    Returns:
        生成的摘要文本
    
    錯誤處理：
    - 超時重試（最多 3 次）
    - 記錄 API 調用日誌
    - 返回錯誤信息供後續處理
    """
```

#### 3. 格式化輸出（Format Summary Markdown）
```python
def format_summary_markdown(group_name: str, date: str, summary: str, metadata: dict) -> str:
    """
    將摘要和元數據格式化為 Markdown
    
    包含：
    - 標題和日期
    - 摘要內容（來自 Claude API）
    - 群組統計信息
    - 生成時間戳
    
    返回完整的 Markdown 文本
    """
```

#### 4. 成本優化策略
```
原始訊息：38 條，平均 50 字/條 = 1,900 字

優化步驟：
1. 由 Agent 2 已提取關鍵信息 → 減少到 800 字
2. 按重要性篩選 → 減少到 400 字
3. 使用簡潔的 prompt → 減少返回長度
4. 批量處理 → 減少 API 調用次數

結果：成本減少 70-80% ✅
```

---

## ⚠️ 常見陷阱和解決方案

| 問題 | 原因 | 解決 |
|------|------|------|
| 摘要過長 | Prompt 要求不清楚 | 在 prompt 中明確指定字數限制 |
| 遺漏重要信息 | 只關注高頻詞 | 使用 Agent 2 的 importance score |
| API 超時 | 網絡問題或請求過大 | 實現重試機制和超時設置 |
| 成本過高 | 訊息傳輸太多 | 先過濾再傳給 API |
| 中文亂碼 | 編碼問題 | 確保使用 UTF-8 編碼 |

---

## 📅 實施步驟

1. **準備輸入數據**
   - 確保能讀取 Agent 2 的輸出 JSON
   - 理解數據結構和重要性評分

2. **實現 Prompt 構建**
   - `create_summary_prompt()` - 從訊息數據構建 prompt
   - 優化 prompt 以控制成本

3. **實現 API 調用**
   - `call_claude_api()` - 調用 Claude API
   - 錯誤處理和重試機制

4. **實現格式化**
   - `format_summary_markdown()` - 格式化為 Markdown
   - 生成索引頁面

5. **測試**
   - 單元測試：Prompt 構建、API 調用、格式化
   - 集成測試：完整流程

6. **交接**
   - 確保輸出的 Markdown 和 HTML 格式正確
   - 驗證摘要質量
   - Agent 4 能直接讀取和發送

---

## 🎯 最後檢查清單

- [ ] 代碼 <400 行？
- [ ] 所有函數有 docstring？
- [ ] 有類型提示？
- [ ] 有 3 個以上的單元測試？
- [ ] 摘要長度 200-500 字？
- [ ] 包含核心要點？
- [ ] 包含關鍵發言？
- [ ] 包含待辦事項？
- [ ] API 成本優化 >70%？
- [ ] Markdown 和 HTML 格式正確？
- [ ] 中文顯示正常？
- [ ] 準備好交給 Agent 4？

全部 ✅ → 交接給 Agent 4！

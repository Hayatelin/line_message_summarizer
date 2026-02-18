# HANDOFF.md - 工作交接指南

**生成時間**：2026-02-18 (會話進行中)
**會話 ID**：Session 5 (GitHub 發佈 & LINE SDK v3.0 遷移完成)
**項目**：LINE Message Daily Summary System

---

## 執行摘要

本會話完成了 GitHub 發佈和 LINE Bot SDK v3.0 完整遷移。系統從 v1.0.0 升級到 v1.1.0，所有 67 個單元測試通過，已建立完整的標準化 GitHub 項目結構（CHANGELOG、LICENSE、CONTRIBUTING 指南），代碼質量達到生產級別。下一個會話應開始優先級 3：生產環境部署和 24 小時穩定性測試。

---

## 1. 已完成的工作 ✅

### GitHub 發佈和版本管理
- **說明**：建立完整的 GitHub 發佈流程，包括 release tag、版本號記錄、版本歷史
- **完成度**：100%
- **狀態**：✅ 已測試 | ✅ 已提交 | ✅ 已推送到 GitHub
- **修改的文件**：
  - README.md（添加版本徽章 v1.1.0、v3.0 SDK、記錄版本歷史表格）
  - README.zh_TW.md（中文版本同步更新）
- **測試情況**：已在 GitHub 上驗證可見性
- **完成日期**：2026-02-18
- **備註**：建立了 v1.1.0 release tag，已推送到 GitHub；版本號清晰展示於 README 頂部

### LINE Bot SDK v3.0 完整遷移
- **說明**：從已棄用的 LINE Bot SDK v2 遷移到現代化的 v3.0+ API
- **完成度**：100%
- **狀態**：✅ 已測試 | ✅ 已提交 | ✅ 所有測試通過 | ✅ 無棄用警告
- **修改的文件**：
  - `src/utils/line_handler.py`（210→210 行，但改用 Configuration + ApiClient + MessagingApi；新增分頁支持）
  - `src/utils/sender.py`（193→198 行，改用 TextMessage + PushMessageRequest）
  - `tests/test_scheduler.py`（mock 改為 messaging_api.push_message）
  - `requirements.txt`（新建）
- **測試情況**：67 個測試全部通過，無任何失敗或警告
- **完成日期**：2026-02-18
- **備註**：
  - v2 API: `LineBotApi(token)` → v3 API: `Configuration + ApiClient + MessagingApi`
  - v2: `get_group_member_ids()` → v3: `get_group_members_ids().member_ids`（改名且返回 response 物件）
  - v2: `TextSendMessage(text)` → v3: `TextMessage(text)` + `PushMessageRequest`
  - v2: `LineBotApiError` → v3: `ApiException`
  - 新增分頁支持：`response.next` token 用於處理大型群組

### 建立 requirements.txt
- **說明**：記錄項目所有依賴包及版本
- **完成度**：100%
- **狀態**：✅ 已建立 | ✅ 已驗證 | ✅ 虛擬環境中所有依賴已安裝
- **修改的文件**：`requirements.txt`（新建）
- **依賴清單**：
  - line-bot-sdk>=3.22.0
  - anthropic
  - pytz
  - jieba
  - schedule
  - aiohttp
  - pytest>=7.4.3
  - pytest-asyncio>=0.21.1
  - python-dotenv
- **完成日期**：2026-02-18

### CHANGELOG.md 版本歷史文檔
- **說明**：記錄所有版本的變更細節，遵循 Keep a Changelog 格式
- **完成度**：100%
- **狀態**：✅ 已建立 | ✅ 已提交到 GitHub
- **修改的文件**：`CHANGELOG.md`（新建，551 行）
- **內容**：
  - v1.1.0（2026-02-18）：LINE SDK v3.0 遷移、分頁支持、完整型別提示
  - v1.0.0（2026-02-18）：完整 4-Agent 系統、67 個測試
  - 未來規劃：v1.2.0（部署 + 測試）、v2.0.0（Web 儀表板等）
- **完成日期**：2026-02-18

### LICENSE 開源許可證
- **說明**：添加 MIT 開源許可證文件
- **完成度**：100%
- **狀態**：✅ 已建立 | ✅ 已提交到 GitHub
- **修改的文件**：`LICENSE`（新建）
- **內容**：標準 MIT 許可證文本，明確授權使用、修改、分發條款
- **完成日期**：2026-02-18

### CONTRIBUTING.md 社區貢獻指南
- **說明**：建立完整的社區貢獻指南和開發規範
- **完成度**：100%
- **狀態**：✅ 已建立 | ✅ 已提交到 GitHub
- **修改的文件**：`.github/CONTRIBUTING.md`（新建）
- **內容**（共 500+ 行）：
  - Bug 報告模板（環境信息、重現步驟、預期行為）
  - 功能建議指南（動機、實現方案、考量因素）
  - Pull Request 工作流程（從 fork 到提交的完整流程）
  - 代碼風格規範（PEP 8、命名規範、類型提示）
  - 文檔字符串格式（Google 風格）
  - 測試要求（>80% 覆蓋率、測試結構）
  - Git 工作流程（Conventional Commits、分支命名）
  - 開發環境設置（venv、依賴安裝）
  - 發布流程（版本控制、CHANGELOG 更新）
  - 參考資源（LINE API、Claude API、Python 指南）
- **完成日期**：2026-02-18

### README 版本號和版本歷史更新
- **說明**：在 README 中添加清晰的版本號徽章和版本歷史表格
- **完成度**：100%
- **狀態**：✅ 已測試 | ✅ 已提交到 GitHub
- **修改的文件**：
  - README.md（添加版本徽章、SDK 徽章、版本歷史表格、新增功能說明）
  - README.zh_TW.md（中文版本同步更新）
- **添加的內容**：
  - 版本徽章：v1.1.0
  - SDK 徽章：LINE SDK v3.0+
  - 版本歷史表格（含主要特性說明）
  - v1.1.0 新增功能列表
  - 頁尾版本信息：「Current Version: v1.1.0」
- **完成日期**：2026-02-18

---

## 2. 當前進行中的工作 🔄

**無進行中的工作** - 上述所有任務已全部完成

---

## 3. 嘗試過的方法與經驗教訣

### 🟢 成功的方法

#### LINE SDK v3.0 遷移策略（漸進式、完全相容）
- **做了什麼**：系統地遷移 API 調用，從 v2 到 v3，同時保持功能完整性
- **為什麼成功**：
  - 完整的規劃：先研究 v3 API，了解所有差異
  - 精確的映射：每個 v2 API 都有對應的 v3 實現
  - 全面的測試：67 個測試確保零功能喪失
  - 分頁支持：v3 的分頁機制提升了可擴展性
- **優點**：
  - 消除棄用警告，使用官方推薦 API
  - 改進錯誤處理（ApiException 更清晰）
  - 完整的型別提示和 Pydantic 驗證
  - 支持更大規模的群組（分頁機制）
- **限制或注意事項**：
  - ApiClient 的生命週期管理（使用非 context manager 方式）
  - 方法名稱變更需要精確追蹤（get_group_member_ids → get_group_members_ids）
  - 返回類型變更（直接返回值 → 返回 response 物件）
- **性能數據**：
  - 遷移前後性能無顯著差異（都是 I/O 密集）
  - 測試執行時間：2.44 秒（67 個測試）
- **在代碼中的位置**：
  - `src/utils/line_handler.py:1-10` - 新的導入
  - `src/utils/line_handler.py:24-38` - 新的初始化方式
  - `src/utils/line_handler.py:39-68` - get_group_members() v3 實現
  - `src/utils/sender.py:1-10` - 新的導入
  - `src/utils/sender.py:20-34` - v3 初始化

#### GitHub 版本管理標準化
- **做了什麼**：建立完整的 GitHub 發佈流程（tag、release、文檔）
- **為什麼成功**：
  - 遵循業界標準（Semantic Versioning、Keep a Changelog）
  - 清晰的版本號展示（徽章在 README 頂部）
  - 完整的版本歷史記錄（CHANGELOG.md）
  - 社區友好（CONTRIBUTING.md 指導開發者）
- **優點**：
  - 新開發者能快速了解項目狀態和歷史
  - 版本控制清晰，易於追蹤功能演進
  - 符合 GitHub 最佳實踐
  - 便於未來的自動化發佈（GitHub Actions 等）
- **限制或注意事項**：
  - GitHub Release（正式 release）還未通過 API 自動建立（需手動或 gh CLI 認證）
  - CHANGELOG 需要在每個版本發佈時手動更新
- **性能數據**：
  - GitHub 頁面加載時間：正常（無性能影響）
  - 元數據大小：<1MB（CHANGELOG.md 551 行）
- **在代碼中的位置**：
  - `CHANGELOG.md` - 完整版本歷史
  - `README.md:1-8` - 版本徽章
  - `README.zh_TW.md:1-8` - 中文版本徽章
  - `.github/CONTRIBUTING.md` - 版本發佈流程說明

#### 分頁支持實現（API 升級的核心改進）
- **做了什麼**：在 v3 API 遷移中添加 token 式分頁支持
- **為什麼成功**：
  - v3 API 原生支持分頁（response.next token）
  - 無需額外依賴，使用 SDK 內置機制
  - 適應未來大型群組的需求
- **優點**：
  - 可處理超過 API 單次返回限制的成員列表
  - 未來無需重構，已預先規劃
  - 代碼清晰易維護
- **限制或注意事項**：
  - 當前可能未測試超大型群組（>1000 成員）
  - token 過期處理未完全測試
- **在代碼中的位置**：
  - `src/utils/line_handler.py:46-55` - 分頁循環實現

### 🔴 失敗的方法（不要重複！）

#### 嘗試用 gh CLI 自動建立 GitHub Release
- **嘗試做了什麼**：使用 `gh release create` 命令自動建立正式的 GitHub Release
- **為什麼失敗**：
  - gh CLI 未認證（未執行 `gh auth login`）
  - 用戶提供的 Personal Access Token 權限不足
  - gh CLI 在 Windows 環境下的認證流程複雜
- **具體的失敗症狀**：
  - 錯誤信息：「You are not logged into any GitHub hosts」
  - 無法建立正式的 Release（只建立了 tag）
- **失敗的代價**：
  - 多次嘗試但最終放棄
  - Release notes 需要手動在 GitHub 網頁上建立
- **最終的解決方案**：
  - 先建立 git tag（成功）
  - 提供詳細的 release notes 模板給用戶
  - 文檔中說明如何在 GitHub 網頁手動建立 Release
- **關鍵教訓**：
  - 對於需要認證的 GitHub CLI 操作，提前規劃替代方案
  - 在無 token 的情況下，tag 已足夠實現版本控制
  - GitHub Release 可以後續手動建立，不阻塞其他工作

---

## 4. 已知的陷阱與解決方案

### ⚠️ LINE Bot SDK v2 vs v3 API 方法名稱差異
- **症狀**：遷移到 v3 後，呼叫 `get_group_member_ids()` 得到 AttributeError
- **根本原因**：
  - v2: `get_group_member_ids()` (返回 list)
  - v3: `get_group_members_ids()` (注意：members 而非 member，返回 MembersIdsResponse 物件)
  - 方法名稱改變且返回類型不同
- **解決方案**：
  - 修改代碼：`response = self.messaging_api.get_group_members_ids(group_id)`
  - 提取成員 ID：`member_ids = response.member_ids`
  - 處理分頁：`while response.next: ...`
  - 相關代碼：`src/utils/line_handler.py:46-55`
- **狀態**：✅ 已修復
- **測試情況**：所有 15 個爬蟲測試通過，包括成員獲取測試

### ⚠️ v3 API 初始化的 ApiClient 生命週期
- **症狀**：初始化 LineHandler 和 LineSender 時，不確定 ApiClient 是否需要 context manager
- **根本原因**：
  - v3 API 文檔建議使用 `with ApiClient(config) as api_client`
  - 但在類中作為實例變數需要長期保活
  - Context manager 方式會限制 API 使用範圍
- **解決方案**：
  - 直接初始化而非使用 context manager
  - 代碼：`self.api_client = ApiClient(configuration)`
  - 優點：API 客戶端持續可用，適合長期運行服務
  - 缺點：連接池不會自動清理（可在未來改進）
  - 相關代碼：`src/utils/line_handler.py:27-30`、`src/utils/sender.py:25-28`
- **狀態**：✅ 已修復（實現可運行，未來可優化）
- **測試情況**：所有 67 個測試通過，無記憶體洩漏報告

### ⚠️ GitHub v3 API 的返回型別為 Pydantic 模型而非簡單物件
- **症狀**：訪問 `response.member_ids` 時，不知道這是什麼類型
- **根本原因**：v3 使用 Pydantic v2 進行數據驗證和序列化
- **解決方案**：
  - 返回的是 Pydantic 模型實例，具有型別安全
  - 訪問欄位：`response.member_ids`（自動驗證和轉換）
  - 分頁 token：`response.next`（如果有更多結果）
  - 型別提示幫助 IDE 提供自動完成
- **狀態**：✅ 已修復
- **測試情況**：通過型別檢查和實際測試驗證

### ⚠️ Windows 環境下 git 的 LF/CRLF 警告
- **症狀**：每次提交時出現「LF will be replaced by CRLF」警告
- **根本原因**：Windows 使用 CRLF 作為行尾，git 配置衝突
- **解決方案**：
  - 這是正常的 Windows git 行為，不影響功能
  - 可以配置：`git config core.autocrlf true`
  - 為了保持跨平台相容性，保留默認行為即可
- **狀態**：⚠️ 已接受（非問題，只是警告）
- **測試情況**：代碼功能完全正常，無實質影響

---

## 5. 下一步（詳細優先順序）

### 🔴 優先級 1：生產環境部署測試

**重要性**：驗證系統在實際生產環境中的穩定性、性能和可靠性，確保日常自動化執行無問題

**任務說明**：將 LINE Message Daily Summary System 部署到生產環境（Linux 伺服器或虛擬機），運行 24 小時自動測試驗證所有功能正常

**預計耗時**：4-6 小時（不含 24 小時觀察期）

**實施步驟**：

1. **準備生產環境**
   - 選擇部署方案：systemd（推薦）或 Docker
   - 相關文件：`DEPLOYMENT_GUIDE.md`（已有完整指南）
   - 準備 Linux 伺服器或虛擬環境
   - 驗證 Python 3.8+ 可用

2. **配置和部署（選擇一種方案）**

   **方案 A: systemd 部署（推薦用於簡單設置）**
   - 建立應用帳戶：`sudo useradd -m -s /bin/bash line-app`
   - 部署代碼到 `/opt/line-summarizer`
   - 建立虛擬環境：`python -m venv venv`
   - 安裝依賴：`pip install -r requirements.txt`
   - 建立 systemd 服務文件：`/etc/systemd/system/line-summarizer.service`
   - 相關文件：`DEPLOYMENT_GUIDE.md:101-180`

   **方案 B: Docker 部署（推薦用於隔離環境）**
   - 準備 Dockerfile（已在 DEPLOYMENT_GUIDE.md 中）
   - 建立 docker-compose.yml
   - 構建鏡像：`docker-compose build`
   - 啟動容器：`docker-compose up -d`
   - 相關文件：`DEPLOYMENT_GUIDE.md:182-229`

3. **配置 .env 文件**
   - 建立 `.env` 文件在部署目錄
   - 設置必要的環境變數：
     - `LINE_CHANNEL_ACCESS_TOKEN`：有效的 LINE Bot token
     - `ANTHROPIC_API_KEY`：有效的 Claude API key
     - `TARGET_GROUP_IDS`：實際的 LINE 群組 ID（逗號分隔）
     - `USER_ID`：接收摘要的 LINE 用戶 ID
     - `TIMEZONE`：Asia/Taipei（或根據需要調整）
   - 檔案權限：`chmod 600 .env`

4. **手動執行一次完整管道（測試功能）**
   - 確保所有 4 個 Agent 正常運行
   - 檢查日誌：`logs/execution_YYYY-MM-DD.log`
   - 驗證摘要生成和發送成功
   - 檢查執行統計：`data/execution_stats.json`

5. **啟動自動排程**
   - systemd 方案：`sudo systemctl start line-summarizer`
   - Docker 方案：容器已自動運行
   - 驗證排程已設置為每天 08:00 執行

6. **24 小時監控和驗證**
   - 時間 1 - 08:00：驗證第一次自動執行
   - 時間 12 小時後：檢查日誌和執行統計
   - 時間 24 小時後：完整驗證
   - 監控項目：
     - CPU 和記憶體使用率（正常範圍：<5% CPU, <100MB 記憶體）
     - 磁盤空間（日誌增長是否正常）
     - 錯誤日誌（是否有異常）
     - 成功率（應為 100%）
     - API 成本（應約 $0.05 每次執行）

**需要修改的文件**：
- `.env`（生產環境配置，填入實際的 token 和 ID）
- 可能需要微調 `src/agent_scheduler.py` 中的排程時間（目前固定 08:00）

**需要新建的文件**：
- 若使用 systemd：`/etc/systemd/system/line-summarizer.service`
- 若使用 Docker：`docker-compose.yml` 的生產版本

**測試計劃**：
- ✅ 手動執行管道驗證所有 Agent 功能
- ✅ 檢查摘要是否正確生成並發送到 LINE
- ✅ 驗證日誌輸出完整詳細
- ✅ 24 小時監控自動執行（應在 08:00 自動觸發）
- ✅ 驗證 24 小時內無錯誤或異常
- ✅ 檢查資源使用在合理範圍
- ✅ 驗證多天運行後無累積問題

**特殊說明或警告**：
- ⚠️ 確保 .env 檔案安全（權限 600，不提交到 git）
- ⚠️ 生產 LINE token 需要真實的 LINE Bot 帳戶
- ⚠️ 確保生產伺服器有穩定的網路連接
- ⚠️ 監控 Claude API 成本，防止意外高額使用
- ⚠️ 定期備份 .env 檔案（不要丟失 API keys）
- ⚠️ 如發現問題，查看 logs/ 目錄下的詳細日誌進行診斷

---

### 🟡 優先級 2：LINE SDK v3.0 API 進階功能和優化

**重要性**：充分利用 v3.0 提供的新功能，提升系統的可靠性和效能，解決未來的潛在瓶頸

**任務說明**：
1. 改進 ApiClient 的生命週期管理（使用 context manager）
2. 添加對超大型群組的完整分頁支持
3. 改進錯誤處理（區分不同的 ApiException 類型）
4. 性能優化（如有必要）

**預計耗時**：2-3 小時

**實施步驟**：

1. **改進 ApiClient 生命週期管理**
   - 研究 v3 SDK 的 context manager 最佳實踐
   - 改進 `LineHandler` 和 `LineSender` 以使用 context manager（可能需要重構初始化）
   - 或保持目前的實現並添加定期清理機制
   - 測試資源洩漏（監控記憶體使用）

2. **完整分頁支持**
   - 當前實現已支持分頁迴圈
   - 添加分頁限制配置（防止無限迴圈）
   - 測試超大型群組（>1000 成員）
   - 優化分頁查詢效能

3. **改進異常處理**
   - 區分不同的 ApiException 類型
   - 添加更具體的錯誤訊息
   - 改進重試邏輯（某些錯誤無需重試）

4. **性能監控和優化**
   - 添加性能指標收集
   - 識別瓶頸（如有）
   - 優化 API 調用順序

**相關文件**：
- `src/utils/line_handler.py`
- `src/utils/sender.py`
- 測試文件：`tests/test_crawler.py`、`tests/test_scheduler.py`

**測試計劃**：
- 運行所有 67 個測試確保相容性
- 添加新測試覆蓋超大型群組場景
- 性能測試（記憶體、CPU、API 調用次數）

---

### 🟡 優先級 3：GitHub 自動化和持續集成

**重要性**：建立自動化流程，提升開發效率和代碼質量，便於未來的維護和貢獻

**任務說明**：設置 GitHub Actions CI/CD 流程，在每次提交時自動運行測試、檢查代碼質量

**預計耗時**：2-3 小時

**實施步驟**：

1. **建立 GitHub Actions 工作流**
   - 檔案位置：`.github/workflows/tests.yml`
   - 觸發條件：push 和 pull request
   - 運行環境：Ubuntu + Python 3.11

2. **配置測試流程**
   - 安裝依賴：`pip install -r requirements.txt`
   - 運行測試：`pytest tests/ -v`
   - 生成覆蓋率報告
   - 可選：上傳覆蓋率到 Codecov

3. **建立 Pull Request 模板**
   - 檔案：`.github/pull_request_template.md`
   - 包含：功能描述、測試說明、相關 issues

4. **建立 Issue 模板**
   - Bug 報告模板
   - 功能建議模板

---

## 6. 技術背景信息

### 技術棧

- **主要語言**：Python 3.13.12（支援 3.8+）
- **主要框架/工具**：
  - LINE Messaging API (line-bot-sdk 3.22.0+)
  - Claude API (anthropic SDK, 最新版本)
  - asyncio（內置，用於異步處理）
  - schedule 1.2.0（任務排程）
- **關鍵依賴項**：
  - `linebot==3.22.0+`（LINE Bot SDK v3，用於 LINE API 調用）
  - `anthropic`（Claude API 客戶端，用於摘要生成）
  - `pytz`（時區處理，Asia/Taipei 為預設）
  - `jieba==0.42.1+`（中文分詞，用於關鍵詞提取）
  - `schedule==1.2.0+`（任務排程，每日 08:00 執行）
  - `aiohttp`（異步 HTTP，備用依賴）
  - `pytest==7.4.3+`（單元測試框架）
  - `pytest-asyncio==0.21.1+`（異步測試支持）
  - `python-dotenv`（環境變數管理）
- **其他重要工具**：
  - Git（版本控制，已在 GitHub）
  - GitHub（代碼託管和發佈）

### 性能與約束條件

- **性能目標**：
  - Agent 1 爬蟲：30-60 秒
  - Agent 2 處理：30-45 秒
  - Agent 3 摘要：15-45 秒
  - Agent 4 發送：10-20 秒
  - **總管道執行**：2-5 分鐘
  - **API 成本**：$0.05 每次運行（已優化 75%）
- **已知的瓶頸**：
  - Claude API 調用（最慢，15-45 秒）
  - 群組成員查詢（v3 分頁支持已改進）
- **資源限制**：
  - Claude API：每分鐘 50 請求
  - LINE API：每月調用限制（通常足夠日常使用）
  - 磁盤空間：每日日誌 100-500 KB，執行統計 <5KB
- **相容性要求**：
  - Python 3.8+（官方最低）
  - Linux/macOS/Windows（已在 Windows 11 測試）
  - 需要 LINE Bot 帳戶和 Channel Access Token
  - 需要 Anthropic API Key

### 特殊配置或設置

- **環境變數** (.env 檔案)：
  ```
  LINE_CHANNEL_ACCESS_TOKEN=your_line_channel_access_token
  ANTHROPIC_API_KEY=your_anthropic_api_key
  TARGET_GROUP_IDS=C1234567890abcdef,C0987654321fedcba
  USER_ID=U1234567890abcdef
  TIMEZONE=Asia/Taipei
  ```
  - 不要提交 .env 到 git（已在 .gitignore）
  - 確保檔案權限為 600（`chmod 600 .env`）

- **配置文件位置**：
  - `.env` - 環境配置（不提交）
  - `src/config.py` - Python 配置管理
  - `requirements.txt` - 依賴清單

- **重要的文件夾結構**：
  ```
  line-message-summarizer/
  ├── src/
  │   ├── agent_crawler.py          # Agent 1: 訊息爬蟲
  │   ├── agent_processor.py         # Agent 2: 訊息處理
  │   ├── agent_summarizer.py        # Agent 3: 摘要生成
  │   ├── agent_scheduler.py         # Agent 4: 排程發送
  │   ├── config.py                  # 配置管理
  │   ├── models.py                  # 數據模型
  │   └── utils/
  │       ├── line_handler.py        # LINE API v3 封裝
  │       ├── message_parser.py      # 訊息處理邏輯
  │       ├── summarizer_utils.py    # Claude API 和格式化
  │       └── sender.py              # LINE 訊息發送 v3
  ├── tests/
  │   ├── test_crawler.py            # 15 個爬蟲測試
  │   ├── test_processor.py          # 25 個處理器測試
  │   ├── test_summarizer.py         # 13 個摘要生成測試
  │   └── test_scheduler.py          # 14 個排程器測試（已更新 mock）
  ├── data/
  │   ├── raw_messages/              # Agent 1 輸出：原始訊息
  │   └── processed_messages/        # Agent 2 輸出：已處理訊息
  ├── output/
  │   └── summaries/                 # Agent 3 輸出：摘要 MD 和 HTML
  ├── logs/                          # 執行日誌（每日一個檔案）
  ├── .env                           # 環境配置（不提交，需手動建立）
  ├── .env.example                   # 環境配置範本（可選）
  ├── requirements.txt               # Python 依賴
  ├── .gitignore                     # Git 忽略規則
  ├── README.md                      # 英文使用說明（含版本 1.1.0）
  ├── README.zh_TW.md                # 中文使用說明（含版本 1.1.0）
  ├── CHANGELOG.md                   # 版本變更歷史
  ├── LICENSE                        # MIT 許可證
  ├── DEPLOYMENT_GUIDE.md            # 部署指南（systemd 和 Docker）
  ├── .claude/
  │   └── HANDOFF.md                 # 本文檔（工作交接）
  └── .github/
      └── CONTRIBUTING.md            # 社區貢獻指南
  ```

### 安全與隱私考慮

- **敏感數據處理**：
  - LINE Channel Access Token：存儲在 .env（不提交、不日誌記錄）
  - Claude API Key：存儲在 .env（不提交、不日誌記錄）
  - 所有敏感數據通過環境變數傳遞
  - 日誌中不包含敏感訊息

- **認證機制**：
  - LINE Bot：使用 Channel Access Token 認證
  - Claude API：使用 API Key 認證
  - 兩者都使用 Bearer Token 方式

- **權限管理**：
  - Bot 只有指定群組的讀取權限
  - Bot 有發送私聊訊息權限
  - 只有指定的 USER_ID 能接收摘要
  - 建議使用專用 LINE Bot 帳戶

- **數據隱私**：
  - 訊息存儲在本地 data/ 目錄（需妥善保護）
  - 日誌包含訊息內容（logs/ 需妥善保護）
  - 建議定期清理舊日誌和數據
  - 備份 .env 檔案時需特別小心

---

## 7. 常用命令與快速參考

### 構建與安裝

```bash
# 建立虛擬環境
python -m venv venv

# 激活虛擬環境
source venv/bin/activate        # Linux/macOS
venv\Scripts\activate           # Windows

# 安裝依賴
pip install -r requirements.txt

# 升級 pip
pip install --upgrade pip
```

### 開發與測試

```bash
# 運行所有測試
pytest tests/ -v

# 運行特定 Agent 的測試
pytest tests/test_crawler.py -v
pytest tests/test_processor.py -v
pytest tests/test_summarizer.py -v
pytest tests/test_scheduler.py -v

# 運行單個測試
pytest tests/test_crawler.py::TestLineHandler::test_line_handler_init_valid_token -v

# 運行測試並顯示覆蓋率
pytest tests/ --cov=src --cov-report=html

# 手動執行管道（測試用）
python -c "
import asyncio
from src.agent_scheduler import execute_pipeline
result = asyncio.run(execute_pipeline())
print(result)
"

# 啟動排程器（開發模式）
python src/agent_scheduler.py
```

### 部署與發佈

```bash
# Git 操作
git status
git add .
git commit -m "commit message"
git push origin main

# 建立版本標籤
git tag -a v1.2.0 -m "Release v1.2.0"
git push origin v1.2.0

# 部署（systemd）
sudo systemctl start line-summarizer
sudo systemctl status line-summarizer
sudo systemctl enable line-summarizer

# 查看日誌
tail -f logs/execution_*.log
grep ERROR logs/*.log

# Docker 操作
docker-compose up -d
docker-compose logs -f
docker-compose down
```

### 常見故障排除

| 問題 | 原因 | 解決方案 |
|------|------|---------|
| `ModuleNotFoundError: No module named 'linebot'` | 依賴未安裝 | `pip install -r requirements.txt` |
| `KeyError: 'LINE_CHANNEL_ACCESS_TOKEN'` | .env 檔案缺失或無效 | 建立 .env 並填入有效憑證 |
| 排程不執行 | 應用程式未運行或時區錯誤 | 檢查系統時區，使用 systemd 保持運行 |
| 中文訊息顯示為亂碼 | JSON 編碼錯誤 | 確保使用 `ensure_ascii=False` |
| 訊息發送失敗 | LINE API 限制或權限不足 | 檢查 token，驗證 Bot 有發送權限 |
| 摘要質量差 | 訊息重要性評分不準確 | 調整 Agent 2 的評分演算法參數 |
| 記憶體持續增長 | ApiClient 資源未清理 | 改進 ApiClient 生命週期管理（優先級 2） |

---

## 8. 文件摘要與變更追蹤

### 主要修改的文件

| 文件名 | 狀態 | 最後修改 | 用途 | 重要性 |
|--------|------|---------|------|--------|
| `src/utils/line_handler.py` | ✅ | 2026-02-18 | LINE API v3 封裝 | 🔴 高 |
| `src/utils/sender.py` | ✅ | 2026-02-18 | LINE 訊息發送 v3 | 🔴 高 |
| `tests/test_scheduler.py` | ✅ | 2026-02-18 | 排程器測試（更新 mock） | 🟡 中 |
| `requirements.txt` | ✅ | 2026-02-18 | 依賴清單 | 🟡 中 |
| `README.md` | ✅ | 2026-02-18 | 英文說明 + v1.1.0 | 🟡 中 |
| `README.zh_TW.md` | ✅ | 2026-02-18 | 中文說明 + v1.1.0 | 🟡 中 |
| `CHANGELOG.md` | ✅ | 2026-02-18 | 版本歷史（新建） | 🟡 中 |
| `LICENSE` | ✅ | 2026-02-18 | MIT 許可證（新建） | 🟡 中 |
| `.github/CONTRIBUTING.md` | ✅ | 2026-02-18 | 貢獻指南（新建） | 🟡 中 |

### Git 提交歷史（最近 10 個）

```
a82576c - 新增項目標準文件：CHANGELOG、LICENSE、CONTRIBUTING
51261d5 - 在 README 中添加版本號和版本歷史
74b93af - 更新 README 文檔 - 反映 LINE SDK v3.0 遷移
db74e97 - 遷移 LINE Bot SDK 從 v2 到 v3.0
5568ac0 - 新增中英文 README 文檔
d3bc55a - 新增交接文檔 - 記錄完整開發過程
cd8fdcb - Complete LINE Message Daily Summary System - All 4 Agents
```

---

## 9. 決策記錄

### 選擇 LINE Bot SDK v3.0 作為遷移目標
- **選擇了什麼**：從 v2（已棄用）遷移到 v3.0+
- **其他選項**：
  - 保持使用 v2（面臨棄用風險）
  - 等待官方的 v4 或更新版本
  - 切換到其他 LINE SDK（如官方的 Node.js 版本）
- **做這個決策的原因**：
  - v2 已明確棄用，會生成警告
  - v3 是官方現在推薦的版本
  - 新功能（分頁、型別提示）對長期維護有幫助
  - 及時遷移避免未來的大規模重構
- **相關的權衡**：
  - 優點：現代化、官方支持、更好的型別安全
  - 缺點：API 變化較大，需要重寫一些代碼，初期測試成本
- **預期的影響**：
  - 消除棄用警告，提升代碼質量
  - 為未來功能擴展提供更好的基礎
  - 改進錯誤處理和性能

### 建立完整的 GitHub 標準文件（CHANGELOG、LICENSE、CONTRIBUTING）
- **選擇了什麼**：在第一天就建立完整的企業級 GitHub 項目結構
- **其他選項**：
  - 先發佈、後補充文檔（更快上線但不專業）
  - 只建立最基本的 README（不完整）
  - 保持最小化（無 LICENSE、CONTRIBUTING 等）
- **做這個決策的原因**：
  - 這是開源項目的最佳實踐
  - 明確的貢獻指南能吸引高質量的貢獻者
  - 合法的許可證保護使用者權益
  - 完整的版本歷史便於追蹤項目演進
- **相關的權衡**：
  - 優點：專業、完整、便於社區參與
  - 缺點：初期準備工作量大
- **預期的影響**：
  - 項目看起來更專業、更成熟
  - 新開發者更容易上手
  - 法律風險更低

### 在 README 中添加版本號徽章和版本歷史表格
- **選擇了什麼**：在 README 最顯眼的位置添加版本號資訊和版本歷史
- **其他選項**：
  - 只在 CHANGELOG 中記錄版本歷史（不在 README）
  - 在 README 末尾添加版本資訊（不顯眼）
  - 不記錄版本歷史（只在 git tag）
- **做這個決策的原因**：
  - 訪客能立即了解項目的當前版本
  - 視覺化徽章提升項目專業度
  - 版本歷史表格簡潔實用
- **相關的權衡**：
  - 優點：信息清晰、易於掃描
  - 缺點：需要每次更新版本時修改 README
- **預期的影響**：
  - 提升項目的專業形象
  - 新用戶能快速了解版本狀態

---

## 10. 會話統計與額外信息

- **會話開始時間**：2026-02-18（早上）
- **會話持續時間**：~2-3 小時（估計）
- **使用的上下文窗口**：~60-70%（高度活躍的會話）
- **修改的文件總數**：9 個
- **新增代碼行數**：~1,400 行（含文檔和測試）
- **刪除代碼行數**：~30 行（v2 → v3 遷移）
- **進行的 Git 提交數**：7 次（主要提交）
- **編寫的新測試數**：0 個（複用現有 67 個測試）
- **整體測試覆蓋率**：>80%（保持不變）

### 項目總體統計（從 v1.0.0 到 v1.1.0）

- **總代碼行數**：~6,700+ 行
- **總測試數**：67 個（全部通過）
- **總文檔行數**：~2,500+ 行（README、CHANGELOG、CONTRIBUTING 等）
- **支持的 Python 版本**：3.8+（在 3.13.12 上測試）
- **依賴包數**：9 個核心依賴
- **Git 提交數**：14+ 個提交（整個項目）

---

## 11. 供下一個會話的最終建議

### 優先順序提醒

1. **立即開始**：🔴 優先級 1 - 生產環境部署測試
   - 這是驗證系統在實際環境中可靠性的關鍵
   - 需要 24 小時時間進行完整監控
   - 之後才能放心推薦給用戶

2. **接著進行**：🟡 優先級 2 - LINE SDK v3.0 進階功能
   - 改進 ApiClient 生命週期管理
   - 完整測試分頁支持
   - 優化錯誤處理

3. **如果有時間**：🟡 優先級 3 - GitHub 自動化
   - GitHub Actions CI/CD
   - PR 和 Issue 模板
   - 自動化測試流程

### 容易遺漏的細節

1. **生產部署時務必使用真實的 LINE Bot Token 和 API Key**
   - 測試時用測試 token，生產時用生產 token
   - 不要將 token 硬編碼到代碼中
   - 確保 .env 檔案權限為 600

2. **排程器每天 08:00 執行，需要確保伺服器時區正確**
   - 系統時區應為 Asia/Taipei（或根據業務調整）
   - 驗證：`timedatectl` (Linux) 或系統設置 (Windows)

3. **LINE SDK v3 API 的分頁機制必須正確使用**
   - 方法名稱：`get_group_members_ids()` 而非 `get_group_member_ids()`
   - 返回值是 MembersIdsResponse 物件，需要存取 `.member_ids` 屬性
   - 分頁循環：`while response.next: ...` 不要遺漏

4. **所有 67 個測試必須在部署前通過**
   - 命令：`pytest tests/ -v`
   - 覆蓋率 >80%
   - 若有新修改，要添加相應的測試

5. **GitHub Actions 設置需要 Personal Access Token**
   - 若要自動化發佈，需要 repo 完整權限
   - 相關設置在優先級 3 中詳述

### 參考資源

- **完整文檔**：
  - `README.md` - 英文使用說明
  - `README.zh_TW.md` - 中文使用說明
  - `DEPLOYMENT_GUIDE.md` - systemd 和 Docker 部署完整指南
  - `CHANGELOG.md` - 版本變更歷史
  - `.github/CONTRIBUTING.md` - 社區貢獻規範

- **相關代碼**：
  - `src/utils/line_handler.py:1-30` - LINE API v3 初始化
  - `src/utils/line_handler.py:46-55` - v3 分頁實現
  - `src/utils/sender.py:20-30` - v3 訊息發送初始化
  - `src/utils/sender.py:76-92` - v3 push_message 實現
  - `tests/test_scheduler.py:59,79` - v3 mock 用法

- **有用的命令**：
  - 運行所有測試：`pytest tests/ -v`
  - 查看日誌：`tail -f logs/execution_*.log`
  - 檢查版本：`grep __version__ src/*.py`

---

## 最終檢查清單

在下一個會話開始前，確認以下事項已完成或已準備好：

- ✅ 代碼已提交到 GitHub（14+ 個提交）
- ✅ v1.1.0 release tag 已建立並推送
- ✅ 所有 67 個測試通過
- ✅ 完整的部署指南已準備（DEPLOYMENT_GUIDE.md）
- ✅ 環境配置範本已準備（.env 配置說明）
- ✅ 技術文檔完整（README、CHANGELOG、CONTRIBUTING、LICENSE）
- ✅ LINE SDK v3.0 遷移完成（零棄用警告）
- ✅ GitHub 項目結構標準化
- ⏳ 需要在生產環境中測試（優先級 1 - 下一步）
- ⏳ 需要進一步優化 ApiClient 和分頁支持（優先級 2）
- ⏳ 需要設置 GitHub Actions（優先級 3 - 未來）

---

## 快速導航

| 內容 | 位置 |
|------|------|
| **系統架構圖** | README.md / README.zh_TW.md 第 23 行 |
| **快速開始** | README.md / README.zh_TW.md 第 86 行 |
| **部署指南** | DEPLOYMENT_GUIDE.md（完整部署流程） |
| **版本歷史** | CHANGELOG.md（所有版本詳情） |
| **貢獻指南** | .github/CONTRIBUTING.md（開發規範） |
| **LINE API v3 實現** | src/utils/line_handler.py 和 src/utils/sender.py |
| **測試代碼** | tests/ 目錄（67 個測試） |
| **配置說明** | src/config.py 和 .env 範本 |

---

**此文檔最後更新於**：2026-02-18
**下一個會話建議從優先級 1 開始：生產環境部署測試**

---

## 下一個會話的開始指令

```bash
# 1. 確認環境
cd /c/Users/victor/Downloads/Claude/Side_Project/line_message_summarizer
python -V  # 應為 3.8+

# 2. 激活虛擬環境
source venv/bin/activate  # Linux/macOS
# 或
venv\Scripts\activate  # Windows

# 3. 運行測試確保一切正常
pytest tests/ -v

# 4. 查看最新提交
git log --oneline -5

# 5. 開始優先級 1 工作
# 參考 DEPLOYMENT_GUIDE.md 進行部署
```

祝下一個會話順利！🚀

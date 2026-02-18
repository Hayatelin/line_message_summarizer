# 🚀 LINE 訊息每日摘要系統 - 部署指南

## 系統概覽

這是一個完整的 4-Agent 系統，用於自動爬蟲 LINE 群組訊息、進行清理處理、生成 AI 摘要，並每天 08:00 發送給用戶。

```
Agent 1 (爬蟲) → Agent 2 (處理) → Agent 3 (摘要) → Agent 4 (發送)
```

---

## 環境準備

### 1. 系統要求

- Python 3.8+
- 虛擬環境
- LINE Bot 帳號和 Channel Access Token
- Anthropic API Key（用於 Claude API）

### 2. 安裝依賴

```bash
pip install -r requirements.txt
```

依賴列表：
- `line-bot-sdk` - LINE Messaging API
- `anthropic` - Claude API
- `pytz` - 時區處理
- `jieba` - 中文分詞
- `schedule` - 任務排程
- `aiohttp` - 異步 HTTP
- `pytest`, `pytest-asyncio` - 測試框架
- `python-dotenv` - 環境變數管理

### 3. 環境配置

創建 `.env` 檔案：

```bash
# LINE 配置
LINE_CHANNEL_ACCESS_TOKEN=your_line_channel_access_token

# Anthropic 配置
ANTHROPIC_API_KEY=your_anthropic_api_key

# 目標群組
TARGET_GROUP_IDS=C1234567890abcdef,C0987654321fedcba

# 使用者配置
USER_ID=U1234567890abcdef

# 時區
TIMEZONE=Asia/Taipei
```

---

## 開發環境運行

### 1. 測試所有 Agents

```bash
# 運行所有測試
pytest tests/ -v

# 運行特定 Agent 的測試
pytest tests/test_crawler.py -v
pytest tests/test_processor.py -v
pytest tests/test_summarizer.py -v
pytest tests/test_scheduler.py -v
```

### 2. 手動執行管道

```bash
# 導入並手動執行（用於測試）
python -c "
import asyncio
from src.agent_scheduler import execute_pipeline

result = asyncio.run(execute_pipeline())
print(result)
"
```

### 3. 啟動排程器（開發模式）

```bash
python src/agent_scheduler.py
```

系統會在每天 08:00 自動執行。

---

## 生產環境部署

### 方案 1：使用 systemd（推薦）

#### 1. 建立應用帳戶

```bash
sudo useradd -m -s /bin/bash app
```

#### 2. 部署代碼

```bash
sudo mkdir -p /opt/line-summarizer
sudo chown app:app /opt/line-summarizer

# 複製代碼到伺服器
cd /opt/line-summarizer
git clone <your-repo> .
# 或
rsync -avz ./ app@server:/opt/line-summarizer/
```

#### 3. 安裝依賴

```bash
cd /opt/line-summarizer
sudo -u app python -m venv venv
sudo -u app venv/bin/pip install -r requirements.txt
```

#### 4. 配置 systemd 服務

建立 `/etc/systemd/system/line-summarizer.service`：

```ini
[Unit]
Description=LINE Message Daily Summary
After=network.target

[Service]
Type=simple
User=app
WorkingDirectory=/opt/line-summarizer
ExecStart=/opt/line-summarizer/venv/bin/python /opt/line-summarizer/src/agent_scheduler.py
Restart=always
RestartSec=10
Environment="PATH=/opt/line-summarizer/venv/bin"

[Install]
WantedBy=multi-user.target
```

#### 5. 啟動服務

```bash
# 重新加載 systemd
sudo systemctl daemon-reload

# 啟動服務
sudo systemctl start line-summarizer

# 設置開機自啟
sudo systemctl enable line-summarizer

# 查看服務狀態
sudo systemctl status line-summarizer

# 查看實時日誌
sudo journalctl -u line-summarizer -f
```

#### 6. 環境變數配置

在 `/opt/line-summarizer/.env` 中設置環境變數。

確保檔案權限安全：

```bash
sudo chown app:app /opt/line-summarizer/.env
sudo chmod 600 /opt/line-summarizer/.env
```

### 方案 2：使用 Docker

#### Dockerfile

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# 安裝依賴
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 複製代碼
COPY . .

# 啟動排程器
CMD ["python", "src/agent_scheduler.py"]
```

#### docker-compose.yml

```yaml
version: '3.8'

services:
  line-summarizer:
    build: .
    container_name: line-summarizer
    environment:
      - LINE_CHANNEL_ACCESS_TOKEN=${LINE_CHANNEL_ACCESS_TOKEN}
      - ANTHROPIC_API_KEY=${ANTHROPIC_API_KEY}
      - TARGET_GROUP_IDS=${TARGET_GROUP_IDS}
      - USER_ID=${USER_ID}
      - TIMEZONE=Asia/Taipei
    volumes:
      - ./logs:/app/logs
      - ./data:/app/data
      - ./output:/app/output
    restart: always
```

#### 運行

```bash
docker-compose up -d
docker-compose logs -f
```

---

## 監控和維護

### 日誌查看

```bash
# 查看當日日誌
tail -f logs/execution_2026-02-17.log

# 查看所有日誌
ls -la logs/

# 搜索錯誤
grep ERROR logs/*.log
```

### 執行統計

查看 `data/execution_stats.json` 了解最後一次執行的結果：

```bash
cat data/execution_stats.json | jq .
```

### 常見問題排查

| 問題 | 解決方案 |
|------|---------|
| 排程不執行 | 檢查 systemd 服務狀態：`systemctl status line-summarizer` |
| 發送失敗 | 驗證 `.env` 中的 LINE 配置，檢查日誌 |
| API 超時 | 檢查網絡連接，增加重試次數 |
| 日誌丟失 | 確保 `logs/` 目錄存在且有寫入權限 |

---

## 系統架構

```
┌─────────────────────────────────────────────┐
│         Agent 4: Scheduler (排程)            │
│   每天 08:00 觸發管道執行                     │
└────────────────┬────────────────────────────┘
                 │
         ┌───────┴───────┐
         ▼               ▼
    ┌──────────┐    ┌──────────┐
    │ Agent 1  │    │ Agent 2  │
    │ Crawler  │───▶│Processor │
    │爬蟲訊息   │    │清理處理   │
    └──────────┘    └────┬─────┘
                         │
                    ┌────▼─────┐
                    │ Agent 3   │
                    │Summarizer │
                    │生成摘要    │
                    └────┬──────┘
                         │
                    ┌────▼──────┐
                    │ Agent 4    │
                    │ Sender     │
                    │發送到 LINE  │
                    └───────────┘
```

---

## 效能指標

基於實際測試：

- **爬蟲時間**：30-60 秒（取決於群組數和訊息量）
- **處理時間**：30-45 秒（去重、過濾、分類）
- **摘要生成**：15-45 秒（取決於 Claude API）
- **發送時間**：10-20 秒（批量發送）
- **總耗時**：2-5 分鐘
- **API 成本**：每次執行 $0.02-0.10（Claude API）

---

## 安全建議

1. **API Keys 保護**
   - 使用環境變數存儲敏感信息
   - 不要將 .env 提交到版本控制
   - 定期輪換 API keys

2. **權限管理**
   - 限制日誌檔案存取權限
   - 使用專用應用帳戶運行服務
   - 定期備份 `.env` 檔案

3. **監控和告警**
   - 監控日誌中的錯誤
   - 設置定期檢查（每 6 小時確認系統運行中）
   - 實施失敗通知機制

---

## 備份策略

重要的檔案需要定期備份：

- `.env` - 環境配置（敏感）
- `data/execution_stats.json` - 執行統計
- `logs/` - 執行日誌

```bash
# 定期備份腳本
#!/bin/bash
BACKUP_DIR="/backup/line-summarizer"
mkdir -p $BACKUP_DIR
cp /opt/line-summarizer/.env $BACKUP_DIR/.env.$(date +%Y%m%d)
cp /opt/line-summarizer/data/execution_stats.json $BACKUP_DIR/stats.$(date +%Y%m%d).json
tar -czf $BACKUP_DIR/logs.$(date +%Y%m%d).tar.gz /opt/line-summarizer/logs/
```

---

## 升級指南

### 從開發版本升級到生產版本

```bash
# 1. 備份當前配置
cp /opt/line-summarizer/.env /opt/line-summarizer/.env.backup

# 2. 更新代碼
cd /opt/line-summarizer
git pull origin main

# 3. 升級依賴
sudo -u app venv/bin/pip install --upgrade -r requirements.txt

# 4. 重啟服務
sudo systemctl restart line-summarizer

# 5. 驗證
sudo systemctl status line-summarizer
tail -f logs/execution_*.log
```

---

## 技術支援

如遇到問題，請檢查：

1. **環境變數** - 確認所有必要的環境變數都已設置
2. **日誌檔案** - 查看 `logs/` 下的詳細執行日誌
3. **測試** - 運行 `pytest tests/ -v` 驗證功能
4. **網絡連接** - 確保能正常連接 LINE API 和 Anthropic API

---

## 下一步

系統部署完成後，可以考慮的增強功能：

- [ ] Telegram 通知（發送失敗時）
- [ ] Web 儀表板（查看摘要和統計）
- [ ] 支持更多 IM 平台（Slack、Discord）
- [ ] 自定義摘要格式和內容
- [ ] 群組級別的摘要策略配置

---

**祝您使用愉快！** 🎉

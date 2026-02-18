"""Summarizer utilities for Agent 3 - Generates summaries using Claude API"""

import logging
import asyncio
from typing import Dict, List
import anthropic

logger = logging.getLogger(__name__)


def create_summary_prompt(group_data: dict) -> str:
    """構建發送給 Claude 的 prompt

    策略：
    1. 只傳遞已過濾和分類的訊息
    2. 按重要性篩選（只傳遞 importance >= 0.5 的訊息）
    3. 使用簡潔的訊息格式
    4. 明確指定輸出格式和字數限制

    Args:
        group_data: 處理後的群組訊息數據，格式：
            {
                "group_id": "...",
                "group_name": "...",
                "date": "...",
                "messages": [...],
                "stats": {...}
            }

    Returns:
        完整的 prompt 字符串，優化了成本

    Note:
        成本優化策略：
        - 原始訊息：38 條 × 50 字/條 = 1,900 字
        - 只傳遞 importance >= 0.5 的訊息 → ~800 字
        - 簡潔 prompt → 總計 ~1,200 字（減少 37%）
    """
    messages = group_data.get('messages', [])
    group_name = group_data.get('group_name', 'Unknown')
    date = group_data.get('date', 'Unknown')

    # 篩選重要訊息 (importance >= 0.5)
    important_messages = [
        msg for msg in messages
        if msg.get('importance', 0) >= 0.5
    ]

    # 如果沒有重要訊息，至少選擇前 5 條
    if not important_messages:
        important_messages = messages[:5]

    # 格式化訊息
    formatted_messages = _format_messages_for_prompt(important_messages)

    # 獲取統計信息
    stats = group_data.get('stats', {})
    top_senders = stats.get('top_senders', [])
    top_keywords = stats.get('top_keywords', [])
    message_types = stats.get('message_types', {})

    # 構建 prompt
    prompt = f"""你是一個專業的 LINE 群組訊息分析師。我需要你為一個工作群組生成高質量的日報摘要。

【群組信息】
群組名稱：{group_name}
日期：{date}
訊息總數：{len(messages)}
已分析訊息：{len(important_messages)}

【關鍵訊息】
{formatted_messages}

【統計信息】
- 最活躍成員：{', '.join(s['name'] for s in top_senders[:3])}
- 關鍵詞：{', '.join(top_keywords[:5]) if top_keywords else 'N/A'}
- 訊息類型分布：{dict(message_types)}

【要求】
請根據上述關鍵訊息生成一份簡潔的日報摘要，遵循以下格式：

## 核心要點
[3-5 個要點，突出重要決議和進度更新]

## 關鍵發言
[2-3 條重要的發言或引用]

## 待辦事項
[提取的待辦項目，使用 - [ ] 格式]

## 統計信息
[簡要的統計總結]

要求：
- 總字數 200-500 字
- 使用簡潔清晰的語言
- 中文輸出
- 突出重要信息和行動項
- 直接返回摘要內容，不需要前言"""

    return prompt


def _format_messages_for_prompt(messages: List[dict]) -> str:
    """格式化訊息用於 prompt

    Args:
        messages: 訊息列表

    Returns:
        格式化的訊息字符串
    """
    formatted = []

    for msg in messages:
        sender = msg.get('sender_name', 'Unknown')
        content = msg.get('content', '')
        category = msg.get('category', 'other')
        importance = msg.get('importance', 0)

        # 只顯示重要訊息
        if len(content) > 100:
            content = content[:100] + "..."

        formatted.append(
            f"- [{category.upper()}] {sender}: {content} (重要度: {importance})"
        )

    return '\n'.join(formatted[:20])  # 最多 20 條訊息


async def call_claude_api(
    prompt: str,
    model: str = "claude-3-5-sonnet-20241022",
    max_retries: int = 3
) -> str:
    """調用 Claude API 生成摘要

    Args:
        prompt: 完整的摘要生成 prompt
        model: 使用的模型
        max_retries: 最大重試次數

    Returns:
        生成的摘要文本

    Raises:
        Exception: 所有重試都失敗時

    Note:
        實現了指數退避重試機制，處理超時和速率限制
    """
    logger.info(f"Calling Claude API with model: {model}")

    client = anthropic.Anthropic()

    for attempt in range(max_retries):
        try:
            logger.debug(f"API call attempt {attempt + 1}/{max_retries}")

            message = client.messages.create(
                model=model,
                max_tokens=1024,
                messages=[
                    {
                        "role": "user",
                        "content": prompt
                    }
                ]
            )

            summary = message.content[0].text
            logger.info("API call successful")
            return summary

        except anthropic.APIStatusError as e:
            logger.warning(f"API status error on attempt {attempt + 1}: {e}")

            # 如果是速率限制或超時，重試
            if e.status_code in [429, 500, 502, 503, 504]:
                if attempt < max_retries - 1:
                    wait_time = 2 ** attempt  # 指數退避: 1, 2, 4 秒
                    logger.info(f"Retrying after {wait_time} seconds...")
                    await asyncio.sleep(wait_time)
                    continue

            raise

        except anthropic.APIConnectionError as e:
            logger.warning(f"API connection error on attempt {attempt + 1}: {e}")

            if attempt < max_retries - 1:
                wait_time = 2 ** attempt
                logger.info(f"Retrying after {wait_time} seconds...")
                await asyncio.sleep(wait_time)
                continue

            raise

        except Exception as e:
            logger.error(f"Unexpected error on attempt {attempt + 1}: {e}")
            raise

    raise Exception(f"API call failed after {max_retries} retries")


def format_summary_markdown(
    group_name: str,
    date: str,
    summary: str,
    metadata: Dict
) -> str:
    """將摘要和元數據格式化為 Markdown

    包含：
    - 標題和日期
    - 摘要內容（來自 Claude API）
    - 群組統計信息
    - 生成時間戳

    Args:
        group_name: 群組名稱
        date: 日期字符串 (YYYY-MM-DD)
        summary: Claude API 生成的摘要內容
        metadata: 元數據字典，包含：
            - total_messages: 訊息總數
            - top_senders: 頂級發送者列表
            - message_types: 訊息類型分布
            - top_keywords: 關鍵詞

    Returns:
        完整的 Markdown 文本
    """
    total_messages = metadata.get('total_messages', 0)
    top_senders = metadata.get('top_senders', [])
    message_types = metadata.get('message_types', {})
    top_keywords = metadata.get('top_keywords', [])

    # 構建發言者列表
    active_members = ', '.join(
        sender['name'] for sender in top_senders[:5]
    )

    # 構建訊息類型統計
    types_stats = ' | '.join(
        f"{msg_type}: {count}"
        for msg_type, count in list(message_types.items())[:3]
    )

    markdown = f"""# 📱 {group_name} - 日報摘要

**日期**：{date}
**訊息數**：{total_messages}
**活躍成員**：{active_members}

---

{summary}

---

## 📊 群組統計

- 總訊息：{total_messages}
- 訊息分布：{types_stats}
- 最活躍：{top_senders[0]['name'] if top_senders else 'N/A'} ({top_senders[0]['count'] if top_senders else 0} 條)
- 關鍵詞：{', '.join(top_keywords[:5]) if top_keywords else 'N/A'}

---

*此摘要由 AI 自動生成*
"""

    return markdown


def generate_index_html(
    date: str,
    summaries: Dict[str, Dict]
) -> str:
    """生成 HTML 索引頁面

    Args:
        date: 日期字符串
        summaries: 摘要數據字典
            {
                "group_id": {
                    "group_name": "...",
                    "file_path": "...",
                    "message_count": ...
                }
            }

    Returns:
        完整的 HTML 字符串
    """
    cards = []

    for group_id, data in summaries.items():
        group_name = data.get('group_name', 'Unknown')
        file_path = data.get('file_path', '')
        message_count = data.get('message_count', 0)

        # 生成文件路徑（相對路徑）
        file_name = file_path.split('/')[-1]  # 只取檔案名

        card = f"""        <div class="summary-card">
            <h2>{group_name}</h2>
            <p>{message_count} 條訊息</p>
            <a href="{file_name}" class="btn">查看摘要</a>
        </div>"""

        cards.append(card)

    cards_html = '\n'.join(cards)

    html = f"""<!DOCTYPE html>
<html lang="zh-TW">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>LINE 群組日報摘要 - {date}</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}

        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 40px 20px;
        }}

        .container {{
            max-width: 1200px;
            margin: 0 auto;
        }}

        header {{
            text-align: center;
            color: white;
            margin-bottom: 50px;
        }}

        header h1 {{
            font-size: 2.5em;
            margin-bottom: 10px;
        }}

        header p {{
            font-size: 1.1em;
            opacity: 0.9;
        }}

        .summaries {{
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
            gap: 20px;
        }}

        .summary-card {{
            background: white;
            border-radius: 12px;
            padding: 25px;
            box-shadow: 0 10px 30px rgba(0, 0, 0, 0.2);
            transition: transform 0.3s, box-shadow 0.3s;
        }}

        .summary-card:hover {{
            transform: translateY(-5px);
            box-shadow: 0 15px 40px rgba(0, 0, 0, 0.3);
        }}

        .summary-card h2 {{
            color: #333;
            margin-bottom: 10px;
            font-size: 1.5em;
        }}

        .summary-card p {{
            color: #666;
            margin-bottom: 20px;
            font-size: 0.95em;
        }}

        .btn {{
            display: inline-block;
            background: #667eea;
            color: white;
            padding: 10px 20px;
            text-decoration: none;
            border-radius: 6px;
            transition: background 0.3s;
            font-weight: 500;
        }}

        .btn:hover {{
            background: #764ba2;
        }}
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>📱 LINE 群組日報摘要</h1>
            <p>生成日期：{date}</p>
        </header>

        <div class="summaries">
{cards_html}
        </div>
    </div>
</body>
</html>"""

    return html

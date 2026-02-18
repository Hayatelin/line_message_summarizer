"""Message crawler for LINE groups - Agent 1"""

import logging
import asyncio
import json
from typing import Dict, List
from datetime import datetime, timedelta
from pathlib import Path
import pytz

from src.config import Config
from src.models import Message, GroupMessages
from src.utils.line_handler import LineHandler

logger = logging.getLogger(__name__)


async def crawl_messages(
    group_ids: List[str],
    date: str
) -> Dict[str, List[dict]]:
    """爬蟲 LINE 群組訊息

    根據指定日期爬取前一天的所有訊息。支持多個群組並發爬取。

    Args:
        group_ids: 群組 ID 列表 (格式: ["C1234...", "C0987..."])
        date: 日期字符串 (格式: "YYYY-MM-DD", 例如 "2026-02-17")
              將爬取此日期前一天的訊息

    Returns:
        字典結構:
        {
            "group_id_1": [
                {
                    "message_id": "100001",
                    "timestamp": "2026-02-17T09:15:30+08:00",
                    "sender_id": "U1234...",
                    "sender_name": "Alice",
                    "message_type": "text",
                    "content": "Hello",
                    "attachments": []
                },
                ...
            ],
            "group_id_2": [...],
            ...
        }

    Raises:
        ValueError: 日期格式錯誤或群組列表為空
        Exception: 爬蟲失敗時
    """
    logger.info(
        f"Starting message crawler for {len(group_ids)} groups, date: {date}"
    )

    # 驗證輸入
    if not group_ids:
        raise ValueError("Group IDs list cannot be empty")

    try:
        # 解析日期並計算時間範圍
        target_date = datetime.strptime(date, "%Y-%m-%d").date()
        tz = pytz.timezone(Config.TIMEZONE)

        # 計算前一天的時間範圍 (00:00:00 - 23:59:59)
        crawl_date = target_date - timedelta(days=1)
        start_datetime = datetime.combine(
            crawl_date,
            datetime.min.time()
        ).replace(tzinfo=tz)
        end_datetime = datetime.combine(
            crawl_date,
            datetime.max.time()
        ).replace(tzinfo=tz)

        # 轉換為毫秒級 Unix time
        start_time_ms = int(start_datetime.timestamp() * 1000)
        end_time_ms = int(end_datetime.timestamp() * 1000)

        logger.info(
            f"Crawling date range: {crawl_date} "
            f"({start_time_ms} - {end_time_ms})"
        )

        # 初始化 LINE Handler
        handler = LineHandler(Config.LINE_CHANNEL_ACCESS_TOKEN)

        # 並發爬取所有群組
        tasks = [
            _crawl_single_group(
                handler,
                group_id,
                crawl_date,
                start_time_ms,
                end_time_ms
            )
            for group_id in group_ids
        ]

        results = await asyncio.gather(*tasks, return_exceptions=True)

        # 構建結果字典
        crawled_data = {}
        for group_id, result in zip(group_ids, results):
            if isinstance(result, Exception):
                logger.error(
                    f"Failed to crawl group {group_id}: {result}"
                )
                crawled_data[group_id] = []
            else:
                crawled_data[group_id] = result

        # 保存結果到 JSON 檔案
        await _save_messages_to_files(crawled_data, date)

        logger.info("Message crawler completed successfully")
        return crawled_data

    except ValueError as e:
        logger.error(f"Invalid input: {e}")
        raise
    except Exception as e:
        logger.error(f"Crawler error: {e}")
        raise


async def _crawl_single_group(
    handler: LineHandler,
    group_id: str,
    crawl_date,
    start_time_ms: int,
    end_time_ms: int
) -> List[dict]:
    """爬取單個群組的訊息 (內部函數)

    Args:
        handler: LineHandler 實例
        group_id: 群組 ID
        crawl_date: 要爬取的日期
        start_time_ms: 開始時間 (毫秒)
        end_time_ms: 結束時間 (毫秒)

    Returns:
        訊息列表
    """
    logger.info(f"Crawling messages for group: {group_id}")

    try:
        # 從 LINE API 獲取訊息
        messages = await handler.get_group_messages(
            group_id,
            start_time_ms,
            end_time_ms
        )

        logger.info(
            f"Successfully fetched {len(messages)} messages from {group_id}"
        )
        return messages

    except Exception as e:
        logger.error(f"Error crawling group {group_id}: {e}")
        return []


async def _save_messages_to_files(
    crawled_data: Dict[str, List[dict]],
    date: str
) -> None:
    """將爬取的訊息保存到 JSON 檔案 (內部函數)

    檔案位置: data/raw_messages/{group_id}_{date}.json

    Args:
        crawled_data: 爬取的訊息數據
        date: 日期字符串 (YYYY-MM-DD)
    """
    output_dir = Path(Config.RAW_MESSAGES_DIR)
    output_dir.mkdir(parents=True, exist_ok=True)

    for group_id, messages in crawled_data.items():
        filename = output_dir / f"{group_id}_{date}.json"

        # 構建輸出數據
        output_data = {
            "group_id": group_id,
            "group_name": f"Group_{group_id[:8]}",
            "date": date,
            "total_messages": len(messages),
            "messages": messages
        }

        try:
            with open(filename, "w", encoding="utf-8") as f:
                json.dump(
                    output_data,
                    f,
                    ensure_ascii=False,
                    indent=2
                )
            logger.info(f"Saved messages to {filename}")
        except Exception as e:
            logger.error(f"Error saving messages to {filename}: {e}")
            raise

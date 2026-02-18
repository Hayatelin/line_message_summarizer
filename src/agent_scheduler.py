"""Scheduler for Agent 4 - Orchestrates daily pipeline execution"""

import logging
import asyncio
import json
import schedule
import time
from typing import Dict, Any
from datetime import datetime, timedelta
from pathlib import Path
import pytz

from src.config import Config
from src.agent_crawler import crawl_messages
from src.agent_processor import process_messages
from src.agent_summarizer import generate_summaries
from src.utils.sender import LineSender

# 配置日誌
log_dir = Path(Config.LOGS_DIR)
log_dir.mkdir(exist_ok=True)

log_file = log_dir / f"execution_{datetime.now().strftime('%Y-%m-%d')}.log"

logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] %(levelname)s: %(message)s',
    handlers=[
        logging.FileHandler(log_file),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)


def schedule_daily_tasks(time_str: str = "08:00") -> None:
    """設置每日定時任務

    Args:
        time_str: 執行時間，格式 "HH:MM" (例如 "08:00")

    Note:
        - 使用 schedule 庫設置
        - 無限循環監控
        - 調用 execute_pipeline() 執行管道
    """
    logger.info(f"Scheduling daily tasks at {time_str}")

    # 設置每日執行
    schedule.every().day.at(time_str).do(
        _run_async_pipeline,
        asyncio.get_event_loop()
    )

    logger.info("Daily schedule configured, waiting for execution time...")

    # 無限循環檢查排程
    try:
        while True:
            schedule.run_pending()
            time.sleep(60)  # 每 60 秒檢查一次
    except KeyboardInterrupt:
        logger.info("Scheduler stopped by user")
    except Exception as e:
        logger.error(f"Scheduler error: {e}")
        raise


def _run_async_pipeline(loop):
    """運行異步管道 (內部函數)

    Args:
        loop: asyncio event loop
    """
    try:
        result = loop.run_until_complete(execute_pipeline())
        logger.info(f"Pipeline result: {result['status']}")
    except Exception as e:
        logger.error(f"Pipeline execution failed: {e}")


async def execute_pipeline() -> Dict[str, Any]:
    """執行完整的摘要生成管道

    流程：
    1. 記錄開始時間
    2. 調用 Agent 1 爬蟲訊息
    3. 調用 Agent 2 處理訊息
    4. 調用 Agent 3 生成摘要
    5. 調用 Agent 4 發送摘要
    6. 記錄統計信息
    7. 保存執行結果

    Returns:
        {
            "status": "success" or "failure",
            "duration_seconds": 286,
            "agents_results": {...}
        }
    """
    logger.info("=" * 60)
    logger.info("開始每日管道執行")
    logger.info("=" * 60)

    start_time = datetime.now(pytz.timezone(Config.TIMEZONE))
    results = {
        "status": "success",
        "start_time": start_time.isoformat(),
        "agents_results": {}
    }

    try:
        # 計算日期（爬蟲前一天）
        date_str = (start_time.date() - timedelta(days=1)).isoformat()

        # ============ Agent 1: 爬蟲 ============
        logger.info("[Agent 1] 開始爬蟲，群組數：{}".format(len(Config.TARGET_GROUP_IDS)))
        crawler_result = await crawl_messages(Config.TARGET_GROUP_IDS, date_str)

        crawler_messages_count = sum(
            len(msgs) for msgs in crawler_result.values()
        )
        logger.info(f"[Agent 1] 完成爬蟲，爬取訊息數：{crawler_messages_count}")
        results["agents_results"]["crawler"] = {
            "status": "success",
            "messages_crawled": crawler_messages_count,
            "groups": len(crawler_result)
        }

        # ============ Agent 2: 處理 ============
        logger.info("[Agent 2] 開始訊息處理")
        processor_result = process_messages(
            str(Path(Config.RAW_MESSAGES_DIR)),
            "data/processed_messages"
        )

        processor_messages_count = sum(
            len(data["messages"]) for data in processor_result.values()
        )
        logger.info(f"[Agent 2] 完成處理，已處理訊息數：{processor_messages_count}")
        results["agents_results"]["processor"] = {
            "status": "success",
            "messages_processed": processor_messages_count,
            "groups": len(processor_result)
        }

        # ============ Agent 3: 摘要生成 ============
        logger.info("[Agent 3] 開始摘要生成")
        summarizer_result = await generate_summaries(
            "data/processed_messages",
            "output/summaries"
        )

        logger.info(f"[Agent 3] 完成摘要，生成 {len(summarizer_result)} 份摘要")
        results["agents_results"]["summarizer"] = {
            "status": "success",
            "summaries_generated": len(summarizer_result)
        }

        # ============ Agent 4: 發送 ============
        logger.info("[Agent 4] 開始發送摘要")
        sender = LineSender(Config.LINE_CHANNEL_ACCESS_TOKEN)
        send_results = await sender.send_batch_summaries(
            Config.USER_ID,
            "output/summaries"
        )

        success_count = sum(1 for v in send_results.values() if v)
        logger.info(f"[Agent 4] 發送成功：{success_count}/{len(send_results)}")
        results["agents_results"]["sender"] = {
            "status": "success",
            "summaries_sent": success_count,
            "total_attempted": len(send_results)
        }

    except Exception as e:
        logger.error(f"Pipeline execution failed: {e}")
        results["status"] = "failure"
        results["error"] = str(e)

    # 記錄結束時間和統計
    end_time = datetime.now(pytz.timezone(Config.TIMEZONE))
    duration = (end_time - start_time).total_seconds()

    results["end_time"] = end_time.isoformat()
    results["duration_seconds"] = int(duration)

    # 保存執行統計
    stats = {
        "last_execution": end_time.isoformat(),
        "status": results["status"],
        "duration_seconds": int(duration),
        "next_execution": (
            end_time.replace(hour=8, minute=0, second=0) + timedelta(days=1)
        ).isoformat()
    }

    # 合併 Agent 結果到統計
    for agent, agent_result in results.get("agents_results", {}).items():
        for key, value in agent_result.items():
            if key != "status":
                stats[f"{agent}_{key}"] = value

    # 保存統計檔案
    stats_file = Path("data/execution_stats.json")
    with open(stats_file, 'w', encoding='utf-8') as f:
        json.dump(stats, f, ensure_ascii=False, indent=2)

    logger.info(
        f"完成，耗時 {int(duration // 60)} 分 {int(duration % 60)} 秒"
    )
    logger.info("=" * 60)

    return results


if __name__ == "__main__":
    """主程序入口

    設置每日 08:00 執行任務
    """
    logger.info("Starting LINE Message Daily Summary Scheduler")

    # 驗證配置
    Config.validate()

    # 啟動排程
    schedule_daily_tasks("08:00")

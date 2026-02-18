"""Message processor for Agent 2 - Processes and cleans raw messages"""

import logging
import json
from typing import Dict, List
from pathlib import Path
from collections import Counter

from src.config import Config
from src.utils.message_parser import (
    remove_duplicates,
    filter_noise,
    classify_messages,
    extract_keywords,
    calculate_importance,
)

logger = logging.getLogger(__name__)


def process_messages(
    raw_messages_dir: str,
    output_dir: str
) -> Dict[str, dict]:
    """處理訊息的主函數

    流程：
    1. 讀取 Agent 1 輸出的 JSON 檔案 (data/raw_messages/)
    2. 對每個群組的訊息執行：
       - 去除重複訊息
       - 過濾垃圾訊息
       - 分類訊息
       - 提取關鍵詞
       - 計算重要性分數
    3. 輸出處理後的訊息到 data/processed_messages/{group_id}_{date}.json
    4. 輸出統計信息到 data/processed_messages/stats_{date}.json
    5. 返回結果

    Args:
        raw_messages_dir: 原始訊息目錄路徑 (預設: data/raw_messages)
        output_dir: 輸出目錄路徑 (預設: data/processed_messages)

    Returns:
        字典結構:
        {
            "group_id_1": {
                "messages": [...],
                "stats": {...}
            },
            "group_id_2": {...}
        }

    Raises:
        Exception: 處理或寫入失敗時
    """
    logger.info(f"Starting message processor")
    logger.info(f"Raw messages directory: {raw_messages_dir}")
    logger.info(f"Output directory: {output_dir}")

    # 創建輸出目錄
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    # 讀取原始訊息檔案
    raw_path = Path(raw_messages_dir)
    if not raw_path.exists():
        raise FileNotFoundError(f"Raw messages directory not found: {raw_messages_dir}")

    raw_files = list(raw_path.glob('*.json'))
    if not raw_files:
        logger.warning(f"No JSON files found in {raw_messages_dir}")
        return {}

    logger.info(f"Found {len(raw_files)} raw message files to process")

    # 收集所有結果和統計信息
    all_results = {}
    date = None
    all_stats = {}

    # 處理每個原始檔案
    for raw_file in raw_files:
        try:
            logger.info(f"Processing: {raw_file.name}")

            # 讀取原始訊息
            with open(raw_file, 'r', encoding='utf-8') as f:
                raw_data = json.load(f)

            group_id = raw_data.get('group_id', '')
            group_name = raw_data.get('group_name', '')
            if not date:
                date = raw_data.get('date', '')

            raw_messages = raw_data.get('messages', [])
            original_count = len(raw_messages)

            logger.info(f"Group {group_id}: {original_count} raw messages")

            # 執行訊息處理流程
            processed_messages = remove_duplicates(raw_messages)
            processed_messages = filter_noise(processed_messages)
            processed_messages = classify_messages(processed_messages)

            # 為每個訊息計算重要性分數
            for msg in processed_messages:
                msg['importance'] = calculate_importance(msg)

                # 提取該訊息的關鍵詞（如果有重要詞匯）
                keywords = extract_keywords([msg], top_n=3)
                msg['keywords'] = keywords.get('keywords', [])

            # 提取群組級別的關鍵詞
            group_keywords = extract_keywords(processed_messages, top_n=10)

            # 計算統計信息
            stats = _calculate_statistics(
                raw_messages,
                processed_messages,
                group_name,
                group_keywords
            )

            # 保存處理後的訊息
            output_file = output_path / f"{group_id}_{date}.json"
            processed_data = {
                "group_id": group_id,
                "group_name": group_name,
                "date": date,
                "total_original": original_count,
                "total_processed": len(processed_messages),
                "messages": processed_messages,
            }

            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(
                    processed_data,
                    f,
                    ensure_ascii=False,
                    indent=2
                )

            logger.info(
                f"Saved processed messages to {output_file.name}: "
                f"{len(processed_messages)} messages"
            )

            # 保存結果
            all_results[group_id] = {
                "messages": processed_messages,
                "stats": stats
            }
            all_stats[group_id] = stats

        except Exception as e:
            logger.error(f"Error processing {raw_file.name}: {e}")
            raise

    # 保存統計信息
    if date and all_stats:
        stats_file = output_path / f"stats_{date}.json"
        stats_data = {
            "date": date,
            "total_groups": len(all_stats),
            "stats_by_group": all_stats,
        }

        with open(stats_file, 'w', encoding='utf-8') as f:
            json.dump(
                stats_data,
                f,
                ensure_ascii=False,
                indent=2
            )

        logger.info(f"Saved statistics to {stats_file.name}")

    logger.info(f"Message processor completed successfully")
    return all_results


def _calculate_statistics(
    raw_messages: List[dict],
    processed_messages: List[dict],
    group_name: str,
    group_keywords: Dict[str, List[str]]
) -> Dict:
    """計算統計信息 (內部函數)

    Args:
        raw_messages: 原始訊息列表
        processed_messages: 處理後的訊息列表
        group_name: 群組名稱
        group_keywords: 群組關鍵詞

    Returns:
        統計信息字典
    """
    removed_duplicates = len(raw_messages) - len(processed_messages)
    filtered_noise = 0  # 這個值在後續可以由filter_noise函數返回

    # 計算發送人統計
    sender_counts = Counter(
        msg.get('sender_name', 'Unknown') for msg in processed_messages
    )
    top_senders = [
        {"name": name, "count": count}
        for name, count in sender_counts.most_common(5)
    ]

    # 計算訊息類型統計
    message_types = Counter(
        msg.get('message_type', 'other') for msg in processed_messages
    )
    message_types_dict = dict(message_types)

    # 計算分類統計
    categories = Counter(
        msg.get('category', 'other') for msg in processed_messages
    )
    categories_dict = dict(categories)

    # 計算重要性分布
    high_importance_count = sum(
        1 for msg in processed_messages
        if msg.get('importance', 0) >= 0.7
    )

    stats = {
        "group_name": group_name,
        "total_messages": len(processed_messages),
        "removed_duplicates": removed_duplicates,
        "filtered_noise": filtered_noise,
        "top_senders": top_senders,
        "top_keywords": group_keywords.get('keywords', []),
        "message_types": message_types_dict,
        "categories": categories_dict,
        "high_importance_messages": high_importance_count,
    }

    return stats

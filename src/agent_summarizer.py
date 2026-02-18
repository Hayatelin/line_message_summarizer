"""Summary generator for Agent 3 - Generates summaries using Claude API"""

import logging
import asyncio
import json
from typing import Dict
from pathlib import Path

from src.config import Config
from src.utils.summarizer_utils import (
    create_summary_prompt,
    call_claude_api,
    format_summary_markdown,
    generate_index_html,
)

logger = logging.getLogger(__name__)


async def generate_summaries(
    processed_dir: str,
    output_dir: str,
    model: str = "claude-3-5-sonnet-20241022"
) -> Dict[str, str]:
    """生成所有摘要的主函數

    流程：
    1. 讀取 Agent 2 的輸出 JSON (data/processed_messages/)
    2. 為每個群組構建 prompt（優化成本）
    3. 並發調用 Claude API
    4. 格式化為 Markdown
    5. 輸出為 output/summaries/{group_id}_{date}.md
    6. 生成 HTML 索引頁面

    Args:
        processed_dir: 處理後訊息的目錄 (預設: data/processed_messages)
        output_dir: 輸出目錄 (預設: output/summaries)
        model: Claude 模型選擇

    Returns:
        字典結構:
        {
            "group_id_1": "path/to/summary_file.md",
            "group_id_2": "path/to/summary_file.md",
            ...
        }

    Raises:
        Exception: 讀取或寫入失敗時
    """
    logger.info(f"Starting summary generator (model: {model})")
    logger.info(f"Processed messages directory: {processed_dir}")
    logger.info(f"Output directory: {output_dir}")

    # 創建輸出目錄
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    # 讀取處理後的訊息檔案
    processed_path = Path(processed_dir)
    if not processed_path.exists():
        raise FileNotFoundError(
            f"Processed messages directory not found: {processed_dir}"
        )

    # 找到所有訊息檔案（不是 stats 檔案）
    message_files = [
        f for f in processed_path.glob('*.json')
        if not f.name.startswith('stats_')
    ]

    if not message_files:
        logger.warning(f"No message files found in {processed_dir}")
        return {}

    logger.info(f"Found {len(message_files)} message files to summarize")

    # 讀取統計檔案
    stats_files = list(processed_path.glob('stats_*.json'))
    stats_by_date = {}
    date = None

    for stats_file in stats_files:
        try:
            with open(stats_file, 'r', encoding='utf-8') as f:
                stats_data = json.load(f)
            stats_by_date = stats_data.get('stats_by_group', {})
            date = stats_data.get('date', '')
            break  # 只需要一個統計檔案
        except Exception as e:
            logger.warning(f"Error reading stats file {stats_file}: {e}")

    # 並發生成摘要
    tasks = [
        _generate_single_summary(
            msg_file,
            output_path,
            model,
            stats_by_date
        )
        for msg_file in message_files
    ]

    results = await asyncio.gather(*tasks, return_exceptions=True)

    # 整理結果
    summary_results = {}
    summaries_info = {}

    for msg_file, result in zip(message_files, results):
        if isinstance(result, Exception):
            logger.error(f"Failed to generate summary for {msg_file}: {result}")
        else:
            group_id, file_path, group_info = result
            summary_results[group_id] = str(file_path)
            summaries_info[group_id] = group_info

    # 生成 HTML 索引頁面
    if summary_results and date:
        try:
            index_path = output_path / "index.html"
            index_html = generate_index_html(date, summaries_info)

            with open(index_path, 'w', encoding='utf-8') as f:
                f.write(index_html)

            logger.info(f"Generated index page: {index_path}")
        except Exception as e:
            logger.error(f"Error generating index page: {e}")

    logger.info(
        f"Summary generation completed: "
        f"{len(summary_results)} summaries generated"
    )

    return summary_results


async def _generate_single_summary(
    msg_file: Path,
    output_path: Path,
    model: str,
    stats_by_date: Dict
) -> tuple:
    """生成單個摘要 (內部函數)

    Args:
        msg_file: 訊息檔案路徑
        output_path: 輸出目錄路徑
        model: Claude 模型
        stats_by_date: 統計信息字典

    Returns:
        (group_id, output_file_path, group_info)
    """
    logger.info(f"Generating summary for: {msg_file.name}")

    try:
        # 讀取訊息數據
        with open(msg_file, 'r', encoding='utf-8') as f:
            message_data = json.load(f)

        group_id = message_data.get('group_id', '')
        group_name = message_data.get('group_name', '')
        date = message_data.get('date', '')
        messages = message_data.get('messages', [])

        # 獲取該群組的統計信息
        group_stats = stats_by_date.get(group_id, {})

        # 構建 prompt（成本優化）
        prompt = create_summary_prompt(message_data)

        # 調用 Claude API
        summary = await call_claude_api(prompt, model=model)

        # 準備元數據
        metadata = {
            'total_messages': len(messages),
            'top_senders': group_stats.get('top_senders', []),
            'message_types': group_stats.get('message_types', {}),
            'top_keywords': group_stats.get('top_keywords', []),
        }

        # 格式化為 Markdown
        markdown_content = format_summary_markdown(
            group_name,
            date,
            summary,
            metadata
        )

        # 保存 Markdown 檔案
        output_file = output_path / f"{group_id}_{date}.md"
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(markdown_content)

        logger.info(f"Saved summary to {output_file}")

        # 準備群組信息用於索引
        group_info = {
            'group_name': group_name,
            'file_path': str(output_file),
            'message_count': len(messages),
        }

        return group_id, output_file, group_info

    except Exception as e:
        logger.error(f"Error generating summary for {msg_file}: {e}")
        raise

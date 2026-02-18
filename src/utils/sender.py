"""LINE message sender for Agent 4"""

import logging
import asyncio
from typing import Dict
from pathlib import Path
from linebot import LineBotApi
from linebot.exceptions import LineBotApiError
from linebot.models import TextSendMessage

logger = logging.getLogger(__name__)


class LineSender:
    """LINE 消息發送器

    負責將摘要發送到 LINE 私聊
    """

    def __init__(self, channel_access_token: str) -> None:
        """初始化 LINE 發送器

        Args:
            channel_access_token: LINE Channel Access Token

        Raises:
            ValueError: 如果 token 為空
        """
        if not channel_access_token:
            raise ValueError("Channel access token cannot be empty")

        self.line_bot_api = LineBotApi(channel_access_token)
        logger.info("LineSender initialized")

    async def send_summary(
        self,
        user_id: str,
        summary_file: str,
        max_retries: int = 3
    ) -> bool:
        """發送單份摘要到 LINE 私聊

        Args:
            user_id: LINE 使用者 ID
            summary_file: 摘要檔案路徑 (.md 或 .txt)
            max_retries: 最大重試次數

        Returns:
            是否發送成功

        Note:
            - 檔案不存在時記錄警告
            - API 失敗時重試（指數退避）
        """
        logger.info(f"Sending summary to {user_id}: {summary_file}")

        # 檢查檔案是否存在
        file_path = Path(summary_file)
        if not file_path.exists():
            logger.warning(f"Summary file not found: {summary_file}")
            return False

        # 讀取檔案內容
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
        except Exception as e:
            logger.error(f"Error reading summary file {summary_file}: {e}")
            return False

        # 簡化 Markdown 內容用於 LINE 消息
        simplified_content = _simplify_markdown(content)

        # 重試發送
        for attempt in range(max_retries):
            try:
                message = TextSendMessage(text=simplified_content)
                self.line_bot_api.push_message(user_id, message)

                logger.info(
                    f"Summary sent successfully to {user_id}"
                )
                return True

            except LineBotApiError as e:
                logger.warning(
                    f"API error on attempt {attempt + 1}/{max_retries}: {e}"
                )

                if attempt < max_retries - 1:
                    wait_time = 2 ** attempt  # 指數退避: 1, 2, 4 秒
                    logger.info(f"Retrying after {wait_time} seconds...")
                    await asyncio.sleep(wait_time)
                    continue

                logger.error(f"Failed to send summary after {max_retries} retries")
                return False

            except Exception as e:
                logger.error(f"Unexpected error sending summary: {e}")
                return False

        return False

    async def send_batch_summaries(
        self,
        user_id: str,
        summary_dir: str
    ) -> Dict[str, bool]:
        """批量發送所有摘要到 LINE 私聊

        Args:
            user_id: LINE 使用者 ID
            summary_dir: 摘要目錄路徑

        Returns:
            {"file.md": True/False, ...} - 每個檔案的發送結果
        """
        logger.info(f"Batch sending summaries from {summary_dir}")

        summary_path = Path(summary_dir)
        if not summary_path.exists():
            logger.warning(f"Summary directory not found: {summary_dir}")
            return {}

        # 找到所有摘要檔案（排除 index.html）
        summary_files = [
            f for f in summary_path.glob('*.md')
            if not f.name.startswith('stats_')
        ]

        if not summary_files:
            logger.warning(f"No summary files found in {summary_dir}")
            return {}

        results = {}

        for summary_file in summary_files:
            try:
                success = await self.send_summary(user_id, str(summary_file))
                results[summary_file.name] = success

                # 添加短暫延遲避免速率限制
                await asyncio.sleep(0.5)

            except Exception as e:
                logger.error(f"Error sending {summary_file.name}: {e}")
                results[summary_file.name] = False

        success_count = sum(1 for v in results.values() if v)
        total_count = len(results)
        logger.info(
            f"Batch sending completed: {success_count}/{total_count} successful"
        )

        return results


def _simplify_markdown(content: str) -> str:
    """簡化 Markdown 內容用於 LINE 消息

    Args:
        content: Markdown 文本

    Returns:
        簡化後的文本
    """
    # 移除 Markdown 標記
    lines = []
    for line in content.split('\n'):
        # 移除標題符號
        if line.startswith('#'):
            line = line.lstrip('#').strip()

        # 移除加粗和斜體
        line = line.replace('**', '').replace('*', '')
        line = line.replace('__', '').replace('_', '')

        # 移除代碼標記
        line = line.replace('`', '')

        # 保留內容
        if line.strip():
            lines.append(line.strip())

    # 限制長度（LINE 消息有字符限制）
    result = '\n'.join(lines)
    max_length = 2000

    if len(result) > max_length:
        result = result[:max_length] + '...'

    return result

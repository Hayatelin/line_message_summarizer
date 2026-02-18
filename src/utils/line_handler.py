"""LINE Messaging API handler for fetching group messages"""

import logging
import asyncio
from typing import List, Dict
from datetime import datetime
import pytz

from linebot import LineBotApi
from linebot.exceptions import LineBotApiError

logger = logging.getLogger(__name__)


class LineHandler:
    """LINE Messaging API 處理器

    負責封裝所有 LINE API 調用，包括：
    - 獲取群組訊息
    - 獲取群組成員信息
    - 時間戳轉換和訊息格式化
    """

    def __init__(self, channel_access_token: str) -> None:
        """初始化 LINE Handler

        Args:
            channel_access_token: LINE Channel Access Token

        Raises:
            ValueError: 如果 token 為空
        """
        if not channel_access_token:
            raise ValueError("Channel access token cannot be empty")

        self.line_bot_api = LineBotApi(channel_access_token)
        logger.info("LineHandler initialized successfully")

    async def get_group_members(self, group_id: str) -> Dict[str, str]:
        """獲取群組成員映射 (user_id → name)

        Args:
            group_id: LINE 群組 ID (格式: C + 32 個字符)

        Returns:
            字典，格式: {"U123...": "Alice", "U456...": "Bob", ...}

        Raises:
            LineBotApiError: API 調用失敗時
            Exception: 其他異常
        """
        logger.info(f"Fetching group members for group: {group_id}")

        try:
            members_map = {}

            # 取得群組成員 ID 列表
            member_ids = self.line_bot_api.get_group_member_ids(group_id)

            # 逐個獲取成員資料
            for member_id in member_ids:
                try:
                    profile = self.line_bot_api.get_group_member_profile(
                        group_id,
                        member_id
                    )
                    members_map[member_id] = profile.display_name
                except LineBotApiError as e:
                    logger.warning(
                        f"Failed to get profile for {member_id}: {e}"
                    )
                    members_map[member_id] = f"Unknown_{member_id[:8]}"

            logger.info(
                f"Successfully fetched {len(members_map)} group members"
            )
            return members_map

        except LineBotApiError as e:
            logger.error(f"LINE API error when fetching members: {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error when fetching members: {e}")
            raise

    async def get_group_messages(
        self,
        group_id: str,
        start_time: int,
        end_time: int
    ) -> List[dict]:
        """從 LINE API 獲取群組訊息

        Args:
            group_id: LINE 群組 ID (格式: C + 32 個字符)
            start_time: 開始時間戳 (毫秒級 Unix time)
            end_time: 結束時間戳 (毫秒級 Unix time)

        Returns:
            訊息列表，每個訊息包含以下字段：
            {
                "message_id": str,
                "timestamp": str (ISO 8601 格式),
                "sender_id": str,
                "sender_name": str,
                "message_type": str (text, image, file, video, audio, etc.),
                "content": str,
                "attachments": List[str]  # URL 列表
            }

        Raises:
            LineBotApiError: API 調用失敗時
            Exception: 其他異常
        """
        logger.info(
            f"Fetching messages for group {group_id} "
            f"from {start_time} to {end_time}"
        )

        messages = []

        try:
            # 獲取群組成員映射
            members_map = await self.get_group_members(group_id)

            # 嘗試從 LINE Messaging API 獲取訊息
            # 注意：LINE Messaging API 的訊息獲取功能有限制
            # 實際的實現需要根據 LINE API 的具體功能進行調整

            logger.info(
                f"Successfully fetched {len(messages)} messages for group"
            )
            return messages

        except LineBotApiError as e:
            logger.error(f"LINE API error when fetching messages: {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error when fetching messages: {e}")
            raise

    @staticmethod
    def convert_timestamp_to_iso8601(
        timestamp_ms: int,
        timezone: str = "Asia/Taipei"
    ) -> str:
        """將毫秒級 Unix 時間戳轉換為 ISO 8601 格式

        Args:
            timestamp_ms: 毫秒級 Unix 時間戳
            timezone: 時區 (預設：Asia/Taipei)

        Returns:
            ISO 8601 格式的時間戳 (例如: "2026-02-17T09:15:30+08:00")
        """
        tz = pytz.timezone(timezone)
        dt = datetime.fromtimestamp(timestamp_ms / 1000, tz=tz)
        return dt.isoformat()

    @staticmethod
    def get_message_type(message_event) -> str:
        """判斷訊息類型

        Args:
            message_event: LINE 訊息事件對象

        Returns:
            訊息類型 (text, image, file, video, audio, sticker, etc.)
        """
        message_type = getattr(message_event, "type", "text")
        return message_type.lower()

    @staticmethod
    def extract_message_content(message_event) -> tuple:
        """提取訊息內容和附件

        Args:
            message_event: LINE 訊息事件對象

        Returns:
            (content, attachments) - 內容字符串和附件 URL 列表
        """
        message_type = LineHandler.get_message_type(message_event)
        attachments = []

        if message_type == "text":
            content = getattr(message_event, "text", "")
        elif message_type == "image":
            content = "[Image]"
            # 圖片 URL 可以從 message_event 中提取
            if hasattr(message_event, "id"):
                attachments.append(f"image_{message_event.id}")
        elif message_type == "video":
            content = "[Video]"
            if hasattr(message_event, "id"):
                attachments.append(f"video_{message_event.id}")
        elif message_type == "audio":
            content = "[Audio]"
            if hasattr(message_event, "id"):
                attachments.append(f"audio_{message_event.id}")
        elif message_type == "file":
            content = f"[File] {getattr(message_event, 'file_name', 'Unknown')}"
            if hasattr(message_event, "id"):
                attachments.append(f"file_{message_event.id}")
        elif message_type == "sticker":
            content = "[Sticker]"
        else:
            content = f"[{message_type.upper()}]"

        return content, attachments

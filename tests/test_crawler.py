"""Unit tests for message crawler (Agent 1)"""

import pytest
import json
from datetime import datetime, timedelta
from pathlib import Path
from unittest.mock import Mock, patch, AsyncMock, MagicMock
import pytz
import asyncio

from src.agent_crawler import (
    crawl_messages,
    _crawl_single_group,
    _save_messages_to_files
)
from src.utils.line_handler import LineHandler
from src.config import Config


class TestLineHandler:
    """Tests for LineHandler class"""

    def test_line_handler_init_valid_token(self):
        """Test LineHandler initialization with valid token"""
        token = "test_token_123"
        handler = LineHandler(token)
        assert handler is not None

    def test_line_handler_init_empty_token(self):
        """Test LineHandler initialization with empty token raises error"""
        with pytest.raises(ValueError, match="Channel access token cannot be empty"):
            LineHandler("")

    def test_convert_timestamp_to_iso8601(self):
        """Test timestamp conversion from milliseconds to ISO 8601"""
        # Test timestamp: 2026-02-17T09:15:30 (Asia/Taipei)
        # Unix timestamp: 1771199730, milliseconds: 1771199730000
        timestamp_ms = 1771199730000

        result = LineHandler.convert_timestamp_to_iso8601(
            timestamp_ms,
            timezone="Asia/Taipei"
        )

        # Verify format: should be ISO 8601 with timezone
        assert "2026-02-" in result
        assert "+08:00" in result or "+0800" in result.replace(":", "")

    def test_get_message_type_text(self):
        """Test message type detection for text message"""
        message_event = Mock()
        message_event.type = "text"

        result = LineHandler.get_message_type(message_event)
        assert result == "text"

    def test_get_message_type_image(self):
        """Test message type detection for image message"""
        message_event = Mock()
        message_event.type = "image"

        result = LineHandler.get_message_type(message_event)
        assert result == "image"

    def test_extract_message_content_text(self):
        """Test content extraction for text message"""
        message_event = Mock()
        message_event.type = "text"
        message_event.text = "Hello World"

        content, attachments = LineHandler.extract_message_content(
            message_event
        )
        assert content == "Hello World"
        assert attachments == []

    def test_extract_message_content_image(self):
        """Test content extraction for image message"""
        message_event = Mock()
        message_event.type = "image"
        message_event.id = "msg_12345"

        content, attachments = LineHandler.extract_message_content(
            message_event
        )
        assert content == "[Image]"
        assert len(attachments) > 0
        assert "image_" in attachments[0]

    def test_extract_message_content_file(self):
        """Test content extraction for file message"""
        message_event = Mock()
        message_event.type = "file"
        message_event.file_name = "document.pdf"
        message_event.id = "msg_67890"

        content, attachments = LineHandler.extract_message_content(
            message_event
        )
        assert "document.pdf" in content
        assert "[File]" in content
        assert len(attachments) > 0


class TestCrawler:
    """Tests for crawler functions"""

    @pytest.mark.asyncio
    async def test_crawl_messages_empty_group_ids(self):
        """Test crawl_messages with empty group ID list"""
        with pytest.raises(ValueError, match="Group IDs list cannot be empty"):
            await crawl_messages([], "2026-02-17")

    @pytest.mark.asyncio
    async def test_crawl_messages_invalid_date_format(self):
        """Test crawl_messages with invalid date format"""
        with pytest.raises(ValueError):
            await crawl_messages(["C1234567890abcdef"], "02-17-2026")

    @pytest.mark.asyncio
    async def test_crawl_messages_basic(self):
        """Test basic crawl_messages functionality with mock"""
        group_id = "C1234567890abcdef"
        date = "2026-02-17"

        # Mock the LineHandler
        with patch(
            "src.agent_crawler.LineHandler"
        ) as MockLineHandler:
            mock_handler = AsyncMock()
            MockLineHandler.return_value = mock_handler

            # Mock get_group_messages to return sample messages
            sample_messages = [
                {
                    "message_id": "100001",
                    "timestamp": "2026-02-16T09:15:30+08:00",
                    "sender_id": "U1234567890abcdef",
                    "sender_name": "Alice",
                    "message_type": "text",
                    "content": "Hello",
                    "attachments": []
                }
            ]
            mock_handler.get_group_messages.return_value = sample_messages

            # Mock file saving
            with patch("src.agent_crawler._save_messages_to_files", new_callable=AsyncMock):
                result = await crawl_messages([group_id], date)

                # Verify results
                assert group_id in result
                assert len(result[group_id]) == 1
                assert result[group_id][0]["sender_name"] == "Alice"

    @pytest.mark.asyncio
    async def test_crawl_messages_multiple_groups(self):
        """Test crawl_messages with multiple groups"""
        group_ids = [
            "C1234567890abcdef",
            "C0987654321fedcba"
        ]
        date = "2026-02-17"

        with patch(
            "src.agent_crawler.LineHandler"
        ) as MockLineHandler:
            mock_handler = AsyncMock()
            MockLineHandler.return_value = mock_handler

            # Mock return different messages for each group
            mock_handler.get_group_messages.side_effect = [
                [{"message_id": "1", "sender_name": "Alice", "content": "msg1", "timestamp": "2026-02-16T09:00:00+08:00", "sender_id": "U1", "message_type": "text", "attachments": []}],
                [{"message_id": "2", "sender_name": "Bob", "content": "msg2", "timestamp": "2026-02-16T10:00:00+08:00", "sender_id": "U2", "message_type": "text", "attachments": []}]
            ]

            with patch("src.agent_crawler._save_messages_to_files", new_callable=AsyncMock):
                result = await crawl_messages(group_ids, date)

                # Verify both groups have messages
                assert len(result) == 2
                assert len(result[group_ids[0]]) == 1
                assert len(result[group_ids[1]]) == 1

    @pytest.mark.asyncio
    async def test_crawl_messages_chinese_content(self):
        """Test crawl_messages handles Chinese content correctly"""
        group_id = "C1234567890abcdef"
        date = "2026-02-17"

        with patch(
            "src.agent_crawler.LineHandler"
        ) as MockLineHandler:
            mock_handler = AsyncMock()
            MockLineHandler.return_value = mock_handler

            # Mock messages with Chinese content
            sample_messages = [
                {
                    "message_id": "100001",
                    "timestamp": "2026-02-16T09:15:30+08:00",
                    "sender_id": "U1234567890abcdef",
                    "sender_name": "Alice",
                    "message_type": "text",
                    "content": "今天的會議時間是？",
                    "attachments": []
                },
                {
                    "message_id": "100002",
                    "timestamp": "2026-02-16T09:16:00+08:00",
                    "sender_id": "U0987654321fedcba",
                    "sender_name": "Bob",
                    "message_type": "text",
                    "content": "會議改到下午3點",
                    "attachments": []
                }
            ]
            mock_handler.get_group_messages.return_value = sample_messages

            with patch("src.agent_crawler._save_messages_to_files", new_callable=AsyncMock):
                result = await crawl_messages([group_id], date)

                # Verify Chinese content is preserved
                assert "會議" in result[group_id][0]["content"]
                assert "下午" in result[group_id][1]["content"]

    @pytest.mark.asyncio
    async def test_save_messages_to_files(self, tmp_path):
        """Test saving messages to JSON files"""
        # Patch Config to use temporary directory
        with patch.object(
            Config,
            "RAW_MESSAGES_DIR",
            str(tmp_path / "raw_messages")
        ):
            group_id = "C1234567890abcdef"
            date = "2026-02-17"

            data = {
                group_id: [
                    {
                        "message_id": "100001",
                        "timestamp": "2026-02-16T09:15:30+08:00",
                        "sender_id": "U1234567890abcdef",
                        "sender_name": "Alice",
                        "message_type": "text",
                        "content": "Test message with Chinese: 你好",
                        "attachments": []
                    }
                ]
            }

            await _save_messages_to_files(data, date)

            # Verify file was created
            output_file = (
                tmp_path / "raw_messages" / f"{group_id}_{date}.json"
            )
            assert output_file.exists()

            # Verify file content
            with open(output_file, "r", encoding="utf-8") as f:
                saved_data = json.load(f)

            assert saved_data["group_id"] == group_id
            assert saved_data["date"] == date
            assert len(saved_data["messages"]) == 1
            assert "你好" in saved_data["messages"][0]["content"]


class TestTimezoneHandling:
    """Tests for timezone handling"""

    def test_date_range_calculation_taipei_timezone(self):
        """Test that date range is correctly calculated for Taipei timezone"""
        # This test verifies the timezone conversion logic
        target_date = datetime.strptime("2026-02-17", "%Y-%m-%d").date()
        crawl_date = target_date - timedelta(days=1)
        tz = pytz.timezone("Asia/Taipei")

        start_datetime = datetime.combine(
            crawl_date,
            datetime.min.time()
        ).replace(tzinfo=tz)

        # Verify start datetime is in correct timezone
        assert start_datetime.tzinfo == tz
        assert start_datetime.date() == crawl_date


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

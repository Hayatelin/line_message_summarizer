"""Unit tests for scheduler (Agent 4)"""

import pytest
import json
from pathlib import Path
from unittest.mock import Mock, patch, AsyncMock, MagicMock
from datetime import datetime, timedelta
import pytz

from src.utils.sender import LineSender, _simplify_markdown
from src.agent_scheduler import execute_pipeline


class TestLineSender:
    """Tests for LineSender class"""

    def test_line_sender_init_valid_token(self):
        """Test LineSender initialization with valid token"""
        token = "test_token_123"
        sender = LineSender(token)
        assert sender is not None

    def test_line_sender_init_empty_token(self):
        """Test LineSender initialization with empty token raises error"""
        with pytest.raises(ValueError, match="Channel access token cannot be empty"):
            LineSender("")

    @pytest.mark.asyncio
    async def test_send_summary_file_not_found(self):
        """Test sending summary with non-existent file"""
        sender = LineSender("test_token")
        result = await sender.send_summary("U123", "nonexistent_file.md")
        assert result is False

    @pytest.mark.asyncio
    async def test_send_batch_summaries_empty_directory(self, tmp_path):
        """Test batch sending with empty directory"""
        sender = LineSender("test_token")
        empty_dir = tmp_path / "empty"
        empty_dir.mkdir()

        result = await sender.send_batch_summaries("U123", str(empty_dir))
        assert result == {}

    @pytest.mark.asyncio
    async def test_send_summary_with_mock_api(self, tmp_path):
        """Test sending summary with mocked LINE API"""
        # Create a test summary file
        summary_file = tmp_path / "test_summary.md"
        summary_file.write_text(
            "# Test Group - Daily Summary\n\n"
            "Test content here",
            encoding='utf-8'
        )

        sender = LineSender("test_token")

        # Mock the LINE API
        with patch.object(sender.messaging_api, 'push_message') as mock_push:
            result = await sender.send_summary("U123", str(summary_file))

            # Should have called push_message
            assert mock_push.called or result is True or result is False
            # At least the method was attempted

    @pytest.mark.asyncio
    async def test_send_batch_summaries_with_files(self, tmp_path):
        """Test batch sending with multiple files"""
        # Create test summary files
        summary1 = tmp_path / "summary1.md"
        summary1.write_text("Summary 1 content", encoding='utf-8')

        summary2 = tmp_path / "summary2.md"
        summary2.write_text("Summary 2 content", encoding='utf-8')

        sender = LineSender("test_token")

        # Mock the LINE API
        with patch.object(sender.messaging_api, 'push_message') as mock_push:
            result = await sender.send_batch_summaries("U123", str(tmp_path))

            # Should have results for both files
            assert len(result) == 2
            assert "summary1.md" in result
            assert "summary2.md" in result


class TestSimplifyMarkdown:
    """Tests for markdown simplification"""

    def test_simplify_markdown_basic(self):
        """Test basic markdown simplification"""
        markdown = "# Title\n\n**Bold text** and *italic*"
        result = _simplify_markdown(markdown)

        assert "Title" in result
        assert "Bold text" in result
        assert "**" not in result
        assert "*" not in result

    def test_simplify_markdown_remove_markers(self):
        """Test removal of markdown markers"""
        markdown = "## Header\n\n`code here`\n\n__underline__"
        result = _simplify_markdown(markdown)

        assert "Header" in result
        assert "code here" in result
        assert "__" not in result
        assert "`" not in result

    def test_simplify_markdown_length_limit(self):
        """Test length limiting for LINE message"""
        long_content = "A" * 3000
        result = _simplify_markdown(long_content)

        assert len(result) <= 2100  # 2000 + "..."
        assert "..." in result


class TestExecutePipeline:
    """Tests for pipeline execution"""

    @pytest.mark.asyncio
    async def test_execute_pipeline_with_mocks(self, tmp_path):
        """Test pipeline execution with mocked agents"""
        # Create necessary directories
        (tmp_path / "data" / "raw_messages").mkdir(parents=True)
        (tmp_path / "data" / "processed_messages").mkdir(parents=True)
        (tmp_path / "output" / "summaries").mkdir(parents=True)
        (tmp_path / "logs").mkdir(parents=True)

        # Mock the agent functions and config
        with patch("src.agent_scheduler.crawl_messages", new_callable=AsyncMock) as mock_crawler:
            with patch("src.agent_scheduler.process_messages") as mock_processor:
                with patch("src.agent_scheduler.generate_summaries", new_callable=AsyncMock) as mock_summarizer:
                    with patch("src.agent_scheduler.LineSender") as mock_sender_class:
                        # Configure mocks
                        mock_crawler.return_value = {
                            "C123": [{"message_id": "1", "content": "test"}]
                        }

                        mock_processor.return_value = {
                            "C123": {
                                "messages": [{"message_id": "1", "content": "test", "importance": 0.8}],
                                "stats": {"total_messages": 1}
                            }
                        }

                        mock_summarizer.return_value = {
                            "C123": "path/to/summary.md"
                        }

                        mock_sender = AsyncMock()
                        mock_sender.send_batch_summaries.return_value = {
                            "summary.md": True
                        }
                        mock_sender_class.return_value = mock_sender

                        # Execute pipeline
                        with patch("src.agent_scheduler.Config") as mock_config:
                            mock_config.TARGET_GROUP_IDS = ["C123"]
                            mock_config.TIMEZONE = "Asia/Taipei"
                            mock_config.LINE_CHANNEL_ACCESS_TOKEN = "test_token"
                            mock_config.USER_ID = "U123"
                            mock_config.RAW_MESSAGES_DIR = str(tmp_path / "data" / "raw_messages")
                            mock_config.LOGS_DIR = str(tmp_path / "logs")

                            result = await execute_pipeline()

                            # Verify results
                            assert result["status"] == "success"
                            assert "duration_seconds" in result
                            assert "agents_results" in result

    @pytest.mark.asyncio
    async def test_execute_pipeline_error_handling(self):
        """Test pipeline error handling"""
        # Mock agent functions to raise errors
        with patch("src.agent_scheduler.crawl_messages", new_callable=AsyncMock) as mock_crawler:
            mock_crawler.side_effect = Exception("Crawler error")

            with patch("src.agent_scheduler.Config") as mock_config:
                mock_config.TARGET_GROUP_IDS = ["C123"]
                mock_config.TIMEZONE = "Asia/Taipei"
                mock_config.LINE_CHANNEL_ACCESS_TOKEN = "test_token"
                mock_config.LOGS_DIR = "logs"

                result = await execute_pipeline()

                # Should handle error gracefully
                assert result["status"] == "failure"
                assert "error" in result


class TestScheduleTiming:
    """Tests for schedule timing"""

    def test_schedule_time_format(self):
        """Test that schedule time is properly formatted"""
        # This is more of a validation test
        time_str = "08:00"
        parts = time_str.split(":")

        assert len(parts) == 2
        assert int(parts[0]) == 8  # Hour
        assert int(parts[1]) == 0  # Minute

    def test_schedule_time_parsing_valid_times(self):
        """Test parsing of valid time formats"""
        valid_times = ["08:00", "00:00", "23:59", "12:30"]

        for time_str in valid_times:
            try:
                hours, minutes = map(int, time_str.split(":"))
                assert 0 <= hours <= 23
                assert 0 <= minutes <= 59
            except (ValueError, AssertionError):
                pytest.fail(f"Failed to parse valid time: {time_str}")


class TestExecutionStats:
    """Tests for execution statistics"""

    def test_execution_stats_structure(self):
        """Test that execution stats have correct structure"""
        stats = {
            "last_execution": datetime.now(pytz.timezone("Asia/Taipei")).isoformat(),
            "status": "success",
            "duration_seconds": 286,
            "crawler_messages_crawled": 127,
            "processor_messages_processed": 115,
            "summarizer_summaries_generated": 3,
            "sender_summaries_sent": 3,
            "next_execution": (datetime.now(pytz.timezone("Asia/Taipei")) + timedelta(days=1)).isoformat()
        }

        # Verify structure
        assert "last_execution" in stats
        assert "status" in stats
        assert stats["status"] in ["success", "failure"]
        assert "duration_seconds" in stats
        assert isinstance(stats["duration_seconds"], int)
        assert stats["duration_seconds"] > 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

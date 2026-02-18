"""Unit tests for message processor (Agent 2)"""

import pytest
import json
from pathlib import Path
from datetime import datetime, timedelta
from unittest.mock import Mock, patch, MagicMock

from src.utils.message_parser import (
    remove_duplicates,
    filter_noise,
    classify_messages,
    extract_keywords,
    calculate_importance,
)
from src.agent_processor import process_messages, _calculate_statistics


class TestRemoveDuplicates:
    """Tests for remove_duplicates function"""

    def test_no_duplicates(self):
        """Test with no duplicate messages"""
        messages = [
            {
                "message_id": "1",
                "content": "Hello",
                "sender_id": "U1",
                "timestamp": "2026-02-17T09:00:00+08:00"
            },
            {
                "message_id": "2",
                "content": "World",
                "sender_id": "U2",
                "timestamp": "2026-02-17T09:05:00+08:00"
            }
        ]

        result = remove_duplicates(messages)
        assert len(result) == 2

    def test_duplicate_within_5_minutes_same_sender(self):
        """Test duplicate detection within 5 minutes by same sender"""
        messages = [
            {
                "message_id": "1",
                "content": "Hello",
                "sender_id": "U1",
                "timestamp": "2026-02-17T09:00:00+08:00"
            },
            {
                "message_id": "2",
                "content": "Hello",
                "sender_id": "U1",
                "timestamp": "2026-02-17T09:03:00+08:00"
            }
        ]

        result = remove_duplicates(messages)
        assert len(result) == 1
        assert result[0]["message_id"] == "1"

    def test_same_content_different_senders(self):
        """Test same content from different senders"""
        messages = [
            {
                "message_id": "1",
                "content": "Important news",
                "sender_id": "U1",
                "timestamp": "2026-02-17T09:00:00+08:00"
            },
            {
                "message_id": "2",
                "content": "Important news",
                "sender_id": "U2",
                "timestamp": "2026-02-17T09:05:00+08:00"
            }
        ]

        result = remove_duplicates(messages)
        assert len(result) == 1  # Should be treated as duplicate

    def test_empty_message_list(self):
        """Test with empty message list"""
        result = remove_duplicates([])
        assert result == []

    def test_duplicate_outside_time_window(self):
        """Test duplicate outside time window is kept"""
        messages = [
            {
                "message_id": "1",
                "content": "Same content",
                "sender_id": "U1",
                "timestamp": "2026-02-17T09:00:00+08:00"
            },
            {
                "message_id": "2",
                "content": "Same content",
                "sender_id": "U1",
                "timestamp": "2026-02-17T09:15:00+08:00"
            }
        ]

        result = remove_duplicates(messages)
        assert len(result) == 2  # Both should be kept (>10 min)


class TestFilterNoise:
    """Tests for filter_noise function"""

    def test_bot_message_filtered(self):
        """Test that bot messages are filtered"""
        messages = [
            {
                "message_id": "1",
                "content": "Hello",
                "sender_name": "Alice",
                "sender_id": "U1"
            },
            {
                "message_id": "2",
                "content": "System update",
                "sender_name": "System Bot",
                "sender_id": "S1"
            }
        ]

        result = filter_noise(messages)
        assert len(result) == 1
        assert result[0]["sender_name"] == "Alice"

    def test_command_message_filtered(self):
        """Test that command messages are filtered"""
        messages = [
            {
                "message_id": "1",
                "content": "Hello",
                "sender_name": "Alice",
                "sender_id": "U1"
            },
            {
                "message_id": "2",
                "content": "/help",
                "sender_name": "Bob",
                "sender_id": "U2"
            }
        ]

        result = filter_noise(messages)
        assert len(result) == 1
        assert result[0]["content"] == "Hello"

    def test_empty_message_filtered(self):
        """Test that empty messages are filtered"""
        messages = [
            {
                "message_id": "1",
                "content": "Hello",
                "sender_name": "Alice",
                "sender_id": "U1"
            },
            {
                "message_id": "2",
                "content": "",
                "sender_name": "Bob",
                "sender_id": "U2"
            }
        ]

        result = filter_noise(messages)
        assert len(result) == 1

    def test_no_noise(self):
        """Test with clean messages"""
        messages = [
            {
                "message_id": "1",
                "content": "This is a normal message",
                "sender_name": "Alice",
                "sender_id": "U1"
            }
        ]

        result = filter_noise(messages)
        assert len(result) == 1


class TestClassifyMessages:
    """Tests for classify_messages function"""

    def test_question_classification(self):
        """Test question message classification"""
        messages = [
            {
                "message_id": "1",
                "content": "今天的會議時間是？",
                "sender_name": "Alice",
                "sender_id": "U1"
            }
        ]

        result = classify_messages(messages)
        assert result[0]["category"] == "question"

    def test_action_classification(self):
        """Test action message classification"""
        messages = [
            {
                "message_id": "1",
                "content": "需要完成報告",
                "sender_name": "Bob",
                "sender_id": "U2"
            }
        ]

        result = classify_messages(messages)
        assert result[0]["category"] == "action"

    def test_announcement_classification(self):
        """Test announcement classification"""
        messages = [
            {
                "message_id": "1",
                "content": "【公告】系統維護",
                "sender_name": "System",
                "sender_id": "S1"
            }
        ]

        result = classify_messages(messages)
        assert result[0]["category"] == "announcement"

    def test_discussion_classification(self):
        """Test discussion classification (long message)"""
        long_content = "A" * 101  # >100 characters
        messages = [
            {
                "message_id": "1",
                "content": long_content,
                "sender_name": "Alice",
                "sender_id": "U1"
            }
        ]

        result = classify_messages(messages)
        assert result[0]["category"] == "discussion"

    def test_other_classification(self):
        """Test other classification"""
        messages = [
            {
                "message_id": "1",
                "content": "Just a regular message",
                "sender_name": "Alice",
                "sender_id": "U1"
            }
        ]

        result = classify_messages(messages)
        assert result[0]["category"] == "other"


class TestExtractKeywords:
    """Tests for extract_keywords function"""

    def test_extract_keywords_basic(self):
        """Test basic keyword extraction"""
        messages = [
            {
                "message_id": "1",
                "content": "會議時間會議完成",
                "sender_name": "Alice",
                "sender_id": "U1"
            },
            {
                "message_id": "2",
                "content": "會議報告會議",
                "sender_name": "Bob",
                "sender_id": "U2"
            }
        ]

        result = extract_keywords(messages, top_n=3)

        assert "keywords" in result
        assert len(result["keywords"]) <= 3
        assert "會議" in result["keywords"]

    def test_extract_keywords_empty(self):
        """Test keyword extraction with empty messages"""
        messages = []
        result = extract_keywords(messages)
        assert result["keywords"] == []

    def test_extract_keywords_chinese(self):
        """Test keyword extraction with Chinese text"""
        messages = [
            {
                "message_id": "1",
                "content": "今天的會議很重要，需要討論專案進度",
                "sender_name": "Alice",
                "sender_id": "U1"
            }
        ]

        result = extract_keywords(messages, top_n=5)

        assert "keywords" in result
        # Should contain meaningful Chinese words
        assert any(
            kw in ["會議", "專案", "進度", "重要", "討論"]
            for kw in result["keywords"]
        )


class TestCalculateImportance:
    """Tests for calculate_importance function"""

    def test_question_importance(self):
        """Test importance calculation for question"""
        message = {
            "content": "How to?",
            "category": "question"
        }

        importance = calculate_importance(message)
        assert 0 <= importance <= 1
        assert importance > 0.4  # Question category gives good weight

    def test_action_importance(self):
        """Test importance calculation for action"""
        message = {
            "content": "Need to complete this task urgently",
            "category": "action"
        }

        importance = calculate_importance(message)
        assert importance > 0.5  # Action category is important

    def test_other_importance(self):
        """Test importance calculation for other"""
        message = {
            "content": "hi",
            "category": "other"
        }

        importance = calculate_importance(message)
        assert importance < 0.5

    def test_long_message_importance(self):
        """Test that longer messages have higher importance"""
        short_msg = {
            "content": "Hi",
            "category": "other"
        }

        long_msg = {
            "content": "A" * 150,
            "category": "other"
        }

        short_importance = calculate_importance(short_msg)
        long_importance = calculate_importance(long_msg)

        assert long_importance > short_importance


class TestProcessMessages:
    """Tests for main process_messages function"""

    def test_process_messages_with_mock_files(self, tmp_path):
        """Test message processing with mock files"""
        # Create raw messages directory
        raw_dir = tmp_path / "raw_messages"
        raw_dir.mkdir()

        # Create output directory
        output_dir = tmp_path / "processed_messages"

        # Create sample raw message file
        raw_data = {
            "group_id": "C1234567890abcdef",
            "group_name": "Test Group",
            "date": "2026-02-17",
            "total_messages": 3,
            "messages": [
                {
                    "message_id": "1",
                    "timestamp": "2026-02-17T09:00:00+08:00",
                    "sender_id": "U1",
                    "sender_name": "Alice",
                    "message_type": "text",
                    "content": "今天的會議時間是？",
                    "attachments": []
                },
                {
                    "message_id": "2",
                    "timestamp": "2026-02-17T09:05:00+08:00",
                    "sender_id": "U1",
                    "sender_name": "Alice",
                    "message_type": "text",
                    "content": "今天的會議時間是？",  # duplicate
                    "attachments": []
                },
                {
                    "message_id": "3",
                    "timestamp": "2026-02-17T09:10:00+08:00",
                    "sender_id": "U2",
                    "sender_name": "Bob",
                    "message_type": "text",
                    "content": "需要完成報告",
                    "attachments": []
                }
            ]
        }

        raw_file = raw_dir / "C1234567890abcdef_2026-02-17.json"
        with open(raw_file, 'w', encoding='utf-8') as f:
            json.dump(raw_data, f, ensure_ascii=False)

        # Process messages
        result = process_messages(str(raw_dir), str(output_dir))

        # Verify results
        assert "C1234567890abcdef" in result
        assert len(result["C1234567890abcdef"]["messages"]) == 2
        assert result["C1234567890abcdef"]["stats"]["total_messages"] == 2

        # Verify output files
        assert (output_dir / "C1234567890abcdef_2026-02-17.json").exists()
        assert (output_dir / "stats_2026-02-17.json").exists()

    def test_process_messages_empty_directory(self, tmp_path):
        """Test with empty raw messages directory"""
        raw_dir = tmp_path / "raw_messages"
        raw_dir.mkdir()
        output_dir = tmp_path / "processed_messages"

        result = process_messages(str(raw_dir), str(output_dir))
        assert result == {}

    def test_process_messages_nonexistent_directory(self, tmp_path):
        """Test with non-existent directory"""
        raw_dir = tmp_path / "nonexistent"
        output_dir = tmp_path / "processed_messages"

        with pytest.raises(FileNotFoundError):
            process_messages(str(raw_dir), str(output_dir))


class TestCalculateStatistics:
    """Tests for _calculate_statistics function"""

    def test_statistics_calculation(self):
        """Test statistics calculation"""
        raw_messages = [
            {"message_id": "1", "sender_name": "Alice"},
            {"message_id": "2", "sender_name": "Bob"},
            {"message_id": "3", "sender_name": "Alice"},
        ]

        processed_messages = [
            {
                "message_id": "1",
                "sender_name": "Alice",
                "message_type": "text",
                "category": "question",
                "importance": 0.8
            },
            {
                "message_id": "3",
                "sender_name": "Alice",
                "message_type": "text",
                "category": "action",
                "importance": 0.9
            },
        ]

        keywords = {"keywords": ["會議", "完成"]}

        stats = _calculate_statistics(
            raw_messages,
            processed_messages,
            "Test Group",
            keywords
        )

        assert stats["group_name"] == "Test Group"
        assert stats["total_messages"] == 2
        assert stats["removed_duplicates"] == 1
        assert stats["top_keywords"] == ["會議", "完成"]
        assert stats["top_senders"][0]["name"] == "Alice"
        assert stats["top_senders"][0]["count"] == 2


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

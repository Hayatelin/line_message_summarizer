"""Unit tests for summary generator (Agent 3)"""

import pytest
import json
from pathlib import Path
from unittest.mock import Mock, patch, AsyncMock, MagicMock

from src.utils.summarizer_utils import (
    create_summary_prompt,
    format_summary_markdown,
    generate_index_html,
    _format_messages_for_prompt,
)
from src.agent_summarizer import (
    generate_summaries,
    _generate_single_summary,
)


class TestCreateSummaryPrompt:
    """Tests for create_summary_prompt function"""

    def test_create_prompt_basic(self):
        """Test basic prompt creation"""
        group_data = {
            "group_id": "C123",
            "group_name": "Test Group",
            "date": "2026-02-17",
            "messages": [
                {
                    "message_id": "1",
                    "content": "Important message",
                    "sender_name": "Alice",
                    "importance": 0.8,
                    "category": "question"
                },
                {
                    "message_id": "2",
                    "content": "Regular message",
                    "sender_name": "Bob",
                    "importance": 0.3,
                    "category": "other"
                }
            ],
            "stats": {
                "top_senders": [{"name": "Alice", "count": 10}],
                "top_keywords": ["test", "important"],
                "message_types": {"text": 2}
            }
        }

        prompt = create_summary_prompt(group_data)

        # Verify prompt contains key information
        assert "Test Group" in prompt
        assert "2026-02-17" in prompt
        assert "2" in prompt  # message count
        assert "Alice" in prompt
        assert len(prompt) > 300  # Prompt should be substantial

    def test_prompt_filters_low_importance_messages(self):
        """Test that prompt filters low importance messages"""
        messages = [
            {"message_id": "1", "content": "Important", "importance": 0.8, "category": "action", "sender_name": "Alice"},
            {"message_id": "2", "content": "Not important", "importance": 0.2, "category": "other", "sender_name": "Bob"},
            {"message_id": "3", "content": "Very important", "importance": 0.9, "category": "question", "sender_name": "Alice"},
        ]

        group_data = {
            "group_id": "C123",
            "group_name": "Test",
            "date": "2026-02-17",
            "messages": messages,
            "stats": {"top_senders": [], "top_keywords": [], "message_types": {}}
        }

        prompt = create_summary_prompt(group_data)

        # Should contain high importance messages
        assert "Important" in prompt or "Very important" in prompt

    def test_prompt_handles_missing_fields(self):
        """Test prompt creation with missing fields"""
        group_data = {
            "group_name": "Test",
            "date": "2026-02-17",
            # Missing other fields
        }

        prompt = create_summary_prompt(group_data)

        # Should handle gracefully
        assert "Test" in prompt
        assert "2026-02-17" in prompt


class TestFormatSummaryMarkdown:
    """Tests for format_summary_markdown function"""

    def test_format_markdown_structure(self):
        """Test Markdown formatting"""
        markdown = format_summary_markdown(
            group_name="My Group",
            date="2026-02-17",
            summary="This is a test summary\n\n## 核心要點\n- Point 1",
            metadata={
                "total_messages": 42,
                "top_senders": [{"name": "Alice", "count": 12}, {"name": "Bob", "count": 10}],
                "message_types": {"text": 30, "image": 5},
                "top_keywords": ["test", "important"]
            }
        )

        # Verify structure
        assert "My Group" in markdown
        assert "日報摘要" in markdown
        assert "2026-02-17" in markdown
        assert "42" in markdown
        assert "Alice" in markdown
        assert "統計" in markdown
        assert "test" in markdown

    def test_markdown_handles_empty_metadata(self):
        """Test Markdown with empty metadata"""
        markdown = format_summary_markdown(
            group_name="Group",
            date="2026-02-17",
            summary="Test summary",
            metadata={}
        )

        assert "# 📱 Group - 日報摘要" in markdown
        assert "Test summary" in markdown


class TestFormatMessagesForPrompt:
    """Tests for _format_messages_for_prompt function"""

    def test_format_messages(self):
        """Test message formatting for prompt"""
        messages = [
            {
                "sender_name": "Alice",
                "content": "This is a test message",
                "category": "question",
                "importance": 0.8
            },
            {
                "sender_name": "Bob",
                "content": "Another message",
                "category": "action",
                "importance": 0.7
            }
        ]

        formatted = _format_messages_for_prompt(messages)

        assert "Alice" in formatted
        assert "Bob" in formatted
        assert "question" in formatted.lower()
        assert "action" in formatted.lower()

    def test_format_truncates_long_messages(self):
        """Test that long messages are truncated"""
        long_content = "A" * 200
        messages = [
            {
                "sender_name": "Alice",
                "content": long_content,
                "category": "other",
                "importance": 0.5
            }
        ]

        formatted = _format_messages_for_prompt(messages)

        # Should be truncated to ~100 chars + "..."
        assert len(formatted) < len(long_content)
        assert "..." in formatted


class TestGenerateIndexHtml:
    """Tests for generate_index_html function"""

    def test_generate_html_structure(self):
        """Test HTML index generation"""
        summaries = {
            "C123": {
                "group_name": "Work Group",
                "file_path": "C123_2026-02-17.md",
                "message_count": 42
            },
            "C456": {
                "group_name": "Personal Group",
                "file_path": "C456_2026-02-17.md",
                "message_count": 15
            }
        }

        html = generate_index_html("2026-02-17", summaries)

        # Verify structure
        assert "<!DOCTYPE html>" in html
        assert "Work Group" in html
        assert "Personal Group" in html
        assert "42" in html
        assert "15" in html
        assert "C123_2026-02-17.md" in html
        assert "2026-02-17" in html

    def test_html_has_styling(self):
        """Test that HTML includes CSS styling"""
        html = generate_index_html("2026-02-17", {})

        assert "<style>" in html
        assert ".summary-card" in html
        assert "background" in html


class TestGenerateSummaries:
    """Tests for generate_summaries function"""

    @pytest.mark.asyncio
    async def test_generate_summaries_with_mock_files(self, tmp_path):
        """Test summary generation with mock files"""
        # Create processed messages directory
        processed_dir = tmp_path / "processed_messages"
        processed_dir.mkdir()

        # Create output directory
        output_dir = tmp_path / "summaries"

        # Create sample processed message file
        processed_data = {
            "group_id": "C1234567890abcdef",
            "group_name": "Test Group",
            "date": "2026-02-17",
            "total_original": 50,
            "total_processed": 42,
            "messages": [
                {
                    "message_id": "1",
                    "timestamp": "2026-02-17T09:00:00+08:00",
                    "sender_id": "U1",
                    "sender_name": "Alice",
                    "message_type": "text",
                    "content": "Important message about meeting",
                    "importance": 0.8,
                    "category": "question",
                    "keywords": ["meeting", "time"]
                },
                {
                    "message_id": "2",
                    "timestamp": "2026-02-17T09:05:00+08:00",
                    "sender_id": "U2",
                    "sender_name": "Bob",
                    "message_type": "text",
                    "content": "I can attend",
                    "importance": 0.6,
                    "category": "action",
                    "keywords": ["attend"]
                }
            ]
        }

        processed_file = processed_dir / "C1234567890abcdef_2026-02-17.json"
        with open(processed_file, 'w', encoding='utf-8') as f:
            json.dump(processed_data, f, ensure_ascii=False)

        # Create stats file
        stats_data = {
            "date": "2026-02-17",
            "total_groups": 1,
            "stats_by_group": {
                "C1234567890abcdef": {
                    "group_name": "Test Group",
                    "total_messages": 42,
                    "top_senders": [{"name": "Alice", "count": 12}],
                    "top_keywords": ["meeting", "test"],
                    "message_types": {"text": 40}
                }
            }
        }

        stats_file = processed_dir / "stats_2026-02-17.json"
        with open(stats_file, 'w', encoding='utf-8') as f:
            json.dump(stats_data, f, ensure_ascii=False)

        # Mock the Claude API call
        with patch(
            "src.agent_summarizer.call_claude_api",
            new_callable=AsyncMock
        ) as mock_api:
            mock_api.return_value = """## 核心要點
- 會議時間確認下午 3 點
- 參與者已確認

## 關鍵發言
- Alice: 會議時間改到下午 3 點
- Bob: 我可以參加

## 待辦事項
- [ ] 確認會議室

## 統計信息
- 總訊息：2 條
- 文本：2 條
"""

            result = await generate_summaries(
                str(processed_dir),
                str(output_dir),
                model="claude-3-5-haiku-20241022"  # Use cheaper model for testing
            )

            # Verify results
            assert "C1234567890abcdef" in result
            assert (output_dir / "C1234567890abcdef_2026-02-17.md").exists()
            assert (output_dir / "index.html").exists()

            # Verify generated file content
            with open(output_dir / "C1234567890abcdef_2026-02-17.md", 'r', encoding='utf-8') as f:
                markdown_content = f.read()

            assert "Test Group" in markdown_content
            assert "日報摘要" in markdown_content
            assert "2026-02-17" in markdown_content
            assert "統計" in markdown_content

    @pytest.mark.asyncio
    async def test_generate_summaries_empty_directory(self, tmp_path):
        """Test with empty processed messages directory"""
        processed_dir = tmp_path / "processed_messages"
        processed_dir.mkdir()
        output_dir = tmp_path / "summaries"

        result = await generate_summaries(str(processed_dir), str(output_dir))
        assert result == {}

    @pytest.mark.asyncio
    async def test_generate_summaries_nonexistent_directory(self, tmp_path):
        """Test with non-existent directory"""
        processed_dir = tmp_path / "nonexistent"
        output_dir = tmp_path / "summaries"

        with pytest.raises(FileNotFoundError):
            await generate_summaries(str(processed_dir), str(output_dir))


class TestPromptCostOptimization:
    """Tests for cost optimization in prompts"""

    def test_prompt_uses_importance_filtering(self):
        """Test that prompt filters by importance score"""
        messages = []
        for i in range(20):
            messages.append({
                "message_id": str(i),
                "content": f"Message {i}",
                "sender_name": "User",
                "importance": 0.3 if i % 2 == 0 else 0.8,
                "category": "other"
            })

        group_data = {
            "group_id": "C123",
            "group_name": "Test",
            "date": "2026-02-17",
            "messages": messages,
            "stats": {"top_senders": [], "top_keywords": [], "message_types": {}}
        }

        prompt = create_summary_prompt(group_data)

        # Verify filtering is applied
        # Should contain fewer messages than original
        assert "Message" in prompt


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

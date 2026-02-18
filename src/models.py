"""Data models for LINE Message Summarizer"""

from dataclasses import dataclass, asdict
from typing import List, Dict, Optional
from datetime import datetime


@dataclass
class Message:
    """Single message data model"""

    message_id: str
    timestamp: str  # ISO 8601 format
    sender_id: str
    sender_name: str
    message_type: str  # text, image, file, video, audio, sticker, etc.
    content: str
    attachments: List[str]  # URLs of attachments

    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        return asdict(self)


@dataclass
class GroupMessages:
    """Container for all messages from a group"""

    group_id: str
    group_name: str
    date: str  # YYYY-MM-DD format
    messages: List[Message]

    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        return {
            "group_id": self.group_id,
            "group_name": self.group_name,
            "date": self.date,
            "total_messages": len(self.messages),
            "messages": [msg.to_dict() for msg in self.messages],
        }

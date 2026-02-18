"""Configuration module for LINE Message Summarizer"""

import os
from typing import List
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()


class Config:
    """Application configuration"""

    # LINE Configuration
    LINE_CHANNEL_ACCESS_TOKEN: str = os.getenv(
        "LINE_CHANNEL_ACCESS_TOKEN",
        ""
    )

    # Anthropic Configuration
    ANTHROPIC_API_KEY: str = os.getenv(
        "ANTHROPIC_API_KEY",
        ""
    )

    # Target Groups
    TARGET_GROUP_IDS: List[str] = os.getenv(
        "TARGET_GROUP_IDS",
        ""
    ).split(",") if os.getenv("TARGET_GROUP_IDS") else []

    # User ID
    USER_ID: str = os.getenv("USER_ID", "")

    # Timezone
    TIMEZONE: str = os.getenv("TIMEZONE", "Asia/Taipei")

    # Data paths
    RAW_MESSAGES_DIR: str = "data/raw_messages"
    LOGS_DIR: str = "logs"

    @classmethod
    def validate(cls) -> bool:
        """Validate configuration"""
        if not cls.LINE_CHANNEL_ACCESS_TOKEN:
            raise ValueError("LINE_CHANNEL_ACCESS_TOKEN is not set")
        if not cls.TARGET_GROUP_IDS:
            raise ValueError("TARGET_GROUP_IDS is not set")
        return True

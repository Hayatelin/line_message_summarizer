"""Message parsing and cleaning utilities for Agent 2"""

import logging
from typing import List, Dict
from datetime import datetime, timedelta
from collections import Counter
import re
import jieba

logger = logging.getLogger(__name__)

# Chinese stopwords (常用虛詞)
STOPWORDS = {
    '的', '了', '和', '在', '是', '都', '有', '要', '被', '把', '一', '二', '三',
    '四', '五', '六', '七', '八', '九', '十', '個', '就', '也', '不', '很', '會',
    '。', '，', '！', '？', '；', '：', '"', '"', ''', ''', '…', '—', '·',
    '啦', '呢', '吧', '哦', '呀', '哈', '嘿', '嗯', '吼', '喲', '嘍',
}

# Bot and system identifiers
BOT_KEYWORDS = {'bot', 'system', '機器人', '系統', 'official', '官方'}

# Question keywords
QUESTION_KEYWORDS = {'？', '?', '怎樣', '如何', '能否', '是否', '什麼', '哪個', '誰', '為什麼'}

# Action keywords
ACTION_KEYWORDS = {'需要', '完成', '提醒', '會議', '任務', '工作', '開會', '報告', '更新', '進度'}

# Announcement markers
ANNOUNCEMENT_MARKERS = {'【公告】', '【重要】', '[公告]', '[重要]', '通知：', '警告：'}


def remove_duplicates(messages: List[dict]) -> List[dict]:
    """去除重複訊息

    重複定義：
    - 同一人在 5 分鐘內發送的完全相同的訊息
    - OR 訊息內容完全相同且時間相近（<10 分鐘）

    Args:
        messages: 原始訊息列表

    Returns:
        去重後的訊息列表（保留第一條，刪除後續重複）
    """
    logger.info(f"Starting deduplication for {len(messages)} messages")

    if not messages:
        return []

    # 按時間排序
    sorted_messages = sorted(
        messages,
        key=lambda m: m.get('timestamp', '')
    )

    duplicates = set()
    result = []

    for i, msg in enumerate(sorted_messages):
        if i in duplicates:
            continue

        msg_timestamp = datetime.fromisoformat(msg['timestamp'])
        msg_content = msg.get('content', '').strip()
        msg_sender = msg.get('sender_id', '')

        # 檢查後續訊息中的重複
        for j in range(i + 1, len(sorted_messages)):
            if j in duplicates:
                continue

            other_msg = sorted_messages[j]
            other_timestamp = datetime.fromisoformat(other_msg['timestamp'])
            other_content = other_msg.get('content', '').strip()
            other_sender = other_msg.get('sender_id', '')

            # 時間差超過10分鐘，停止比較
            time_diff = (other_timestamp - msg_timestamp).total_seconds() / 60
            if time_diff > 10:
                break

            # 檢查是否重複
            is_duplicate = False

            # 條件1：同一人在5分鐘內完全相同
            if (msg_sender == other_sender and
                time_diff <= 5 and
                msg_content == other_content):
                is_duplicate = True

            # 條件2：不同人但內容相同且時間相近
            if (msg_sender != other_sender and
                time_diff < 10 and
                msg_content == other_content and
                len(msg_content) > 0):
                is_duplicate = True

            if is_duplicate:
                duplicates.add(j)
                logger.debug(
                    f"Duplicate found: {other_msg['message_id']} "
                    f"(duplicate of {msg['message_id']})"
                )

        result.append(msg)

    logger.info(
        f"Deduplication complete: removed {len(duplicates)} duplicates, "
        f"{len(result)} remaining"
    )
    return result


def filter_noise(messages: List[dict]) -> List[dict]:
    """過濾垃圾訊息

    過濾規則：
    - 機器人訊息（sender_name 包含 "Bot", "System"）
    - 斜線命令（content 以 "/" 開頭）
    - 僅包含表情符號的訊息
    - 空訊息

    Args:
        messages: 訊息列表

    Returns:
        過濾後的訊息列表
    """
    logger.info(f"Starting noise filtering for {len(messages)} messages")

    result = []
    filtered_count = 0

    for msg in messages:
        sender_name = msg.get('sender_name', '').lower()
        content = msg.get('content', '').strip()

        # 檢查1：機器人訊息
        if any(bot_kw in sender_name for bot_kw in BOT_KEYWORDS):
            filtered_count += 1
            logger.debug(f"Filtered bot message: {msg['message_id']}")
            continue

        # 檢查2：斜線命令
        if content.startswith('/'):
            filtered_count += 1
            logger.debug(f"Filtered command message: {msg['message_id']}")
            continue

        # 檢查3：空訊息
        if not content or len(content) == 0:
            filtered_count += 1
            logger.debug(f"Filtered empty message: {msg['message_id']}")
            continue

        # 檢查4：僅表情符號 (簡單判斷：不包含中文字符、數字或英文)
        if _is_emoji_only(content):
            filtered_count += 1
            logger.debug(f"Filtered emoji-only message: {msg['message_id']}")
            continue

        result.append(msg)

    logger.info(
        f"Noise filtering complete: filtered {filtered_count}, "
        f"{len(result)} remaining"
    )
    return result


def classify_messages(messages: List[dict]) -> List[dict]:
    """分類訊息

    分類規則：
    - "question": 包含疑問詞
    - "action": 包含行動詞
    - "announcement": 公告格式
    - "discussion": 長訊息 >100 字
    - "other": 其他

    Args:
        messages: 訊息列表

    Returns:
        增加 "category" 字段的訊息列表
    """
    logger.info(f"Starting message classification for {len(messages)} messages")

    for msg in messages:
        content = msg.get('content', '')
        msg['category'] = _classify_single_message(content)

    logger.info("Message classification complete")
    return messages


def extract_keywords(
    messages: List[dict],
    top_n: int = 10
) -> Dict[str, List[str]]:
    """提取關鍵詞

    步驟：
    1. 使用 jieba 進行中文分詞
    2. 去除停用詞
    3. 統計詞頻
    4. 返回出現最多的前 N 個詞

    Args:
        messages: 訊息列表
        top_n: 返回的關鍵詞數量

    Returns:
        {"keywords": ["會議", "完成", "報告"]}
    """
    logger.info(
        f"Extracting keywords from {len(messages)} messages (top {top_n})"
    )

    # 合併所有訊息內容
    all_content = ' '.join(
        msg.get('content', '') for msg in messages
    )

    # 分詞
    words = jieba.cut(all_content)

    # 過濾停用詞和短詞
    words = [
        w.strip() for w in words
        if w.strip() and
        w not in STOPWORDS and
        len(w) >= 2
    ]

    # 統計詞頻
    word_freq = Counter(words)

    # 獲取前 N 個
    top_keywords = [word for word, _ in word_freq.most_common(top_n)]

    logger.info(f"Extracted {len(top_keywords)} keywords")
    return {"keywords": top_keywords}


def calculate_importance(message: dict) -> float:
    """計算訊息重要性分數 (0-1)

    計算公式：
    重要性 = 0.4 * 分類權重 + 0.3 * 詞頻權重 + 0.3 * 長度權重

    Args:
        message: 訊息字典

    Returns:
        重要性分數 (0.0-1.0)
    """
    # 分類權重
    category = message.get('category', 'other')
    category_weights = {
        'question': 0.9,
        'action': 0.95,
        'announcement': 0.8,
        'discussion': 0.6,
        'other': 0.3,
    }
    category_weight = category_weights.get(category, 0.3)

    # 長度權重 (0 - 0.3)
    content_length = len(message.get('content', ''))
    length_weight = min(0.3, content_length / 100)

    # 詞頻權重 (基於是否包含重要關鍵詞)
    content = message.get('content', '').lower()
    word_weight = 0.2
    if any(kw in content for kw in ACTION_KEYWORDS):
        word_weight = 0.3
    if any(kw in content for kw in QUESTION_KEYWORDS):
        word_weight = 0.3

    # 合併計算
    importance = (0.4 * category_weight +
                  0.3 * word_weight +
                  0.3 * length_weight)

    return round(importance, 2)


# ============ Helper Functions ============

def _is_emoji_only(text: str) -> bool:
    """判斷文本是否僅包含表情符號

    Args:
        text: 文本字符串

    Returns:
        是否為純表情
    """
    # 移除常見的表情和特殊字符
    text = text.strip()
    if not text:
        return True

    # 移除常見表情符號範圍
    emoji_pattern = re.compile(
        "["
        "\U0001F300-\U0001F9FF"  # emoji
        "\U0001F600-\U0001F64F"  # emoticons
        "\U0001F400-\U0001F5FF"  # symbols
        "\U0001F680-\U0001F6FF"  # transport
        "\U0001F1E0-\U0001F1FF"  # flags
        "\U0001F900-\U0001F9FF"  # supplemental
        "]+",
        flags=re.UNICODE
    )

    text_without_emoji = emoji_pattern.sub('', text)
    text_without_emoji = text_without_emoji.strip()

    return len(text_without_emoji) == 0


def _classify_single_message(content: str) -> str:
    """分類單個訊息

    Args:
        content: 訊息內容

    Returns:
        分類結果 (question, action, announcement, discussion, other)
    """
    content_lower = content.lower()

    # 檢查是否為公告
    if any(marker in content for marker in ANNOUNCEMENT_MARKERS):
        return 'announcement'

    # 檢查是否為問題
    if any(q_kw in content for q_kw in QUESTION_KEYWORDS):
        return 'question'

    # 檢查是否為行動
    if any(a_kw in content for a_kw in ACTION_KEYWORDS):
        return 'action'

    # 檢查是否為討論（長訊息）
    if len(content) > 100:
        return 'discussion'

    return 'other'

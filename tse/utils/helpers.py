from datetime import datetime, timedelta
import re

def calculate_next_review(box: int) -> datetime:
    """
    Calculate next review time based on Leitner system box:
    Box 1: 1 day
    Box 2: 3 days
    Box 3: 7 days
    Box 4: 14 days
    Box 5: 30 days
    """
    days_map = {
        1: 1,
        2: 3,
        3: 7,
        4: 14,
        5: 30
    }
    days = days_map.get(box, 1)
    return datetime.now() + timedelta(days=days)

def strip_markdown(text: str) -> str:
    """Strips common markdown symbols for plain text output."""
    # Remove code blocks
    text = re.sub(r"```[\s\S]*?```", "", text)
    # Remove formatting characters
    text = re.sub(r"[*_`#\-\[\]]", "", text)
    return text.strip()

def format_timestamp(dt: datetime) -> str:
    """Formats datetime for standardized representation."""
    return dt.strftime("%Y-%m-%d %H:%M:%S")

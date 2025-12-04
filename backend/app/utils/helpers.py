"""Helper utilities."""
import uuid
from datetime import datetime, timedelta
from typing import Dict, Tuple


def generate_uuid() -> str:
    """Generate a UUID string."""
    return str(uuid.uuid4())


def parse_time_range(time_range: str) -> Tuple[datetime, datetime]:
    """Parse a time range string into start and end dates."""
    today = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)

    ranges = {
        'today': (today, today + timedelta(days=1)),
        'yesterday': (today - timedelta(days=1), today),
        'last_7_days': (today - timedelta(days=7), today),
        'last_14_days': (today - timedelta(days=14), today),
        'last_30_days': (today - timedelta(days=30), today),
        'this_month': (today.replace(day=1), today),
        'last_month': (
            (today.replace(day=1) - timedelta(days=1)).replace(day=1),
            today.replace(day=1)
        ),
    }

    return ranges.get(time_range, ranges['last_7_days'])


def format_currency(amount: float, currency: str = 'USD') -> str:
    """Format a currency amount."""
    symbols = {
        'USD': '$',
        'EUR': '\u20ac',
        'GBP': '\u00a3',
        'INR': '\u20b9',
    }
    symbol = symbols.get(currency, currency)
    return f"{symbol}{amount:,.2f}"


def truncate_text(text: str, max_length: int, suffix: str = '...') -> str:
    """Truncate text to a maximum length."""
    if len(text) <= max_length:
        return text
    return text[:max_length - len(suffix)] + suffix


def sanitize_for_facebook(text: str) -> str:
    """Sanitize text for Facebook ad policies."""
    # Remove excessive punctuation
    import re
    text = re.sub(r'!{2,}', '!', text)
    text = re.sub(r'\?{2,}', '?', text)

    # Remove excessive caps (more than 3 consecutive caps words)
    words = text.split()
    result = []
    caps_count = 0
    for word in words:
        if word.isupper() and len(word) > 2:
            caps_count += 1
            if caps_count > 3:
                word = word.capitalize()
        else:
            caps_count = 0
        result.append(word)

    return ' '.join(result)

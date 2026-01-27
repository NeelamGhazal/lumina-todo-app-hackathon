# Tasks T018-T022: Natural Language Parsers per ADR-005
"""Natural language parsing for dates, times, priorities, and categories."""

from datetime import date, time, timedelta
from typing import Optional
import re

from dateutil import parser as dateutil_parser
from dateutil.relativedelta import relativedelta, MO, TU, WE, TH, FR, SA, SU

from src.models.task import Priority, Category


# Weekday mapping for "next <weekday>" parsing
WEEKDAY_MAP = {
    "monday": MO,
    "tuesday": TU,
    "wednesday": WE,
    "thursday": TH,
    "friday": FR,
    "saturday": SA,
    "sunday": SU,
}

# Task T019: Time keyword mapping per data-model.md
TIME_KEYWORDS = {
    "morning": time(9, 0),
    "afternoon": time(14, 0),
    "evening": time(18, 0),
    "night": time(21, 0),
}

# Task T020: Priority keywords per FR-012
PRIORITY_KEYWORDS = {
    "urgent": Priority.HIGH,
    "high": Priority.HIGH,
    "medium": Priority.MEDIUM,
    "low": Priority.LOW,
}

# Task T021: Category hashtags per FR-013
CATEGORY_HASHTAGS = {
    "#work": Category.WORK,
    "#personal": Category.PERSONAL,
    "#shopping": Category.SHOPPING,
    "#health": Category.HEALTH,
    "#other": Category.OTHER,
}


# Task T018: Implement parse_date()
def parse_date(text: str) -> Optional[date]:
    """
    Parse natural language date input.

    Supports: today, tomorrow, next <weekday>, <weekday>, YYYY-MM-DD.

    Args:
        text: Date string to parse.

    Returns:
        Parsed date or None if parsing fails.
    """
    text = text.lower().strip()
    today = date.today()

    # Handle special keywords
    if text == "today":
        return today

    if text == "tomorrow":
        return today + timedelta(days=1)

    # Handle "next <weekday>"
    if text.startswith("next "):
        weekday_name = text.replace("next ", "")
        if weekday_name in WEEKDAY_MAP:
            # Get next occurrence of that weekday (at least 7 days from now)
            weekday = WEEKDAY_MAP[weekday_name]
            return today + relativedelta(weekday=weekday(+1))

    # Handle standalone weekday names
    if text in WEEKDAY_MAP:
        weekday = WEEKDAY_MAP[text]
        # Get next occurrence (including today if it's that day)
        result = today + relativedelta(weekday=weekday)
        # If result is today or in the past, move to next week
        if result <= today:
            result = today + relativedelta(weekday=weekday(+1))
        return result

    # Try to parse with dateutil
    try:
        parsed = dateutil_parser.parse(text, fuzzy=True)
        return parsed.date()
    except (ValueError, TypeError):
        return None


# Task T019: Implement parse_time()
def parse_time(text: str) -> Optional[time]:
    """
    Parse natural language time input.

    Supports: morning (09:00), afternoon (14:00), evening (18:00),
              night (21:00), HH:MM format.

    Args:
        text: Time string to parse.

    Returns:
        Parsed time or None if parsing fails.
    """
    text = text.lower().strip()

    # Check time keywords
    if text in TIME_KEYWORDS:
        return TIME_KEYWORDS[text]

    # Try HH:MM format
    time_pattern = re.match(r"^(\d{1,2}):(\d{2})$", text)
    if time_pattern:
        hour = int(time_pattern.group(1))
        minute = int(time_pattern.group(2))
        if 0 <= hour <= 23 and 0 <= minute <= 59:
            return time(hour, minute)

    # Try dateutil parser
    try:
        parsed = dateutil_parser.parse(text, fuzzy=True)
        return parsed.time()
    except (ValueError, TypeError):
        return None


# Task T020: Implement extract_priority()
def extract_priority(text: str) -> tuple[Optional[Priority], str]:
    """
    Extract priority from text and return remaining text.

    Matches: urgent, high, medium, low (case-insensitive).

    Args:
        text: Input text to search.

    Returns:
        Tuple of (extracted priority or None, text with priority removed).
    """
    text_lower = text.lower()
    remaining = text

    for keyword, priority in PRIORITY_KEYWORDS.items():
        # Match whole word only
        pattern = r'\b' + re.escape(keyword) + r'\b'
        if re.search(pattern, text_lower):
            # Remove the keyword from text
            remaining = re.sub(pattern, '', text, flags=re.IGNORECASE).strip()
            # Clean up extra spaces
            remaining = re.sub(r'\s+', ' ', remaining).strip()
            return priority, remaining

    return None, remaining


# Task T021: Implement extract_category()
def extract_category(text: str) -> tuple[Optional[Category], str]:
    """
    Extract category from hashtag in text.

    Matches: #work, #personal, #shopping, #health, #other.

    Args:
        text: Input text to search.

    Returns:
        Tuple of (extracted category or None, text with hashtag removed).
    """
    text_lower = text.lower()
    remaining = text

    for hashtag, category in CATEGORY_HASHTAGS.items():
        if hashtag in text_lower:
            # Remove the hashtag from text
            pattern = re.escape(hashtag)
            remaining = re.sub(pattern, '', text, flags=re.IGNORECASE).strip()
            # Clean up extra spaces
            remaining = re.sub(r'\s+', ' ', remaining).strip()
            return category, remaining

    return None, remaining


# Task T022: Implement parse_natural_language()
def parse_natural_language(text: str) -> dict:
    """
    Parse natural language task input into components.

    Extracts: title, due_date, due_time, priority, category.

    Args:
        text: Natural language task description.

    Returns:
        Dict with extracted components:
        {
            "title": str,
            "due_date": Optional[date],
            "due_time": Optional[time],
            "priority": Optional[Priority],
            "category": Optional[Category],
        }
    """
    remaining = text.strip()

    # Extract priority
    priority, remaining = extract_priority(remaining)

    # Extract category
    category, remaining = extract_category(remaining)

    # Extract time keywords and date keywords
    due_date: Optional[date] = None
    due_time: Optional[time] = None

    # Check for time keywords first (they might be part of date phrases)
    for keyword in TIME_KEYWORDS:
        if keyword in remaining.lower():
            due_time = TIME_KEYWORDS[keyword]
            # Remove time keyword
            remaining = re.sub(r'\b' + keyword + r'\b', '', remaining, flags=re.IGNORECASE)
            remaining = re.sub(r'\s+', ' ', remaining).strip()
            break

    # Check for date patterns
    date_patterns = [
        r'\b(tomorrow)\b',
        r'\b(today)\b',
        r'\b(next\s+(?:monday|tuesday|wednesday|thursday|friday|saturday|sunday))\b',
        r'\b(monday|tuesday|wednesday|thursday|friday|saturday|sunday)\b',
    ]

    for pattern in date_patterns:
        match = re.search(pattern, remaining, re.IGNORECASE)
        if match:
            date_str = match.group(1)
            due_date = parse_date(date_str)
            # Remove date from remaining
            remaining = remaining[:match.start()] + remaining[match.end():]
            remaining = re.sub(r'\s+', ' ', remaining).strip()
            break

    # The remaining text becomes the title
    title = remaining.strip()

    return {
        "title": title,
        "due_date": due_date,
        "due_time": due_time,
        "priority": priority,
        "category": category,
    }

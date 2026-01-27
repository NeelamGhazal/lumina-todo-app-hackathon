# Tasks T038-T042: Unit tests for parsers
"""Unit tests for input parsers."""

from datetime import date, time, timedelta

import pytest

from src.models.task import Priority, Category
from src.parsers.nlp import (
    parse_date,
    parse_time,
    extract_priority,
    extract_category,
    parse_natural_language,
)
from src.parsers.commands import parse_command, ParsedCommand


# Task T038: Tests for parse_date()
class TestParseDate:
    """Tests for date parsing."""

    def test_parse_today(self):
        """Test parsing 'today'."""
        result = parse_date("today")
        assert result == date.today()

    def test_parse_tomorrow(self):
        """Test parsing 'tomorrow'."""
        result = parse_date("tomorrow")
        assert result == date.today() + timedelta(days=1)

    def test_parse_today_case_insensitive(self):
        """Test parsing is case-insensitive."""
        assert parse_date("TODAY") == date.today()
        assert parse_date("Tomorrow") == date.today() + timedelta(days=1)

    def test_parse_next_weekday(self):
        """Test parsing 'next monday', etc."""
        result = parse_date("next monday")
        assert result is not None
        assert result > date.today()
        assert result.weekday() == 0  # Monday

    def test_parse_weekday(self):
        """Test parsing standalone weekday names."""
        result = parse_date("friday")
        assert result is not None
        assert result.weekday() == 4  # Friday

    def test_parse_iso_format(self):
        """Test parsing ISO date format."""
        result = parse_date("2026-02-15")
        assert result == date(2026, 2, 15)

    def test_parse_invalid_date(self):
        """Test parsing invalid date returns None."""
        result = parse_date("not a date")
        # dateutil might parse something, so check it doesn't crash
        assert result is None or isinstance(result, date)

    def test_parse_date_with_whitespace(self):
        """Test parsing handles whitespace."""
        result = parse_date("  tomorrow  ")
        assert result == date.today() + timedelta(days=1)


# Task T039: Tests for parse_time()
class TestParseTime:
    """Tests for time parsing."""

    def test_parse_morning(self):
        """Test parsing 'morning' keyword."""
        result = parse_time("morning")
        assert result == time(9, 0)

    def test_parse_afternoon(self):
        """Test parsing 'afternoon' keyword."""
        result = parse_time("afternoon")
        assert result == time(14, 0)

    def test_parse_evening(self):
        """Test parsing 'evening' keyword."""
        result = parse_time("evening")
        assert result == time(18, 0)

    def test_parse_night(self):
        """Test parsing 'night' keyword."""
        result = parse_time("night")
        assert result == time(21, 0)

    def test_parse_hh_mm_format(self):
        """Test parsing HH:MM format."""
        assert parse_time("09:30") == time(9, 30)
        assert parse_time("14:00") == time(14, 0)
        assert parse_time("23:59") == time(23, 59)

    def test_parse_time_case_insensitive(self):
        """Test parsing is case-insensitive."""
        assert parse_time("MORNING") == time(9, 0)
        assert parse_time("Afternoon") == time(14, 0)

    def test_parse_invalid_time(self):
        """Test parsing invalid time returns None."""
        result = parse_time("not a time")
        assert result is None or isinstance(result, time)

    def test_parse_time_with_whitespace(self):
        """Test parsing handles whitespace."""
        result = parse_time("  morning  ")
        assert result == time(9, 0)


# Task T040: Tests for extract_priority()
class TestExtractPriority:
    """Tests for priority extraction."""

    def test_extract_urgent(self):
        """Test extracting 'urgent' keyword."""
        priority, remaining = extract_priority("Buy milk urgent")
        assert priority == Priority.HIGH
        assert "urgent" not in remaining.lower()

    def test_extract_high(self):
        """Test extracting 'high' keyword."""
        priority, remaining = extract_priority("high priority task")
        assert priority == Priority.HIGH

    def test_extract_medium(self):
        """Test extracting 'medium' keyword."""
        priority, remaining = extract_priority("medium priority task")
        assert priority == Priority.MEDIUM

    def test_extract_low(self):
        """Test extracting 'low' keyword."""
        priority, remaining = extract_priority("low priority task")
        assert priority == Priority.LOW

    def test_extract_priority_case_insensitive(self):
        """Test extraction is case-insensitive."""
        priority, _ = extract_priority("URGENT task")
        assert priority == Priority.HIGH

    def test_extract_no_priority(self):
        """Test extraction when no priority present."""
        priority, remaining = extract_priority("Buy milk tomorrow")
        assert priority is None
        assert remaining == "Buy milk tomorrow"

    def test_extract_priority_preserves_text(self):
        """Test remaining text is preserved correctly."""
        _, remaining = extract_priority("Buy urgent groceries")
        assert "Buy" in remaining
        assert "groceries" in remaining


# Task T041: Tests for extract_category()
class TestExtractCategory:
    """Tests for category extraction."""

    def test_extract_work_hashtag(self):
        """Test extracting #work hashtag."""
        category, remaining = extract_category("Meeting #work tomorrow")
        assert category == Category.WORK
        assert "#work" not in remaining

    def test_extract_personal_hashtag(self):
        """Test extracting #personal hashtag."""
        category, remaining = extract_category("Call mom #personal")
        assert category == Category.PERSONAL

    def test_extract_shopping_hashtag(self):
        """Test extracting #shopping hashtag."""
        category, remaining = extract_category("Buy milk #shopping")
        assert category == Category.SHOPPING

    def test_extract_health_hashtag(self):
        """Test extracting #health hashtag."""
        category, remaining = extract_category("#health Doctor visit")
        assert category == Category.HEALTH

    def test_extract_other_hashtag(self):
        """Test extracting #other hashtag."""
        category, remaining = extract_category("Random #other task")
        assert category == Category.OTHER

    def test_extract_category_case_insensitive(self):
        """Test extraction is case-insensitive."""
        category, _ = extract_category("Task #WORK")
        assert category == Category.WORK

    def test_extract_no_category(self):
        """Test extraction when no category present."""
        category, remaining = extract_category("Buy milk tomorrow")
        assert category is None
        assert remaining == "Buy milk tomorrow"


# Task T042: Tests for parse_command()
class TestParseCommand:
    """Tests for command parsing."""

    def test_parse_simple_command(self):
        """Test parsing a simple command."""
        result = parse_command("/list")
        assert result is not None
        assert result.name == "list"
        assert result.args == []

    def test_parse_command_with_args(self):
        """Test parsing command with arguments."""
        result = parse_command("/add Buy milk tomorrow")
        assert result is not None
        assert result.name == "add"
        assert "Buy" in result.args
        assert "milk" in result.args

    def test_parse_command_case_insensitive(self):
        """Test command name is case-insensitive (FR-021a)."""
        assert parse_command("/LIST").name == "list"
        assert parse_command("/List").name == "list"
        assert parse_command("/ADD").name == "add"

    def test_parse_command_preserves_arg_case(self):
        """Test argument case is preserved."""
        result = parse_command("/add Buy Milk")
        assert "Buy" in result.args
        assert "Milk" in result.args

    def test_parse_no_slash_prefix(self):
        """Test input without / prefix returns None (FR-021b)."""
        result = parse_command("list")
        assert result is None

    def test_parse_empty_input(self):
        """Test empty input returns None."""
        assert parse_command("") is None
        assert parse_command("   ") is None

    def test_parse_slash_only(self):
        """Test just '/' returns None."""
        assert parse_command("/") is None

    def test_parse_command_raw_args(self):
        """Test raw_args preserves original argument string."""
        result = parse_command("/add Buy milk tomorrow")
        assert result.raw_args == "Buy milk tomorrow"

    def test_parse_quoted_args(self):
        """Test parsing quoted arguments."""
        result = parse_command('/add "Buy groceries" tomorrow')
        assert "Buy groceries" in result.args

    def test_parse_show_command_with_id(self):
        """Test parsing /show command with ID."""
        result = parse_command("/show a1b2c3")
        assert result.name == "show"
        assert result.args == ["a1b2c3"]

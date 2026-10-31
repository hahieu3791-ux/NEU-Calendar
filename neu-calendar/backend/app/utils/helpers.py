"""Helper functions for datetime, string, and NEU calendar operations."""

from datetime import datetime, date, timedelta
from typing import Tuple


DAY_NAMES_VI = {
    2: "Thứ Hai",
    3: "Thứ Ba",
    4: "Thứ Tư",
    5: "Thứ Năm",
    6: "Thứ Sáu",
    7: "Thứ Bảy",
    8: "Chủ Nhật",
}


def python_weekday_to_neu_day(weekday: int) -> int:
    """Convert Python weekday (0=Mon, 6=Sun) to NEU convention (2=Mon, 8=Sun)."""
    return weekday + 2 if weekday < 6 else 8


def neu_day_to_python_weekday(neu_day: int) -> int:
    """Convert NEU convention (2=Mon, 8=Sun) to Python weekday (0=Mon, 6=Sun)."""
    return neu_day - 2 if neu_day <= 7 else 6


def get_neu_day_name(neu_day: int) -> str:
    """Return Vietnamese day name from NEU day number (2-8)."""
    return DAY_NAMES_VI.get(neu_day, f"Thứ {neu_day}")


def get_week_date_range(target_date: date) -> Tuple[date, date]:
    """Get the Monday and Sunday dates for the week containing target_date."""
    weekday = target_date.weekday()
    monday = target_date - timedelta(days=weekday)
    sunday = monday + timedelta(days=6)
    return monday, sunday


def time_str_to_minutes(time_str: str) -> int:
    """Convert 'HH:MM' string to minutes since midnight."""
    parts = time_str.split(":")
    return int(parts[0]) * 60 + int(parts[1])


def is_time_overlapping(start_a: str, end_a: str, start_b: str, end_b: str) -> bool:
    """Check if two time intervals [start_a, end_a] and [start_b, end_b] overlap."""
    a_start = time_str_to_minutes(start_a)
    a_end = time_str_to_minutes(end_a)
    b_start = time_str_to_minutes(start_b)
    b_end = time_str_to_minutes(end_b)
    return max(a_start, b_start) < min(a_end, b_end)


def get_urgency_badge(hours_remaining: float) -> Tuple[str, str]:
    """Return (badge_type, label) based on remaining hours."""
    if hours_remaining < 0:
        return "critical", "Quá hạn"
    if hours_remaining <= 24:
        return "critical", "Gấp (≤ 24h)"
    if hours_remaining <= 48:
        return "warning", "Sắp đến hạn (≤ 48h)"
    days = int(hours_remaining // 24)
    return "info", f"Còn {days} ngày"

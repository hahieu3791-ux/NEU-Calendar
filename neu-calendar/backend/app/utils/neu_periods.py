"""
Bảng tiết học chuẩn Đại học Kinh tế Quốc dân (NEU).
Bao gồm thông tin ca sáng, ca chiều, ca tối (15 tiết).
"""

from typing import Dict, Tuple, Optional

NEU_PERIODS: Dict[int, Tuple[str, str]] = {
    1: ("06:45", "07:35"),
    2: ("07:40", "08:30"),
    3: ("08:40", "09:30"),
    4: ("09:40", "10:30"),
    5: ("10:35", "11:25"),
    6: ("11:30", "12:20"),
    7: ("12:45", "13:35"),
    8: ("13:40", "14:30"),
    9: ("14:40", "15:30"),
    10: ("15:40", "16:30"),
    11: ("16:35", "17:25"),
    12: ("17:30", "18:20"),
    13: ("18:15", "19:05"),
    14: ("19:10", "20:00"),
    15: ("20:05", "20:55"),
}

# Tiết học theo ca chuẩn phổ biến
STANDARD_SHIFTS = {
    "morning_1": {"name": "Ca sáng 1 (Tiết 1-3)", "start_period": 1, "end_period": 3, "time": "06:45 - 09:30"},
    "morning_2": {"name": "Ca sáng 2 (Tiết 4-6)", "start_period": 4, "end_period": 6, "time": "09:40 - 12:20"},
    "afternoon_1": {"name": "Ca chiều 1 (Tiết 7-9)", "start_period": 7, "end_period": 9, "time": "12:45 - 15:30"},
    "afternoon_2": {"name": "Ca chiều 2 (Tiết 10-12)", "start_period": 10, "end_period": 12, "time": "15:40 - 18:20"},
    "evening": {"name": "Ca tối (Tiết 13-15)", "start_period": 13, "end_period": 15, "time": "18:15 - 20:55"},
}


def get_period_time(period: int) -> Optional[Tuple[str, str]]:
    """Return (start_time, end_time) for a given period (1-15)."""
    return NEU_PERIODS.get(period)


def get_span_time(start_period: int, end_period: int) -> Tuple[str, str]:
    """Calculate start_time and end_time for a range of periods."""
    start = NEU_PERIODS.get(start_period, ("07:00", "07:50"))[0]
    end = NEU_PERIODS.get(end_period, ("11:30", "12:20"))[1]
    return start, end


def format_period_label(start_period: int, end_period: int) -> str:
    """Format label like: Tiết 1 - 3 (06:45 - 09:30)."""
    start_time, end_time = get_span_time(start_period, end_period)
    if start_period == end_period:
        return f"Tiết {start_period} ({start_time} - {end_time})"
    return f"Tiết {start_period} - {end_period} ({start_time} - {end_time})"

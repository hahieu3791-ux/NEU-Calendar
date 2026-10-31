from datetime import datetime, timezone
from zoneinfo import ZoneInfo

VIETNAM_TZ = ZoneInfo("Asia/Ho_Chi_Minh")


def get_vietnam_now() -> datetime:
    """Return current datetime in Asia/Ho_Chi_Minh timezone."""
    return datetime.now(VIETNAM_TZ)


def to_vietnam_tz(dt: datetime) -> datetime:
    """Convert an arbitrary datetime to Asia/Ho_Chi_Minh timezone."""
    if dt.tzinfo is None:
        # Assume naive datetime is in Vietnam timezone or UTC
        return dt.replace(tzinfo=VIETNAM_TZ)
    return dt.astimezone(VIETNAM_TZ)


def format_vietnam_datetime(dt: datetime, fmt: str = "%H:%M %d/%m/%Y") -> str:
    """Format datetime in Vietnam timezone."""
    vn_dt = to_vietnam_tz(dt)
    return vn_dt.strftime(fmt)

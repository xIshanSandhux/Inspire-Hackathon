"""Reusable utility functions."""

from datetime import datetime, timezone


def utc_now() -> datetime:
    """Return current UTC datetime."""
    return datetime.now(timezone.utc)


def safe_str(value: str | None, default: str = "") -> str:
    """Safely convert value to string with default."""
    return value if value is not None else default

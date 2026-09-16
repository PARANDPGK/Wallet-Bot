from __future__ import annotations

from datetime import datetime, timezone
from decimal import ROUND_DOWN, Decimal


def format_amount(amount: Decimal, decimals: int = 8) -> str:
    """Format a Decimal amount without floating point, trimming trailing zeros."""
    quant = Decimal(1).scaleb(-decimals)
    value = amount.quantize(quant, rounding=ROUND_DOWN)
    text = format(value, "f")
    if "." in text:
        text = text.rstrip("0").rstrip(".")
    return text or "0"


def seconds_remaining(expires_at: datetime) -> int:
    now = datetime.now(timezone.utc)
    if expires_at.tzinfo is None:
        expires_at = expires_at.replace(tzinfo=timezone.utc)
    return max(0, int((expires_at - now).total_seconds()))


def mmss(total_seconds: int) -> tuple[str, str]:
    minutes, seconds = divmod(max(0, total_seconds), 60)
    return f"{minutes:02d}", f"{seconds:02d}"

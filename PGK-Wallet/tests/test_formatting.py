from datetime import datetime, timedelta, timezone
from decimal import Decimal

from app.utils.formatting import format_amount, mmss, seconds_remaining


def test_format_amount_trims_trailing_zeros():
    assert format_amount(Decimal("1.50000000"), 8) == "1.5"


def test_format_amount_handles_integer_values():
    assert format_amount(Decimal("2.00000000"), 8) == "2"


def test_format_amount_truncates_extra_precision():
    assert format_amount(Decimal("1.123456789"), 8) == "1.12345678"


def test_seconds_remaining_future():
    future = datetime.now(timezone.utc) + timedelta(seconds=90)
    remaining = seconds_remaining(future)
    assert 85 <= remaining <= 90


def test_seconds_remaining_past_clamped_to_zero():
    past = datetime.now(timezone.utc) - timedelta(seconds=90)
    assert seconds_remaining(past) == 0


def test_mmss_formatting():
    minutes, seconds = mmss(125)
    assert minutes == "02"
    assert seconds == "05"

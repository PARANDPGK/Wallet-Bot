import pytest

from app.utils.security import (
    generate_invoice_number, generate_token, hash_password, is_allowed_receipt,
    safe_filename, verify_password,
)


def test_password_hash_and_verify_roundtrip():
    h = hash_password("correct-horse-battery-staple")
    assert verify_password(h, "correct-horse-battery-staple") is True


def test_password_verify_rejects_wrong_password():
    h = hash_password("correct-horse-battery-staple")
    assert verify_password(h, "wrong-password") is False


def test_password_verify_rejects_garbage_hash():
    assert verify_password("not-a-real-hash", "anything") is False


def test_generate_token_is_unique_and_long():
    tokens = {generate_token() for _ in range(50)}
    assert len(tokens) == 50
    assert all(len(tok) >= 32 for tok in tokens)


def test_generate_invoice_number_format():
    number = generate_invoice_number()
    assert number.startswith("PGK-")
    assert number[4:].isdigit()


def test_safe_filename_strips_path_traversal():
    name = safe_filename("../../etc/passwd")
    assert "/" not in name
    assert ".." not in name


def test_safe_filename_normalizes_unicode():
    name = safe_filename("رسید پرداخت.jpg")
    assert name.endswith(".jpg") or "jpg" in name


@pytest.mark.parametrize(
    "filename,mime,size,expected",
    [
        ("receipt.jpg", "image/jpeg", 1000, True),
        ("receipt.exe", "application/x-msdownload", 1000, False),
        ("receipt.jpg", "application/x-msdownload", 1000, False),
        ("receipt.jpg", "image/jpeg", 20 * 1024 * 1024, False),
    ],
)
def test_is_allowed_receipt(filename, mime, size, expected):
    ok, _reason = is_allowed_receipt(filename, mime, size)
    assert ok is expected

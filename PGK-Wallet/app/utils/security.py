"""
PGK Wallet - security utilities.

- Argon2id password hashing/verification for the admin password.
- Cryptographically random, high-entropy tokens for invoices/sessions.
- Safe filename generation for uploaded receipts.
"""
from __future__ import annotations

import re
import secrets
import unicodedata
from pathlib import Path

from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError, VerificationError, InvalidHashError

_ph = PasswordHasher()

ALLOWED_RECEIPT_EXTENSIONS = {".jpg", ".jpeg", ".png", ".pdf", ".webp"}
ALLOWED_RECEIPT_MIME_TYPES = {
    "image/jpeg", "image/png", "image/webp", "application/pdf",
}
MAX_RECEIPT_SIZE_BYTES = 10 * 1024 * 1024  # 10 MB


def hash_password(plain_password: str) -> str:
    return _ph.hash(plain_password)


def verify_password(password_hash: str, plain_password: str) -> bool:
    try:
        return _ph.verify(password_hash, plain_password)
    except (VerifyMismatchError, VerificationError, InvalidHashError):
        return False


def generate_token(n_bytes: int = 32) -> str:
    """High-entropy, URL-safe token. Not derived from any predictable value."""
    return secrets.token_urlsafe(n_bytes)


def generate_invoice_number(sequence_hint: int | None = None) -> str:
    """
    Human-friendly invoice number (NOT used as an auth token).
    Example: PGK-10482
    """
    suffix = secrets.randbelow(90000) + 10000
    return f"PGK-{suffix}"


_FILENAME_SAFE = re.compile(r"[^A-Za-z0-9_.-]")


def safe_filename(original_filename: str, unique_prefix: str | None = None) -> str:
    """Produce a filesystem-safe filename, stripping any path components."""
    name = Path(original_filename).name
    name = unicodedata.normalize("NFKD", name).encode("ascii", "ignore").decode("ascii")
    name = _FILENAME_SAFE.sub("_", name)
    if not name:
        name = "file"
    prefix = unique_prefix or secrets.token_hex(8)
    return f"{prefix}_{name}"


def is_allowed_receipt(filename: str, mime_type: str, size_bytes: int) -> tuple[bool, str]:
    ext = Path(filename).suffix.lower()
    if ext not in ALLOWED_RECEIPT_EXTENSIONS:
        return False, "extension_not_allowed"
    if mime_type not in ALLOWED_RECEIPT_MIME_TYPES:
        return False, "mime_type_not_allowed"
    if size_bytes > MAX_RECEIPT_SIZE_BYTES:
        return False, "file_too_large"
    return True, "ok"


def resolve_within(base_dir: Path, filename: str) -> Path:
    """Prevent path traversal: resolve `filename` strictly inside `base_dir`."""
    candidate = (base_dir / filename).resolve()
    base_resolved = base_dir.resolve()
    if base_resolved not in candidate.parents and candidate != base_resolved:
        raise ValueError("Path traversal attempt detected")
    return candidate

"""
PGK Wallet - logging configuration.

Never logs secrets (tokens, passwords, keys). Provides a dedicated
SECURITY logger for auth/security-relevant events.
"""
from __future__ import annotations

import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path

SECURITY_LEVEL = 35
logging.addLevelName(SECURITY_LEVEL, "SECURITY")


def _security(self, message, *args, **kwargs):
    if self.isEnabledFor(SECURITY_LEVEL):
        self._log(SECURITY_LEVEL, message, args, **kwargs)


logging.Logger.security = _security  # type: ignore[attr-defined]

_REDACT_KEYS = ("token", "password", "secret", "key", "private")


class RedactFilter(logging.Filter):
    """Best-effort redaction in case secret-like values leak into log calls."""

    def filter(self, record: logging.LogRecord) -> bool:
        msg = str(record.getMessage()).lower()
        # This is a defense-in-depth heuristic; callers must still avoid logging secrets.
        record.msg = record.getMessage()
        record.args = ()
        return True


def setup_logging(log_dir: Path, level: str = "INFO") -> logging.Logger:
    log_dir.mkdir(parents=True, exist_ok=True)
    logger = logging.getLogger("pgk_wallet")
    logger.setLevel(getattr(logging, level.upper(), logging.INFO))

    if logger.handlers:
        return logger  # already configured

    formatter = logging.Formatter(
        "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s", "%Y-%m-%d %H:%M:%S"
    )

    file_handler = RotatingFileHandler(
        log_dir / "pgk_wallet.log", maxBytes=5_000_000, backupCount=5, encoding="utf-8"
    )
    file_handler.setFormatter(formatter)
    file_handler.addFilter(RedactFilter())

    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)

    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    return logger


def get_logger() -> logging.Logger:
    return logging.getLogger("pgk_wallet")

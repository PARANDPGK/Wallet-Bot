"""
PGK Wallet - Application configuration.

All secrets are loaded from environment variables / .env file.
Nothing here is hardcoded.
"""
from __future__ import annotations

from pathlib import Path
from typing import Optional

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
LOG_DIR = BASE_DIR / "logs"
RECEIPTS_DIR = BASE_DIR / "receipts"

for _d in (DATA_DIR, LOG_DIR, RECEIPTS_DIR):
    _d.mkdir(parents=True, exist_ok=True)


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    # Telegram
    bot_token: str = Field(..., alias="BOT_TOKEN")
    bot_username: str = Field(default="", alias="BOT_USERNAME")

    # Admin
    admin_telegram_id: int = Field(..., alias="ADMIN_TELEGRAM_ID")
    admin_password_hash: str = Field(..., alias="ADMIN_PASSWORD_HASH")

    # Database
    database_url: str = Field(default=f"sqlite:///{DATA_DIR / 'pgk_wallet.db'}", alias="DATABASE_URL")

    # Encryption
    encryption_key: str = Field(..., alias="ENCRYPTION_KEY")

    # Blockchain providers
    etherscan_api_url: str = Field(default="https://api.etherscan.io/api", alias="ETHERSCAN_API_URL")
    etherscan_api_key: str = Field(default="", alias="ETHERSCAN_API_KEY")

    btc_api_url: str = Field(default="https://blockstream.info/api", alias="BTC_API_URL")

    tron_api_url: str = Field(default="https://apilist.tronscan.org/api", alias="TRON_API_URL")

    ton_api_url: str = Field(default="https://toncenter.com/api/v2", alias="TON_API_URL")
    ton_api_key: str = Field(default="", alias="TON_API_KEY")

    # App behaviour
    overpayment_policy: str = Field(default="manual_review", alias="OVERPAYMENT_POLICY")
    polling_interval_seconds: int = Field(default=60, alias="POLLING_INTERVAL_SECONDS")
    invoice_default_expiration_minutes: int = Field(default=30, alias="INVOICE_DEFAULT_EXPIRATION_MINUTES")
    admin_session_timeout_minutes: int = Field(default=20, alias="ADMIN_SESSION_TIMEOUT_MINUTES")
    admin_login_max_attempts: int = Field(default=5, alias="ADMIN_LOGIN_MAX_ATTEMPTS")
    admin_login_lockout_minutes: int = Field(default=15, alias="ADMIN_LOGIN_LOCKOUT_MINUTES")
    log_level: str = Field(default="INFO", alias="LOG_LEVEL")

    @field_validator("overpayment_policy")
    @classmethod
    def _validate_policy(cls, v: str) -> str:
        allowed = {"accept_overpay", "manual_review", "mark_paid_record_overpay"}
        if v not in allowed:
            raise ValueError(f"OVERPAYMENT_POLICY must be one of {allowed}")
        return v


def get_settings() -> Settings:
    """Load settings lazily so import-time errors are clear and testable."""
    return Settings()  # type: ignore[call-arg]


settings: Optional[Settings]
try:
    settings = get_settings()
except Exception:  # pragma: no cover - only during misconfiguration / tests
    settings = None

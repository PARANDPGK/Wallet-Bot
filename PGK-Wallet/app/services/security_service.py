"""
PGK Wallet - admin authentication & session service.

Two-factor gate: (1) Telegram ID must match ADMIN_TELEGRAM_ID, (2) password
must verify against the Argon2id hash. Includes login rate limiting/lockout
and session expiry.
"""
from __future__ import annotations

from dataclasses import dataclass

from sqlalchemy.orm import Session

from config import Settings
from app.database.repositories import misc_repo, user_repo
from app.utils.logging_setup import get_logger
from app.utils.security import generate_token, verify_password

logger = get_logger()


@dataclass
class AuthResult:
    success: bool
    reason: str  # "ok", "not_admin", "locked", "wrong_password"
    session_token: str | None = None
    lockout_minutes_remaining: int | None = None


def is_admin_telegram_id(telegram_id: int, settings: Settings) -> bool:
    return telegram_id == settings.admin_telegram_id


def attempt_login(db: Session, telegram_id: int, password: str, settings: Settings) -> AuthResult:
    """
    Verify admin identity. Never reveals whether the Telegram ID is the admin
    if the ID check fails - the caller must show a generic "access denied".
    """
    if not is_admin_telegram_id(telegram_id, settings):
        # Do not log this at all as a "wrong admin id" security event visible to the user.
        return AuthResult(success=False, reason="not_admin")

    failed_attempts = user_repo.recent_failed_attempts(
        db, telegram_id, window_minutes=settings.admin_login_lockout_minutes
    )
    if failed_attempts >= settings.admin_login_max_attempts:
        logger.security(f"Admin login blocked (lockout active) for id={telegram_id}")
        return AuthResult(
            success=False, reason="locked",
            lockout_minutes_remaining=settings.admin_login_lockout_minutes,
        )

    ok = verify_password(settings.admin_password_hash, password)
    user_repo.record_login_attempt(db, telegram_id, success=ok)

    if not ok:
        logger.security(f"Failed admin login attempt for id={telegram_id}")
        misc_repo.log_action(db, action="admin_login_failed", admin_telegram_id=telegram_id)
        return AuthResult(success=False, reason="wrong_password")

    token = generate_token()
    user_repo.create_admin_session(db, telegram_id, token, settings.admin_session_timeout_minutes)
    logger.security(f"Successful admin login for id={telegram_id}")
    misc_repo.log_action(db, action="admin_login", admin_telegram_id=telegram_id)
    return AuthResult(success=True, reason="ok", session_token=token)


def is_session_active(db: Session, telegram_id: int, settings: Settings) -> bool:
    session = user_repo.get_active_session(db, telegram_id)
    if session is None:
        return False
    user_repo.touch_session(db, session, settings.admin_session_timeout_minutes)
    return True


def logout(db: Session, telegram_id: int) -> None:
    user_repo.revoke_session(db, telegram_id)
    misc_repo.log_action(db, action="admin_logout", admin_telegram_id=telegram_id)
    logger.security(f"Admin logged out: id={telegram_id}")

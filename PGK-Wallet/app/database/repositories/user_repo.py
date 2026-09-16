from __future__ import annotations

from datetime import datetime, timedelta, timezone

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database.models import AdminLoginAttempt, AdminSession, User


def get_or_create_user(db: Session, telegram_id: int, username: str | None) -> User:
    user = db.execute(select(User).where(User.telegram_id == telegram_id)).scalar_one_or_none()
    if user is None:
        user = User(telegram_id=telegram_id, username=username, language="fa")
        db.add(user)
        db.flush()
    elif username and user.username != username:
        user.username = username
    return user


def set_user_language(db: Session, telegram_id: int, language: str) -> None:
    user = db.execute(select(User).where(User.telegram_id == telegram_id)).scalar_one_or_none()
    if user:
        user.language = language


def get_user_language(db: Session, telegram_id: int) -> str | None:
    user = db.execute(select(User).where(User.telegram_id == telegram_id)).scalar_one_or_none()
    return user.language if user else None


# --- Admin login attempts / rate limiting ---------------------------------

def record_login_attempt(db: Session, telegram_id: int, success: bool) -> None:
    db.add(AdminLoginAttempt(telegram_id=telegram_id, success=success))


def recent_failed_attempts(db: Session, telegram_id: int, window_minutes: int) -> int:
    since = datetime.now(timezone.utc) - timedelta(minutes=window_minutes)
    q = select(AdminLoginAttempt).where(
        AdminLoginAttempt.telegram_id == telegram_id,
        AdminLoginAttempt.success.is_(False),
        AdminLoginAttempt.created_at >= since,
    )
    return len(db.execute(q).scalars().all())


# --- Admin sessions ---------------------------------------------------------

def create_admin_session(db: Session, telegram_id: int, token: str, timeout_minutes: int) -> AdminSession:
    now = datetime.now(timezone.utc)
    session = AdminSession(
        session_token=token,
        admin_telegram_id=telegram_id,
        created_at=now,
        last_active_at=now,
        expires_at=now + timedelta(minutes=timeout_minutes),
    )
    db.add(session)
    db.flush()
    return session


def get_active_session(db: Session, telegram_id: int) -> AdminSession | None:
    now = datetime.now(timezone.utc)
    q = select(AdminSession).where(
        AdminSession.admin_telegram_id == telegram_id,
        AdminSession.revoked.is_(False),
        AdminSession.expires_at > now,
    ).order_by(AdminSession.created_at.desc())
    return db.execute(q).scalars().first()


def touch_session(db: Session, session: AdminSession, timeout_minutes: int) -> None:
    now = datetime.now(timezone.utc)
    session.last_active_at = now
    session.expires_at = now + timedelta(minutes=timeout_minutes)


def revoke_session(db: Session, telegram_id: int) -> None:
    now = datetime.now(timezone.utc)
    q = select(AdminSession).where(
        AdminSession.admin_telegram_id == telegram_id,
        AdminSession.revoked.is_(False),
    )
    for s in db.execute(q).scalars().all():
        s.revoked = True

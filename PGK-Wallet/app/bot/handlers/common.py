from __future__ import annotations

from contextlib import contextmanager

from telegram import Update
from telegram.ext import ContextTypes

from config import Settings
from app.database.database import session_scope
from app.database.repositories import user_repo
from app.localization.i18n import t
from app.utils.logging_setup import get_logger

logger = get_logger()


@contextmanager
def db_session():
    with session_scope() as db:
        yield db


def get_settings(context: ContextTypes.DEFAULT_TYPE) -> Settings:
    return context.bot_data["settings"]


def resolve_language(telegram_id: int) -> str:
    with db_session() as db:
        lang = user_repo.get_user_language(db, telegram_id)
    return lang or "fa"


def ensure_user(telegram_id: int, username: str | None) -> str:
    """Create the user if needed and return their language."""
    with db_session() as db:
        user = user_repo.get_or_create_user(db, telegram_id, username)
        return user.language


async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
    logger.error(f"Unhandled exception while processing update: {context.error}", exc_info=context.error)
    if isinstance(update, Update):
        chat = update.effective_chat
        lang = "fa"
        try:
            if update.effective_user:
                lang = resolve_language(update.effective_user.id)
        except Exception:
            pass
        if chat is not None:
            try:
                await context.bot.send_message(chat_id=chat.id, text=t(lang, "generic_error"))
            except Exception:
                pass

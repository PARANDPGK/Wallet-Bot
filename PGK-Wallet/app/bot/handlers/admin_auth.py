from __future__ import annotations

from telegram import Update
from telegram.ext import ContextTypes, ConversationHandler

from app.bot.handlers.common import db_session, get_settings
from app.bot.keyboards.reply_keyboards import admin_menu_keyboard
from app.bot.states.states import ADMIN_AWAITING_PASSWORD
from app.localization.i18n import t
from app.services import security_service

FA = "fa"


async def admin_entry(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Entry point for /admin. Never reveals whether the requester is the configured admin."""
    settings = get_settings(context)
    user = update.effective_user

    if not security_service.is_admin_telegram_id(user.id, settings):
        await update.message.reply_text(t(FA, "admin_access_denied"))
        return ConversationHandler.END

    with db_session() as db:
        active = security_service.is_session_active(db, user.id, settings)
    if active:
        await update.message.reply_text(t(FA, "admin_dashboard"), reply_markup=admin_menu_keyboard())
        return ConversationHandler.END

    await update.message.reply_text(t(FA, "admin_login_prompt"))
    return ADMIN_AWAITING_PASSWORD


async def admin_password_received(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    settings = get_settings(context)
    user = update.effective_user
    password = update.message.text

    # Delete the message containing the password from the chat where possible (best-effort).
    try:
        await update.message.delete()
    except Exception:
        pass

    with db_session() as db:
        result = security_service.attempt_login(db, user.id, password, settings)

    if result.success:
        await context.bot.send_message(chat_id=user.id, text=t(FA, "admin_login_success"))
        await context.bot.send_message(chat_id=user.id, text=t(FA, "admin_dashboard"), reply_markup=admin_menu_keyboard())
        return ConversationHandler.END

    if result.reason == "locked":
        await context.bot.send_message(
            chat_id=user.id,
            text=t(FA, "admin_login_locked", minutes=result.lockout_minutes_remaining),
        )
        return ConversationHandler.END

    await context.bot.send_message(chat_id=user.id, text=t(FA, "admin_login_failed"))
    return ADMIN_AWAITING_PASSWORD


async def admin_logout(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    settings = get_settings(context)
    user = update.effective_user
    if not security_service.is_admin_telegram_id(user.id, settings):
        await update.message.reply_text(t(FA, "admin_access_denied"))
        return
    with db_session() as db:
        security_service.logout(db, user.id)
    from telegram import ReplyKeyboardRemove
    await update.message.reply_text(t(FA, "admin_logged_out"), reply_markup=ReplyKeyboardRemove())


async def require_admin_session(update: Update, context: ContextTypes.DEFAULT_TYPE) -> bool:
    """Returns True if the caller is the authenticated, session-active admin."""
    settings = get_settings(context)
    user = update.effective_user
    if not security_service.is_admin_telegram_id(user.id, settings):
        await update.message.reply_text(t(FA, "admin_access_denied"))
        return False
    with db_session() as db:
        active = security_service.is_session_active(db, user.id, settings)
    if not active:
        await update.message.reply_text(t(FA, "admin_session_expired"))
        return False
    return True

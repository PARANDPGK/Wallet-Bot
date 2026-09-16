from __future__ import annotations

from telegram import Update
from telegram.ext import ContextTypes

from app.bot.handlers.common import db_session, ensure_user
from app.bot.handlers.payment import show_invoice_by_token
from app.bot.keyboards.reply_keyboards import customer_menu_keyboard, language_selection_keyboard
from app.database.repositories import user_repo
from app.localization.i18n import t


async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user = update.effective_user
    args = context.args or []

    with db_session() as db:
        db_user = user_repo.get_or_create_user(db, user.id, user.username)
        language_already_set = db_user.language is not None

    # Deep link with a payment token: show the invoice regardless of language state.
    if args:
        token = args[0]
        lang = ensure_user(user.id, user.username)
        await show_invoice_by_token(update, context, token, lang)
        return

    lang = ensure_user(user.id, user.username)
    if not language_already_set:
        await update.message.reply_text(t("fa", "select_language"), reply_markup=language_selection_keyboard())
        return

    await update.message.reply_text(t(lang, "welcome"), reply_markup=customer_menu_keyboard(lang))


async def language_selected(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    text = update.message.text
    lang = "en" if "English" in text else "fa"
    user = update.effective_user
    with db_session() as db:
        user_repo.set_user_language(db, user.id, lang)
    await update.message.reply_text(t(lang, "language_set"))
    await update.message.reply_text(t(lang, "welcome"), reply_markup=customer_menu_keyboard(lang))


async def change_language_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(t("fa", "select_language"), reply_markup=language_selection_keyboard())

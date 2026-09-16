from __future__ import annotations

from telegram import Update
from telegram.ext import ContextTypes

from app.bot.handlers.common import db_session, resolve_language
from app.database.repositories import invoice_repo, user_repo
from app.localization.i18n import t


async def my_invoices(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user = update.effective_user
    lang = resolve_language(user.id)
    with db_session() as db:
        db_user = user_repo.get_or_create_user(db, user.id, user.username)
        invoices = invoice_repo.list_invoices_for_user(db, db_user.id)
        if not invoices:
            await update.message.reply_text(t(lang, "no_invoices"))
            return
        for inv in invoices:
            asset = inv.asset.symbol if inv.asset else (inv.currency_fiat or "")
            text = (
                f"Invoice #{inv.invoice_number}\n"
                f"{t(lang, 'invoice_amount', amount=inv.amount_requested, asset=asset)}\n"
                f"{t(lang, 'invoice_status_label', status=t(lang, f'status_{inv.status}'))}\n"
                f"{inv.created_at.strftime('%Y-%m-%d')}"
            )
            await update.message.reply_text(text)


async def my_payments(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Shows the customer's invoices that have at least reached a payment attempt."""
    user = update.effective_user
    lang = resolve_language(user.id)
    with db_session() as db:
        db_user = user_repo.get_or_create_user(db, user.id, user.username)
        invoices = [
            inv for inv in invoice_repo.list_invoices_for_user(db, db_user.id)
            if inv.amount_received is not None
        ]
        if not invoices:
            await update.message.reply_text(t(lang, "no_invoices"))
            return
        for inv in invoices:
            asset = inv.asset.symbol if inv.asset else (inv.currency_fiat or "")
            text = (
                f"#{inv.invoice_number}: {inv.amount_received} {asset} — "
                f"{t(lang, f'status_{inv.status}')}"
            )
            await update.message.reply_text(text)


async def my_account(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user = update.effective_user
    lang = resolve_language(user.id)
    await update.message.reply_text(t(lang, "account_info", telegram_id=user.id))


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user = update.effective_user
    lang = resolve_language(user.id)
    await update.message.reply_text(t(lang, "help_text"))

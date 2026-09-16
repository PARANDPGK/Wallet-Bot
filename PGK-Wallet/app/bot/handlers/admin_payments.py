from __future__ import annotations

from sqlalchemy import select

from telegram import Update
from telegram.ext import ContextTypes

from app.bot.handlers.admin_auth import require_admin_session
from app.bot.handlers.common import db_session
from app.database.models import Invoice
from app.database.repositories import wallet_repo
from app.localization.i18n import t

FA = "fa"


async def payments_list(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not await require_admin_session(update, context):
        return
    with db_session() as db:
        q = select(Invoice).order_by(Invoice.created_at.desc()).limit(15)
        invoices = list(db.execute(q).scalars().all())
        if not invoices:
            await update.message.reply_text("فاکتوری ثبت نشده است.")
            return
        for inv in invoices:
            asset = inv.asset.symbol if inv.asset else (inv.currency_fiat or "")
            text = (
                f"#{inv.invoice_number} | {inv.amount_requested} {asset} | "
                f"{t(FA, f'status_{inv.status}')} | {inv.created_at.strftime('%Y-%m-%d %H:%M')}"
            )
            await update.message.reply_text(text)


async def payment_links_list(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not await require_admin_session(update, context):
        return
    settings = context.bot_data["settings"]
    with db_session() as db:
        from app.database.models import InvoiceStatus
        q = select(Invoice).where(
            Invoice.status.in_([InvoiceStatus.PENDING.value, InvoiceStatus.VERIFYING.value])
        ).order_by(Invoice.created_at.desc()).limit(15)
        invoices = list(db.execute(q).scalars().all())
        if not invoices:
            await update.message.reply_text("لینک پرداخت فعالی وجود ندارد.")
            return
        for inv in invoices:
            link = f"https://t.me/{settings.bot_username}?start={inv.payment_token}"
            await update.message.reply_text(f"#{inv.invoice_number}\n{link}")


async def assets_networks_view(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not await require_admin_session(update, context):
        return
    with db_session() as db:
        assets = wallet_repo.list_assets(db, enabled_only=False)
        networks = wallet_repo.list_networks(db, enabled_only=False)
    asset_lines = "\n".join(f"{a.symbol} - {a.name} ({'فعال' if a.enabled else 'غیرفعال'})" for a in assets)
    network_lines = "\n".join(f"{n.code} - {n.name} ({'فعال' if n.enabled else 'غیرفعال'})" for n in networks)
    await update.message.reply_text(f"🪙 ارزها:\n{asset_lines}\n\n🌐 شبکه‌ها:\n{network_lines}")

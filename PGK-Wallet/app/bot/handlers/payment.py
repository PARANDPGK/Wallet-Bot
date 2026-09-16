from __future__ import annotations

import io
import re

from telegram import Update
from telegram.ext import ContextTypes

from app.bot.handlers.common import db_session, get_settings
from app.bot.keyboards.inline_keyboards import invoice_payment_keyboard
from app.database.models import InvoiceKind, InvoiceStatus
from app.database.repositories import invoice_repo
from app.localization.i18n import t
from app.services import invoice_service, notification_service, payment_service
from app.utils.formatting import format_amount, mmss, seconds_remaining
from app.utils.qr import build_payment_uri, generate_qr_png


def _format_invoice_message(lang: str, invoice) -> str:
    minutes, seconds = mmss(seconds_remaining(invoice.expires_at))
    if invoice.kind == InvoiceKind.CRYPTO.value:
        asset = invoice.asset.symbol if invoice.asset else "?"
        network = invoice.network.name if invoice.network else "?"
        address = invoice.wallet.address if invoice.wallet else "?"
        amount = format_amount(invoice.amount_requested, invoice.asset.decimals if invoice.asset else 8)
        lines = [
            t(lang, "invoice_header", invoice_number=invoice.invoice_number),
            "",
            t(lang, "invoice_amount", amount=amount, asset=asset),
            "",
            t(lang, "invoice_network", network=network),
            "",
            t(lang, "invoice_address", address=address),
            "",
            t(lang, "invoice_status_label", status=t(lang, f"status_{invoice.status}")),
            "",
            t(lang, "invoice_expires_in", minutes=minutes, seconds=seconds),
        ]
        return "\n".join(lines)
    else:
        lines = [
            t(lang, "invoice_header", invoice_number=invoice.invoice_number),
            "",
            f"{invoice.amount_requested} {invoice.currency_fiat}",
            "",
            t(lang, "invoice_status_label", status=t(lang, f"status_{invoice.status}")),
        ]
        return "\n".join(lines)


async def show_invoice_by_token(update: Update, context: ContextTypes.DEFAULT_TYPE, token: str, lang: str) -> None:
    with db_session() as db:
        invoice = invoice_repo.get_invoice_by_token(db, token)
        if invoice is None:
            await update.message.reply_text(t(lang, "invoice_not_found"))
            return
        invoice_service.expire_if_needed(db, invoice)
        text = _format_invoice_message(lang, invoice)
        number = invoice.invoice_number
        kind = invoice.kind

    if kind == InvoiceKind.CRYPTO.value:
        await update.message.reply_text(text, reply_markup=invoice_payment_keyboard(lang, number))
    else:
        from app.bot.keyboards.inline_keyboards import fiat_upload_keyboard
        await update.message.reply_text(text, reply_markup=fiat_upload_keyboard(number))


async def handle_copy_address(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()
    number = query.data.split(":", 1)[1]
    with db_session() as db:
        invoice = invoice_repo.get_invoice_by_number(db, number)
        if invoice is None or invoice.wallet is None:
            return
        address = invoice.wallet.address
    # Escape MarkdownV2 special characters so unusual address formats never break rendering.
    escaped = re.sub(r"([_*\[\]()~`>#+\-=|{}.!\\])", r"\\\1", address)
    await query.message.reply_text(f"`{escaped}`", parse_mode="MarkdownV2")


async def handle_show_qr(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()
    number = query.data.split(":", 1)[1]
    with db_session() as db:
        invoice = invoice_repo.get_invoice_by_number(db, number)
        if invoice is None or invoice.wallet is None or invoice.asset is None or invoice.network is None:
            return
        uri = build_payment_uri(invoice.asset.symbol, invoice.network.code, invoice.wallet.address, invoice.amount_requested)
    png_bytes = generate_qr_png(uri)
    await query.message.reply_photo(photo=io.BytesIO(png_bytes))


async def handle_ive_paid(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()
    number = query.data.split(":", 1)[1]
    settings = get_settings(context)
    user = update.effective_user

    with db_session() as db:
        invoice = invoice_repo.get_invoice_by_number(db, number)
        if invoice is None:
            return
        lang = "fa"
        if invoice.user and invoice.user.language:
            lang = invoice.user.language

        if invoice_service.expire_if_needed(db, invoice):
            await query.message.reply_text(t(lang, "invoice_expired"))
            return

        invoice_repo.update_invoice_status(db, invoice, InvoiceStatus.VERIFYING)

    await query.message.reply_text(t(lang, "verifying_payment"))

    status_messages = {
        InvoiceStatus.PAID: "payment_confirmed",
        InvoiceStatus.UNDERPAID: "payment_underpaid",
        InvoiceStatus.OVERPAID: "payment_overpaid",
        InvoiceStatus.MANUAL_REVIEW: "payment_manual_review",
        InvoiceStatus.EXPIRED: "invoice_expired",
    }

    with db_session() as db:
        invoice = invoice_repo.get_invoice_by_number(db, number)
        outcome = await payment_service.verify_invoice_payment(db, invoice, settings)
        final_status = outcome.status
        tx_hash = outcome.transaction.tx_hash if outcome.transaction else "-"
        should_notify_admin = final_status in status_messages
        if should_notify_admin:
            # Access relationships while the session is still open.
            await notification_service.notify_payment_event(
                context.bot, settings, invoice, f"status_{final_status.value}", tx_hash
            )

    if final_status in status_messages:
        await query.message.reply_text(t(lang, status_messages[final_status]))
    else:
        await query.message.reply_text(t(lang, "payment_not_detected"))

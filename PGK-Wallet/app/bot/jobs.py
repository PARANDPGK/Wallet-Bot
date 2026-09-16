"""
PGK Wallet - background payment monitoring.

Periodically checks pending/verifying invoices against the blockchain so
payment detection does not rely solely on the customer pressing "I've Paid".
Uses configurable polling intervals and stops once an invoice reaches a
terminal state.
"""
from __future__ import annotations

from telegram.ext import ContextTypes

from app.bot.handlers.common import db_session
from app.database.models import InvoiceKind, InvoiceStatus
from app.database.repositories import invoice_repo
from app.localization.i18n import t
from app.services import invoice_service, notification_service, payment_service
from app.utils.logging_setup import get_logger

logger = get_logger()

_TERMINAL_MESSAGE_KEYS = {
    InvoiceStatus.PAID: "payment_confirmed",
    InvoiceStatus.UNDERPAID: "payment_underpaid",
    InvoiceStatus.OVERPAID: "payment_overpaid",
    InvoiceStatus.MANUAL_REVIEW: "payment_manual_review",
}


async def poll_pending_invoices(context: ContextTypes.DEFAULT_TYPE) -> None:
    settings = context.bot_data["settings"]

    with db_session() as db:
        pending = [
            inv for inv in invoice_repo.list_pending_invoices(db) if inv.kind == InvoiceKind.CRYPTO.value
        ]
        pending_ids = [inv.id for inv in pending]

    for invoice_id in pending_ids:
        try:
            await _check_one_invoice(context, invoice_id, settings)
        except Exception:
            logger.error(f"Error while polling invoice id={invoice_id}", exc_info=True)


async def _check_one_invoice(context: ContextTypes.DEFAULT_TYPE, invoice_id: int, settings) -> None:
    with db_session() as db:
        invoice = invoice_repo.get_invoice(db, invoice_id)
        if invoice is None:
            return

        if invoice_service.expire_if_needed(db, invoice):
            customer_id = invoice.user.telegram_id if invoice.user else None
            customer_lang = invoice.user.language if invoice.user else "fa"
            number = invoice.invoice_number
            await notification_service.notify_expired(context.bot, settings, invoice)
            if customer_id:
                await notification_service.notify_customer(context.bot, customer_id, t(customer_lang, "invoice_expired"))
            return

        outcome = await payment_service.verify_invoice_payment(db, invoice, settings)
        if outcome.status in _TERMINAL_MESSAGE_KEYS:
            customer_id = invoice.user.telegram_id if invoice.user else None
            customer_lang = invoice.user.language if invoice.user else "fa"
            tx_hash = outcome.transaction.tx_hash if outcome.transaction else "-"
            await notification_service.notify_payment_event(
                context.bot, settings, invoice, f"status_{outcome.status.value}", tx_hash
            )
            if customer_id:
                await notification_service.notify_customer(
                    context.bot, customer_id, t(customer_lang, _TERMINAL_MESSAGE_KEYS[outcome.status])
                )

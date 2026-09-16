from __future__ import annotations

from telegram import Update
from telegram.ext import ContextTypes

from app.bot.handlers.admin_auth import require_admin_session
from app.bot.handlers.common import db_session
from app.database.models import FiatStatus, InvoiceStatus
from app.database.repositories import invoice_repo, misc_repo
from app.localization.i18n import t

FA = "fa"


async def fiat_payments_menu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not await require_admin_session(update, context):
        return
    with db_session() as db:
        from sqlalchemy import select
        from app.database.models import FiatPayment
        q = select(FiatPayment).where(FiatPayment.status == FiatStatus.WAITING_FOR_ADMIN_REVIEW.value)
        pending = list(db.execute(q).scalars().all())
        if not pending:
            await update.message.reply_text("هیچ پرداخت ریالی در انتظار بررسی نیست.")
            return
        for fp in pending:
            invoice = invoice_repo.get_invoice(db, fp.invoice_id)
            from app.bot.keyboards.inline_keyboards import fiat_admin_review_keyboard
            text = t(
                FA, "fiat_new_notification",
                invoice_number=invoice.invoice_number if invoice else "?",
                amount=fp.amount, currency=fp.currency, customer="-",
            )
            await update.message.reply_text(text, reply_markup=fiat_admin_review_keyboard(fp.id))


async def fiat_view_receipt(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()
    fp_id = int(query.data.split(":", 1)[1])
    with db_session() as db:
        from sqlalchemy import select
        from app.database.models import PaymentReceipt
        q = select(PaymentReceipt).where(PaymentReceipt.fiat_payment_id == fp_id).order_by(PaymentReceipt.created_at.desc())
        receipt = db.execute(q).scalars().first()
        if receipt is None:
            await query.message.reply_text("فیشی یافت نشد.")
            return
        path = receipt.file_path
        mime = receipt.mime_type
    with open(path, "rb") as f:
        if mime == "application/pdf":
            await query.message.reply_document(document=f)
        else:
            await query.message.reply_photo(photo=f)


async def fiat_approve(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await _fiat_review(update, context, approve=True)


async def fiat_reject(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await _fiat_review(update, context, approve=False)


async def _fiat_review(update: Update, context: ContextTypes.DEFAULT_TYPE, approve: bool) -> None:
    query = update.callback_query
    await query.answer()
    fp_id = int(query.data.split(":", 1)[1])
    admin = update.effective_user

    with db_session() as db:
        fp = misc_repo.review_fiat_payment(db, fp_id, approve, admin.id)
        if fp is None:
            return
        invoice = invoice_repo.get_invoice(db, fp.invoice_id)
        invoice_repo.update_invoice_status(
            db, invoice, InvoiceStatus.PAID if approve else InvoiceStatus.FAILED, amount_received=fp.amount if approve else None
        )
        misc_repo.log_action(db, action="fiat_payment_approved" if approve else "fiat_payment_rejected",
                              admin_telegram_id=admin.id, entity=invoice.invoice_number)
        customer_telegram_id = invoice.user.telegram_id if invoice.user else None
        customer_lang = invoice.user.language if invoice.user else "fa"

    await query.message.reply_text(t(FA, "fiat_approved" if approve else "fiat_rejected"))

    if customer_telegram_id:
        key = "fiat_customer_approved" if approve else "fiat_customer_rejected"
        try:
            await context.bot.send_message(chat_id=customer_telegram_id, text=t(customer_lang, key))
        except Exception:
            pass

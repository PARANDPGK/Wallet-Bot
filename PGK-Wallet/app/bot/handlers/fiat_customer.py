from __future__ import annotations

from telegram import Update
from telegram.ext import ContextTypes, ConversationHandler

from app.bot.handlers.common import db_session, get_settings
from app.bot.keyboards.inline_keyboards import fiat_admin_review_keyboard
from app.bot.states.states import FIAT_AWAITING_RECEIPT
from app.database.repositories import invoice_repo, misc_repo
from app.localization.i18n import t
from app.services import notification_service
from app.utils.security import is_allowed_receipt, safe_filename

FA = "fa"
RECEIPTS_SUBDIR = "receipts"


async def fiat_upload_start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    await query.answer()
    number = query.data.split(":", 1)[1]
    context.user_data["fiat_invoice_number"] = number
    lang = "fa"
    with db_session() as db:
        invoice = invoice_repo.get_invoice_by_number(db, number)
        if invoice and invoice.user and invoice.user.language:
            lang = invoice.user.language
    await query.message.reply_text(t(lang, "fiat_upload_prompt"))
    return FIAT_AWAITING_RECEIPT


async def fiat_receipt_received(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    from config import RECEIPTS_DIR

    number = context.user_data.get("fiat_invoice_number")
    settings = get_settings(context)
    user = update.effective_user

    document = update.message.document
    photo = update.message.photo[-1] if update.message.photo else None
    file_obj = document or photo
    lang = "fa"

    with db_session() as db:
        invoice = invoice_repo.get_invoice_by_number(db, number) if number else None
        if invoice and invoice.user and invoice.user.language:
            lang = invoice.user.language

    if file_obj is None or invoice is None:
        await update.message.reply_text(t(lang, "generic_error"))
        return ConversationHandler.END

    mime_type = document.mime_type if document else "image/jpeg"
    filename = document.file_name if document else "photo.jpg"
    file_size = file_obj.file_size or 0

    ok, reason = is_allowed_receipt(filename, mime_type, file_size)
    if not ok:
        await update.message.reply_text(t(lang, "generic_error"))
        return ConversationHandler.END

    tg_file = await file_obj.get_file()
    safe_name = safe_filename(filename, unique_prefix=number)
    dest_path = RECEIPTS_DIR / safe_name
    await tg_file.download_to_drive(custom_path=str(dest_path))

    with db_session() as db:
        invoice = invoice_repo.get_invoice_by_number(db, number)
        fiat_payment = misc_repo.get_fiat_payment_for_invoice(db, invoice.id)
        if fiat_payment is None:
            fiat_payment = misc_repo.create_fiat_payment(db, invoice.id, invoice.amount_requested, invoice.currency_fiat or "IRR")
        misc_repo.add_receipt(db, fiat_payment.id, str(dest_path), filename, mime_type, file_size)
        misc_repo.log_action(db, action="fiat_receipt_submitted", entity=invoice.invoice_number)

        text = t(
            FA, "fiat_new_notification",
            invoice_number=invoice.invoice_number,
            amount=fiat_payment.amount,
            currency=fiat_payment.currency,
            customer=f"@{user.username}" if user.username else str(user.id),
        )
        fp_id = fiat_payment.id

    await update.message.reply_text(t(lang, "fiat_receipt_received"))
    await context.bot.send_message(
        chat_id=settings.admin_telegram_id, text=text, reply_markup=fiat_admin_review_keyboard(fp_id)
    )
    context.user_data.pop("fiat_invoice_number", None)
    return ConversationHandler.END


async def fiat_upload_cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data.pop("fiat_invoice_number", None)
    return ConversationHandler.END

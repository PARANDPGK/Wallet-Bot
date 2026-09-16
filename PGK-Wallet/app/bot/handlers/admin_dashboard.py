from __future__ import annotations

from datetime import datetime, timedelta, timezone

from sqlalchemy import select

from telegram import Update
from telegram.ext import ContextTypes

from app.bot.handlers.admin_auth import require_admin_session
from app.bot.handlers.common import db_session
from app.bot.keyboards.reply_keyboards import admin_menu_keyboard
from app.database.models import AdminLoginAttempt, AuditLog, Invoice, InvoiceStatus, User
from app.localization.i18n import t

FA = "fa"


async def dashboard(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not await require_admin_session(update, context):
        return
    await update.message.reply_text(t(FA, "admin_dashboard"), reply_markup=admin_menu_keyboard())


async def reports(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not await require_admin_session(update, context):
        return
    start_of_day = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)

    with db_session() as db:
        q = select(Invoice).where(Invoice.created_at >= start_of_day)
        todays_invoices = list(db.execute(q).scalars().all())

    total = len(todays_invoices)
    paid = sum(1 for i in todays_invoices if i.status == InvoiceStatus.PAID.value)
    pending = sum(1 for i in todays_invoices if i.status in (InvoiceStatus.PENDING.value, InvoiceStatus.VERIFYING.value))
    expired = sum(1 for i in todays_invoices if i.status == InvoiceStatus.EXPIRED.value)

    totals_by_asset: dict[str, float] = {}
    for inv in todays_invoices:
        if inv.status == InvoiceStatus.PAID.value and inv.asset and inv.amount_received:
            totals_by_asset[inv.asset.symbol] = totals_by_asset.get(inv.asset.symbol, 0) + float(inv.amount_received)

    asset_lines = "\n".join(f"{sym}: {amt}" for sym, amt in totals_by_asset.items()) or "—"

    await update.message.reply_text(t(FA, "report_title"))
    await update.message.reply_text(
        t(FA, "report_body", total=total, paid=paid, pending=pending, expired=expired, asset_totals=asset_lines)
    )


async def users_list(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not await require_admin_session(update, context):
        return
    with db_session() as db:
        q = select(User).order_by(User.created_at.desc()).limit(30)
        users = list(db.execute(q).scalars().all())
    if not users:
        await update.message.reply_text("کاربری ثبت نشده است.")
        return
    lines = [f"{u.telegram_id} | @{u.username or '-'} | {u.language}" for u in users]
    await update.message.reply_text("\n".join(lines))


async def notifications_menu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not await require_admin_session(update, context):
        return
    await update.message.reply_text(
        "اعلان‌های مهم به‌صورت خودکار برای شما ارسال می‌شوند: فاکتور جدید، پرداخت، پرداخت ریالی، رویدادهای امنیتی."
    )


async def settings_menu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not await require_admin_session(update, context):
        return
    settings = context.bot_data["settings"]
    text = (
        "⚙️ تنظیمات فعلی\n\n"
        f"سیاست اضافه‌پرداخت: {settings.overpayment_policy}\n"
        f"بازه بررسی پرداخت: {settings.polling_interval_seconds} ثانیه\n"
        f"انقضای پیش‌فرض فاکتور: {settings.invoice_default_expiration_minutes} دقیقه\n"
        f"انقضای نشست ادمین: {settings.admin_session_timeout_minutes} دقیقه\n\n"
        "برای تغییر این مقادیر، فایل .env را ویرایش و ربات را مجدداً راه‌اندازی کنید."
    )
    await update.message.reply_text(text)


async def security_menu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not await require_admin_session(update, context):
        return
    since = datetime.now(timezone.utc) - timedelta(days=1)
    with db_session() as db:
        q = select(AdminLoginAttempt).where(AdminLoginAttempt.created_at >= since).order_by(AdminLoginAttempt.created_at.desc()).limit(20)
        attempts = list(db.execute(q).scalars().all())
        q2 = select(AuditLog).order_by(AuditLog.created_at.desc()).limit(15)
        recent_actions = list(db.execute(q2).scalars().all())

    failed = sum(1 for a in attempts if not a.success)
    lines = [f"🛡 تلاش‌های ورود ۲۴ ساعت اخیر: {len(attempts)} (ناموفق: {failed})", "", "آخرین رویدادها:"]
    for a in recent_actions:
        lines.append(f"- {a.action} | {a.created_at.strftime('%Y-%m-%d %H:%M')}")
    await update.message.reply_text("\n".join(lines))

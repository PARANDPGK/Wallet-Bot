"""
PGK Wallet - notification service.

Centralizes all "notify the admin" / "notify the customer" messaging so
handlers and background jobs don't duplicate formatting logic.
"""
from __future__ import annotations

from telegram import Bot
from telegram.error import TelegramError

from config import Settings
from app.localization.i18n import t
from app.utils.logging_setup import get_logger

logger = get_logger()


async def notify_admin(bot: Bot, settings: Settings, text: str) -> None:
    try:
        await bot.send_message(chat_id=settings.admin_telegram_id, text=text)
    except TelegramError as exc:
        logger.error(f"Failed to notify admin: {exc}")


async def notify_customer(bot: Bot, telegram_id: int, text: str) -> None:
    try:
        await bot.send_message(chat_id=telegram_id, text=text)
    except TelegramError as exc:
        logger.warning(f"Failed to notify customer {telegram_id}: {exc}")


async def notify_new_invoice(bot: Bot, settings: Settings, invoice) -> None:
    text = t("fa", "notify_new_invoice", invoice_number=invoice.invoice_number, amount=invoice.amount_requested,
              asset=invoice.asset.symbol if invoice.asset else invoice.currency_fiat)
    await notify_admin(bot, settings, text)


async def notify_payment_event(bot: Bot, settings: Settings, invoice, status_key: str, tx_hash: str = "-") -> None:
    text = t(
        "fa", "notify_payment_detected",
        invoice_number=invoice.invoice_number,
        amount=invoice.amount_received or invoice.amount_requested,
        asset=invoice.asset.symbol if invoice.asset else "",
        network=invoice.network.name if invoice.network else "",
        wallet=invoice.wallet.label if invoice.wallet else "",
        status=t("fa", status_key),
        tx_hash=tx_hash,
    )
    await notify_admin(bot, settings, text)


async def notify_expired(bot: Bot, settings: Settings, invoice) -> None:
    text = t("fa", "notify_expired", invoice_number=invoice.invoice_number)
    await notify_admin(bot, settings, text)


async def notify_security_event(bot: Bot, settings: Settings, text_key: str, **kwargs) -> None:
    text = t("fa", text_key, **kwargs)
    await notify_admin(bot, settings, text)

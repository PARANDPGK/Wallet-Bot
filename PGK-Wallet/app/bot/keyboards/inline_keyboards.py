from __future__ import annotations

from telegram import InlineKeyboardButton, InlineKeyboardMarkup

from app.localization.i18n import t


def invoice_payment_keyboard(lang: str, invoice_number: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([
        [InlineKeyboardButton(t(lang, "btn_copy_address"), callback_data=f"copyaddr:{invoice_number}")],
        [InlineKeyboardButton(t(lang, "btn_show_qr"), callback_data=f"showqr:{invoice_number}")],
        [InlineKeyboardButton(t(lang, "btn_paid"), callback_data=f"ivpaid:{invoice_number}")],
    ])


def fiat_upload_keyboard(invoice_number: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([[InlineKeyboardButton("📤 Upload receipt", callback_data=f"fiatupload:{invoice_number}")]])


def fiat_admin_review_keyboard(fiat_payment_id: int) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🖼 مشاهده فیش", callback_data=f"fiatview:{fiat_payment_id}")],
        [
            InlineKeyboardButton("✅ تأیید پرداخت", callback_data=f"fiatapprove:{fiat_payment_id}"),
            InlineKeyboardButton("❌ رد پرداخت", callback_data=f"fiatreject:{fiat_payment_id}"),
        ],
    ])


def asset_selection_keyboard(assets: list[tuple[int, str]], prefix: str) -> InlineKeyboardMarkup:
    rows = [[InlineKeyboardButton(symbol, callback_data=f"{prefix}:{asset_id}")] for asset_id, symbol in assets]
    return InlineKeyboardMarkup(rows)


def network_selection_keyboard(networks: list[tuple[int, str]], prefix: str) -> InlineKeyboardMarkup:
    rows = [[InlineKeyboardButton(name, callback_data=f"{prefix}:{net_id}")] for net_id, name in networks]
    return InlineKeyboardMarkup(rows)


def wallet_selection_keyboard(wallets: list[tuple[int, str]], prefix: str) -> InlineKeyboardMarkup:
    rows = [[InlineKeyboardButton(label, callback_data=f"{prefix}:{wallet_id}")] for wallet_id, label in wallets]
    return InlineKeyboardMarkup(rows)


def wallet_actions_keyboard(wallet_id: int) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🔄 بروزرسانی موجودی", callback_data=f"walletrefresh:{wallet_id}")],
        [InlineKeyboardButton("⛔ غیرفعال کردن", callback_data=f"walletdisable:{wallet_id}")],
    ])


def pagination_keyboard(prefix: str, page: int, has_next: bool) -> InlineKeyboardMarkup:
    buttons = []
    if page > 0:
        buttons.append(InlineKeyboardButton("◀️", callback_data=f"{prefix}:{page - 1}"))
    if has_next:
        buttons.append(InlineKeyboardButton("▶️", callback_data=f"{prefix}:{page + 1}"))
    return InlineKeyboardMarkup([buttons]) if buttons else InlineKeyboardMarkup([])

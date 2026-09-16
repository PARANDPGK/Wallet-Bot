from __future__ import annotations

from telegram import KeyboardButton, ReplyKeyboardMarkup

from app.localization.i18n import t


def language_selection_keyboard() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        [[KeyboardButton("🇬🇧 English"), KeyboardButton("🇮🇷 فارسی")]],
        resize_keyboard=True,
        one_time_keyboard=True,
    )


def customer_menu_keyboard(lang: str) -> ReplyKeyboardMarkup:
    rows = [
        [t(lang, "menu_my_payments"), t(lang, "menu_my_invoices")],
        [t(lang, "menu_my_account"), t(lang, "menu_language")],
        [t(lang, "menu_help")],
    ]
    return ReplyKeyboardMarkup(rows, resize_keyboard=True)


ADMIN_MENU_ROWS = [
    ["🏠 داشبورد", "🧾 ساخت فاکتور"],
    ["💳 پرداخت‌ها", "🔗 لینک‌های پرداخت"],
    ["👛 کیف‌پول‌ها", "🪙 ارزها و شبکه‌ها"],
    ["📊 آمار و گزارشات", "👥 کاربران"],
    ["💵 پرداخت‌های ریالی", "🔔 اعلان‌ها"],
    ["⚙️ تنظیمات", "🛡 امنیت"],
    ["🚪 خروج"],
]


def admin_menu_keyboard() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(ADMIN_MENU_ROWS, resize_keyboard=True)


def cancel_keyboard(lang: str = "fa") -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup([[t(lang, "cancel")]], resize_keyboard=True, one_time_keyboard=True)

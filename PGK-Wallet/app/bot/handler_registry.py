"""
PGK Wallet - handler registration.

Keeps main.py thin: all Telegram wiring lives here.
"""
from __future__ import annotations

from telegram.ext import (
    Application, CallbackQueryHandler, CommandHandler, ConversationHandler,
    MessageHandler, filters,
)

from app.bot.handlers import (
    admin_auth, admin_dashboard, admin_fiat, admin_invoice, admin_payments,
    admin_wallet, customer, fiat_customer, payment, start,
)
from app.bot.handlers.common import error_handler
from app.bot.states.states import (
    ADMIN_AWAITING_PASSWORD, FIAT_AWAITING_RECEIPT, INVOICE_AMOUNT, INVOICE_ASSET,
    INVOICE_DESCRIPTION, INVOICE_EXPIRATION, INVOICE_NETWORK, INVOICE_WALLET,
    WALLET_ADDRESS, WALLET_ASSET, WALLET_LABEL, WALLET_NETWORK,
)

FA = "fa"


def register_handlers(app: Application) -> None:
    # ---- /start & language ------------------------------------------------
    app.add_handler(CommandHandler("start", start.start_command))
    app.add_handler(MessageHandler(filters.Regex("^(🇬🇧 English|🇮🇷 فارسی)$"), start.language_selected))
    app.add_handler(MessageHandler(filters.Regex("^(🌐 تغییر زبان|🌐 Language)$"), start.change_language_command))

    # ---- Customer menu ------------------------------------------------------
    app.add_handler(MessageHandler(filters.Regex("^(💳 پرداخت‌های من|💳 My Payments)$"), customer.my_payments))
    app.add_handler(MessageHandler(filters.Regex("^(🧾 فاکتورهای من|🧾 My Invoices)$"), customer.my_invoices))
    app.add_handler(MessageHandler(filters.Regex("^(👤 حساب من|👤 My Account)$"), customer.my_account))
    app.add_handler(MessageHandler(filters.Regex("^(ℹ️ راهنما|ℹ️ Help)$"), customer.help_command))

    # ---- Payment page inline callbacks --------------------------------------
    app.add_handler(CallbackQueryHandler(payment.handle_copy_address, pattern=r"^copyaddr:"))
    app.add_handler(CallbackQueryHandler(payment.handle_show_qr, pattern=r"^showqr:"))
    app.add_handler(CallbackQueryHandler(payment.handle_ive_paid, pattern=r"^ivpaid:"))

    # ---- Fiat receipt upload (customer) -------------------------------------
    fiat_conv = ConversationHandler(
        entry_points=[CallbackQueryHandler(fiat_customer.fiat_upload_start, pattern=r"^fiatupload:")],
        states={
            FIAT_AWAITING_RECEIPT: [
                MessageHandler(filters.Document.ALL | filters.PHOTO, fiat_customer.fiat_receipt_received),
            ],
        },
        fallbacks=[CommandHandler("cancel", fiat_customer.fiat_upload_cancel)],
        name="fiat_upload_conversation",
        persistent=False,
    )
    app.add_handler(fiat_conv)

    # ---- Admin login ---------------------------------------------------------
    admin_login_conv = ConversationHandler(
        entry_points=[CommandHandler("admin", admin_auth.admin_entry)],
        states={
            ADMIN_AWAITING_PASSWORD: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, admin_auth.admin_password_received),
            ],
        },
        fallbacks=[CommandHandler("cancel", admin_auth.admin_logout)],
        name="admin_login_conversation",
        persistent=False,
    )
    app.add_handler(admin_login_conv)
    app.add_handler(MessageHandler(filters.Regex("^🚪 خروج$"), admin_auth.admin_logout))

    # ---- Admin dashboard menu -------------------------------------------------
    app.add_handler(MessageHandler(filters.Regex("^🏠 داشبورد$"), admin_dashboard.dashboard))
    app.add_handler(MessageHandler(filters.Regex("^📊 آمار و گزارشات$"), admin_dashboard.reports))
    app.add_handler(MessageHandler(filters.Regex("^👥 کاربران$"), admin_dashboard.users_list))
    app.add_handler(MessageHandler(filters.Regex("^🔔 اعلان‌ها$"), admin_dashboard.notifications_menu))
    app.add_handler(MessageHandler(filters.Regex("^⚙️ تنظیمات$"), admin_dashboard.settings_menu))
    app.add_handler(MessageHandler(filters.Regex("^🛡 امنیت$"), admin_dashboard.security_menu))
    app.add_handler(MessageHandler(filters.Regex("^💳 پرداخت‌ها$"), admin_payments.payments_list))
    app.add_handler(MessageHandler(filters.Regex("^🔗 لینک‌های پرداخت$"), admin_payments.payment_links_list))
    app.add_handler(MessageHandler(filters.Regex("^🪙 ارزها و شبکه‌ها$"), admin_payments.assets_networks_view))
    app.add_handler(MessageHandler(filters.Regex("^💵 پرداخت‌های ریالی$"), admin_fiat.fiat_payments_menu))

    # ---- Admin: create invoice conversation ------------------------------------
    invoice_conv = ConversationHandler(
        entry_points=[MessageHandler(filters.Regex("^🧾 ساخت فاکتور$"), admin_invoice.create_invoice_entry)],
        states={
            INVOICE_AMOUNT: [MessageHandler(filters.TEXT & ~filters.COMMAND, admin_invoice.invoice_amount_received)],
            INVOICE_ASSET: [CallbackQueryHandler(admin_invoice.invoice_asset_selected, pattern=r"^invasset:")],
            INVOICE_NETWORK: [CallbackQueryHandler(admin_invoice.invoice_network_selected, pattern=r"^invnet:")],
            INVOICE_WALLET: [CallbackQueryHandler(admin_invoice.invoice_wallet_selected, pattern=r"^invwallet:")],
            INVOICE_EXPIRATION: [MessageHandler(filters.TEXT & ~filters.COMMAND, admin_invoice.invoice_expiration_received)],
            INVOICE_DESCRIPTION: [MessageHandler(filters.TEXT & ~filters.COMMAND, admin_invoice.invoice_description_received)],
        },
        fallbacks=[MessageHandler(filters.Regex("^❌ لغو$"), admin_invoice.invoice_cancel)],
        name="invoice_creation_conversation",
        persistent=False,
    )
    app.add_handler(invoice_conv)

    # ---- Admin: wallet management ------------------------------------------------
    app.add_handler(MessageHandler(filters.Regex("^👛 کیف‌پول‌ها$"), admin_wallet.wallets_menu))
    wallet_conv = ConversationHandler(
        entry_points=[CommandHandler("addwallet", admin_wallet.add_wallet_entry)],
        states={
            WALLET_ASSET: [CallbackQueryHandler(admin_wallet.wallet_asset_selected, pattern=r"^wasset:")],
            WALLET_NETWORK: [CallbackQueryHandler(admin_wallet.wallet_network_selected, pattern=r"^wnet:")],
            WALLET_ADDRESS: [MessageHandler(filters.TEXT & ~filters.COMMAND, admin_wallet.wallet_address_received)],
            WALLET_LABEL: [MessageHandler(filters.TEXT & ~filters.COMMAND, admin_wallet.wallet_label_received)],
        },
        fallbacks=[MessageHandler(filters.Regex("^❌ لغو$"), admin_wallet.wallet_cancel)],
        name="wallet_creation_conversation",
        persistent=False,
    )
    app.add_handler(wallet_conv)
    app.add_handler(CallbackQueryHandler(admin_wallet.wallet_disable_callback, pattern=r"^walletdisable:"))
    app.add_handler(CallbackQueryHandler(admin_wallet.wallet_refresh_callback, pattern=r"^walletrefresh:"))

    # ---- Admin: fiat payment review -----------------------------------------------
    app.add_handler(CallbackQueryHandler(admin_fiat.fiat_view_receipt, pattern=r"^fiatview:"))
    app.add_handler(CallbackQueryHandler(admin_fiat.fiat_approve, pattern=r"^fiatapprove:"))
    app.add_handler(CallbackQueryHandler(admin_fiat.fiat_reject, pattern=r"^fiatreject:"))

    # ---- Errors ---------------------------------------------------------------------
    app.add_error_handler(error_handler)

from __future__ import annotations

from telegram import Update
from telegram.ext import ContextTypes, ConversationHandler

from app.bot.handlers.admin_auth import require_admin_session
from app.bot.handlers.common import db_session, get_settings
from app.bot.keyboards.inline_keyboards import asset_selection_keyboard, network_selection_keyboard, wallet_selection_keyboard
from app.bot.keyboards.reply_keyboards import admin_menu_keyboard, cancel_keyboard
from app.bot.states.states import (
    INVOICE_AMOUNT, INVOICE_ASSET, INVOICE_DESCRIPTION, INVOICE_EXPIRATION, INVOICE_NETWORK, INVOICE_WALLET,
)
from app.database.repositories import wallet_repo
from app.localization.i18n import t
from app.services import invoice_service

FA = "fa"


async def create_invoice_entry(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    if not await require_admin_session(update, context):
        return ConversationHandler.END
    context.user_data["invoice_draft"] = {}
    await update.message.reply_text(t(FA, "ask_invoice_amount"), reply_markup=cancel_keyboard())
    return INVOICE_AMOUNT


async def invoice_amount_received(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    if update.message.text == t(FA, "cancel"):
        await update.message.reply_text(t(FA, "cancelled"), reply_markup=admin_menu_keyboard())
        return ConversationHandler.END
    try:
        amount = invoice_service.parse_amount(update.message.text)
    except invoice_service.InvalidAmountError:
        await update.message.reply_text(t(FA, "invalid_amount"))
        return INVOICE_AMOUNT
    context.user_data["invoice_draft"]["amount"] = amount

    with db_session() as db:
        assets = wallet_repo.list_assets(db)
        options = [(a.id, a.symbol) for a in assets]
    await update.message.reply_text(t(FA, "ask_invoice_asset"), reply_markup=asset_selection_keyboard(options, "invasset"))
    return INVOICE_ASSET


async def invoice_asset_selected(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    await query.answer()
    asset_id = int(query.data.split(":", 1)[1])
    context.user_data["invoice_draft"]["asset_id"] = asset_id

    with db_session() as db:
        networks = wallet_repo.list_networks(db)
        options = [(n.id, n.name) for n in networks]
    await query.message.reply_text(t(FA, "ask_invoice_network"), reply_markup=network_selection_keyboard(options, "invnet"))
    return INVOICE_NETWORK


async def invoice_network_selected(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    await query.answer()
    network_id = int(query.data.split(":", 1)[1])
    context.user_data["invoice_draft"]["network_id"] = network_id
    asset_id = context.user_data["invoice_draft"]["asset_id"]

    with db_session() as db:
        wallets = wallet_repo.wallets_for_asset_network(db, asset_id, network_id)
        options = [(w.id, w.label) for w in wallets]

    if not options:
        await query.message.reply_text(t(FA, "no_wallets_for_pair"), reply_markup=admin_menu_keyboard())
        return ConversationHandler.END

    await query.message.reply_text(t(FA, "ask_invoice_wallet"), reply_markup=wallet_selection_keyboard(options, "invwallet"))
    return INVOICE_WALLET


async def invoice_wallet_selected(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    await query.answer()
    wallet_id = int(query.data.split(":", 1)[1])
    context.user_data["invoice_draft"]["wallet_id"] = wallet_id
    await query.message.reply_text(t(FA, "ask_invoice_expiration"), reply_markup=cancel_keyboard())
    return INVOICE_EXPIRATION


async def invoice_expiration_received(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    if update.message.text == t(FA, "cancel"):
        await update.message.reply_text(t(FA, "cancelled"), reply_markup=admin_menu_keyboard())
        return ConversationHandler.END
    try:
        minutes = int(update.message.text.strip())
        if minutes <= 0:
            raise ValueError
    except ValueError:
        await update.message.reply_text(t(FA, "invalid_number"))
        return INVOICE_EXPIRATION
    context.user_data["invoice_draft"]["expiration_minutes"] = minutes
    await update.message.reply_text(t(FA, "ask_invoice_description"), reply_markup=cancel_keyboard())
    return INVOICE_DESCRIPTION


async def invoice_description_received(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    text = update.message.text.strip()
    if text == t(FA, "cancel"):
        await update.message.reply_text(t(FA, "cancelled"), reply_markup=admin_menu_keyboard())
        return ConversationHandler.END
    description = None if text in ("رد شود", "-", "") else text
    draft = context.user_data["invoice_draft"]
    settings = get_settings(context)

    with db_session() as db:
        invoice = invoice_service.create_crypto_invoice(
            db,
            amount=draft["amount"],
            asset_id=draft["asset_id"],
            network_id=draft["network_id"],
            wallet_id=draft["wallet_id"],
            expiration_minutes=draft["expiration_minutes"],
            description=description,
        )
        number = invoice.invoice_number
        token = invoice.payment_token

    link = f"https://t.me/{settings.bot_username}?start={token}" if settings.bot_username else "(configure BOT_USERNAME in .env)"
    await update.message.reply_text(
        t(FA, "invoice_created", invoice_number=number, link=link),
        reply_markup=admin_menu_keyboard(),
    )
    context.user_data.pop("invoice_draft", None)
    return ConversationHandler.END


async def invoice_cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.message.reply_text(t(FA, "cancelled"), reply_markup=admin_menu_keyboard())
    context.user_data.pop("invoice_draft", None)
    return ConversationHandler.END

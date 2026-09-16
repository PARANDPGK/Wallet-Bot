from __future__ import annotations

from telegram import Update
from telegram.ext import ContextTypes, ConversationHandler

from app.bot.handlers.admin_auth import require_admin_session
from app.bot.handlers.common import db_session, get_settings
from app.bot.keyboards.inline_keyboards import asset_selection_keyboard, network_selection_keyboard, wallet_actions_keyboard
from app.bot.keyboards.reply_keyboards import admin_menu_keyboard, cancel_keyboard
from app.bot.states.states import WALLET_ADDRESS, WALLET_ASSET, WALLET_LABEL, WALLET_NETWORK
from app.database.repositories import wallet_repo
from app.localization.i18n import t
from app.services import wallet_service
from app.utils.formatting import format_amount

FA = "fa"


async def wallets_menu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not await require_admin_session(update, context):
        return
    with db_session() as db:
        wallets = wallet_repo.list_wallets(db, enabled_only=False)
        if not wallets:
            await update.message.reply_text(t(FA, "no_wallets") + "\n\nبرای افزودن کیف‌پول جدید: /addwallet")
            return
        for w in wallets:
            status = t(FA, "status_active") if w.enabled else t(FA, "status_disabled")
            text = t(
                FA, "wallet_detail", id=w.id, asset=w.asset.symbol, network=w.network.name,
                label=w.label, address=w.address, status=status, balance="—",
            )
            await update.message.reply_text(text, reply_markup=wallet_actions_keyboard(w.id))
        await update.message.reply_text("برای افزودن کیف‌پول جدید: /addwallet")


async def add_wallet_entry(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    if not await require_admin_session(update, context):
        return ConversationHandler.END
    context.user_data["wallet_draft"] = {}
    with db_session() as db:
        assets = wallet_repo.list_assets(db)
        options = [(a.id, a.symbol) for a in assets]
    await update.message.reply_text(t(FA, "ask_wallet_asset"), reply_markup=asset_selection_keyboard(options, "wasset"))
    return WALLET_ASSET


async def wallet_asset_selected(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    await query.answer()
    asset_id = int(query.data.split(":", 1)[1])
    context.user_data["wallet_draft"]["asset_id"] = asset_id
    with db_session() as db:
        networks = wallet_repo.list_networks(db)
        options = [(n.id, n.name) for n in networks]
    await query.message.reply_text(t(FA, "ask_wallet_network"), reply_markup=network_selection_keyboard(options, "wnet"))
    return WALLET_NETWORK


async def wallet_network_selected(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    await query.answer()
    network_id = int(query.data.split(":", 1)[1])
    context.user_data["wallet_draft"]["network_id"] = network_id
    await query.message.reply_text(t(FA, "ask_wallet_address"), reply_markup=cancel_keyboard())
    return WALLET_ADDRESS


async def wallet_address_received(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    if update.message.text == t(FA, "cancel"):
        await update.message.reply_text(t(FA, "cancelled"), reply_markup=admin_menu_keyboard())
        return ConversationHandler.END
    context.user_data["wallet_draft"]["address"] = update.message.text.strip()
    await update.message.reply_text(t(FA, "ask_wallet_label"), reply_markup=cancel_keyboard())
    return WALLET_LABEL


async def wallet_label_received(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    text = update.message.text.strip()
    if text == t(FA, "cancel"):
        await update.message.reply_text(t(FA, "cancelled"), reply_markup=admin_menu_keyboard())
        return ConversationHandler.END
    draft = context.user_data["wallet_draft"]
    user = update.effective_user
    with db_session() as db:
        wallet_service.add_wallet(db, draft["asset_id"], draft["network_id"], draft["address"], text, user.id)
    await update.message.reply_text(t(FA, "wallet_created"), reply_markup=admin_menu_keyboard())
    context.user_data.pop("wallet_draft", None)
    return ConversationHandler.END


async def wallet_cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.message.reply_text(t(FA, "cancelled"), reply_markup=admin_menu_keyboard())
    context.user_data.pop("wallet_draft", None)
    return ConversationHandler.END


async def wallet_disable_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()
    wallet_id = int(query.data.split(":", 1)[1])
    user = update.effective_user
    with db_session() as db:
        wallet_service.disable_wallet(db, wallet_id, user.id)
    await query.message.reply_text(t(FA, "wallet_disabled"))


async def wallet_refresh_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()
    wallet_id = int(query.data.split(":", 1)[1])
    settings = get_settings(context)
    with db_session() as db:
        wallet = wallet_repo.get_wallet(db, wallet_id)
        if wallet is None:
            return
        balance = await wallet_service.fetch_live_balance(wallet, settings)
        symbol = wallet.asset.symbol
    if balance is None:
        await query.message.reply_text(t(FA, "generic_error"))
        return
    await query.message.reply_text(
        f"{t(FA, 'balance_refreshed')}\n\n{format_amount(balance.balance)} {symbol}"
    )

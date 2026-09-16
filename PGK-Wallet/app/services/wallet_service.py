from __future__ import annotations

from sqlalchemy.orm import Session

from config import Settings
from app.blockchain.base import BlockchainProviderError, WalletBalance
from app.blockchain.factory import get_provider
from app.database.models import Wallet
from app.database.repositories import misc_repo, wallet_repo


def add_wallet(
    db: Session, asset_id: int, network_id: int, address: str, label: str, admin_telegram_id: int
) -> Wallet:
    wallet = wallet_repo.create_wallet(db, asset_id, network_id, address.strip(), label.strip())
    misc_repo.log_action(db, action="add_wallet", admin_telegram_id=admin_telegram_id, entity=str(wallet.id))
    return wallet


def disable_wallet(db: Session, wallet_id: int, admin_telegram_id: int) -> Wallet | None:
    wallet = wallet_repo.disable_wallet(db, wallet_id)
    if wallet:
        misc_repo.log_action(db, action="disable_wallet", admin_telegram_id=admin_telegram_id, entity=str(wallet_id))
    return wallet


async def fetch_live_balance(wallet: Wallet, settings: Settings) -> WalletBalance | None:
    """Fetch balance directly from the blockchain. Never derived from local DB totals."""
    try:
        provider = get_provider(wallet.network.code, settings)
        return await provider.get_wallet_balance(wallet.address, wallet.asset.symbol)
    except BlockchainProviderError:
        return None

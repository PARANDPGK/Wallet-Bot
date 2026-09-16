from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database.models import Asset, Network, Wallet


def list_assets(db: Session, enabled_only: bool = True) -> list[Asset]:
    q = select(Asset)
    if enabled_only:
        q = q.where(Asset.enabled.is_(True))
    return list(db.execute(q).scalars().all())


def list_networks(db: Session, enabled_only: bool = True) -> list[Network]:
    q = select(Network)
    if enabled_only:
        q = q.where(Network.enabled.is_(True))
    return list(db.execute(q).scalars().all())


def get_asset_by_symbol(db: Session, symbol: str) -> Asset | None:
    return db.execute(select(Asset).where(Asset.symbol == symbol.upper())).scalar_one_or_none()


def get_network_by_code(db: Session, code: str) -> Network | None:
    return db.execute(select(Network).where(Network.code == code.lower())).scalar_one_or_none()


def create_wallet(
    db: Session, asset_id: int, network_id: int, address: str, label: str
) -> Wallet:
    wallet = Wallet(asset_id=asset_id, network_id=network_id, address=address, label=label, enabled=True)
    db.add(wallet)
    db.flush()
    return wallet


def list_wallets(db: Session, enabled_only: bool = True) -> list[Wallet]:
    q = select(Wallet)
    if enabled_only:
        q = q.where(Wallet.enabled.is_(True))
    return list(db.execute(q).scalars().all())


def get_wallet(db: Session, wallet_id: int) -> Wallet | None:
    return db.get(Wallet, wallet_id)


def update_wallet(db: Session, wallet_id: int, **fields) -> Wallet | None:
    wallet = db.get(Wallet, wallet_id)
    if wallet is None:
        return None
    for key, value in fields.items():
        if value is not None:
            setattr(wallet, key, value)
    wallet.updated_at = datetime.now(timezone.utc)
    return wallet


def disable_wallet(db: Session, wallet_id: int) -> Wallet | None:
    return update_wallet(db, wallet_id, enabled=False)


def wallets_for_asset_network(db: Session, asset_id: int, network_id: int) -> list[Wallet]:
    q = select(Wallet).where(
        Wallet.asset_id == asset_id, Wallet.network_id == network_id, Wallet.enabled.is_(True)
    )
    return list(db.execute(q).scalars().all())

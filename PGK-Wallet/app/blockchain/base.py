"""
PGK Wallet - blockchain provider abstraction.

Every network-specific provider (BTC, ETH, TRON, TON) implements this
interface, so business logic never depends on a specific chain or API.
"""
from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal


class BlockchainProviderError(Exception):
    """Raised when a provider cannot fulfil a request (network/API failure)."""


@dataclass
class TransactionInfo:
    tx_hash: str
    transfer_index: str  # "0" for native transfers; log index for token transfers
    from_address: str | None
    to_address: str
    amount: Decimal
    confirmations: int
    succeeded: bool
    block_time: datetime | None
    asset_symbol: str


@dataclass
class WalletBalance:
    address: str
    asset_symbol: str
    balance: Decimal


class BlockchainProvider(ABC):
    """Common interface for all network providers."""

    network_code: str

    @abstractmethod
    async def get_transactions_for_address(
        self, address: str, asset_symbol: str, since: datetime | None = None
    ) -> list[TransactionInfo]:
        """Return recent incoming transactions to `address` for the given asset."""

    @abstractmethod
    async def get_transaction(self, tx_hash: str, asset_symbol: str) -> TransactionInfo | None:
        """Look up a single transaction by hash."""

    async def verify_transaction(
        self,
        tx_hash: str,
        asset_symbol: str,
        expected_address: str,
        expected_amount: Decimal,
        min_confirmations: int,
    ) -> tuple[bool, TransactionInfo | None, str]:
        """
        Generic verification: fetch tx, then check destination/status/confirmations.
        Amount comparison (exact/under/over) is left to the payment service,
        which returns the TransactionInfo for that purpose.
        """
        tx = await self.get_transaction(tx_hash, asset_symbol)
        if tx is None:
            return False, None, "not_found"
        if tx.to_address.lower() != expected_address.lower():
            return False, tx, "wrong_destination"
        if not tx.succeeded:
            return False, tx, "failed"
        if tx.confirmations < min_confirmations:
            return False, tx, "insufficient_confirmations"
        return True, tx, "ok"

    @abstractmethod
    async def get_wallet_balance(self, address: str, asset_symbol: str) -> WalletBalance:
        """Fetch current on-chain balance for `address`."""

    @abstractmethod
    async def get_confirmations(self, tx_hash: str) -> int:
        """Return the number of confirmations for a given transaction hash."""

    async def get_native_balance(self, address: str) -> WalletBalance:
        """Balance of the network's native coin (used e.g. for gas checks)."""
        raise NotImplementedError

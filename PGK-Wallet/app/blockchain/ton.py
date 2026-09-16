"""
PGK Wallet - TON provider (TonCenter API).

Docs: https://toncenter.com/api/v2/
"""
from __future__ import annotations

from datetime import datetime, timezone
from decimal import Decimal

import httpx

from app.blockchain.base import BlockchainProvider, BlockchainProviderError, TransactionInfo, WalletBalance

NANOTON_PER_TON = Decimal(10) ** 9
TON_FINALITY_CONFIRMATIONS = 1  # TON finalizes quickly; a transaction visible on masterchain is final


class TONProvider(BlockchainProvider):
    network_code = "ton"

    def __init__(self, api_url: str, api_key: str = "", timeout: float = 15.0):
        self.api_url = api_url.rstrip("/")
        self.api_key = api_key
        self.timeout = timeout

    async def _get(self, path: str, params: dict | None = None) -> dict:
        url = f"{self.api_url}{path}"
        headers = {"X-API-Key": self.api_key} if self.api_key else {}
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                resp = await client.get(url, params=params or {}, headers=headers)
        except httpx.HTTPError as exc:
            raise BlockchainProviderError(f"TON provider request failed: {exc}") from exc
        if resp.status_code >= 400:
            raise BlockchainProviderError(f"TON provider returned HTTP {resp.status_code}")
        return resp.json()

    async def get_transactions_for_address(
        self, address: str, asset_symbol: str, since=None
    ) -> list[TransactionInfo]:
        if asset_symbol.upper() != "TON":
            raise BlockchainProviderError("TONProvider only supports native TON")
        data = await self._get("/getTransactions", params={"address": address, "limit": 30})
        rows = data.get("result") or []
        results = []
        for tx in rows:
            in_msg = tx.get("in_msg") or {}
            value = in_msg.get("value")
            source = in_msg.get("source")
            if not value or not source:
                continue  # not an incoming payment
            tx_hash = tx.get("transaction_id", {}).get("hash", "")
            amount = Decimal(value) / NANOTON_PER_TON
            utime = tx.get("utime")
            results.append(TransactionInfo(
                tx_hash=tx_hash, transfer_index="0",
                from_address=source, to_address=address,
                amount=amount, confirmations=TON_FINALITY_CONFIRMATIONS,
                succeeded=True,
                block_time=datetime.fromtimestamp(utime, tz=timezone.utc) if utime else None,
                asset_symbol="TON",
            ))
        return results

    async def get_transaction(self, tx_hash: str, asset_symbol: str) -> TransactionInfo | None:
        # TonCenter does not offer a simple global hash lookup on the free tier;
        # callers should use get_transactions_for_address + hash matching instead.
        raise NotImplementedError(
            "Direct hash lookup is not supported for TON on the free API tier; "
            "use get_transactions_for_address and match by tx_hash."
        )

    async def get_transaction_matching_hash(
        self, address: str, tx_hash: str
    ) -> TransactionInfo | None:
        txs = await self.get_transactions_for_address(address, "TON")
        for tx in txs:
            if tx.tx_hash == tx_hash:
                return tx
        return None

    async def get_wallet_balance(self, address: str, asset_symbol: str) -> WalletBalance:
        if asset_symbol.upper() != "TON":
            raise BlockchainProviderError("TONProvider only supports native TON")
        data = await self._get("/getAddressBalance", params={"address": address})
        balance = Decimal(data.get("result", 0)) / NANOTON_PER_TON
        return WalletBalance(address=address, asset_symbol="TON", balance=balance)

    async def get_confirmations(self, tx_hash: str) -> int:
        # TON transactions are final once included; treat any found tx as confirmed.
        return TON_FINALITY_CONFIRMATIONS

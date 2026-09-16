"""
PGK Wallet - TRON provider (Tronscan public API).

Docs: https://docs.tronscan.org/api-endpoints
"""
from __future__ import annotations

from datetime import datetime, timezone
from decimal import Decimal

import httpx

from app.blockchain.base import BlockchainProvider, BlockchainProviderError, TransactionInfo, WalletBalance

SUN_PER_TRX = Decimal(10) ** 6
TRON_REQUIRED_CONFIRMATIONS_BLOCKS = 19  # TRON finality is fast; treat "confirmed" flag as source of truth


class TRXProvider(BlockchainProvider):
    network_code = "tron"

    def __init__(self, api_url: str, timeout: float = 15.0):
        self.api_url = api_url.rstrip("/")
        self.timeout = timeout

    async def _get(self, path: str, params: dict | None = None) -> dict:
        url = f"{self.api_url}{path}"
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                resp = await client.get(url, params=params or {})
        except httpx.HTTPError as exc:
            raise BlockchainProviderError(f"TRON provider request failed: {exc}") from exc
        if resp.status_code >= 400:
            raise BlockchainProviderError(f"TRON provider returned HTTP {resp.status_code}")
        return resp.json()

    async def get_transactions_for_address(
        self, address: str, asset_symbol: str, since=None
    ) -> list[TransactionInfo]:
        if asset_symbol.upper() != "TRX":
            raise BlockchainProviderError("TRXProvider (v1) only supports native TRX")
        data = await self._get("/transaction", params={"address": address, "limit": 50, "sort": "-timestamp"})
        rows = data.get("data") or []
        results = []
        for tx in rows:
            if tx.get("toAddress") != address:
                continue
            contract_ret = (tx.get("contractRet") or "").upper()
            amount = Decimal(tx.get("amount", 0)) / SUN_PER_TRX
            results.append(TransactionInfo(
                tx_hash=tx.get("hash"), transfer_index="0",
                from_address=tx.get("ownerAddress"), to_address=address,
                amount=amount,
                confirmations=1 if tx.get("confirmed") else 0,
                succeeded=(contract_ret == "SUCCESS") if contract_ret else bool(tx.get("confirmed")),
                block_time=datetime.fromtimestamp(tx["timestamp"] / 1000, tz=timezone.utc) if tx.get("timestamp") else None,
                asset_symbol="TRX",
            ))
        return results

    async def get_transaction(self, tx_hash: str, asset_symbol: str) -> TransactionInfo | None:
        if asset_symbol.upper() != "TRX":
            raise BlockchainProviderError("TRXProvider (v1) only supports native TRX")
        data = await self._get(f"/transaction-info", params={"hash": tx_hash})
        if not data or not data.get("hash"):
            return None
        contract_ret = (data.get("contractRet") or "").upper()
        amount = Decimal(data.get("contractData", {}).get("amount", 0)) / SUN_PER_TRX
        return TransactionInfo(
            tx_hash=data.get("hash"), transfer_index="0",
            from_address=data.get("ownerAddress"),
            to_address=data.get("toAddress", ""),
            amount=amount,
            confirmations=1 if data.get("confirmed") else 0,
            succeeded=(contract_ret == "SUCCESS") if contract_ret else bool(data.get("confirmed")),
            block_time=datetime.fromtimestamp(data["timestamp"] / 1000, tz=timezone.utc) if data.get("timestamp") else None,
            asset_symbol="TRX",
        )

    async def get_wallet_balance(self, address: str, asset_symbol: str) -> WalletBalance:
        if asset_symbol.upper() != "TRX":
            raise BlockchainProviderError("TRXProvider (v1) only supports native TRX")
        data = await self._get("/api/accountv2", params={"address": address})
        balance = Decimal(data.get("balance", 0)) / SUN_PER_TRX
        return WalletBalance(address=address, asset_symbol="TRX", balance=balance)

    async def get_confirmations(self, tx_hash: str) -> int:
        tx = await self.get_transaction(tx_hash, "TRX")
        return tx.confirmations if tx else 0

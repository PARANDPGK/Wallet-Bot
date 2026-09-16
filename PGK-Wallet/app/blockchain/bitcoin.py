"""
PGK Wallet - Bitcoin provider (Blockstream Esplora API).

Docs: https://github.com/Blockstream/esplora/blob/master/API.md
"""
from __future__ import annotations

from datetime import datetime, timezone
from decimal import Decimal

import httpx

from app.blockchain.base import BlockchainProvider, BlockchainProviderError, TransactionInfo, WalletBalance

SATS_PER_BTC = Decimal(10) ** 8


class BTCProvider(BlockchainProvider):
    network_code = "bitcoin"

    def __init__(self, api_url: str, timeout: float = 15.0):
        self.api_url = api_url.rstrip("/")
        self.timeout = timeout

    async def _get(self, path: str) -> httpx.Response:
        url = f"{self.api_url}{path}"
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                resp = await client.get(url)
        except httpx.HTTPError as exc:
            raise BlockchainProviderError(f"BTC provider request failed: {exc}") from exc
        if resp.status_code == 404:
            return resp
        if resp.status_code >= 400:
            raise BlockchainProviderError(f"BTC provider returned HTTP {resp.status_code}")
        return resp

    async def _tip_height(self) -> int:
        resp = await self._get("/blocks/tip/height")
        return int(resp.text)

    def _tx_to_transactions(self, tx: dict, address: str, tip_height: int) -> list[TransactionInfo]:
        """Convert an Esplora tx JSON into TransactionInfo entries for outputs paying `address`."""
        results: list[TransactionInfo] = []
        status = tx.get("status", {})
        confirmed = status.get("confirmed", False)
        confirmations = 0
        block_time = None
        if confirmed:
            block_height = status.get("block_height")
            if block_height is not None:
                confirmations = max(0, tip_height - block_height + 1)
            block_time_ts = status.get("block_time")
            if block_time_ts:
                block_time = datetime.fromtimestamp(block_time_ts, tz=timezone.utc)

        vin_addresses = [
            vin.get("prevout", {}).get("scriptpubkey_address")
            for vin in tx.get("vin", [])
        ]
        from_address = vin_addresses[0] if vin_addresses else None

        for idx, vout in enumerate(tx.get("vout", [])):
            if vout.get("scriptpubkey_address") == address:
                amount = Decimal(vout.get("value", 0)) / SATS_PER_BTC
                results.append(
                    TransactionInfo(
                        tx_hash=tx["txid"],
                        transfer_index=str(idx),
                        from_address=from_address,
                        to_address=address,
                        amount=amount,
                        confirmations=confirmations,
                        succeeded=True,  # Bitcoin transactions in a block are final/successful
                        block_time=block_time,
                        asset_symbol="BTC",
                    )
                )
        return results

    async def get_transactions_for_address(
        self, address: str, asset_symbol: str, since=None
    ) -> list[TransactionInfo]:
        if asset_symbol.upper() != "BTC":
            raise BlockchainProviderError("BTCProvider only supports BTC")
        tip_height = await self._tip_height()
        resp = await self._get(f"/address/{address}/txs")
        txs = resp.json() if resp.status_code == 200 else []
        results: list[TransactionInfo] = []
        for tx in txs:
            results.extend(self._tx_to_transactions(tx, address, tip_height))
        return results

    async def get_transaction(self, tx_hash: str, asset_symbol: str) -> TransactionInfo | None:
        if asset_symbol.upper() != "BTC":
            raise BlockchainProviderError("BTCProvider only supports BTC")
        resp = await self._get(f"/tx/{tx_hash}")
        if resp.status_code == 404:
            return None
        tx = resp.json()
        tip_height = await self._tip_height()
        # Without knowing the destination address in advance, return the first output;
        # payment_service.verify_transaction supplies the expected address and will match accordingly.
        candidates = self._tx_to_transactions(tx, tx["vout"][0]["scriptpubkey_address"], tip_height) if tx.get("vout") else []
        return candidates[0] if candidates else None

    async def get_transaction_matching_address(self, tx_hash: str, address: str) -> TransactionInfo | None:
        resp = await self._get(f"/tx/{tx_hash}")
        if resp.status_code == 404:
            return None
        tx = resp.json()
        tip_height = await self._tip_height()
        matches = self._tx_to_transactions(tx, address, tip_height)
        return matches[0] if matches else None

    async def get_wallet_balance(self, address: str, asset_symbol: str) -> WalletBalance:
        if asset_symbol.upper() != "BTC":
            raise BlockchainProviderError("BTCProvider only supports BTC")
        resp = await self._get(f"/address/{address}")
        data = resp.json()
        funded = Decimal(data["chain_stats"]["funded_txo_sum"])
        spent = Decimal(data["chain_stats"]["spent_txo_sum"])
        balance = (funded - spent) / SATS_PER_BTC
        return WalletBalance(address=address, asset_symbol="BTC", balance=balance)

    async def get_confirmations(self, tx_hash: str) -> int:
        resp = await self._get(f"/tx/{tx_hash}/status")
        status = resp.json()
        if not status.get("confirmed"):
            return 0
        tip_height = await self._tip_height()
        return max(0, tip_height - status["block_height"] + 1)

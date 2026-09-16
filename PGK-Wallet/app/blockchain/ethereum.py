"""
PGK Wallet - Ethereum provider (Etherscan API).

Handles both native ETH transfers and ERC20 token transfers (e.g. DAI).
Docs: https://docs.etherscan.io/
"""
from __future__ import annotations

from datetime import datetime, timezone
from decimal import Decimal

import httpx

from app.blockchain.base import BlockchainProvider, BlockchainProviderError, TransactionInfo, WalletBalance

WEI_PER_ETH = Decimal(10) ** 18

# Well-known ERC20 contracts this system currently supports.
ERC20_CONTRACTS: dict[str, dict] = {
    "DAI": {
        "address": "0x6b175474e89094c44da98b954eedeac495271d0",
        "decimals": 18,
    }
}


class ETHProvider(BlockchainProvider):
    network_code = "ethereum"

    def __init__(self, api_url: str, api_key: str, timeout: float = 15.0):
        self.api_url = api_url
        self.api_key = api_key
        self.timeout = timeout

    async def _get(self, params: dict) -> dict:
        params = {**params, "apikey": self.api_key}
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                resp = await client.get(self.api_url, params=params)
        except httpx.HTTPError as exc:
            raise BlockchainProviderError(f"ETH provider request failed: {exc}") from exc
        if resp.status_code >= 400:
            raise BlockchainProviderError(f"ETH provider returned HTTP {resp.status_code}")
        data = resp.json()
        return data

    async def _current_block(self) -> int:
        data = await self._get({"module": "proxy", "action": "eth_blockNumber"})
        result = data.get("result")
        if not result:
            raise BlockchainProviderError("Could not fetch current ETH block number")
        return int(result, 16)

    async def get_transactions_for_address(
        self, address: str, asset_symbol: str, since=None
    ) -> list[TransactionInfo]:
        symbol = asset_symbol.upper()
        current_block = await self._current_block()

        if symbol == "ETH":
            data = await self._get({
                "module": "account", "action": "txlist", "address": address,
                "startblock": 0, "endblock": 99999999, "sort": "desc",
            })
            rows = data.get("result") or []
            results = []
            for tx in rows:
                if tx.get("to", "").lower() != address.lower():
                    continue
                confs = current_block - int(tx["blockNumber"]) + 1
                results.append(TransactionInfo(
                    tx_hash=tx["hash"], transfer_index="0",
                    from_address=tx.get("from"), to_address=address,
                    amount=Decimal(tx["value"]) / WEI_PER_ETH,
                    confirmations=max(0, confs),
                    succeeded=tx.get("isError") == "0",
                    block_time=datetime.fromtimestamp(int(tx["timeStamp"]), tz=timezone.utc),
                    asset_symbol="ETH",
                ))
            return results

        if symbol in ERC20_CONTRACTS:
            contract = ERC20_CONTRACTS[symbol]
            data = await self._get({
                "module": "account", "action": "tokentx", "address": address,
                "contractaddress": contract["address"], "startblock": 0,
                "endblock": 99999999, "sort": "desc",
            })
            rows = data.get("result") or []
            results = []
            for tx in rows:
                if tx.get("to", "").lower() != address.lower():
                    continue
                confs = current_block - int(tx["blockNumber"]) + 1
                decimals = int(tx.get("tokenDecimal", contract["decimals"]))
                results.append(TransactionInfo(
                    tx_hash=tx["hash"], transfer_index=tx.get("logIndex", "0"),
                    from_address=tx.get("from"), to_address=address,
                    amount=Decimal(tx["value"]) / (Decimal(10) ** decimals),
                    confirmations=max(0, confs),
                    succeeded=True,  # only successful transfers emit a Transfer log
                    block_time=datetime.fromtimestamp(int(tx["timeStamp"]), tz=timezone.utc),
                    asset_symbol=symbol,
                ))
            return results

        raise BlockchainProviderError(f"Unsupported asset on Ethereum: {asset_symbol}")

    async def get_transaction(self, tx_hash: str, asset_symbol: str) -> TransactionInfo | None:
        symbol = asset_symbol.upper()
        receipt = await self._get({
            "module": "proxy", "action": "eth_getTransactionReceipt", "txhash": tx_hash,
        })
        result = receipt.get("result")
        if not result:
            return None
        succeeded = result.get("status") == "0x1"
        current_block = await self._current_block()
        tx_block = int(result["blockNumber"], 16)
        confirmations = max(0, current_block - tx_block + 1)

        tx_data = await self._get({"module": "proxy", "action": "eth_getTransactionByHash", "txhash": tx_hash})
        tx_result = tx_data.get("result") or {}
        block_data = await self._get({
            "module": "proxy", "action": "eth_getBlockByNumber",
            "tag": result["blockNumber"], "boolean": "false",
        })
        ts_hex = (block_data.get("result") or {}).get("timestamp")
        block_time = datetime.fromtimestamp(int(ts_hex, 16), tz=timezone.utc) if ts_hex else None

        if symbol == "ETH":
            value = Decimal(int(tx_result.get("value", "0x0"), 16)) / WEI_PER_ETH
            return TransactionInfo(
                tx_hash=tx_hash, transfer_index="0",
                from_address=tx_result.get("from"), to_address=tx_result.get("to", ""),
                amount=value, confirmations=confirmations, succeeded=succeeded,
                block_time=block_time, asset_symbol="ETH",
            )

        if symbol in ERC20_CONTRACTS:
            contract = ERC20_CONTRACTS[symbol]
            transfer_topic = "0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef"
            for log in result.get("logs", []):
                if log.get("address", "").lower() != contract["address"].lower():
                    continue
                topics = log.get("topics", [])
                if not topics or topics[0].lower() != transfer_topic:
                    continue
                to_addr = "0x" + topics[2][-40:] if len(topics) > 2 else None
                from_addr = "0x" + topics[1][-40:] if len(topics) > 1 else None
                amount = Decimal(int(log.get("data", "0x0"), 16)) / (Decimal(10) ** contract["decimals"])
                return TransactionInfo(
                    tx_hash=tx_hash, transfer_index=str(int(log.get("logIndex", "0x0"), 16)),
                    from_address=from_addr, to_address=to_addr or "",
                    amount=amount, confirmations=confirmations, succeeded=succeeded,
                    block_time=block_time, asset_symbol=symbol,
                )
            return None

        raise BlockchainProviderError(f"Unsupported asset on Ethereum: {asset_symbol}")

    async def get_wallet_balance(self, address: str, asset_symbol: str) -> WalletBalance:
        symbol = asset_symbol.upper()
        if symbol == "ETH":
            data = await self._get({"module": "account", "action": "balance", "address": address, "tag": "latest"})
            balance = Decimal(data.get("result", "0")) / WEI_PER_ETH
            return WalletBalance(address=address, asset_symbol="ETH", balance=balance)
        if symbol in ERC20_CONTRACTS:
            contract = ERC20_CONTRACTS[symbol]
            data = await self._get({
                "module": "account", "action": "tokenbalance", "address": address,
                "contractaddress": contract["address"], "tag": "latest",
            })
            balance = Decimal(data.get("result", "0")) / (Decimal(10) ** contract["decimals"])
            return WalletBalance(address=address, asset_symbol=symbol, balance=balance)
        raise BlockchainProviderError(f"Unsupported asset on Ethereum: {asset_symbol}")

    async def get_confirmations(self, tx_hash: str) -> int:
        receipt = await self._get({"module": "proxy", "action": "eth_getTransactionReceipt", "txhash": tx_hash})
        result = receipt.get("result")
        if not result:
            return 0
        current_block = await self._current_block()
        tx_block = int(result["blockNumber"], 16)
        return max(0, current_block - tx_block + 1)

    async def get_native_balance(self, address: str) -> WalletBalance:
        return await self.get_wallet_balance(address, "ETH")

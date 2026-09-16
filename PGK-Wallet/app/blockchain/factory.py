from __future__ import annotations

from config import Settings

from app.blockchain.base import BlockchainProvider, BlockchainProviderError
from app.blockchain.bitcoin import BTCProvider
from app.blockchain.ethereum import ETHProvider
from app.blockchain.ton import TONProvider
from app.blockchain.tron import TRXProvider

# Only networks with a real, implemented verification provider are enabled.
# Adding a new network later means: implement a provider + register it here.
SUPPORTED_NETWORKS = {"bitcoin", "ethereum", "tron", "ton"}


def get_provider(network_code: str, settings: Settings) -> BlockchainProvider:
    code = network_code.lower()
    if code == "bitcoin":
        return BTCProvider(api_url=settings.btc_api_url)
    if code == "ethereum":
        return ETHProvider(api_url=settings.etherscan_api_url, api_key=settings.etherscan_api_key)
    if code == "tron":
        return TRXProvider(api_url=settings.tron_api_url)
    if code == "ton":
        return TONProvider(api_url=settings.ton_api_url, api_key=settings.ton_api_key)
    raise BlockchainProviderError(
        f"Network '{network_code}' has no verification implementation and cannot be enabled."
    )

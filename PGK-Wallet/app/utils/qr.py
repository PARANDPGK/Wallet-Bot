"""
PGK Wallet - QR code generation for crypto payment addresses.

Uses standardized payment URI schemes where they exist, falling back to
the bare address otherwise. Never encodes incorrect amount/network data.
"""
from __future__ import annotations

import io
from decimal import Decimal

import qrcode


def build_payment_uri(asset_symbol: str, network_code: str, address: str, amount: Decimal) -> str:
    symbol = asset_symbol.upper()
    network = network_code.lower()

    if symbol == "BTC" and network == "bitcoin":
        return f"bitcoin:{address}?amount={amount}"

    if network == "ethereum" and symbol == "ETH":
        # value in wei
        wei = int(amount * Decimal(10) ** 18)
        return f"ethereum:{address}?value={wei}"

    if network == "ton" and symbol == "TON":
        nano = int(amount * Decimal(10) ** 9)
        return f"ton://transfer/{address}?amount={nano}"

    if network == "tron" and symbol == "TRX":
        return f"tron:{address}?amount={amount}"

    # No standardized URI for this asset/network (e.g. ERC20 tokens like DAI) -> plain address.
    return address


def generate_qr_png(data: str) -> bytes:
    img = qrcode.make(data)
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return buf.getvalue()

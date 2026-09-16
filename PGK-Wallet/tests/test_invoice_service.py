from datetime import datetime, timedelta, timezone
from decimal import Decimal

import pytest

from app.database.models import InvoiceStatus
from app.database.repositories import invoice_repo, wallet_repo
from app.services import invoice_service


def test_parse_amount_accepts_valid_decimal():
    assert invoice_service.parse_amount("12.5") == Decimal("12.5")


def test_parse_amount_strips_thousands_separators():
    assert invoice_service.parse_amount("1,250.75") == Decimal("1250.75")


@pytest.mark.parametrize("raw", ["abc", "-5", "0", ""])
def test_parse_amount_rejects_invalid_input(raw):
    with pytest.raises(invoice_service.InvalidAmountError):
        invoice_service.parse_amount(raw)


def test_create_crypto_invoice_generates_unique_number_and_token(db):
    asset = wallet_repo.get_asset_by_symbol(db, "BTC")
    network = wallet_repo.get_network_by_code(db, "bitcoin")
    wallet = wallet_repo.create_wallet(db, asset.id, network.id, "bc1qtestaddress", "Main BTC")

    inv1 = invoice_service.create_crypto_invoice(db, Decimal("0.01"), asset.id, network.id, wallet.id, 30)
    inv2 = invoice_service.create_crypto_invoice(db, Decimal("0.02"), asset.id, network.id, wallet.id, 30)

    assert inv1.invoice_number != inv2.invoice_number
    assert inv1.payment_token != inv2.payment_token
    assert inv1.status == InvoiceStatus.PENDING.value


def test_expire_if_needed_marks_expired_invoice(db):
    asset = wallet_repo.get_asset_by_symbol(db, "BTC")
    network = wallet_repo.get_network_by_code(db, "bitcoin")
    wallet = wallet_repo.create_wallet(db, asset.id, network.id, "bc1qtestaddress", "Main BTC")
    invoice = invoice_service.create_crypto_invoice(db, Decimal("0.01"), asset.id, network.id, wallet.id, 30)

    # Force expiry into the past
    invoice.expires_at = datetime.now(timezone.utc) - timedelta(minutes=1)

    changed = invoice_service.expire_if_needed(db, invoice)
    assert changed is True
    assert invoice.status == InvoiceStatus.EXPIRED.value


def test_expire_if_needed_leaves_active_invoice_untouched(db):
    asset = wallet_repo.get_asset_by_symbol(db, "BTC")
    network = wallet_repo.get_network_by_code(db, "bitcoin")
    wallet = wallet_repo.create_wallet(db, asset.id, network.id, "bc1qtestaddress", "Main BTC")
    invoice = invoice_service.create_crypto_invoice(db, Decimal("0.01"), asset.id, network.id, wallet.id, 30)

    changed = invoice_service.expire_if_needed(db, invoice)
    assert changed is False
    assert invoice.status == InvoiceStatus.PENDING.value

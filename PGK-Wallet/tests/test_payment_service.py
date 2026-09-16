from dataclasses import dataclass
from decimal import Decimal

from app.blockchain.base import TransactionInfo
from app.database.models import InvoiceStatus
from app.database.repositories import invoice_repo, wallet_repo
from app.services import invoice_service, payment_service


@dataclass
class FakeSettings:
    overpayment_policy: str = "manual_review"


def _make_invoice(db, amount: str):
    asset = wallet_repo.get_asset_by_symbol(db, "BTC")
    network = wallet_repo.get_network_by_code(db, "bitcoin")
    wallet = wallet_repo.create_wallet(db, asset.id, network.id, "bc1qtestaddress", "Main BTC")
    return invoice_service.create_crypto_invoice(db, Decimal(amount), asset.id, network.id, wallet.id, 30)


def _tx(amount: str):
    return TransactionInfo(
        tx_hash="deadbeef", transfer_index="0", from_address="sender",
        to_address="bc1qtestaddress", amount=Decimal(amount), confirmations=6,
        succeeded=True, block_time=None, asset_symbol="BTC",
    )


def test_evaluate_amount_exact_match_marks_paid(db):
    invoice = _make_invoice(db, "0.05")
    outcome = payment_service._evaluate_amount(db, invoice, _tx("0.05"), FakeSettings())
    assert outcome.status == InvoiceStatus.PAID
    assert invoice.status == InvoiceStatus.PAID.value
    assert invoice.amount_received == Decimal("0.05")


def test_evaluate_amount_underpaid(db):
    invoice = _make_invoice(db, "0.05")
    outcome = payment_service._evaluate_amount(db, invoice, _tx("0.03"), FakeSettings())
    assert outcome.status == InvoiceStatus.UNDERPAID
    assert invoice.status == InvoiceStatus.UNDERPAID.value


def test_evaluate_amount_overpaid_manual_review_policy(db):
    invoice = _make_invoice(db, "0.05")
    outcome = payment_service._evaluate_amount(db, invoice, _tx("0.10"), FakeSettings(overpayment_policy="manual_review"))
    assert outcome.status == InvoiceStatus.MANUAL_REVIEW


def test_evaluate_amount_overpaid_accept_policy(db):
    invoice = _make_invoice(db, "0.05")
    outcome = payment_service._evaluate_amount(db, invoice, _tx("0.10"), FakeSettings(overpayment_policy="accept_overpay"))
    assert outcome.status == InvoiceStatus.PAID


def test_evaluate_amount_overpaid_record_policy(db):
    invoice = _make_invoice(db, "0.05")
    outcome = payment_service._evaluate_amount(
        db, invoice, _tx("0.10"), FakeSettings(overpayment_policy="mark_paid_record_overpay")
    )
    assert outcome.status == InvoiceStatus.OVERPAID


def test_duplicate_transaction_is_rejected(db):
    invoice1 = _make_invoice(db, "0.05")
    invoice2 = _make_invoice(db, "0.05")

    tx1 = invoice_repo.record_transaction(
        db, tx_hash="sametx", transfer_index="0", network_id=invoice1.network_id,
        asset_id=invoice1.asset_id, to_address="bc1qtestaddress", amount=Decimal("0.05"),
        confirmations=6, block_time=None, from_address="sender", used_for_invoice_id=invoice1.id,
    )
    assert tx1 is not None

    # Attempting to record the exact same tx (hash+index+network) again must fail (return None).
    tx2 = invoice_repo.record_transaction(
        db, tx_hash="sametx", transfer_index="0", network_id=invoice2.network_id,
        asset_id=invoice2.asset_id, to_address="bc1qtestaddress", amount=Decimal("0.05"),
        confirmations=6, block_time=None, from_address="sender", used_for_invoice_id=invoice2.id,
    )
    assert tx2 is None

"""
PGK Wallet - payment verification service.

This is the security-critical core of the bot: a crypto payment is only ever
marked PAID after independent, on-chain verification. Screenshots, user
claims, and manually entered data are never trusted on their own.
"""
from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal

from sqlalchemy.orm import Session

from config import Settings
from app.blockchain.base import BlockchainProviderError, TransactionInfo
from app.blockchain.factory import get_provider
from app.database.models import Invoice, InvoiceStatus
from app.database.repositories import invoice_repo, misc_repo

# Minimum confirmations required per network before a payment is considered final.
MIN_CONFIRMATIONS = {
    "bitcoin": 2,
    "ethereum": 12,
    "tron": 1,   # TRON's "confirmed" flag already reflects solidified/finalized state
    "ton": 1,
}


@dataclass
class VerificationOutcome:
    status: InvoiceStatus
    reason: str
    transaction: TransactionInfo | None = None


async def verify_invoice_payment(db: Session, invoice: Invoice, settings: Settings) -> VerificationOutcome:
    """
    Attempt to find and verify an on-chain payment for `invoice`.
    Never marks PAID without independent blockchain confirmation.
    """
    if invoice_repo.is_expired(invoice):
        return VerificationOutcome(status=InvoiceStatus.EXPIRED, reason="expired")

    if invoice.wallet is None or invoice.network is None or invoice.asset is None:
        return VerificationOutcome(status=InvoiceStatus.FAILED, reason="misconfigured_invoice")

    network_code = invoice.network.code
    try:
        provider = get_provider(network_code, settings)
    except BlockchainProviderError:
        return VerificationOutcome(status=invoice.status, reason="network_not_supported")  # type: ignore[arg-type]

    min_confirmations = MIN_CONFIRMATIONS.get(network_code, 1)
    address = invoice.wallet.address
    asset_symbol = invoice.asset.symbol

    try:
        candidates = await provider.get_transactions_for_address(address, asset_symbol)
    except BlockchainProviderError as exc:
        misc_repo.log_action(db, action="provider_failure", entity=invoice.invoice_number, metadata={"error": str(exc)})
        return VerificationOutcome(status=invoice.status, reason="provider_unavailable")  # type: ignore[arg-type]

    # Only consider transactions created after the invoice was opened.
    created_at = invoice.created_at
    relevant = [
        tx for tx in candidates
        if tx.block_time is None or created_at is None or tx.block_time.replace(tzinfo=None) >= (
            created_at.replace(tzinfo=None) if created_at.tzinfo is None else created_at.astimezone(tz=None).replace(tzinfo=None)
        )
    ] or candidates  # fall back to all candidates if timestamps are unavailable

    if not relevant:
        return VerificationOutcome(status=InvoiceStatus.PENDING, reason="not_found")

    # Prefer a transaction whose amount matches or exceeds the requested amount.
    relevant.sort(key=lambda t: t.amount, reverse=True)
    best_tx = relevant[0]

    # Duplicate protection: has this exact tx already been used for another invoice?
    existing = invoice_repo.find_transaction(db, best_tx.tx_hash, best_tx.transfer_index, invoice.network_id)
    if existing is not None and existing.used_for_invoice_id not in (None, invoice.id):
        return VerificationOutcome(status=InvoiceStatus.PENDING, reason="tx_already_used", transaction=best_tx)

    if not best_tx.succeeded:
        return VerificationOutcome(status=InvoiceStatus.FAILED, reason="tx_failed", transaction=best_tx)

    if best_tx.confirmations < min_confirmations:
        return VerificationOutcome(status=InvoiceStatus.VERIFYING, reason="awaiting_confirmations", transaction=best_tx)

    # Record the transaction (idempotent -- returns None if it already exists).
    recorded = invoice_repo.record_transaction(
        db,
        tx_hash=best_tx.tx_hash,
        transfer_index=best_tx.transfer_index,
        network_id=invoice.network_id,
        asset_id=invoice.asset_id,
        to_address=address,
        amount=best_tx.amount,
        confirmations=best_tx.confirmations,
        block_time=best_tx.block_time,
        from_address=best_tx.from_address,
        used_for_invoice_id=invoice.id,
    )
    if recorded is None:
        # Already recorded (possibly by a previous poll for this same invoice) -- idempotent, re-check status.
        pass

    return _evaluate_amount(db, invoice, best_tx, settings)


def _evaluate_amount(db: Session, invoice: Invoice, tx: TransactionInfo, settings: Settings) -> VerificationOutcome:
    requested: Decimal = invoice.amount_requested
    received: Decimal = tx.amount

    if received < requested:
        invoice_repo.update_invoice_status(db, invoice, InvoiceStatus.UNDERPAID, amount_received=received)
        invoice_repo.create_payment(db, invoice.id, None, received, InvoiceStatus.UNDERPAID.value)
        misc_repo.log_action(db, action="payment_underpaid", entity=invoice.invoice_number)
        return VerificationOutcome(status=InvoiceStatus.UNDERPAID, reason="underpaid", transaction=tx)

    if received == requested:
        invoice_repo.update_invoice_status(db, invoice, InvoiceStatus.PAID, amount_received=received)
        invoice_repo.create_payment(db, invoice.id, None, received, InvoiceStatus.PAID.value)
        misc_repo.log_action(db, action="payment_confirmed", entity=invoice.invoice_number)
        return VerificationOutcome(status=InvoiceStatus.PAID, reason="paid", transaction=tx)

    # received > requested -> apply overpayment policy
    policy = settings.overpayment_policy
    if policy == "accept_overpay":
        invoice_repo.update_invoice_status(db, invoice, InvoiceStatus.PAID, amount_received=received)
        invoice_repo.create_payment(db, invoice.id, None, received, InvoiceStatus.PAID.value)
        misc_repo.log_action(db, action="payment_overpaid_accepted", entity=invoice.invoice_number)
        return VerificationOutcome(status=InvoiceStatus.PAID, reason="overpaid_accepted", transaction=tx)
    if policy == "mark_paid_record_overpay":
        invoice_repo.update_invoice_status(db, invoice, InvoiceStatus.OVERPAID, amount_received=received)
        invoice_repo.create_payment(db, invoice.id, None, received, InvoiceStatus.OVERPAID.value)
        misc_repo.log_action(db, action="payment_overpaid_recorded", entity=invoice.invoice_number)
        return VerificationOutcome(status=InvoiceStatus.OVERPAID, reason="overpaid_recorded", transaction=tx)

    # default: manual_review
    invoice_repo.update_invoice_status(db, invoice, InvoiceStatus.MANUAL_REVIEW, amount_received=received)
    invoice_repo.create_payment(db, invoice.id, None, received, InvoiceStatus.MANUAL_REVIEW.value)
    misc_repo.log_action(db, action="payment_overpaid_manual_review", entity=invoice.invoice_number)
    return VerificationOutcome(status=InvoiceStatus.MANUAL_REVIEW, reason="overpaid_manual_review", transaction=tx)

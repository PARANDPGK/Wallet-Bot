"""
PGK Wallet - invoice lifecycle service.
"""
from __future__ import annotations

from datetime import datetime, timedelta, timezone
from decimal import Decimal, InvalidOperation

from sqlalchemy.orm import Session

from app.database.models import Invoice, InvoiceKind, InvoiceStatus
from app.database.repositories import invoice_repo, misc_repo
from app.utils.security import generate_invoice_number, generate_token


class InvalidAmountError(ValueError):
    pass


def parse_amount(raw: str) -> Decimal:
    raw = raw.strip().replace(",", "")
    try:
        value = Decimal(raw)
    except InvalidOperation as exc:
        raise InvalidAmountError("Invalid amount") from exc
    if value <= 0:
        raise InvalidAmountError("Amount must be positive")
    return value


def create_crypto_invoice(
    db: Session,
    amount: Decimal,
    asset_id: int,
    network_id: int,
    wallet_id: int,
    expiration_minutes: int,
    user_id: int | None = None,
    description: str | None = None,
) -> Invoice:
    number = _unique_invoice_number(db)
    token = generate_token()
    expires_at = datetime.now(timezone.utc) + timedelta(minutes=expiration_minutes)
    invoice = invoice_repo.create_invoice(
        db,
        invoice_number=number,
        payment_token=token,
        kind=InvoiceKind.CRYPTO.value,
        amount_requested=amount,
        expires_at=expires_at,
        user_id=user_id,
        asset_id=asset_id,
        network_id=network_id,
        wallet_id=wallet_id,
        description=description,
    )
    misc_repo.log_action(db, action="create_invoice", entity=number, metadata={"amount": str(amount)})
    return invoice


def create_fiat_invoice(
    db: Session,
    amount: Decimal,
    currency: str,
    expiration_minutes: int,
    user_id: int | None = None,
    description: str | None = None,
) -> Invoice:
    number = _unique_invoice_number(db)
    token = generate_token()
    expires_at = datetime.now(timezone.utc) + timedelta(minutes=expiration_minutes)
    invoice = invoice_repo.create_invoice(
        db,
        invoice_number=number,
        payment_token=token,
        kind=InvoiceKind.FIAT.value,
        amount_requested=amount,
        expires_at=expires_at,
        user_id=user_id,
        currency_fiat=currency,
        description=description,
    )
    misc_repo.log_action(db, action="create_fiat_invoice", entity=number, metadata={"amount": str(amount)})
    return invoice


def _unique_invoice_number(db: Session) -> str:
    for _ in range(20):
        number = generate_invoice_number()
        if invoice_repo.get_invoice_by_number(db, number) is None:
            return number
    raise RuntimeError("Could not generate a unique invoice number")


def expire_if_needed(db: Session, invoice: Invoice) -> bool:
    """Mark invoice as EXPIRED if past expiry and still pending. Returns True if changed."""
    if invoice.status in (InvoiceStatus.PENDING.value, InvoiceStatus.VERIFYING.value) and invoice_repo.is_expired(invoice):
        invoice_repo.update_invoice_status(db, invoice, InvoiceStatus.EXPIRED)
        misc_repo.log_action(db, action="invoice_expired", entity=invoice.invoice_number)
        return True
    return False


def cancel_invoice(db: Session, invoice: Invoice, admin_telegram_id: int) -> None:
    invoice_repo.update_invoice_status(db, invoice, InvoiceStatus.CANCELLED)
    misc_repo.log_action(db, action="cancel_invoice", admin_telegram_id=admin_telegram_id, entity=invoice.invoice_number)

from __future__ import annotations

from datetime import datetime, timezone
from decimal import Decimal

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.database.models import Invoice, InvoiceStatus, Payment, Transaction


def get_invoice_by_token(db: Session, token: str) -> Invoice | None:
    return db.execute(select(Invoice).where(Invoice.payment_token == token)).scalar_one_or_none()


def get_invoice_by_number(db: Session, number: str) -> Invoice | None:
    return db.execute(select(Invoice).where(Invoice.invoice_number == number)).scalar_one_or_none()


def get_invoice(db: Session, invoice_id: int) -> Invoice | None:
    return db.get(Invoice, invoice_id)


def list_invoices_for_user(db: Session, user_id: int, limit: int = 20) -> list[Invoice]:
    q = (
        select(Invoice)
        .where(Invoice.user_id == user_id)
        .order_by(Invoice.created_at.desc())
        .limit(limit)
    )
    return list(db.execute(q).scalars().all())


def list_pending_invoices(db: Session) -> list[Invoice]:
    q = select(Invoice).where(
        Invoice.status.in_([InvoiceStatus.PENDING.value, InvoiceStatus.VERIFYING.value])
    )
    return list(db.execute(q).scalars().all())


def create_invoice(
    db: Session,
    invoice_number: str,
    payment_token: str,
    kind: str,
    amount_requested: Decimal,
    expires_at: datetime,
    user_id: int | None = None,
    asset_id: int | None = None,
    network_id: int | None = None,
    wallet_id: int | None = None,
    currency_fiat: str | None = None,
    description: str | None = None,
) -> Invoice:
    invoice = Invoice(
        invoice_number=invoice_number,
        payment_token=payment_token,
        kind=kind,
        amount_requested=amount_requested,
        expires_at=expires_at,
        user_id=user_id,
        asset_id=asset_id,
        network_id=network_id,
        wallet_id=wallet_id,
        currency_fiat=currency_fiat,
        description=description,
        status=InvoiceStatus.PENDING.value,
    )
    db.add(invoice)
    db.flush()
    return invoice


def update_invoice_status(
    db: Session, invoice: Invoice, status: InvoiceStatus, amount_received: Decimal | None = None
) -> None:
    invoice.status = status.value
    if amount_received is not None:
        invoice.amount_received = amount_received
    invoice.updated_at = datetime.now(timezone.utc)


def is_expired(invoice: Invoice) -> bool:
    now = datetime.now(timezone.utc)
    expires_at = invoice.expires_at
    if expires_at.tzinfo is None:
        expires_at = expires_at.replace(tzinfo=timezone.utc)
    return now > expires_at


# --- Transactions (duplicate protection) -----------------------------------

def find_transaction(db: Session, tx_hash: str, transfer_index: str, network_id: int) -> Transaction | None:
    q = select(Transaction).where(
        Transaction.tx_hash == tx_hash,
        Transaction.transfer_index == transfer_index,
        Transaction.network_id == network_id,
    )
    return db.execute(q).scalar_one_or_none()


def record_transaction(
    db: Session,
    tx_hash: str,
    transfer_index: str,
    network_id: int,
    asset_id: int,
    to_address: str,
    amount: Decimal,
    confirmations: int,
    block_time: datetime | None,
    from_address: str | None,
    used_for_invoice_id: int | None,
) -> Transaction | None:
    """
    Atomically record a transaction. Returns None if this exact transaction
    (hash+transfer_index+network) already exists -> caller must treat as duplicate.
    """
    existing = find_transaction(db, tx_hash, transfer_index, network_id)
    if existing is not None:
        return None
    tx = Transaction(
        tx_hash=tx_hash,
        transfer_index=transfer_index,
        network_id=network_id,
        asset_id=asset_id,
        from_address=from_address,
        to_address=to_address,
        amount=amount,
        confirmations=confirmations,
        block_time=block_time,
        used_for_invoice_id=used_for_invoice_id,
    )
    db.add(tx)
    try:
        db.flush()
    except IntegrityError:
        db.rollback()
        return None
    return tx


def create_payment(db: Session, invoice_id: int, transaction_id: int | None, amount: Decimal, status: str) -> Payment:
    payment = Payment(invoice_id=invoice_id, transaction_id=transaction_id, amount=amount, status=status)
    db.add(payment)
    db.flush()
    return payment

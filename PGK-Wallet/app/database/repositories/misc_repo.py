from __future__ import annotations

import json
from datetime import datetime, timezone
from decimal import Decimal

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database.models import AuditLog, FiatPayment, FiatStatus, PaymentReceipt, Setting


# --- Fiat payments -----------------------------------------------------------

def create_fiat_payment(db: Session, invoice_id: int, amount: Decimal, currency: str = "IRR") -> FiatPayment:
    fp = FiatPayment(invoice_id=invoice_id, amount=amount, currency=currency)
    db.add(fp)
    db.flush()
    return fp


def get_fiat_payment(db: Session, fiat_payment_id: int) -> FiatPayment | None:
    return db.get(FiatPayment, fiat_payment_id)


def get_fiat_payment_for_invoice(db: Session, invoice_id: int) -> FiatPayment | None:
    q = select(FiatPayment).where(FiatPayment.invoice_id == invoice_id).order_by(FiatPayment.created_at.desc())
    return db.execute(q).scalars().first()


def review_fiat_payment(db: Session, fiat_payment_id: int, approve: bool, admin_telegram_id: int) -> FiatPayment | None:
    fp = db.get(FiatPayment, fiat_payment_id)
    if fp is None:
        return None
    fp.status = FiatStatus.APPROVED.value if approve else FiatStatus.REJECTED.value
    fp.reviewed_by = admin_telegram_id
    fp.reviewed_at = datetime.now(timezone.utc)
    return fp


def add_receipt(
    db: Session, fiat_payment_id: int, file_path: str, original_filename: str, mime_type: str, size_bytes: int
) -> PaymentReceipt:
    receipt = PaymentReceipt(
        fiat_payment_id=fiat_payment_id,
        file_path=file_path,
        original_filename=original_filename,
        mime_type=mime_type,
        size_bytes=size_bytes,
    )
    db.add(receipt)
    db.flush()
    return receipt


# --- Audit log ---------------------------------------------------------------

def log_action(
    db: Session,
    action: str,
    admin_telegram_id: int | None = None,
    entity: str | None = None,
    metadata: dict | None = None,
) -> AuditLog:
    entry = AuditLog(
        action=action,
        admin_telegram_id=admin_telegram_id,
        entity=entity,
        metadata_json=json.dumps(metadata, ensure_ascii=False, default=str) if metadata else None,
    )
    db.add(entry)
    db.flush()
    return entry


# --- Settings (key/value) -----------------------------------------------------

def get_setting(db: Session, key: str, default: str | None = None) -> str | None:
    row = db.get(Setting, key)
    return row.value if row else default


def set_setting(db: Session, key: str, value: str) -> None:
    row = db.get(Setting, key)
    if row:
        row.value = value
    else:
        db.add(Setting(key=key, value=value))

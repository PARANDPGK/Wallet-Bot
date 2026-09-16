"""
PGK Wallet - Database models (SQLAlchemy 2.x).
"""
from __future__ import annotations

import enum
from datetime import datetime
from decimal import Decimal

from sqlalchemy import (
    BigInteger, Boolean, DateTime, Enum, ForeignKey, Index, Numeric,
    String, Text, UniqueConstraint, func
)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    pass


# ---------------------------------------------------------------------------
# Enums
# ---------------------------------------------------------------------------

class Language(str, enum.Enum):
    fa = "fa"
    en = "en"


class InvoiceStatus(str, enum.Enum):
    PENDING = "PENDING"
    VERIFYING = "VERIFYING"
    PAID = "PAID"
    UNDERPAID = "UNDERPAID"
    OVERPAID = "OVERPAID"
    EXPIRED = "EXPIRED"
    CANCELLED = "CANCELLED"
    FAILED = "FAILED"
    MANUAL_REVIEW = "MANUAL_REVIEW"


class FiatStatus(str, enum.Enum):
    WAITING_FOR_ADMIN_REVIEW = "WAITING_FOR_ADMIN_REVIEW"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"


class InvoiceKind(str, enum.Enum):
    CRYPTO = "CRYPTO"
    FIAT = "FIAT"


# ---------------------------------------------------------------------------
# Users & sessions
# ---------------------------------------------------------------------------

class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    telegram_id: Mapped[int] = mapped_column(BigInteger, unique=True, index=True, nullable=False)
    username: Mapped[str | None] = mapped_column(String(64), nullable=True)
    language: Mapped[str] = mapped_column(String(8), default=Language.fa.value, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    invoices: Mapped[list["Invoice"]] = relationship(back_populates="user")


class AdminSession(Base):
    __tablename__ = "admin_sessions"

    id: Mapped[int] = mapped_column(primary_key=True)
    session_token: Mapped[str] = mapped_column(String(128), unique=True, index=True, nullable=False)
    admin_telegram_id: Mapped[int] = mapped_column(BigInteger, nullable=False, index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    last_active_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    revoked: Mapped[bool] = mapped_column(Boolean, default=False)


class AdminLoginAttempt(Base):
    __tablename__ = "admin_login_attempts"

    id: Mapped[int] = mapped_column(primary_key=True)
    telegram_id: Mapped[int] = mapped_column(BigInteger, nullable=False, index=True)
    success: Mapped[bool] = mapped_column(Boolean, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


# ---------------------------------------------------------------------------
# Assets / Networks / Wallets
# ---------------------------------------------------------------------------

class Asset(Base):
    __tablename__ = "assets"

    id: Mapped[int] = mapped_column(primary_key=True)
    symbol: Mapped[str] = mapped_column(String(16), unique=True, nullable=False)  # BTC, ETH, TON, TRX, DAI
    name: Mapped[str] = mapped_column(String(64), nullable=False)
    decimals: Mapped[int] = mapped_column(default=8)
    enabled: Mapped[bool] = mapped_column(Boolean, default=True)


class Network(Base):
    __tablename__ = "networks"

    id: Mapped[int] = mapped_column(primary_key=True)
    code: Mapped[str] = mapped_column(String(32), unique=True, nullable=False)  # bitcoin, ethereum, tron, ton
    name: Mapped[str] = mapped_column(String(64), nullable=False)
    enabled: Mapped[bool] = mapped_column(Boolean, default=True)


class Wallet(Base):
    __tablename__ = "wallets"

    id: Mapped[int] = mapped_column(primary_key=True)
    asset_id: Mapped[int] = mapped_column(ForeignKey("assets.id"), nullable=False)
    network_id: Mapped[int] = mapped_column(ForeignKey("networks.id"), nullable=False)
    address: Mapped[str] = mapped_column(String(256), nullable=False)
    label: Mapped[str] = mapped_column(String(128), nullable=False)
    enabled: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    asset: Mapped["Asset"] = relationship()
    network: Mapped["Network"] = relationship()

    __table_args__ = (Index("ix_wallet_asset_network", "asset_id", "network_id"),)


# ---------------------------------------------------------------------------
# Invoices / Payments / Transactions
# ---------------------------------------------------------------------------

class Invoice(Base):
    __tablename__ = "invoices"

    id: Mapped[int] = mapped_column(primary_key=True)
    invoice_number: Mapped[str] = mapped_column(String(32), unique=True, index=True, nullable=False)  # PGK-xxxxx
    payment_token: Mapped[str] = mapped_column(String(128), unique=True, index=True, nullable=False)
    kind: Mapped[str] = mapped_column(String(16), default=InvoiceKind.CRYPTO.value, nullable=False)

    user_id: Mapped[int | None] = mapped_column(ForeignKey("users.id"), nullable=True)

    asset_id: Mapped[int | None] = mapped_column(ForeignKey("assets.id"), nullable=True)
    network_id: Mapped[int | None] = mapped_column(ForeignKey("networks.id"), nullable=True)
    wallet_id: Mapped[int | None] = mapped_column(ForeignKey("wallets.id"), nullable=True)

    amount_requested: Mapped[Decimal] = mapped_column(Numeric(36, 18), nullable=False)
    amount_received: Mapped[Decimal | None] = mapped_column(Numeric(36, 18), nullable=True)

    currency_fiat: Mapped[str | None] = mapped_column(String(8), nullable=True)  # e.g. IRR

    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    status: Mapped[str] = mapped_column(String(24), default=InvoiceStatus.PENDING.value, index=True, nullable=False)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    user: Mapped["User | None"] = relationship(back_populates="invoices")
    asset: Mapped["Asset | None"] = relationship()
    network: Mapped["Network | None"] = relationship()
    wallet: Mapped["Wallet | None"] = relationship()
    payments: Mapped[list["Payment"]] = relationship(back_populates="invoice")


class Payment(Base):
    __tablename__ = "payments"

    id: Mapped[int] = mapped_column(primary_key=True)
    invoice_id: Mapped[int] = mapped_column(ForeignKey("invoices.id"), nullable=False, index=True)
    transaction_id: Mapped[int | None] = mapped_column(ForeignKey("transactions.id"), nullable=True)
    amount: Mapped[Decimal] = mapped_column(Numeric(36, 18), nullable=False)
    status: Mapped[str] = mapped_column(String(24), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    invoice: Mapped["Invoice"] = relationship(back_populates="payments")


class Transaction(Base):
    """An independently-verified on-chain transaction, never reused across invoices."""
    __tablename__ = "transactions"

    id: Mapped[int] = mapped_column(primary_key=True)
    tx_hash: Mapped[str] = mapped_column(String(128), nullable=False)
    transfer_index: Mapped[str] = mapped_column(String(32), default="0", nullable=False)
    network_id: Mapped[int] = mapped_column(ForeignKey("networks.id"), nullable=False)
    asset_id: Mapped[int] = mapped_column(ForeignKey("assets.id"), nullable=False)
    from_address: Mapped[str | None] = mapped_column(String(256), nullable=True)
    to_address: Mapped[str] = mapped_column(String(256), nullable=False)
    amount: Mapped[Decimal] = mapped_column(Numeric(36, 18), nullable=False)
    confirmations: Mapped[int] = mapped_column(default=0)
    block_time: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    used_for_invoice_id: Mapped[int | None] = mapped_column(ForeignKey("invoices.id"), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    __table_args__ = (
        UniqueConstraint("tx_hash", "transfer_index", "network_id", name="uq_tx_hash_transfer_network"),
    )


class FiatPayment(Base):
    __tablename__ = "fiat_payments"

    id: Mapped[int] = mapped_column(primary_key=True)
    invoice_id: Mapped[int] = mapped_column(ForeignKey("invoices.id"), nullable=False, index=True)
    amount: Mapped[Decimal] = mapped_column(Numeric(18, 2), nullable=False)
    currency: Mapped[str] = mapped_column(String(8), default="IRR")
    status: Mapped[str] = mapped_column(String(32), default=FiatStatus.WAITING_FOR_ADMIN_REVIEW.value)
    reviewed_by: Mapped[int | None] = mapped_column(BigInteger, nullable=True)
    reviewed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class PaymentReceipt(Base):
    __tablename__ = "payment_receipts"

    id: Mapped[int] = mapped_column(primary_key=True)
    fiat_payment_id: Mapped[int] = mapped_column(ForeignKey("fiat_payments.id"), nullable=False)
    file_path: Mapped[str] = mapped_column(String(512), nullable=False)
    original_filename: Mapped[str] = mapped_column(String(256), nullable=False)
    mime_type: Mapped[str] = mapped_column(String(64), nullable=False)
    size_bytes: Mapped[int] = mapped_column(nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class AuditLog(Base):
    __tablename__ = "audit_logs"

    id: Mapped[int] = mapped_column(primary_key=True)
    action: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    admin_telegram_id: Mapped[int | None] = mapped_column(BigInteger, nullable=True)
    entity: Mapped[str | None] = mapped_column(String(128), nullable=True)
    metadata_json: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class Setting(Base):
    __tablename__ = "settings"

    key: Mapped[str] = mapped_column(String(64), primary_key=True)
    value: Mapped[str] = mapped_column(Text, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

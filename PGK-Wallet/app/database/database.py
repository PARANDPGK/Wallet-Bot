"""
PGK Wallet - Database engine and session management.
"""
from __future__ import annotations

from contextlib import contextmanager
from typing import Iterator

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from app.database.models import Asset, Base, Network

_engine = None
_SessionLocal: sessionmaker | None = None


def init_engine(database_url: str):
    global _engine, _SessionLocal
    connect_args = {"check_same_thread": False} if database_url.startswith("sqlite") else {}
    kwargs = {}
    if database_url.startswith("sqlite") and ":memory:" in database_url:
        from sqlalchemy.pool import StaticPool
        kwargs["poolclass"] = StaticPool
    _engine = create_engine(database_url, connect_args=connect_args, future=True, **kwargs)
    _SessionLocal = sessionmaker(bind=_engine, autoflush=False, autocommit=False, future=True)
    return _engine


def init_db(database_url: str) -> None:
    """Create tables and seed default assets/networks if missing."""
    engine = init_engine(database_url)
    Base.metadata.create_all(engine)
    _seed_defaults()


def _seed_defaults() -> None:
    default_assets = [
        ("TON", "Toncoin", 9),
        ("DAI", "Dai Stablecoin", 18),
        ("BTC", "Bitcoin", 8),
        ("ETH", "Ethereum", 18),
        ("TRX", "TRON", 6),
    ]
    default_networks = [
        ("ton", "TON"),
        ("ethereum", "Ethereum"),
        ("bitcoin", "Bitcoin"),
        ("tron", "TRON"),
    ]
    with session_scope() as db:
        for symbol, name, decimals in default_assets:
            if not db.query(Asset).filter_by(symbol=symbol).first():
                db.add(Asset(symbol=symbol, name=name, decimals=decimals))
        for code, name in default_networks:
            if not db.query(Network).filter_by(code=code).first():
                db.add(Network(code=code, name=name))


@contextmanager
def session_scope() -> Iterator[Session]:
    """Provide a transactional scope for a series of operations."""
    if _SessionLocal is None:
        raise RuntimeError("Database not initialized. Call init_db() first.")
    db = _SessionLocal()
    try:
        yield db
        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


def get_session() -> Session:
    if _SessionLocal is None:
        raise RuntimeError("Database not initialized. Call init_db() first.")
    return _SessionLocal()

import pytest

from app.database import database as db_module
from app.database.database import init_db, session_scope


@pytest.fixture()
def db():
    """A fresh in-memory SQLite database per test, with default assets/networks seeded."""
    init_db("sqlite:///:memory:")
    with session_scope() as session:
        yield session


@pytest.fixture(autouse=True)
def _reset_engine():
    yield
    db_module._engine = None
    db_module._SessionLocal = None
